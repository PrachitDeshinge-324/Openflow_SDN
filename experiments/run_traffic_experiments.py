#!/usr/bin/env python3
"""
Realistic traffic: reactive vs proactive under published workloads (Mininet + POX)
CS G525 Advanced Computer Networks - Project SA7

Each scenario pairs a network with the traffic measured in that kind of
network (sources in docs/Realism_Sources.md and experiments/workloads.py):

  tree-d2-f4 : university  - campus / enterprise tree, Benson et al. IMC 2010
  fattree-k4 : websearch   - data centre, DCTCP (SIGCOMM 2010) via pFabric
  fattree-k4 : datamining  - data centre, VL2 (SIGCOMM 2009) via pFabric

Every host runs a TCP server; flows follow a schedule computed in advance from
the workload (same seed, so every controller gets exactly the same flows). Each
flow: connect, send N bytes, wait for the receiver's 1-byte reply.

Measured per run:
  - flow completion time (FCT) of small (< 100 KB), medium and large (> 10 MB) flows
  - flows that failed (no connection or no reply within --flow-timeout)
  - controller load: PACKET_IN/s, FLOW_MOD/s, controller CPU %
  - rules in the switches during the run (peak total, peak in one switch)

Usage (Mininet needs root):
  sudo python3 experiments/run_traffic_experiments.py            # 3 scenarios, ~10 min
  sudo python3 experiments/run_traffic_experiments.py --quick    # university only, ~2 min
  sudo python3 experiments/run_traffic_experiments.py --scenarios fattree-k4:university
Output: results/measured/traffic-<timestamp>/ (traffic.md, traffic.json, plots).
"""

import argparse
import json
import os
import random
import re
import statistics
import subprocess
import sys
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
import workloads as wl
from run_experiments import (OF_PORT, POX_DIR, REPO, LateStartController, cpu_seconds,
                             fresh_stats, log, read_stats, stop_pox, wait_for, write_topology)
from run_path_experiments import MODE_LABEL, TX_CSUM_OFF, start_pox, wait_for_spanning_tree

NETWORKS = {
  'tree-d2-f4': lambda: (TreeTopo(depth=2, fanout=4), {}, {}),
  'tree-d3-f2': lambda: (TreeTopo(depth=3, fanout=2), {}, {}),
  'fattree-k4': pt.BUILTIN['fattree-k4'],
}
DEFAULT_SCENARIOS = ['tree-d2-f4:university', 'fattree-k4:websearch', 'fattree-k4:datamining']
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


def run_one(net_name, workload, mode, args, run_dir):
  tag = '%s-%s-%s' % (net_name, workload, mode)
  log('\n' + '=' * 70)
  log('[*] %s | %s traffic | %s' % (net_name, workload, mode))
  log('=' * 70)

  cleanup()
  topo, delays, labels = NETWORKS[net_name]()
  for a, b, info in topo.links(withInfo=True):
    info['bw'] = args.bw
  switch = partial(OVSSwitch, datapath=args.datapath, protocols='OpenFlow10')
  net = Mininet(topo=topo, switch=switch, link=TCLink,
                controller=partial(LateStartController, ip='127.0.0.1', port=OF_PORT),
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
  flows, info = wl.make_schedule(workload, sorted(edge_of, key=lambda n: int(n[1:])), edge_of,
                                 args.duration, args.load, args.bw, args.max_bytes,
                                 '%s-%s-%d' % (net_name, workload, args.seed))
  log('    schedule: %d flows in %d s (%.1f flows/s), offered %.1f Mbit/s = %.0f%% of host capacity, '
      '%d capped at %d MB, %.0f%% leave the edge switch'
      % (info['flows'], args.duration, info['flows_per_s'], info['offered_mbps'],
         100 * info['offered_load'], info['capped_flows'], args.max_bytes // 10**6, info['off_rack_pct']))

  proc, stats_file = start_pox(mode, run_dir, tag, topo_file)
  result = {'network': net_name, 'workload': workload, 'mode': mode, 'hosts': len(net.hosts),
            'switches': len(net.switches), 'bw_mbps': args.bw, 'schedule': info}
  try:
    net.start()
    connected_at = time.time()
    if not net.waitConnected(timeout=30):
      raise RuntimeError("Switches did not connect to POX")
    helper = os.path.join(run_dir, 'tx_csum_off.py')
    server, client = os.path.join(run_dir, 'flow_server.py'), os.path.join(run_dir, 'flow_client.py')
    for path, text in ((helper, TX_CSUM_OFF), (server, SERVER), (client, CLIENT)):
      with open(path, 'w') as f:
        f.write(text)
    for h in net.hosts:
      h.cmd('sysctl -qw net.ipv6.conf.all.disable_ipv6=1 net.ipv6.conf.default.disable_ipv6=1')
      h.cmd('python3 %s %s' % (helper, h.defaultIntf().name))
    net.staticArp()

    if mode == 'reactive':
      wait_for_spanning_tree(stats_file, n_links, connected_at)
      for h in net.hosts:   # host discovery: one broadcast per host
        h.cmd('ping -n -b -c 1 -W 1 10.255.255.255 > /dev/null 2>&1')
      time.sleep(0.5)
    else:
      wait_for(lambda: sum(1 for s in read_stats(stats_file)['switches'].values()
                           if s['install_ms'] is not None) >= len(net.switches), 30)

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

    time.sleep(max(0, t0 - time.time()))
    s0, c0, w0 = fresh_stats(stats_file, time.time())['totals'], cpu_seconds(proc.pid), time.time()
    peak_total, peak_switch = 0, 0
    while time.time() < t0 + args.duration:   # sample the flow tables while traffic runs
      time.sleep(min(5, max(0.1, t0 + args.duration - time.time())))
      now = rule_counts(net)
      data = {k: max(0, now[k] - ctrl_rules.get(k, 0)) for k in now}   # data rules only
      peak_total = max(peak_total, sum(data.values()))
      peak_switch = max(peak_switch, max(data.values()))
    s1, c1, w1 = fresh_stats(stats_file, time.time())['totals'], cpu_seconds(proc.pid), time.time()

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
    window = w1 - w0
    result.update({
      'fct': fct_summary(rows), 'flows_detail': rows,
      'control': {'packet_in_per_s': (s1['packet_in'] - s0['packet_in']) / window,
                  'flow_mod_per_s': (s1['flow_mod'] - s0['flow_mod']) / window,
                  'controller_cpu_pct': 100.0 * (c1 - c0) / window,
                  'peak_rules_total': peak_total, 'peak_rules_one_switch': peak_switch},
      'start_late_ms_p99': pct([r['late_ms'] for r in rows], 0.99),
    })
    f, c = result['fct'], result['control']
    fmt = lambda d, k: '%.1f' % d[k] if k in d else '-'
    log('    flows: %d done, %d failed | FCT small (<100KB) mean %s p99 %s ms | large (>10MB) mean %s ms'
        % (f['completed'], f['failed'], fmt(f['small'], 'mean_ms'), fmt(f['small'], 'p99_ms'),
           fmt(f['large'], 'mean_ms')))
    log('    controller: %.0f PACKET_IN/s, %.0f FLOW_MOD/s, CPU %.1f%% | rules: peak %d total, %d in one switch'
        % (c['packet_in_per_s'], c['flow_mod_per_s'], c['controller_cpu_pct'],
           c['peak_rules_total'], c['peak_rules_one_switch']))
  finally:
    net.stop()
    stop_pox(proc)
  return result


def write_markdown(results, meta, run_dir):
  f = lambda d, k, p=1: ('%.*f' % (p, d[k])) if d and k in d else '-'
  a = meta['args']
  lines = ['# Realistic traffic results (%s)' % os.path.basename(run_dir.rstrip('/')), '',
           'Testbed: %s | Python %s | %s | datapath=%s | every link %d Mbit/s | %d s of arrivals | '
           'target load %.0f%% (websearch/datamining) | flows capped at %d MB'
           % (meta['uname'], meta['python'], meta['ovs'], a['datapath'], a['bw'], a['duration'],
              100 * a['load'], a['max_bytes'] // 10**6), '',
           '## Traffic generated (identical for every controller)', '',
           '| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |',
           '| --- | --- | --- | --- | --- | --- | --- | --- |']
  seen = set()
  for r in results:
    key = (r['network'], r['workload'])
    if key in seen:
      continue
    seen.add(key)
    s = r['schedule']
    lines.append('| %s | %s | %s | %d | %.1f | %.1f (%.0f%%) | %d | %.0f%% |' % (
      r['network'], r['workload'], s['source'], s['flows'], s['flows_per_s'], s['offered_mbps'],
      100 * s['offered_load'], s['capped_flows'], s['off_rack_pct']))
  lines += ['', '## Flow completion time (ms)', '',
            '| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | '
            'Medium: mean | Large > 10 MB: mean |',
            '| --- | --- | --- | --- | --- | --- | --- |']
  for r in results:
    x = r['fct']
    lines.append('| %s | %s | %s | %d / %d | %s / %s / %s | %s | %s |' % (
      r['network'], r['workload'], MODE_LABEL[r['mode']], x['completed'], x['failed'],
      f(x['small'], 'mean_ms', 2), f(x['small'], 'p50_ms', 2), f(x['small'], 'p99_ms', 2),
      f(x['medium'], 'mean_ms'), f(x['large'], 'mean_ms')))
  lines += ['', '## Controller load and rules', '',
            '| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | '
            'Peak rules (all switches) | Peak rules (one switch) |',
            '| --- | --- | --- | --- | --- | --- | --- | --- |']
  for r in results:
    c = r['control']
    lines.append('| %s | %s | %s | %.0f | %.0f | %.1f | %d | %d |' % (
      r['network'], r['workload'], MODE_LABEL[r['mode']], c['packet_in_per_s'], c['flow_mod_per_s'],
      c['controller_cpu_pct'], c['peak_rules_total'], c['peak_rules_one_switch']))
  path = os.path.join(run_dir, 'traffic.md')
  with open(path, 'w') as fh:
    fh.write('\n'.join(lines) + '\n')
  return path


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
  ap.add_argument('--flow-timeout', type=int, default=30, help='seconds before a flow counts as failed')
  ap.add_argument('--datapath', default='kernel', choices=['kernel', 'user'])
  ap.add_argument('--seed', type=int, default=7)
  ap.add_argument('--quick', action='store_true', help='university traffic on the tree, 10 s (smoke run)')
  ap.add_argument('--out', default=None, help='output directory')
  args = ap.parse_args()

  if os.geteuid() != 0:
    sys.exit("Mininet needs root: run with sudo")
  if not os.path.exists(os.path.join(POX_DIR, 'pox.py')):
    sys.exit("POX not found at %s (clone it there or set POX_DIR)" % POX_DIR)
  if args.quick:
    args.scenarios, args.duration = ['tree-d2-f4:university'], 10
  args.max_bytes = args.max_mb * 10**6
  scenarios = []
  for s in args.scenarios:
    net_name, _, workload = s.partition(':')
    if net_name not in NETWORKS or workload not in wl.WORKLOADS:
      sys.exit("Unknown scenario %s" % s)
    modes = args.modes or (['reactive', 'proactive', 'proactive-ecmp'] if 'fattree' in net_name
                           else ['reactive', 'proactive'])
    scenarios += [(net_name, workload, m) for m in modes]

  run_dir = args.out or os.path.join(REPO, 'results', 'measured', 'traffic-' + time.strftime('%Y%m%d-%H%M%S'))
  os.makedirs(run_dir, exist_ok=True)
  setLogLevel('warning')
  # tc warns that the HTB quantum is large at 100 Mbit/s; it is harmless, so hide it
  lg.addFilter(lambda record: 'quantum of class' not in record.getMessage())

  results = []
  try:
    for net_name, workload, mode in scenarios:
      results.append(run_one(net_name, workload, mode, args, run_dir))
  finally:
    cleanup()
    meta = {'args': vars(args), 'started_by': os.environ.get('SUDO_USER'),
            'uname': ' '.join(os.uname()), 'python': sys.version.split()[0],
            'ovs': subprocess.run(['ovs-vsctl', '--version'], capture_output=True,
                                  text=True).stdout.split('\n')[0]}
    with open(os.path.join(run_dir, 'traffic.json'), 'w') as fh:
      json.dump({'meta': meta, 'results': results}, fh, indent=1)

  # If even the best controller in a scenario loses flows, the network or the machine is overloaded
  for key in sorted({(r['network'], r['workload']) for r in results}):
    runs = [r for r in results if (r['network'], r['workload']) == key]
    best = min(runs, key=lambda r: r['fct']['failed'])
    if best['fct']['failed'] > 0.01 * best['fct']['flows']:
      log('[!] %s / %s: even the best controller (%s) lost %d of %d flows. Either the links are '
          'overloaded or this machine cannot keep up; try a lower --load or --bw and say which you used.'
          % (key[0], key[1], best['mode'], best['fct']['failed'], best['fct']['flows']))

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
