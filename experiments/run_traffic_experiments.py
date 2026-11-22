#!/usr/bin/env python3
"""
Realistic traffic: reactive vs proactive under published workloads (Mininet + POX)
CS G525 Advanced Computer Networks - Project SA7

Each scenario pairs a network with the traffic measured in that kind of
network (sources in docs/Realism_Sources.md and experiments/workloads.py):

  tree-d2-f4 : university  - campus / enterprise tree, Benson et al. IMC 2010
  fattree-k4 : websearch   - data centre, DCTCP (SIGCOMM 2010) via pFabric
  fattree-k4 : datamining  - data centre, VL2 (SIGCOMM 2009) via pFabric
  abilene    : isp         - ISP backbone, real Abilene traffic matrices
                             (Zhang et al. IMC 2005), one day replayed;
                             real link speeds (Atlanta-Indianapolis is a
                             quarter of the others) and city-to-city delays

Every host runs a TCP server; flows follow a schedule computed in advance from
the workload (same seed, so every controller gets exactly the same flows). Each
flow: connect, send N bytes, wait for the receiver's 1-byte reply.

Measured per run:
  - flow completion time (FCT) of small (< 100 KB), medium and large (> 10 MB) flows
  - flows that failed (no connection or no reply within --flow-timeout)
  - controller load: PACKET_IN/s, FLOW_MOD/s, controller CPU %
  - rules in the switches during the run (peak total, peak in one switch)

Usage (Mininet needs root):
  sudo python3 experiments/run_traffic_experiments.py            # 4 scenarios, ~12 min
  sudo python3 experiments/run_traffic_experiments.py --quick    # university only, ~2 min
  sudo python3 experiments/run_traffic_experiments.py --scenarios fattree-k4:university
  # Step 4: reactive with long timeouts, budgeted hybrid and oracle at 10/25/50% of pairs
  sudo python3 experiments/run_traffic_experiments.py --scenarios tree-d2-f4:university \
      --budget-sweep --pair-zipf 1        # add --random-baseline for random-10/25/50,
                                          # --granularity-baselines for reactive-pair / reactive-dst
  # 5 runs with different seeds: tables show mean +- 95% confidence interval
  sudo python3 experiments/run_traffic_experiments.py --repeats 5
  # controller on a second PC (start experiments/controller_agent.py there first)
  sudo python3 experiments/run_traffic_experiments.py --controller-host 192.168.1.20
Output: results/measured/traffic-<timestamp>/ (traffic.md, traffic.json, plots).
"""

import argparse
import base64
import json
import os
import random
import re
import signal
import socket
import statistics
import subprocess
import sys
import threading
import time
from functools import partial

from mininet.clean import cleanup
from mininet.link import TCLink
from mininet.log import lg, setLogLevel
from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.topolib import TreeTopo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import path_topologies as pt
import repeats
import workloads as wl
from run_experiments import (CONTROLLER_DIR, OF_PORT, POX_DIR, REPO, LateStartController,
                             cpu_seconds, fresh_stats, log, port_open, read_stats, stop_pox,
                             wait_for, write_topology)
from run_path_experiments import MODE_LABEL, TX_CSUM_OFF, netem_available

# Extra controller modes (Step 4: long timeouts and the budgeted hybrid)
#   reactive-long : reactive learning switch with long timeouts (the SmartTime / AH-IHTA
#                   idea in its simplest form: keep rules longer)
#   reactive-sp   : hybrid_eval with budget 0 = reactive, but on shortest paths
#   reactive-pair : reactive-sp, but each rule matches source + destination MAC, so later flows
#                   of a pair hit it (no prediction; tests whether wildcards alone explain the hybrid)
#   reactive-dst  : the same with the destination MAC only
#   hybrid-NN     : hybrid_eval, weighted counter keeps the top NN% of host pairs pre-installed
#   oracle-NN     : hindsight reference (the best FIXED set with an exact-match fallback; not a bound for
#                   a predictor that changes its set): pre-install the NN% of pairs that really
#                   carry the most flows in this run's schedule, from the start
#   proactive-dst : tap_eval --taps=off: the same destination rules as tap, without the copies
#   tap           : tap_eval: destination rules installed in advance, plus a copy of every TCP
#                   SYN / FIN / RST to the controller from the receiver's switch. No flow waits
#                   and no rule is installed per flow, yet the controller hears of every flow
#   random-NN     : no knowledge: pre-install a random NN% of host pairs (both directions of
#                   each chosen pair), from the start; the baseline a smart choice must beat
MODE_LABEL = dict(MODE_LABEL)
MODE_LABEL.update({'reactive-long': 'Reactive, long timeouts',
                   'reactive-sp': 'Reactive on shortest paths (hybrid, budget 0%)',
                   'reactive-pair': 'Reactive on shortest paths, pair rules',
                   'reactive-dst': 'Reactive on shortest paths, destination rules',
                   'tap': 'Forward first, tell the controller (destination rules + SYN/FIN copies)',
                   'proactive-dst': 'Proactive, one rule per destination (tap without its copy rules)'})
SPANNING_TREE_MODES = ('reactive', 'reactive-long')


def mode_label(mode):
  if mode.startswith('hybrid-'):
    return 'Hybrid, counter keeps top %s%% of pairs' % mode.split('-', 1)[1]
  if mode.startswith('lstm-'):
    return 'Hybrid, LSTM forecasts top %s%% of pairs' % mode.split('-', 1)[1]
  if mode.startswith('oracle-'):
    return 'Oracle, busiest %s%% of pairs (hindsight)' % mode.split('-', 1)[1]
  if mode.startswith('random-'):
    return 'Random %s%% of pairs (no knowledge)' % mode.split('-', 1)[1]
  return MODE_LABEL[mode]


def pox_module(mode, run_dir, tag, topo_file, net_name, args, flows=None, mac_of=None):
  """The POX modules and options (after openflow.of_01) that make up each controller mode."""
  paths = 'ecmp' if 'fattree' in net_name else 'shortest'
  if mode == 'reactive':   # as in run_path_experiments.start_pox
    return ['openflow.discovery', 'openflow.spanning_tree', '--no-flood', '--hold-down',
            'reactive_eval', '--match=exact']
  if mode in ('proactive', 'proactive-ecmp'):
    return ['proactive_eval', '--topo=%s' % topo_file, '--granularity=pair',
            '--paths=%s' % ('ecmp' if mode == 'proactive-ecmp' else 'shortest')]
  if mode == 'proactive-dst':   # tap_eval without its copy rules: proactive, one rule per destination
    return ['tap_eval', '--topo=%s' % topo_file, '--paths=%s' % paths, '--taps=off']
  if mode == 'tap':   # tap_eval: nobody waits, the controller still hears of every TCP connection
    return ['tap_eval', '--topo=%s' % topo_file, '--paths=%s' % paths,
            '--flow_log=%s' % os.path.join(run_dir, '%s-flowlog.jsonl' % tag)]
  if mode == 'reactive-long':
    return ['openflow.discovery', 'openflow.spanning_tree', '--no-flood', '--hold-down',
            'reactive_eval', '--match=exact', '--idle_timeout=%d' % args.long_idle,
            '--hard_timeout=%d' % args.long_hard]
  if (mode in ('reactive-sp', 'reactive-pair', 'reactive-dst') or
      mode.startswith('hybrid-') or mode.startswith('lstm-')):
    budgeted = mode.startswith(('hybrid-', 'lstm-'))
    budget = float(mode.split('-', 1)[1]) / 100.0 if budgeted else 0.0
    match = {'reactive-pair': 'pair', 'reactive-dst': 'dst'}.get(mode, 'exact')
    module = ['hybrid_eval', '--topo=%s' % topo_file, '--budget=%g' % budget,
            '--decay=%g' % args.decay, '--hysteresis=%g' % args.hysteresis, '--paths=%s' % paths,
            '--match=%s' % match, '--strategy=%s' % ('lstm' if mode.startswith('lstm-') else 'counter')]
    if mode.startswith('lstm-'):
      module.append('--model_file=%s' % os.path.abspath(args.lstm_model))
      module.append('--warmup_intervals=%d' % args.lstm_warmup)
    return module
  if mode.startswith('oracle-'):
    counts = {}
    for _, src, dst, _ in flows:   # a TCP flow uses both directions (data, then the reply)
      counts[(src, dst)] = counts.get((src, dst), 0) + 1
      counts[(dst, src)] = counts.get((dst, src), 0) + 1
    n = len(mac_of)
    k = int(round(float(mode.split('-', 1)[1]) / 100.0 * n * (n - 1)))
    pairs_file = os.path.join(run_dir, '%s-pairs.txt' % tag)
    with open(pairs_file, 'w') as f:
      for (src, dst), _ in sorted(counts.items(), key=lambda kv: -kv[1])[:k]:
        f.write('%s %s\n' % (mac_of[src], mac_of[dst]))
    return ['hybrid_eval', '--topo=%s' % topo_file, '--pairs_file=%s' % pairs_file, '--paths=%s' % paths]
  if mode.startswith('random-'):
    # Pairs are drawn as unordered pairs and installed in both directions, because a TCP
    # flow needs both (data, then the reply), as for the oracle. The choice is fixed by the
    # run's tag, so it does not depend on the traffic at all.
    hosts = sorted(mac_of, key=lambda h: int(h[1:]))
    n = len(hosts)
    k = int(round(float(mode.split('-', 1)[1]) / 100.0 * n * (n - 1)))
    unordered = [(a, b) for i, a in enumerate(hosts) for b in hosts[i + 1:]]
    random.Random('%s-random-pairs' % tag).shuffle(unordered)
    chosen = []
    for a, b in unordered:
      if len(chosen) >= k:
        break
      chosen.append((a, b))
      if len(chosen) < k:
        chosen.append((b, a))
    pairs_file = os.path.join(run_dir, '%s-pairs.txt' % tag)
    with open(pairs_file, 'w') as f:
      for src, dst in chosen:
        f.write('%s %s\n' % (mac_of[src], mac_of[dst]))
    return ['hybrid_eval', '--topo=%s' % topo_file, '--pairs_file=%s' % pairs_file, '--paths=%s' % paths]
  raise SystemExit("Unknown mode %s" % mode)


class LocalPox(object):
  """POX on this machine (the default)."""

  def __init__(self, module, run_dir, tag):
    self.stats_file = os.path.join(run_dir, '%s-stats.json' % tag)
    cmd = [sys.executable, os.path.join(POX_DIR, 'pox.py'),
           'openflow.of_01', '--port=%d' % OF_PORT] + module + ['--stats_file=%s' % self.stats_file]
    env = dict(os.environ)
    env['PYTHONPATH'] = CONTROLLER_DIR + os.pathsep + env.get('PYTHONPATH', '')
    logf = open(os.path.join(run_dir, '%s-pox.log' % tag), 'w')
    self.proc = subprocess.Popen(cmd, cwd=POX_DIR, env=env, stdout=logf, stderr=subprocess.STDOUT)
    if (not wait_for(lambda: port_open(OF_PORT) or self.proc.poll() is not None, 20)
        or self.proc.poll() is not None):
      raise RuntimeError("POX did not start - see %s-pox.log" % tag)

  def stats(self):
    return read_stats(self.stats_file)

  def fresh(self):
    """A stats dump written after this call (dumps happen every second)."""
    return fresh_stats(self.stats_file, time.time())

  def cpu_seconds(self):
    return cpu_seconds(self.proc.pid)

  def stop(self):
    stop_pox(self.proc)


def agent_call(host, port, req, timeout=30):
  """One request to experiments/controller_agent.py on the controller PC."""
  with socket.create_connection((host, port), timeout=timeout) as s:
    s.sendall((json.dumps(req) + '\n').encode())
    data = b''
    while not data.endswith(b'\n'):
      chunk = s.recv(1 << 16)
      if not chunk:
        break
      data += chunk
  reply = json.loads(data.decode())
  if not reply['ok']:
    raise RuntimeError('controller agent on %s: %s' % (host, reply['error']))
  return reply['result']


class AgentPox(object):
  """POX on another PC, started and read through controller_agent.py running there."""

  def __init__(self, host, port, module, run_dir, tag):
    self.host, self.port, self.run_dir, self.tag = host, port, run_dir, tag
    files, sent = {}, []
    for a in module:   # input files (topology, oracle pairs) are sent along with the command
      key, eq, value = a.partition('=')
      if eq and os.path.isfile(value):
        if key == '--model_file':   # binary: sent as base64
          with open(value, 'rb') as f:
            files[os.path.basename(value)] = {
              'encoding': 'base64', 'data': base64.b64encode(f.read()).decode('ascii')}
        else:
          with open(value) as f:
            files[os.path.basename(value)] = f.read()
        a = '%s={dir}/%s' % (key, os.path.basename(value))
      sent.append(a)
    agent_call(host, port, {'cmd': 'start', 'tag': tag, 'args': sent, 'files': files})

  def stats(self):
    return agent_call(self.host, self.port, {'cmd': 'stats'})['stats']

  def fresh(self):
    return agent_call(self.host, self.port, {'cmd': 'fresh'})['stats']

  def cpu_seconds(self):
    return agent_call(self.host, self.port, {'cmd': 'cpu'})['cpu_seconds']

  def stop(self):
    out = agent_call(self.host, self.port, {'cmd': 'stop'})
    with open(os.path.join(self.run_dir, '%s-pox.log' % self.tag), 'w') as f:
      f.write(out['log'])
    if out['stats']:
      with open(os.path.join(self.run_dir, '%s-stats.json' % self.tag), 'w') as f:
        json.dump(out['stats'], f)


def start_controller(mode, run_dir, tag, topo_file, net_name, args, flows=None, mac_of=None):
  module = pox_module(mode, run_dir, tag, topo_file, net_name, args, flows, mac_of)
  if args.controller_host:
    return AgentPox(args.controller_host, args.agent_port, module, run_dir, tag)
  return LocalPox(module, run_dir, tag)


def wait_for_spanning_tree(ctrl, n_links, connected_at):
  """Reactive only: wait until discovery has seen every link, then for the tree's ports."""
  ok = wait_for(lambda: ctrl.stats()['extra'].get('links', 0) >= 2 * n_links, 60, 0.5)
  found = ctrl.stats()['extra'].get('links', 0)
  if not ok:
    log('    WARNING: discovery found %d of %d link directions' % (found, 2 * n_links))
  # spanning_tree --hold-down keeps flooding off for one discovery cycle (5 s) + 1 s
  # after a switch connects, and port updates are confirmed 2 s later
  time.sleep(max(0, connected_at + 9 - time.time()) + 2)
  return found


def controller_info(args):
  """Where the controller runs, and the round-trip time to it from this machine."""
  if not args.controller_host:
    return {'where': 'same machine', 'host': socket.gethostname(), 'rtt_ms': None}
  info = agent_call(args.controller_host, args.agent_port, {'cmd': 'info'})
  if not info['pox_found']:
    sys.exit("The controller agent on %s cannot find POX (set POX_DIR there)" % args.controller_host)
  # Round-trip time = time of a TCP handshake with the agent (Windows drops ping by default)
  rtts = []
  for _ in range(20):
    t = time.perf_counter()
    with socket.create_connection((args.controller_host, args.agent_port), timeout=5) as s:
      rtts.append((time.perf_counter() - t) * 1000)
      s.sendall(b'{}\n')   # the agent answers with an error and closes; nothing is started
      s.recv(1024)
    time.sleep(0.05)
  info.update(where='separate PC', address=args.controller_host, rtt_ms=statistics.median(rtts))
  return info


NETWORKS = {
  'tree-d2-f4': lambda: (TreeTopo(depth=2, fanout=4), {}, {}),
  'tree-d3-f2': lambda: (TreeTopo(depth=3, fanout=2), {}, {}),
  'fattree-k4': pt.BUILTIN['fattree-k4'],
  'fattree-k6': pt.BUILTIN['fattree-k6'],   # larger network: 54 hosts, 2,862 pairs
  'abilene': pt.BUILTIN['abilene'],
}
# Real Abilene link speeds (data/abilene/topo-2003-04-10.txt): all 9.92 Gbit/s except
# Atlanta-Indianapolis at 2.48 Gbit/s, so that link gets a quarter of --bw
LINK_SPEED_FACTOR = {'abilene': {frozenset(('Atlanta', 'Indianapolis')): 0.25}}
DEFAULT_TM = os.path.join(REPO, 'data', 'abilene', 'tm-2004-03-01.json')
DEFAULT_SCENARIOS = ['tree-d2-f4:university', 'fattree-k4:websearch', 'fattree-k4:datamining',
                     'abilene:isp']
FLOW_PORT = 5001
SMALL, LARGE = 100 * 1000, 10 * 1000 * 1000

SERVER = r'''
import socket, sys, threading
s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', int(sys.argv[1]))); s.listen(1024)
def handle(c):
    try:
        c.settimeout(120)
        while c.recv(65536):
            pass
        c.sendall(b'k')
    except OSError:
        pass
    c.close()
while True:
    c, _ = s.accept()
    threading.Thread(target=handle, args=(c,), daemon=True).start()
'''

# Client: follows its schedule (start offset, destination IP, bytes) from time t0.
# Prints one line per flow as soon as it ends: start size fct_s ok late_s
CLIENT = r'''
import socket, sys, threading, time
sched, t0, port, timeout = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
flows = [l.split() for l in open(sched) if l.strip()]
lock, buf = threading.Lock(), b'x' * 65536
def run(start, dst, size):
    t = time.time(); ok = 0
    try:
        s = socket.create_connection((dst, port), timeout=timeout)
        s.settimeout(timeout)
        left = size
        while left > 0:
            n = min(left, len(buf)); s.sendall(buf[:n]); left -= n
        s.shutdown(socket.SHUT_WR)
        ok = 1 if s.recv(1) == b'k' else 0
        s.close()
    except OSError:
        pass
    with lock:
        print('%s %d %.6f %d %.6f' % (start, size, time.time() - t, ok, t - (t0 + float(start))), flush=True)
threads = []
for start, dst, size in flows:
    d = t0 + float(start) - time.time()
    if d > 0:
        time.sleep(d)
    th = threading.Thread(target=run, args=(start, dst, int(size)), daemon=True)
    th.start(); threads.append(th)
deadline = time.time() + timeout + 5
for th in threads:
    th.join(max(0, deadline - time.time()))
print('DONE', flush=True)
'''


def control_rules(net):
  """Per switch: rules that are not data rules (table-miss drop, discovery's LLDP rule)."""
  counts = {}
  for sw in net.switches:
    out = sw.cmd('ovs-ofctl --no-names -O OpenFlow10 dump-flows %s' % sw.name)
    counts[sw.name] = sum(1 for line in out.splitlines() if 'cookie=' in line and
                          (re.search(r'priority=0[ ,]', line) or 'dl_type=0x88cc' in line))
  return counts


def rule_counts(net):
  """Rules per switch (all of them), cheap enough to call every few seconds."""
  counts = {}
  for sw in net.switches:
    out = sw.cmd('ovs-ofctl -O OpenFlow10 dump-aggregate %s' % sw.name)
    m = re.search(r'flow_count=(\d+)', out)
    counts[sw.name] = int(m.group(1)) if m else 0
  return counts


def pct(xs, q):
  xs = sorted(xs)
  return xs[min(len(xs) - 1, int(q * len(xs)))] if xs else None


def hybrid_summary(st0, st1, rows):
  """Hit rate = new TCP connections whose first packet (SYN) found a rule at the sender's switch."""
  e0, e1 = st0.get('extra', {}), st1.get('extra', {})
  misses = e1['ingress_syn_misses'] - e0.get('ingress_syn_misses', 0)
  # Installs are counted from controller start: the oracle installs its pairs before the
  # first flow, the counter only once traffic arrives
  return {'budget_pairs': e1['budget_pairs'], 'total_pairs': e1['total_pairs'],
          'syn_misses': misses, 'flows': len(rows),
          'hit_rate_pct': 100.0 * max(0, len(rows) - misses) / max(1, len(rows)),
          'pair_installs': e1['pair_installs'], 'pair_removals': e1['pair_removals'],
          'wasted_installs': e1['wasted_installs'], 'pairs_installed_end': e1['pairs_installed']}


def fct_summary(rows):
  ok = [r for r in rows if r['ok']]
  res = {'flows': len(rows), 'completed': len(ok), 'failed': len(rows) - len(ok),
         'unfinished': sum(1 for r in rows if r.get('unfinished'))}
  for name, sel in (('small', lambda s: s < SMALL), ('medium', lambda s: SMALL <= s <= LARGE),
                    ('large', lambda s: s > LARGE), ('all', lambda s: True)):
    xs = [r['fct_ms'] for r in ok if sel(r['size'])]
    res[name] = {'count': len(xs), 'failed': sum(1 for r in rows if not r['ok'] and sel(r['size']))}
    if xs:
      res[name].update(mean_ms=statistics.mean(xs), p50_ms=pct(xs, 0.5), p99_ms=pct(xs, 0.99))
  return res


# ---------------------------------------------------------------- control-channel delay
# --ctrl-delay MS delays OpenFlow traffic only: TCP to or from OF_PORT on the loopback device, where
# the switches meet a local POX. Both directions leave through lo once, so MS is the ONE-WAY delay and
# the control round trip grows by 2 x MS. Host traffic uses the Mininet veth links and is not touched.
CTRL_QDISC = 'a7:'      # our own handle, so we never remove a qdisc we did not add
CTRL_NETEM = 'a71:'


def _tc(cmd, check=True):
  return subprocess.run('tc ' + cmd, shell=True, check=check, capture_output=True, text=True)


def ctrl_delay_off():
  if ('qdisc prio %s' % CTRL_QDISC) in _tc('qdisc show dev lo', check=False).stdout:
    _tc('qdisc del dev lo root')


def ctrl_delay_on(ms):
  ctrl_delay_off()
  show = _tc('qdisc show dev lo', check=False).stdout.strip()
  if show and 'noqueue' not in show:
    raise RuntimeError('lo already has a queueing discipline (%s); not replacing it' % show)
  _tc('qdisc add dev lo root handle %s prio bands 4 priomap %s' % (CTRL_QDISC, ' '.join(['3'] * 16)))
  _tc('qdisc add dev lo parent %s1 handle %s netem delay %gms limit 100000' % (CTRL_QDISC, CTRL_NETEM, ms))
  for field in ('dport', 'sport'):
    _tc('filter add dev lo parent %s protocol ip prio 1 u32 match ip %s %d 0xffff flowid %s1'
        % (CTRL_QDISC, field, OF_PORT, CTRL_QDISC))


def ctrl_delay_packets():
  """Packets the netem band has delayed so far (proof that the filter matched OpenFlow traffic)."""
  lines = _tc('-s qdisc show dev lo', check=False).stdout.splitlines()
  for i, line in enumerate(lines):
    if line.startswith('qdisc netem %s' % CTRL_NETEM) and i + 1 < len(lines):
      m = re.search(r'Sent \d+ bytes (\d+) pkt', lines[i + 1])
      return int(m.group(1)) if m else None
  return None


def run_one(net_name, workload, mode, args, run_dir, repeat=0):
  seed = args.seed + repeat
  tag = '%s-%s-%s' % (net_name, workload, mode) + ('-s%d' % seed if args.repeats > 1 else '')
  log('\n' + '=' * 70)
  log('[*] %s | %s traffic | %s%s' % (net_name, workload, mode,
                                     ' | run %d of %d (seed %d)' % (repeat + 1, args.repeats, seed)
                                     if args.repeats > 1 else ''))
  log('=' * 70)

  cleanup()
  ctrl_delay_off()   # never inherit a delay from a crashed run
  topo, delays, labels = NETWORKS[net_name]()
  factors = LINK_SPEED_FACTOR.get(net_name, {})
  for a, b, info in topo.links(withInfo=True):
    info['bw'] = args.bw * factors.get(frozenset((labels.get(a), labels.get(b))), 1.0)
    d = delays.get((a, b), delays.get((b, a)))
    if d is not None and args.netem:
      info['delay'] = '%.2fms' % d
  switch = partial(OVSSwitch, datapath=args.datapath, protocols='OpenFlow10')
  net = Mininet(topo=topo, switch=switch, link=TCLink,
                controller=partial(LateStartController, ip=args.controller_host or '127.0.0.1',
                                    port=OF_PORT),
                autoSetMacs=True, waitConnected=False)
  topo_file = os.path.join(run_dir, '%s-topo.json' % net_name)
  write_topology(net, topo_file, delays)
  with open(topo_file) as f:
    topo_json = json.load(f)
  n_links = len(topo_json['links'])
  dpid_name = {int(sw.dpid, 16): sw.name for sw in net.switches}
  edge_of = {h['name']: dpid_name[h['dpid']] for h in topo_json['hosts']}
  ip_of = {h['name']: h['ip'] for h in topo_json['hosts']}

  # Same schedule for every controller: the seed depends only on network + workload
  city_of = {h: labels[e] for h, e in edge_of.items() if e in labels}
  flows, info = wl.make_schedule(workload, sorted(edge_of, key=lambda n: int(n[1:])), edge_of,
                                 args.duration, args.load, args.bw, args.max_bytes,
                                 '%s-%s-%d' % (net_name, workload, seed),
                                 city_of=city_of, tm_file=args.tm, pair_zipf=args.pair_zipf)
  log('    schedule: %d flows in %d s (%.1f flows/s), offered %.1f Mbit/s = %.0f%% of host capacity, '
      '%d capped at %d MB, %.0f%% leave the edge switch'
      % (info['flows'], args.duration, info['flows_per_s'], info['offered_mbps'],
         100 * info['offered_load'], info['capped_flows'], args.max_bytes // 10**6, info['off_rack_pct']))

  mac_of = {h['name']: h['mac'] for h in topo_json['hosts']}
  ctrl = start_controller(mode, run_dir, tag, topo_file, net_name, args, flows, mac_of)
  result = {'network': net_name, 'workload': workload, 'mode': mode, 'seed': seed, 'repeat': repeat,
            'hosts': len(net.hosts),
            'switches': len(net.switches), 'bw_mbps': args.bw, 'schedule': info,
            'delay_emulated': bool(delays) and args.netem, 'ctrl_delay_ms': args.ctrl_delay}
  try:
    if args.ctrl_delay:   # before the switches connect, so the handshake is delayed too
      ctrl_delay_on(args.ctrl_delay)
    net.start()
    connected_at = time.time()
    if not net.waitConnected(timeout=30):
      raise RuntimeError("Switches did not connect to POX at %s:%d%s" % (
        args.controller_host or '127.0.0.1', OF_PORT,
        ' (check that TCP %d is open on the controller PC, see docs/Controller_On_Second_PC.md)'
        % OF_PORT if args.controller_host else ''))
    helper = os.path.join(run_dir, 'tx_csum_off.py')
    server, client = os.path.join(run_dir, 'flow_server.py'), os.path.join(run_dir, 'flow_client.py')
    for path, text in ((helper, TX_CSUM_OFF), (server, SERVER), (client, CLIENT)):
      with open(path, 'w') as f:
        f.write(text)
    for h in net.hosts:
      h.cmd('sysctl -qw net.ipv6.conf.all.disable_ipv6=1 net.ipv6.conf.default.disable_ipv6=1')
      h.cmd('python3 %s %s' % (helper, h.defaultIntf().name))
    net.staticArp()

    if mode in SPANNING_TREE_MODES:
      wait_for_spanning_tree(ctrl, n_links, connected_at)
      for h in net.hosts:   # host discovery: one broadcast per host
        h.cmd('ping -n -b -c 1 -W 1 10.255.255.255 > /dev/null 2>&1')
      time.sleep(0.5)
    elif mode.startswith('proactive') or mode == 'tap':
      wait_for(lambda: sum(1 for s in ctrl.stats()['switches'].values()
                           if s['install_ms'] is not None) >= len(net.switches), 30)
    else:   # hybrid: wait until every switch has connected to the controller
      wait_for(lambda: len(ctrl.stats()['switches']) >= len(net.switches), 30)

    ctrl_rules = control_rules(net)
    for h in net.hosts:
      h.cmd('timeout %d python3 %s %d > /dev/null 2>&1 &'
            % (args.duration + args.flow_timeout + 60, server, FLOW_PORT))
    per_host = {h: [] for h in edge_of}
    for start, src, dst, size in flows:
      per_host[src].append('%.6f %s %d' % (start, ip_of[dst], size))
    outs = {}
    t0 = time.time() + 3
    for h in net.hosts:
      sched = os.path.join(run_dir, '%s-sched-%s.txt' % (tag, h.name))
      with open(sched, 'w') as f:
        f.write('\n'.join(per_host[h.name]) + '\n')
      outs[h.name] = os.path.join(run_dir, '%s-fct-%s.txt' % (tag, h.name))
      h.cmd('python3 %s %s %.6f %d %d > %s 2>&1 &' % (client, sched, t0, FLOW_PORT,
                                                       args.flow_timeout, outs[h.name]))

    st_pre = ctrl.fresh()   # before the first flow: hybrid counters start here
    freeze = []
    if args.pause_controller:
      # SIGSTOP freezes POX as a crash or a long garbage-collection pause would; SIGCONT resumes it
      p_start, p_len = args.pause_controller
      pid = ctrl.proc.pid
      freeze = [threading.Timer(max(0, t0 + p_start - time.time()), os.kill, (pid, signal.SIGSTOP)),
                threading.Timer(max(0, t0 + p_start + p_len - time.time()), os.kill, (pid, signal.SIGCONT))]
      for tm in freeze:
        tm.start()
    time.sleep(max(0, t0 - time.time()))
    st0 = ctrl.fresh()
    s0, c0, w0 = st0['totals'], ctrl.cpu_seconds(), time.time()
    peak_total, peak_switch = 0, 0
    while time.time() < t0 + args.duration:   # sample the flow tables while traffic runs
      time.sleep(min(5, max(0.1, t0 + args.duration - time.time())))
      now = rule_counts(net)
      data = {k: max(0, now[k] - ctrl_rules.get(k, 0)) for k in now}   # data rules only
      peak_total = max(peak_total, sum(data.values()))
      peak_switch = max(peak_switch, max(data.values()))
    for tm in freeze:   # the controller must be running again before we read its stats
      tm.join()
    st1 = ctrl.fresh()
    s1, c1, w1 = st1['totals'], ctrl.cpu_seconds(), time.time()

    def done():
      for o in outs.values():
        try:
          if 'DONE' not in open(o).read():
            return False
        except OSError:
          return False
      return True
    wait_for(done, args.flow_timeout + 30, 1)

    rows = []
    for name, o in outs.items():
      reported = set()
      for line in open(o):
        p = line.split()
        if len(p) == 5:
          reported.add(p[0])
          rows.append({'src': name, 'start': float(p[0]), 'size': int(p[1]), 'unfinished': False,
                       'fct_ms': float(p[2]) * 1000, 'ok': p[3] == '1', 'late_ms': float(p[4]) * 1000})
      for line in per_host[name]:   # still running when we stopped waiting: count as failed
        start, _, size = line.split()
        if start not in reported:
          rows.append({'src': name, 'start': float(start), 'size': int(size), 'unfinished': True,
                       'fct_ms': None, 'ok': False, 'late_ms': 0.0})
    if args.ctrl_delay:
      result['ctrl_delay_packets'] = ctrl_delay_packets()
      if not result['ctrl_delay_packets']:
        raise RuntimeError('--ctrl-delay: netem delayed no OpenFlow packets; the delay was not applied')
      log('    control channel: +%g ms one way, %d OpenFlow packets delayed'
          % (args.ctrl_delay, result['ctrl_delay_packets']))
    window = w1 - w0
    result.update({
      'fct': fct_summary(rows), 'flows_detail': rows,
      'control': {'packet_in_per_s': (s1['packet_in'] - s0['packet_in']) / window,
                  'flow_mod_per_s': (s1['flow_mod'] - s0['flow_mod']) / window,
                  'controller_cpu_pct': 100.0 * (c1 - c0) / window,
                  'peak_rules_total': peak_total, 'peak_rules_one_switch': peak_switch},
      'hybrid': hybrid_summary(st_pre, st1, rows) if 'ingress_syn_misses' in st1.get('extra', {}) else None,
      'start_late_ms_p99': pct([r['late_ms'] for r in rows], 0.99),
    })
    if args.pause_controller:   # flows that started while the controller was frozen
      p_start, p_len = args.pause_controller
      inside = [r for r in rows if p_start <= r['start'] < p_start + p_len]
      outside = [r for r in rows if not p_start <= r['start'] < p_start + p_len]
      def small_median(rs):
        v = sorted(r['fct_ms'] for r in rs if r['ok'] and r['fct_ms'] is not None and r['size'] < SMALL)
        return v[len(v) // 2] if v else None
      done_in = [r['fct_ms'] for r in inside if r['ok'] and r['fct_ms'] is not None]
      result['pause'] = {'start_s': p_start, 'seconds': p_len, 'flows': len(inside),
                         'failed': sum(1 for r in inside if not r['ok']),
                         'small_median_ms': small_median(inside),
                         'small_median_outside_ms': small_median(outside),
                         'max_fct_ms': max(done_in) if done_in else None,
                         'over_1s': sum(1 for v in done_in if v > 1000)}
      pz = result['pause']
      fmt_ms = lambda v: '-' if v is None else '%.1f' % v
      log('    controller frozen %g-%g s: %d flows started, %d failed, %d took over 1 s, '
          'small-flow median %s ms (outside the freeze %s ms), slowest %s ms'
          % (p_start, p_start + p_len, pz['flows'], pz['failed'], pz['over_1s'],
             fmt_ms(pz['small_median_ms']), fmt_ms(pz['small_median_outside_ms']), fmt_ms(pz['max_fct_ms'])))
    if mode == 'tap':   # how many of the flows the hosts started did the controller hear of?
      # read after every flow has finished, so no copy is still on its way
      e0, e1 = st_pre.get('extra', {}), ctrl.fresh().get('extra', {})
      seen = e1.get('flows_seen', 0) - e0.get('flows_seen', 0)
      result['tap'] = {'flows_seen': seen, 'flows_ended': e1.get('flows_ended', 0) - e0.get('flows_ended', 0),
                       'seen_pct': 100.0 * seen / max(1, len(rows)), 'tap_rules': e1.get('tap_rules'),
                       'switch_errors': e1.get('switch_errors', 0)}
      log('    tap: controller heard of %d of %d flows (%.1f%%), %d switch errors'
          % (seen, len(rows), result['tap']['seen_pct'], result['tap']['switch_errors']))
    f, c = result['fct'], result['control']
    fmt = lambda d, k: '%.1f' % d[k] if k in d else '-'
    log('    flows: %d done, %d failed | FCT small (<100KB) mean %s p99 %s ms | large (>10MB) mean %s ms'
        % (f['completed'], f['failed'], fmt(f['small'], 'mean_ms'), fmt(f['small'], 'p99_ms'),
           fmt(f['large'], 'mean_ms')))
    log('    controller: %.0f PACKET_IN/s, %.0f FLOW_MOD/s, CPU %.1f%% | rules: peak %d total, %d in one switch'
        % (c['packet_in_per_s'], c['flow_mod_per_s'], c['controller_cpu_pct'],
           c['peak_rules_total'], c['peak_rules_one_switch']))
  finally:
    if args.pause_controller and hasattr(ctrl, 'proc') and ctrl.proc.poll() is None:
      os.kill(ctrl.proc.pid, signal.SIGCONT)   # never leave POX frozen
    net.stop()
    ctrl.stop()
    ctrl_delay_off()
  return result


def write_markdown(results, meta, run_dir):
  """Tables; with --repeats N every value is the mean of N runs +- the 95% confidence interval."""
  a = meta['args']
  n_rep = a.get('repeats', 1)
  merged = repeats.aggregate(results)
  v = repeats.fmt
  ctrl = meta.get('controller') or {'where': 'same machine'}
  where = ('separate PC %s (%s, %s CPUs, round-trip time %s ms)'
           % (ctrl.get('address'), ctrl.get('host'), ctrl.get('cpus'),
              '%.2f' % ctrl['rtt_ms'] if ctrl.get('rtt_ms') is not None else '?')
           if ctrl['where'] == 'separate PC' else 'same machine as Mininet')
  if a.get('ctrl_delay'):
    where += ', control channel delayed by %g ms one way (netem on lo)' % a['ctrl_delay']
  lines = ['# Realistic traffic results (%s)' % os.path.basename(run_dir.rstrip('/')), '',
           'Testbed: %s | Python %s | %s | datapath=%s | every link %d Mbit/s | %d s of arrivals | '
           'target load %.0f%% (websearch/datamining) | flows capped at %d MB | pair popularity: %s'
           % (meta['uname'], meta['python'], meta['ovs'], a['datapath'], a['bw'], a['duration'],
              100 * a['load'], a['max_bytes'] // 10**6,
              'Zipf %.1f' % a['pair_zipf'] if a.get('pair_zipf') else 'uniform'), '',
           'Controller: %s' % where, '']
  if 'git_commit' in meta:   # batches from 20 Nov 2026 on
    lines[-1:-1] = ['CPU: %s, %s threads | code: commit %s%s' % (
      meta.get('cpu_model') or 'unknown', meta.get('cpu_threads'), (meta.get('git_commit') or 'unknown')[:10],
      ' with uncommitted changes' if meta.get('git_dirty') else ''), '']
  if n_rep > 1:
    lines += ['**Every value is the mean of %d runs (seeds %d to %d, a new flow schedule each time) '
              '± the half-width of its 95%% confidence interval (Student\'s t).**'
              % (n_rep, a['seed'], a['seed'] + n_rep - 1), '']
  lines += ['## Traffic generated (identical for every controller%s)' % (' within one seed' if n_rep > 1 else ''), '',
            '| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |',
            '| --- | --- | --- | --- | --- | --- | --- | --- |']
  seen = set()
  for r in merged:
    key = (r['network'], r['workload'])
    if key in seen:
      continue
    seen.add(key)
    s = r['schedule']
    lines.append('| %s | %s | %s | %s | %s | %s (%.0f%%) | %s | %s%% |' % (
      r['network'], r['workload'], s['source'], v(r, ('schedule', 'flows'), 0),
      v(r, ('schedule', 'flows_per_s')), v(r, ('schedule', 'offered_mbps')), 100 * s['offered_load'],
      v(r, ('schedule', 'capped_flows'), 0), v(r, ('schedule', 'off_rack_pct'), 0)))
  lines += ['', '## Flow completion time (ms)', '',
            '| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | '
            'Medium: mean | Large > 10 MB: mean |',
            '| --- | --- | --- | --- | --- | --- | --- |']
  for r in merged:
    lines.append('| %s | %s | %s | %s / %s | %s / %s / %s | %s | %s |' % (
      r['network'], r['workload'], mode_label(r['mode']), v(r, ('fct', 'completed'), 0),
      v(r, ('fct', 'failed'), 0), v(r, ('fct', 'small', 'mean_ms'), 2), v(r, ('fct', 'small', 'p50_ms'), 2),
      v(r, ('fct', 'small', 'p99_ms'), 2), v(r, ('fct', 'medium', 'mean_ms')), v(r, ('fct', 'large', 'mean_ms'))))
  lines += ['', '## Controller load and rules', '',
            '| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | '
            'Peak rules (all switches) | Peak rules (one switch) |',
            '| --- | --- | --- | --- | --- | --- | --- | --- |']
  for r in merged:
    lines.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (
      r['network'], r['workload'], mode_label(r['mode']), v(r, ('control', 'packet_in_per_s'), 0),
      v(r, ('control', 'flow_mod_per_s'), 0), v(r, ('control', 'controller_cpu_pct')),
      v(r, ('control', 'peak_rules_total'), 0), v(r, ('control', 'peak_rules_one_switch'), 0)))
  hyb = [r for r in merged if r.get('hybrid')]
  if hyb:
    lines += ['', '## Budgeted hybrid (hit rate = new connections whose first packet found a rule)', '',
              '| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |',
              '| --- | --- | --- | --- | --- | --- | --- |']
    for r in hyb:
      h = r['hybrid']
      lines.append('| %s | %s | %s | %d of %d | %s | %s | %s |' % (
        r['network'], r['workload'], mode_label(r['mode']), h['budget_pairs'], h['total_pairs'],
        v(r, ('hybrid', 'hit_rate_pct')), v(r, ('hybrid', 'pair_installs'), 0),
        v(r, ('hybrid', 'wasted_installs'), 0)))
  lstm_modes = sorted({r['mode'] for r in results if r['mode'].startswith('lstm-')})
  comparisons = []
  for lstm_mode in lstm_modes:
    counter_mode = 'hybrid-' + lstm_mode.split('-', 1)[1]
    scenarios = sorted({(r['network'], r['workload']) for r in results if r['mode'] == lstm_mode})
    for network, workload in scenarios:
      lstm_runs = {r.get('seed'): r for r in results if r['network'] == network and
                   r['workload'] == workload and r['mode'] == lstm_mode}
      counter_runs = {r.get('seed'): r for r in results if r['network'] == network and
                      r['workload'] == workload and r['mode'] == counter_mode}
      paired = [(lstm_runs[seed], counter_runs[seed]) for seed in sorted(set(lstm_runs) & set(counter_runs))]
      if not paired:
        continue
      hit_delta = [repeats.get(lstm, ('hybrid', 'hit_rate_pct')) -
                   repeats.get(counter, ('hybrid', 'hit_rate_pct')) for lstm, counter in paired]
      fct_delta = [repeats.get(lstm, ('fct', 'small', 'p50_ms')) -
                   repeats.get(counter, ('fct', 'small', 'p50_ms')) for lstm, counter in paired
                   if repeats.get(lstm, ('fct', 'small', 'p50_ms')) is not None and
                   repeats.get(counter, ('fct', 'small', 'p50_ms')) is not None]
      packet_delta = [repeats.get(lstm, ('control', 'packet_in_per_s')) -
                      repeats.get(counter, ('control', 'packet_in_per_s')) for lstm, counter in paired]
      comparisons.append((network, workload, lstm_mode, len(paired), hit_delta, fct_delta, packet_delta))
  if comparisons:
    def delta_fmt(values, precision=1):
      mean, half = repeats.mean_ci(values)
      if mean is None:
        return '-'
      text = ('%+.*f' % (precision, mean))
      return text + (' ± %.*f' % (precision, half) if half is not None else '')

    lines += ['', '## LSTM vs weighted counter (paired by seed; delta = LSTM - counter)', '',
              'Negative flow-time and PACKET_IN deltas favor the LSTM; positive hit-rate deltas favor it. '
              'Intervals use paired seeds.', '',
              '| Network | Workload | Budget | Paired runs | Hit-rate delta (pp) | Small p50 delta (ms) | PACKET_IN/s delta |',
              '| --- | --- | --- | --- | --- | --- | --- |']
    for network, workload, mode, count, hit, fct, packet in comparisons:
      lines.append('| %s | %s | %s%% | %d | %s | %s | %s |' % (
        network, workload, mode.split('-', 1)[1], count, delta_fmt(hit), delta_fmt(fct), delta_fmt(packet, 0)))
  if n_rep > 1:
    lines += ['', '## Every run', '',
              '| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | '
              'CPU % | Peak rules | Hit rate % |',
              '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for r in results:
      lines.append('| %s | %s | %s | %s | %d | %s / %s | %.0f | %.1f | %d | %s |' % (
        r['network'], r['workload'], mode_label(r['mode']), r.get('seed'), r['fct']['failed'],
        v(r, ('fct', 'small', 'p50_ms'), 2), v(r, ('fct', 'small', 'p99_ms'), 2),
        r['control']['packet_in_per_s'], r['control']['controller_cpu_pct'],
        r['control']['peak_rules_total'], v(r, ('hybrid', 'hit_rate_pct'))))
  path = os.path.join(run_dir, 'traffic.md')
  with open(path, 'w') as fh:
    fh.write('\n'.join(lines) + '\n')
  return path


def environment_info():
  """CPU and code version of this batch, for the reproduction table. Never fails the batch."""
  info = {'cpu_model': None, 'cpu_threads': os.cpu_count(), 'git_commit': None, 'git_dirty': None}
  try:
    with open('/proc/cpuinfo') as f:
      for line in f:
        if line.lower().startswith(('model name', 'hardware', 'cpu model')):
          info['cpu_model'] = line.split(':', 1)[1].strip()
          break
  except OSError:
    pass
  if not info['cpu_model']:   # ARM: /proc/cpuinfo has no model line
    try:
      out = subprocess.run(['lscpu'], capture_output=True, text=True, timeout=10).stdout
      names = [l.split(':', 1)[1].strip() for l in out.splitlines()
               if l.startswith(('Model name', 'Vendor ID'))]
      info['cpu_model'] = ' / '.join(n for n in names if n and n != '-') or None
    except (OSError, subprocess.SubprocessError):
      pass
  repo = os.path.dirname(HERE)
  git = ['git', '-c', 'safe.directory=*', '-C', repo]   # the harness runs under sudo
  try:
    info['git_commit'] = subprocess.run(git + ['rev-parse', 'HEAD'], capture_output=True,
                                        text=True, timeout=10).stdout.strip() or None
    status = subprocess.run(git + ['status', '--porcelain', '--untracked-files=no'],
                            capture_output=True, text=True, timeout=10).stdout
    info['git_dirty'] = bool(status.strip()) if info['git_commit'] else None
  except (OSError, subprocess.SubprocessError):
    pass
  return info


def main():
  ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  ap.add_argument('--scenarios', nargs='+', default=DEFAULT_SCENARIOS,
                  help='network:workload pairs, networks %s, workloads %s'
                       % (', '.join(NETWORKS), ', '.join(wl.WORKLOADS)))
  ap.add_argument('--modes', nargs='+', default=None,
                  help='default: reactive proactive (+ proactive-ecmp on the fat-tree)')
  ap.add_argument('--duration', type=int, default=30, help='seconds of flow arrivals')
  ap.add_argument('--load', type=float, default=0.3, help='offered load for websearch/datamining')
  ap.add_argument('--bw', type=int, default=100, help='bandwidth of every link, Mbit/s')
  ap.add_argument('--max-mb', type=int, default=20, help='cap on flow size, MB')
  ap.add_argument('--budget-sweep', action='store_true',
                  help='Step 4: reactive, reactive-long, reactive-sp, hybrid at each --budgets, proactive')
  ap.add_argument('--budgets', nargs='+', type=int, default=[10, 25, 50],
                  help='hybrid budgets, %% of all host pairs')
  ap.add_argument('--random-baseline', action='store_true',
                  help='budget sweep: also pre-install a random NN%% of pairs at each budget')
  ap.add_argument('--lstm-baseline', action='store_true',
                  help='budget sweep: also rank pairs with a pretrained LSTM at each budget')
  ap.add_argument('--lstm-model', default=None,
                  help='trained .npz model from experiments/train_lstm.py (required for LSTM modes)')
  ap.add_argument('--lstm-warmup', type=int, default=10,
                  help='intervals to fine-tune online before switching to frozen LSTM inference')
  ap.add_argument('--granularity-baselines', action='store_true',
                  help='budget sweep: also run reactive-pair and reactive-dst (reactive on shortest paths '
                       'with wildcard rules, no pre-installation)')
  ap.add_argument('--decay', type=float, default=0.97, help='hybrid counter decay per second')
  ap.add_argument('--hysteresis', type=float, default=1.5,
                  help='hybrid: a newcomer must score this many times the weakest kept pair')
  ap.add_argument('--long-idle', type=int, default=60, help='reactive-long idle timeout, s')
  ap.add_argument('--long-hard', type=int, default=300, help='reactive-long hard timeout, s')
  ap.add_argument('--pair-zipf', type=float, default=0.0,
                  help='Zipf exponent of host-pair popularity (0 = uniform destinations)')
  ap.add_argument('--tm', default=DEFAULT_TM, help='hourly traffic matrices for the isp workload '
                  '(make others with experiments/abilene_tm.py)')
  ap.add_argument('--flow-timeout', type=int, default=30, help='seconds before a flow counts as failed')
  ap.add_argument('--datapath', default='kernel', choices=['kernel', 'user'])
  ap.add_argument('--seed', type=int, default=7)
  ap.add_argument('--repeats', type=int, default=1,
                  help='run everything N times with seeds seed..seed+N-1; tables then show the mean '
                       'and the 95%% confidence interval')
  ap.add_argument('--controller-host', default=None,
                  help='run POX on another PC at this address (start experiments/controller_agent.py '
                       'there first); default: POX on this machine')
  ap.add_argument('--agent-port', type=int, default=6000, help='TCP port of controller_agent.py')
  ap.add_argument('--quick', action='store_true', help='university traffic on the tree, 10 s (smoke run)')
  ap.add_argument('--out', default=None, help='output directory')
  ap.add_argument('--pause-controller', default=None, metavar='START:SECONDS',
                  help='freeze POX (SIGSTOP) START seconds into the traffic for SECONDS seconds, '
                       'then resume it; reports the flows that started while it was frozen')
  ap.add_argument('--ctrl-delay', type=float, default=0.0, metavar='MS',
                  help='add MS ms of one-way delay to the OpenFlow channel only (netem on lo, TCP port '
                       '%d); the control round trip grows by 2 x MS. Local controller only' % OF_PORT)
  args = ap.parse_args()
  if args.pause_controller:
    try:
      args.pause_controller = tuple(float(x) for x in args.pause_controller.split(':'))
      assert len(args.pause_controller) == 2
    except (ValueError, AssertionError):
      sys.exit('--pause-controller takes START:SECONDS, e.g. 10:5')
    if args.controller_host:
      sys.exit('--pause-controller works only with POX on this machine')

  if os.geteuid() != 0:
    sys.exit("Mininet needs root: run with sudo")
  if not os.path.exists(os.path.join(POX_DIR, 'pox.py')):
    sys.exit("POX not found at %s (clone it there or set POX_DIR)" % POX_DIR)
  if args.quick:
    args.scenarios, args.duration = ['tree-d2-f4:university'], 10
  if args.pause_controller and sum(args.pause_controller) >= args.duration:
    sys.exit('--pause-controller must end before --duration (%d s)' % args.duration)
  args.max_bytes = args.max_mb * 10**6
  args.netem = netem_available()
  if args.ctrl_delay < 0:
    sys.exit('--ctrl-delay must be >= 0')
  if args.ctrl_delay and args.controller_host:
    sys.exit('--ctrl-delay works with a local controller only (the real network adds the delay)')
  if args.ctrl_delay and not args.netem:
    sys.exit('--ctrl-delay needs netem, which this kernel lacks')
  scenarios = []
  for s in args.scenarios:
    net_name, _, workload = s.partition(':')
    if net_name not in NETWORKS or workload not in wl.WORKLOADS:
      sys.exit("Unknown scenario %s" % s)
    if args.budget_sweep:
      modes = (['reactive', 'reactive-long', 'reactive-sp'] +
               (['reactive-pair', 'reactive-dst'] if args.granularity_baselines else []) +
               ['hybrid-%d' % b for b in args.budgets] + ['oracle-%d' % b for b in args.budgets] +
               (['lstm-%d' % b for b in args.budgets] if args.lstm_baseline else []) +
               (['random-%d' % b for b in args.budgets] if args.random_baseline else []) +
               ['proactive-ecmp' if 'fattree' in net_name else 'proactive'])
    else:
      modes = args.modes or (['reactive', 'proactive', 'proactive-ecmp'] if 'fattree' in net_name
                             else ['reactive', 'proactive'])
    scenarios += [(net_name, workload, m) for m in modes]
  needs_lstm = args.lstm_baseline or any(mode.startswith('lstm-') for _, _, mode in scenarios)
  if needs_lstm and not args.lstm_model:
    ap.error('LSTM modes require --lstm-model; train one with experiments/train_lstm.py')
  if needs_lstm and not os.path.isfile(args.lstm_model):
    ap.error('LSTM model file not found: %s' % args.lstm_model)
  if args.lstm_warmup < 0:
    ap.error('--lstm-warmup must be non-negative')
  if args.repeats < 1:
    sys.exit("--repeats must be at least 1")
  controller = controller_info(args)
  if args.controller_host:
    log('[*] Controller on %s (%s, %s, %d CPUs), round-trip time %s ms'
        % (args.controller_host, controller['host'], controller['cpu'], controller['cpus'],
           '%.2f' % controller['rtt_ms'] if controller['rtt_ms'] is not None else '?'))

  run_dir = args.out or os.path.join(REPO, 'results', 'measured', 'traffic-' + time.strftime('%Y%m%d-%H%M%S'))
  os.makedirs(run_dir, exist_ok=True)
  setLogLevel('warning')
  # tc warns that the HTB quantum is large at 100 Mbit/s; it is harmless, so hide it
  lg.addFilter(lambda record: 'quantum of class' not in record.getMessage())

  results = []
  try:
    # Repeats on the outside: a slow drift of the machine (heat, background load)
    # then hits every controller equally instead of the last ones only
    for repeat in range(args.repeats):
      for net_name, workload, mode in scenarios:
        results.append(run_one(net_name, workload, mode, args, run_dir, repeat))
  finally:
    cleanup()
    ctrl_delay_off()
    meta = {'args': vars(args), 'started_by': os.environ.get('SUDO_USER'), 'controller': controller,
            'uname': ' '.join(os.uname()), 'python': sys.version.split()[0],
            'ovs': subprocess.run(['ovs-vsctl', '--version'], capture_output=True,
                                  text=True).stdout.split('\n')[0]}
    meta.update(environment_info())
    with open(os.path.join(run_dir, 'traffic.json'), 'w') as fh:
      json.dump({'meta': meta, 'results': results}, fh, indent=1)

  # If even the best controller in a scenario loses flows, the network or the machine is overloaded
  for key in sorted({(r['network'], r['workload'], r.get('seed')) for r in results}):
    runs = [r for r in results if (r['network'], r['workload'], r.get('seed')) == key]
    best = min(runs, key=lambda r: r['fct']['failed'])
    if best['fct']['failed'] > 0.01 * best['fct']['flows']:
      log('[!] %s / %s (seed %s): even the best controller (%s) lost %d of %d flows. Either the links '
          'are overloaded or this machine cannot keep up; try a lower --load or --bw and say which you used.'
          % (key[0], key[1], key[2], best['mode'], best['fct']['failed'], best['fct']['flows']))

  md = write_markdown(results, meta, run_dir)
  log('\n[+] Raw results: %s' % os.path.join(run_dir, 'traffic.json'))
  log('[+] Tables:      %s' % md)
  subprocess.run([sys.executable, os.path.join(HERE, 'plot_traffic.py'), run_dir])

  uid, gid = os.environ.get('SUDO_UID'), os.environ.get('SUDO_GID')
  if uid and gid:   # files were created as root; hand them back to the user who ran sudo
    for root, dirs, files in os.walk(run_dir):
      for name in dirs + files:
        os.chown(os.path.join(root, name), int(uid), int(gid))
    os.chown(run_dir, int(uid), int(gid))


if __name__ == '__main__':
  main()
