#!/usr/bin/env python3
"""
Measured Evaluation: Reactive vs. Proactive Flow Installation (Mininet + POX)
CS G525 Advanced Computer Networks - Project SA7

For every topology and every controller mode this script:
  1. builds the Mininet tree topology and writes its description to topo.json
  2. starts POX with controllers/reactive_eval.py or controllers/proactive_eval.py
  3. Experiment 1 - latency: pings host pairs and records the RTT of packet 1,
     packet 2 and the steady state (packets 3..N)
  4. Experiment 2 - flow-table occupancy: generates traffic between 25/50/100%
     of host pairs and counts the rules actually present in every switch
  5. Experiment 3 - churn: sends new UDP flows at increasing rates and measures
     PACKET_IN/FLOW_MOD rates and controller CPU usage

Everything is measured; nothing is modelled. Output goes to
results/measured/<timestamp>/ (results.json, summary.csv, POX logs, plots).

Usage (Mininet needs root):
  sudo python3 experiments/run_experiments.py            # full run (~10-15 min)
  sudo python3 experiments/run_experiments.py --quick    # 4-host smoke run (~1-2 min)
  sudo python3 experiments/run_experiments.py --datapath user   # if 'modprobe openvswitch' fails
"""

import argparse
import csv
import json
import os
import random
import re
import socket
import statistics
import subprocess
import sys
import time
from functools import partial

from mininet.clean import cleanup
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController
from mininet.topolib import TreeTopo

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POX_DIR = os.environ.get('POX_DIR', os.path.join(REPO, 'pox'))
CONTROLLER_DIR = os.path.join(REPO, 'controllers')
OF_PORT = 6633

# name -> (depth, fanout); hosts = fanout ** depth
TOPOLOGIES = {
  'tree-d2-f2': (2, 2),   # 4 hosts, 3 switches
  'tree-d3-f2': (3, 2),   # 8 hosts, 7 switches
  'tree-d2-f4': (2, 4),   # 16 hosts, 5 switches
}



class LateStartController(RemoteController):
  """POX is started after the network is built, so skip Mininet's early 'is it listening?' check."""
  def checkListening(self):
    pass


CHURN_SENDER = r'''
import random, socket, sys, time
dsts = sys.argv[1].split(','); rate = float(sys.argv[2]); dur = float(sys.argv[3])
n = int(rate * dur); t0 = time.time()
for i in range(n):
    d = t0 + i / rate - time.time()
    if d > 0:
        time.sleep(d)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   # new socket = new source port = new flow
    s.sendto(b'sa7-churn', (random.choice(dsts), 9))
    s.close()
print(n, time.time() - t0)
'''

CHURN_SINK = ("import socket; s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); "
              "s.bind(('', 9)); [s.recv(64) for _ in iter(int, 1)]")


# ---------------------------------------------------------------- helpers

def log(msg):
  print(msg, flush=True)


def mean_std(xs):
  xs = [x for x in xs if x is not None]
  if not xs:
    return None, None
  return statistics.mean(xs), (statistics.stdev(xs) if len(xs) > 1 else 0.0)


def wait_for(cond, timeout, interval=0.2):
  end = time.time() + timeout
  while time.time() < end:
    if cond():
      return True
    time.sleep(interval)
  return False


def port_open(port):
  try:
    with socket.create_connection(('127.0.0.1', port), timeout=0.5):
      return True
  except OSError:
    return False


def read_stats(path):
  for _ in range(20):
    try:
      with open(path) as f:
        return json.load(f)
    except (OSError, ValueError):
      time.sleep(0.1)
  raise RuntimeError("Could not read controller stats file %s" % path)


def fresh_stats(path, after):
  """Wait for a stats dump written after time `after` (dumps happen every 1 s)."""
  wait_for(lambda: read_stats(path)['written_at'] > after, 5)
  return read_stats(path)


def cpu_seconds(pid):
  with open('/proc/%d/stat' % pid) as f:
    fields = f.read().rsplit(')', 1)[1].split()
  return (int(fields[11]) + int(fields[12])) / os.sysconf('SC_CLK_TCK')   # utime + stime


# ---------------------------------------------------------------- topology / controller

def write_topology(net, path):
  switches = {sw.name: int(sw.dpid, 16) for sw in net.switches}
  hosts, links = [], []
  for h in net.hosts:
    intf = h.defaultIntf()
    link = intf.link
    peer = link.intf2 if link.intf1 is intf else link.intf1
    hosts.append({'name': h.name, 'mac': h.MAC(), 'ip': h.IP(),
                  'dpid': switches[peer.node.name], 'port': peer.node.ports[peer]})
  for link in net.links:
    n1, n2 = link.intf1.node, link.intf2.node
    if n1.name in switches and n2.name in switches:
      links.append({'dpid1': switches[n1.name], 'port1': n1.ports[link.intf1],
                    'dpid2': switches[n2.name], 'port2': n2.ports[link.intf2]})
  with open(path, 'w') as f:
    json.dump({'switches': sorted(switches.values()), 'hosts': hosts, 'links': links}, f, indent=2)


def start_pox(mode, run_dir, tag, topo_file, args):
  stats_file = os.path.join(run_dir, '%s-stats.json' % tag)
  if mode == 'reactive':
    module = ['reactive_eval', '--match=%s' % args.reactive_match,
              '--idle_timeout=%d' % args.idle_timeout, '--hard_timeout=%d' % args.hard_timeout]
  else:
    module = ['proactive_eval', '--topo=%s' % topo_file, '--granularity=%s' % args.granularity]
  cmd = [sys.executable, os.path.join(POX_DIR, 'pox.py'),
         'openflow.of_01', '--port=%d' % OF_PORT] + module + ['--stats_file=%s' % stats_file]
  env = dict(os.environ)
  env['PYTHONPATH'] = CONTROLLER_DIR + os.pathsep + env.get('PYTHONPATH', '')
  logf = open(os.path.join(run_dir, '%s-pox.log' % tag), 'w')
  proc = subprocess.Popen(cmd, cwd=POX_DIR, env=env, stdout=logf, stderr=subprocess.STDOUT)
  if not wait_for(lambda: port_open(OF_PORT) or proc.poll() is not None, 20) or proc.poll() is not None:
    raise RuntimeError("POX did not start - see %s-pox.log" % tag)
  return proc, stats_file


def stop_pox(proc):
  proc.send_signal(2)   # SIGINT: POX shuts down cleanly and writes final stats
  try:
    proc.wait(timeout=5)
  except subprocess.TimeoutExpired:
    proc.kill()
    proc.wait()


def flow_counts(net):
  """Rules per switch, excluding the priority-0 table-miss entry."""
  counts = {}
  for sw in net.switches:
    out = sw.dpctl('dump-flows')
    counts[sw.name] = sum(1 for line in out.splitlines()
                          if 'cookie=' in line and not re.search(r'priority=0[ ,]', line))
  return counts


def clear_reactive_flows(net):
  # Equivalent to waiting for idle timeouts, but instant and deterministic
  for sw in net.switches:
    sw.dpctl('del-flows')


# ---------------------------------------------------------------- experiments

PING_RE = re.compile(r'icmp_seq=(\d+) ttl=\d+ time=([\d.]+) ms')


def ping_rtts(src, dst, count, interval):
  out = src.cmd('ping -n -c %d -i %s -W 1 %s' % (count, interval, dst.IP()))
  rtts = [None] * count
  for seq, t in PING_RE.findall(out):
    if 1 <= int(seq) <= count:
      rtts[int(seq) - 1] = float(t)
  return rtts


def experiment_latency(net, pairs, args, stats_file):
  before = read_stats(stats_file)['totals']
  per_pair = []
  for src, dst in pairs:
    rtts = ping_rtts(src, dst, args.count, args.interval)
    per_pair.append({'src': src.name, 'dst': dst.name, 'rtts_ms': rtts})
  after = fresh_stats(stats_file, time.time())['totals']

  pkt1 = [p['rtts_ms'][0] for p in per_pair]
  pkt2 = [p['rtts_ms'][1] for p in per_pair]
  steady = []
  for p in per_pair:
    rest = [r for r in p['rtts_ms'][2:] if r is not None]
    steady.append(statistics.median(rest) if rest else None)
  lost = sum(r is None for p in per_pair for r in p['rtts_ms'])
  res = {'pairs': per_pair, 'lost_packets': lost,
         'packet_in': after['packet_in'] - before['packet_in'],
         'flow_mod': after['flow_mod'] - before['flow_mod']}
  for name, xs in (('pkt1', pkt1), ('pkt2', pkt2), ('steady', steady)):
    res[name + '_mean_ms'], res[name + '_std_ms'] = mean_std(xs)
  return res


def experiment_occupancy(net, mode, all_pairs, fractions, rng):
  res = {}
  for frac in fractions:
    if mode == 'reactive':
      clear_reactive_flows(net)
    k = max(1, round(frac * len(all_pairs)))
    for src, dst in rng.sample(all_pairs, k):
      src.cmd('ping -n -c 3 -i 0.2 -W 1 %s > /dev/null 2>&1 &' % dst.IP())
    time.sleep(1.5)
    counts = flow_counts(net)
    res[str(frac)] = {'active_pairs': k, 'total_rules': sum(counts.values()),
                      'max_rules_per_switch': max(counts.values()), 'per_switch': counts}
    log('    occupancy %3d%% of pairs (%3d active): %5d rules total, max %4d per switch'
        % (frac * 100, k, sum(counts.values()), max(counts.values())))
  return res


def experiment_churn(net, mode, rates, duration, run_dir, stats_file, pox_pid):
  sender = net.hosts[0]
  others = net.hosts[1:]
  script = os.path.join(run_dir, 'churn_sender.py')
  with open(script, 'w') as f:
    f.write(CHURN_SENDER)
  dsts = ','.join(h.IP() for h in others)
  res = []
  for rate in rates:
    if mode == 'reactive':
      clear_reactive_flows(net)
    for h in others:   # listen on UDP/9 so receivers don't answer with ICMP port-unreachable
      h.cmd('timeout %d python3 -c "%s" > /dev/null 2>&1 &' % (duration + 5, CHURN_SINK))
    time.sleep(0.5)
    s0 = fresh_stats(stats_file, time.time())['totals']
    c0, t0 = cpu_seconds(pox_pid), time.time()
    out = sender.cmd('python3 %s %s %s %s' % (script, dsts, rate, duration)).split()
    s1 = fresh_stats(stats_file, time.time())['totals']
    c1, t1 = cpu_seconds(pox_pid), time.time()
    flows = sum(flow_counts(net).values())
    elapsed = float(out[1]) if len(out) == 2 else duration
    row = {'rate_flows_per_s': rate, 'flows_sent': int(out[0]) if out else 0,
           'send_duration_s': elapsed,
           'packet_in_per_s': (s1['packet_in'] - s0['packet_in']) / elapsed,
           'flow_mod_per_s': (s1['flow_mod'] - s0['flow_mod']) / elapsed,
           'controller_cpu_pct': 100.0 * (c1 - c0) / (t1 - t0),
           'rules_after': flows}
    res.append(row)
    log('    churn %4d flows/s: %7.1f PACKET_IN/s, %7.1f FLOW_MOD/s, controller CPU %5.1f%%, %5d rules'
        % (rate, row['packet_in_per_s'], row['flow_mod_per_s'], row['controller_cpu_pct'], flows))
  return res


def run_one(topo_name, mode, args, run_dir):
  depth, fanout = TOPOLOGIES[topo_name]
  tag = '%s-%s' % (topo_name, mode)
  log('\n' + '=' * 70)
  log('[*] %s | %s controller' % (topo_name, mode.upper()))
  log('=' * 70)

  cleanup()
  switch = partial(OVSSwitch, datapath=args.datapath, protocols='OpenFlow10')
  net = Mininet(topo=TreeTopo(depth=depth, fanout=fanout), switch=switch,
                controller=partial(LateStartController, ip='127.0.0.1', port=OF_PORT),
                autoSetMacs=True, waitConnected=False)
  topo_file = os.path.join(run_dir, '%s-topo.json' % topo_name)
  write_topology(net, topo_file)

  proc, stats_file = start_pox(mode, run_dir, tag, topo_file, args)
  rng = random.Random(args.seed)
  try:
    net.start()
    if not net.waitConnected(timeout=20):
      raise RuntimeError("Switches did not connect to POX")
    for h in net.hosts:
      h.cmd('sysctl -qw net.ipv6.conf.all.disable_ipv6=1 net.ipv6.conf.default.disable_ipv6=1')
    net.staticArp()   # same for both modes: keeps ARP out of the flow-setup measurement

    result = {'topology': topo_name, 'mode': mode, 'hosts': len(net.hosts),
              'switches': len(net.switches)}
    if mode == 'proactive':
      n_sw = len(net.switches)
      wait_for(lambda: sum(1 for s in read_stats(stats_file)['switches'].values()
                           if s['install_ms'] is not None) >= n_sw, 20)
      sw = read_stats(stats_file)['switches']
      result['proactive_install'] = {d: {'rules': s['rules_installed'], 'install_ms': s['install_ms']}
                                     for d, s in sw.items()}
      log('    proactive rules pushed: %d total, install time max %.1f ms'
          % (sum(s['rules_installed'] for s in sw.values()),
             max(s['install_ms'] or 0 for s in sw.values())))
    else:
      # Host discovery: one broadcast per host so switches learn every MAC (installs no rules)
      for h in net.hosts:
        h.cmd('ping -n -b -c 1 -W 1 10.255.255.255 > /dev/null 2>&1')
      time.sleep(0.5)

    hosts = net.hosts
    all_pairs = [(hosts[i], hosts[j]) for i in range(len(hosts)) for j in range(i + 1, len(hosts))]
    pairs = rng.sample(all_pairs, min(args.pairs, len(all_pairs)))

    log('[1] Latency: %d host pairs x %d pings' % (len(pairs), args.count))
    lat = experiment_latency(net, pairs, args, stats_file)
    result['latency'] = lat
    log('    packet 1: %.3f +/- %.3f ms | packet 2: %.3f ms | steady: %.3f +/- %.3f ms | lost %d'
        % (lat['pkt1_mean_ms'], lat['pkt1_std_ms'], lat['pkt2_mean_ms'],
           lat['steady_mean_ms'], lat['steady_std_ms'], lat['lost_packets']))

    log('[2] Flow-table occupancy')
    result['occupancy'] = experiment_occupancy(net, mode, all_pairs, args.fractions, rng)

    log('[3] Control-plane load under churn (%ds per rate)' % args.churn_duration)
    result['churn'] = experiment_churn(net, mode, args.rates, args.churn_duration,
                                       run_dir, stats_file, proc.pid)
  finally:
    net.stop()
    stop_pox(proc)

  result['controller'] = read_stats(stats_file)
  return result


# ---------------------------------------------------------------- output

def write_summary(results, run_dir):
  path = os.path.join(run_dir, 'summary.csv')
  with open(path, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['topology', 'mode', 'hosts', 'switches', 'pkt1_ms', 'pkt1_std', 'pkt2_ms',
                'steady_ms', 'steady_std', 'rules_100pct_total', 'rules_100pct_max_switch',
                'ctrl_packet_in_proc_us_mean'])
    for r in results:
      lat, occ = r['latency'], r['occupancy']
      full = occ[max(occ, key=float)]
      w.writerow([r['topology'], r['mode'], r['hosts'], r['switches'],
                  '%.3f' % lat['pkt1_mean_ms'], '%.3f' % lat['pkt1_std_ms'],
                  '%.3f' % lat['pkt2_mean_ms'], '%.3f' % lat['steady_mean_ms'],
                  '%.3f' % lat['steady_std_ms'], full['total_rules'], full['max_rules_per_switch'],
                  '%.1f' % r['controller']['packet_in_processing_us'].get('mean', 0)])
  return path


def write_markdown(results, meta, run_dir):
  """results.md: tables ready to paste into the report."""
  f2 = lambda x: '%.3f' % x
  lines = ['# Measured results (%s)' % os.path.basename(run_dir.rstrip('/')), '',
           'Testbed: %s | Python %s | %s | datapath=%s' % (meta['uname'], meta['python'],
                                                           meta['ovs'], meta['args']['datapath']), '',
           '## Experiment 1: flow-setup latency (RTT, ms, mean +/- std over host pairs)', '',
           '| Hosts | Mode | Packet 1 | Packet 2 | Steady state (pkts 3..N) | Lost |',
           '| --- | --- | --- | --- | --- | --- |']
  for r in results:
    l = r['latency']
    lines.append('| %d | %s | %s +/- %s | %s +/- %s | %s +/- %s | %d |' % (
      r['hosts'], r['mode'], f2(l['pkt1_mean_ms']), f2(l['pkt1_std_ms']), f2(l['pkt2_mean_ms']),
      f2(l['pkt2_std_ms']), f2(l['steady_mean_ms']), f2(l['steady_std_ms']), l['lost_packets']))
  lines += ['', '## Experiment 2: flow-table occupancy (rules in all switches / max in one switch)', '']
  fracs = sorted({f for r in results for f in r['occupancy']}, key=float)
  lines.append('| Hosts | Mode | ' + ' | '.join('%d%% pairs active' % (float(f) * 100) for f in fracs) + ' |')
  lines.append('| --- | --- |' + ' --- |' * len(fracs))
  for r in results:
    cells = ['%d / %d' % (r['occupancy'][f]['total_rules'], r['occupancy'][f]['max_rules_per_switch'])
             if f in r['occupancy'] else '-' for f in fracs]
    lines.append('| %d | %s | %s |' % (r['hosts'], r['mode'], ' | '.join(cells)))
  lines += ['', '## Experiment 3: control-plane load under churn', '',
            '| Hosts | Mode | New flows/s | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Rules after |',
            '| --- | --- | --- | --- | --- | --- | --- |']
  for r in results:
    for c in r['churn']:
      lines.append('| %d | %s | %d | %.1f | %.1f | %.1f | %d |' % (
        r['hosts'], r['mode'], c['rate_flows_per_s'], c['packet_in_per_s'], c['flow_mod_per_s'],
        c['controller_cpu_pct'], c['rules_after']))
  lines += ['', '## Controller-side numbers', '',
            '| Hosts | Mode | PACKET_IN handling time (us, mean / p95) | Proactive install time (ms, max over switches) |',
            '| --- | --- | --- | --- |']
  for r in results:
    p = r['controller']['packet_in_processing_us']
    inst = r.get('proactive_install')
    lines.append('| %d | %s | %s | %s |' % (
      r['hosts'], r['mode'], '%.0f / %.0f' % (p['mean'], p['p95']) if p.get('count') else '-',
      '%.1f' % max(v['install_ms'] or 0 for v in inst.values()) if inst else '-'))
  path = os.path.join(run_dir, 'results.md')
  with open(path, 'w') as f:
    f.write('\n'.join(lines) + '\n')
  return path


def main():
  ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  ap.add_argument('--topos', nargs='+', default=list(TOPOLOGIES), choices=list(TOPOLOGIES))
  ap.add_argument('--modes', nargs='+', default=['reactive', 'proactive'], choices=['reactive', 'proactive'])
  ap.add_argument('--pairs', type=int, default=20, help='host pairs sampled for the latency test')
  ap.add_argument('--count', type=int, default=10, help='pings per pair')
  ap.add_argument('--interval', default='0.1', help='seconds between pings')
  ap.add_argument('--fractions', nargs='+', type=float, default=[0.25, 0.5, 1.0])
  ap.add_argument('--rates', nargs='+', type=int, default=[10, 50, 100, 200])
  ap.add_argument('--churn-duration', type=int, default=5)
  ap.add_argument('--reactive-match', default='exact', choices=['exact', 'pair', 'dst'])
  ap.add_argument('--granularity', default='pair', choices=['pair', 'dst'])
  ap.add_argument('--idle-timeout', type=int, default=10)
  ap.add_argument('--hard-timeout', type=int, default=30)
  ap.add_argument('--datapath', default='kernel', choices=['kernel', 'user'])
  ap.add_argument('--seed', type=int, default=7)
  ap.add_argument('--quick', action='store_true', help='4-host topology, fewer rates (smoke run)')
  ap.add_argument('--out', default=None, help='output directory')
  args = ap.parse_args()

  if os.geteuid() != 0:
    sys.exit("Mininet needs root: run with sudo")
  if not os.path.exists(os.path.join(POX_DIR, 'pox.py')):
    sys.exit("POX not found at %s (clone it there or set POX_DIR)" % POX_DIR)
  if args.quick:
    args.topos, args.rates, args.fractions, args.churn_duration = ['tree-d2-f2'], [10, 100], [0.5, 1.0], 3

  run_dir = args.out or os.path.join(REPO, 'results', 'measured', time.strftime('%Y%m%d-%H%M%S'))
  os.makedirs(run_dir, exist_ok=True)
  setLogLevel('warning')

  results = []
  try:
    for topo_name in args.topos:
      for mode in args.modes:
        results.append(run_one(topo_name, mode, args, run_dir))
  finally:
    cleanup()
    meta = {'args': vars(args), 'started_by': os.environ.get('SUDO_USER'),
            'uname': ' '.join(os.uname()), 'python': sys.version.split()[0],
            'ovs': subprocess.run(['ovs-vsctl', '--version'], capture_output=True,
                                  text=True).stdout.split('\n')[0]}
    with open(os.path.join(run_dir, 'results.json'), 'w') as f:
      json.dump({'meta': meta, 'results': results}, f, indent=2)

  summary = write_summary(results, run_dir)
  write_markdown(results, meta, run_dir)
  log('\n[+] Raw results: %s' % os.path.join(run_dir, 'results.json'))
  log('[+] Summary:     %s' % summary)
  log('[+] Tables:      %s' % os.path.join(run_dir, 'results.md'))

  subprocess.run([sys.executable, os.path.join(REPO, 'experiments', 'plot_results.py'), run_dir])

  # Files were created as root; hand them back to the user who ran sudo
  uid, gid = os.environ.get('SUDO_UID'), os.environ.get('SUDO_GID')
  if uid and gid:
    for root, dirs, files in os.walk(os.path.join(REPO, 'results', 'measured')):
      for name in dirs + files:
        os.chown(os.path.join(root, name), int(uid), int(gid))
    os.chown(os.path.join(REPO, 'results', 'measured'), int(uid), int(gid))


if __name__ == '__main__':
  main()
