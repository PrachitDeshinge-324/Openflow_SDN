#!/usr/bin/env python3
"""
Path quality: optimal path vs haphazard path (Mininet + POX)
CS G525 Advanced Computer Networks - Project SA7

The tree networks in run_experiments.py have exactly one path between any two
hosts, so every controller uses the same path. This script uses networks with
many paths and checks which path each controller actually picks:

  fattree-k4 : data-centre fat-tree, 20 switches, 16 hosts, 4 paths between pods
  abilene    : US research backbone (Internet Topology Zoo), 11 cities, link
               delays from the distance between the cities
  --gml F    : any other Topology Zoo map, e.g. Geant2012.gml

Controllers compared (all links have the same bandwidth, --bw):
  reactive       : learning switch (reactive_eval) + POX spanning tree. Floods
                   follow the tree, so paths are whatever the tree gives
                   ("haphazard": nobody chose them for being short)
  proactive      : proactive_eval, one lowest-delay path per host pair
  proactive-ecmp : proactive_eval, host pairs spread over all equal-cost paths

Experiment A - path stretch and delay: for sampled host pairs, ping, then
  follow the installed rules switch by switch to find the path actually used.
  Hop stretch   = hops used / fewest hops possible
  Delay stretch = path delay used / lowest path delay possible
Experiment B - throughput and link balance: every host sends one TCP flow to
  another host at the same time (random permutation). Measures per-flow and
  total throughput and how evenly bytes are spread over the switch links
  (max link utilisation, Jain's fairness index, links left unused).

Usage (Mininet needs root):
  sudo python3 experiments/run_path_experiments.py              # ~10 min
  sudo python3 experiments/run_path_experiments.py --quick      # Abilene only, ~2 min
  sudo python3 experiments/run_path_experiments.py --gml ~/Downloads/Geant2012.gml
Output: results/measured/paths-<timestamp>/ (paths.json, paths.md, plots).
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
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import OVSSwitch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import path_topologies as pt
from run_experiments import (CONTROLLER_DIR, OF_PORT, POX_DIR, REPO, LateStartController,
                             log, ping_rtts, port_open, read_stats, stop_pox, wait_for,
                             write_topology)
sys.path.insert(0, CONTROLLER_DIR)
from sa7_common import load_link_weights, load_topology, shortest_paths

MODES = ['reactive', 'proactive', 'proactive-ecmp']
FLOW_PORT = 5001

# Receiver: counts the bytes that arrive between second 1 and second W-1 after the
# connection opens (skipping TCP start-up), then exits; prints bytes and seconds
RECEIVER = r'''
import socket, sys, time
port, wait, w = int(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])
s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', port)); s.listen(1); s.settimeout(wait)
c, _ = s.accept(); c.settimeout(1)
n, t0 = 0, time.time()
while time.time() - t0 < w:
    try:
        b = c.recv(65536)
    except socket.timeout:
        continue
    if not b:
        break
    if 1 <= time.time() - t0 <= w - 1:
        n += len(b)
print(n, w - 2)
'''

# `ethtool -K <intf> tx off` without needing ethtool: with Open vSwitch's userspace
# datapath, TCP packets with offloaded (unfinished) checksums are dropped
TX_CSUM_OFF = r'''
import array, fcntl, socket, struct, sys
buf = array.array('B', struct.pack('II', 0x17, 0))   # ETHTOOL_STXCSUM, off
ifr = struct.pack('16sP', sys.argv[1].encode(), buf.buffer_info()[0])
fcntl.ioctl(socket.socket(socket.AF_INET, socket.SOCK_DGRAM), 0x8946, ifr)   # SIOCETHTOOL
'''

SENDER = r'''
import socket, sys, time
s = socket.create_connection((sys.argv[1], int(sys.argv[2])), timeout=10)
buf = b'x' * 65536; end = time.time() + float(sys.argv[3])
try:
    while time.time() < end:
        s.sendall(buf)
except OSError:
    pass   # the receiver stops when its window ends
'''


def netem_available():
  """Link delay needs the kernel's netem queue; some kernels (e.g. some cloud VMs) lack it."""
  subprocess.run('ip link del sa7nt0', shell=True, stderr=subprocess.DEVNULL)
  subprocess.run('ip link add sa7nt0 type veth peer name sa7nt1', shell=True, check=True)
  ok = subprocess.run('tc qdisc add dev sa7nt0 root netem delay 1ms', shell=True,
                      stderr=subprocess.DEVNULL).returncode == 0
  subprocess.run('ip link del sa7nt0', shell=True)
  return ok


# ---------------------------------------------------------------- controller

def start_pox(mode, run_dir, tag, topo_file):
  stats_file = os.path.join(run_dir, '%s-stats.json' % tag)
  if mode == 'reactive':
    module = ['openflow.discovery', 'openflow.spanning_tree', '--no-flood', '--hold-down',
              'reactive_eval', '--match=exact']
  else:
    module = ['proactive_eval', '--topo=%s' % topo_file, '--granularity=pair',
              '--paths=%s' % ('ecmp' if mode == 'proactive-ecmp' else 'shortest')]
  cmd = [sys.executable, os.path.join(POX_DIR, 'pox.py'),
         'openflow.of_01', '--port=%d' % OF_PORT] + module + ['--stats_file=%s' % stats_file]
  env = dict(os.environ)
  env['PYTHONPATH'] = CONTROLLER_DIR + os.pathsep + env.get('PYTHONPATH', '')
  logf = open(os.path.join(run_dir, '%s-pox.log' % tag), 'w')
  proc = subprocess.Popen(cmd, cwd=POX_DIR, env=env, stdout=logf, stderr=subprocess.STDOUT)
  if not wait_for(lambda: port_open(OF_PORT) or proc.poll() is not None, 20) or proc.poll() is not None:
    raise RuntimeError("POX did not start - see %s-pox.log" % tag)
  return proc, stats_file


def wait_for_spanning_tree(stats_file, n_links, connected_at):
  """Reactive only: wait until discovery has seen every link, then for the tree's ports."""
  ok = wait_for(lambda: read_stats(stats_file)['extra'].get('links', 0) >= 2 * n_links, 60, 0.5)
  found = read_stats(stats_file)['extra'].get('links', 0)
  if not ok:
    log('    WARNING: discovery found %d of %d link directions' % (found, 2 * n_links))
  # spanning_tree --hold-down keeps flooding off for one discovery cycle (5 s) + 1 s
  # after a switch connects, and port updates are confirmed 2 s later
  time.sleep(max(0, connected_at + 9 - time.time()) + 2)
  return found


# ---------------------------------------------------------------- path tracing

FLOW_RE = {
  'priority': re.compile(r'priority=(\d+)'),
  'n_packets': re.compile(r'n_packets=(\d+)'),
  'in_port': re.compile(r'in_port=(\d+)'),
  'dl_src': re.compile(r'dl_src=([0-9a-f:]{17})'),
  'dl_dst': re.compile(r'dl_dst=([0-9a-f:]{17})'),
  'output': re.compile(r'actions=output:(\d+)'),
}


def dump_rules(sw):
  out = sw.cmd('ovs-ofctl --no-names -O OpenFlow10 dump-flows %s' % sw.name)
  rules = []
  for line in out.splitlines():
    if 'cookie=' not in line:
      continue
    r = {}
    for k, rx in FLOW_RE.items():
      m = rx.search(line)
      r[k] = m.group(1) if m else None
    if r['output']:
      rules.append(r)
  return rules


class Tracer(object):
  """Follows the rules installed in the switches to find the path a host pair uses."""

  def __init__(self, net, topo_file):
    self.hosts, self.adj = load_topology(topo_file)
    self.host = {h['name']: h for h in self.hosts}
    self.peer = {}   # (dpid, port) -> neighbour dpid, port there
    with open(topo_file) as f:
      for l in json.load(f)['links']:
        self.peer[(l['dpid1'], l['port1'])] = (l['dpid2'], l['port2'])
        self.peer[(l['dpid2'], l['port2'])] = (l['dpid1'], l['port1'])
    self.switch = {int(sw.dpid, 16): sw for sw in net.switches}

  def path(self, src_name, dst_name):
    src, dst = self.host[src_name], self.host[dst_name]
    cur, in_port, path = src['dpid'], src['port'], [src['dpid']]
    while len(path) <= 2 * len(self.adj):
      best = None
      for r in dump_rules(self.switch[cur]):
        if r['dl_dst'] != dst['mac'].lower() or r['dl_src'] not in (None, src['mac'].lower()):
          continue
        if r['in_port'] is not None and int(r['in_port']) != in_port:
          continue
        key = (int(r['priority'] or 0), int(r['n_packets'] or 0))
        if best is None or key > best[0]:
          best = (key, int(r['output']))
      if best is None:
        return None   # no rule: the pair's rules were never installed or have expired
      out = best[1]
      if cur == dst['dpid'] and out == dst['port']:
        return path
      if (cur, out) not in self.peer:
        return None
      cur, in_port = self.peer[(cur, out)]
      path.append(cur)
    return None   # loop


# ---------------------------------------------------------------- experiments

def path_cost(path, weights):
  return sum(weights[(a, b)] for a, b in zip(path, path[1:]))


def experiment_paths(net, pairs, tracer, weights, has_delay, args):
  rows = []
  for src, dst in pairs:
    rtts = ping_rtts(src, dst, args.count, args.interval)
    used = tracer.path(src.name, dst.name)
    a, b = tracer.host[src.name]['dpid'], tracer.host[dst.name]['dpid']
    min_hops = len(shortest_paths(tracer.adj, None, a, b)[0]) - 1
    best_delay = path_cost(shortest_paths(tracer.adj, weights, a, b)[0], weights) if has_delay else None
    rest = [r for r in rtts[2:] if r is not None]
    row = {'src': src.name, 'dst': dst.name, 'path': used, 'rtts_ms': rtts,
           'rtt_ms': statistics.median(rest) if rest else None,
           'min_hops': min_hops, 'best_delay_ms': best_delay}
    if used:
      row['hops'] = len(used) - 1
      row['hop_stretch'] = row['hops'] / min_hops if min_hops else 1.0
      if has_delay:
        row['delay_ms'] = path_cost(used, weights)
        row['delay_stretch'] = row['delay_ms'] / best_delay if best_delay else 1.0
    rows.append(row)

  traced = [r for r in rows if r['path']]
  res = {'pairs': rows, 'traced': len(traced),
         'lost_packets': sum(x is None for r in rows for x in r['rtts_ms'])}
  for key in ('hop_stretch', 'delay_stretch', 'hops', 'rtt_ms'):
    xs = [r[key] for r in traced if r.get(key) is not None]
    if xs:
      res[key] = {'mean': statistics.mean(xs), 'max': max(xs),
                  'longer_than_best_pct': (100.0 * sum(x > 1 + 1e-9 for x in xs) / len(xs)
                                           if 'stretch' in key else None)}
  if has_delay and traced:   # round trip over the map's link delays (both ways, same path)
    res['path_rtt_ms'] = statistics.mean(2 * r['delay_ms'] for r in traced)
    res['best_path_rtt_ms'] = statistics.mean(2 * r['best_delay_ms'] for r in traced)
  return res


def switch_links(net):
  """[(name, interface, from switch, to switch)] for both directions of every switch link."""
  out = []
  for link in net.links:
    n1, n2 = link.intf1.node, link.intf2.node
    if n1 in net.switches and n2 in net.switches:
      out.append(('%s>%s' % (n1.name, n2.name), link.intf1.name))
      out.append(('%s>%s' % (n2.name, n1.name), link.intf2.name))
  return out


def tx_bytes(intf):
  with open('/sys/class/net/%s/statistics/tx_bytes' % intf) as f:
    return int(f.read())


def jain(xs):
  s2 = sum(x * x for x in xs)
  return (sum(xs) ** 2) / (len(xs) * s2) if s2 else 0.0


def derangement(n, rng):
  while True:
    p = list(range(n))
    rng.shuffle(p)
    if all(i != p[i] for i in range(n)):
      return p


def experiment_throughput(net, run_dir, tag, rng, args):
  recv = os.path.join(run_dir, 'flow_receiver.py')
  send = os.path.join(run_dir, 'flow_sender.py')
  with open(recv, 'w') as f:
    f.write(RECEIVER)
  with open(send, 'w') as f:
    f.write(SENDER)
  hosts, links = net.hosts, switch_links(net)
  runs = []
  for p in range(args.perms):
    perm = derangement(len(hosts), rng)
    outs = {}
    w = args.flow_seconds
    for i, h in enumerate(hosts):
      outs[h.name] = os.path.join(run_dir, '%s-perm%d-%s.txt' % (tag, p, h.name))
      h.cmd('python3 %s %d 20 %d > %s 2>&1 &' % (recv, FLOW_PORT, w, outs[h.name]))
    time.sleep(1)
    for i, h in enumerate(hosts):
      h.cmd('python3 %s %s %d %d > /dev/null 2>&1 &' % (send, hosts[perm[i]].IP(), FLOW_PORT, w + 3))
    # Link counters over the same steady window the receivers count (second 1 to w-1)
    time.sleep(1)
    before, t0 = {name: tx_bytes(intf) for name, intf in links}, time.time()
    time.sleep(w - 2)
    after, elapsed = {name: tx_bytes(intf) for name, intf in links}, time.time() - t0
    wait_for(lambda: all(os.path.getsize(o) > 0 for o in outs.values()), 25, 0.5)

    flows = []
    for i, h in enumerate(hosts):
      dst = hosts[perm[i]]
      try:
        n, secs = open(outs[dst.name]).read().split()[:2]
        mbps = int(n) * 8 / float(secs) / 1e6
      except (ValueError, ZeroDivisionError):
        mbps = 0.0   # the flow never connected
      flows.append({'src': h.name, 'dst': dst.name, 'mbps': mbps})
    load = {name: (after[name] - before[name]) * 8 / elapsed / 1e6 for name, _ in links}
    util = sorted(load.values(), reverse=True)
    runs.append({
      'flows': flows, 'link_mbps': load,
      'total_mbps': sum(f['mbps'] for f in flows),
      'mean_flow_mbps': statistics.mean(f['mbps'] for f in flows),
      'min_flow_mbps': min(f['mbps'] for f in flows),
      'max_link_util_pct': 100.0 * util[0] / args.bw,
      'jain_links': jain(util),
      'unused_links_pct': 100.0 * sum(x < 0.1 for x in util) / len(util),
    })
    r = runs[-1]
    log('    permutation %d: total %6.1f Mbit/s, flow mean %5.2f / min %5.2f, '
        'busiest link %5.1f%%, Jain %.2f, %4.1f%% links unused'
        % (p + 1, r['total_mbps'], r['mean_flow_mbps'], r['min_flow_mbps'],
           r['max_link_util_pct'], r['jain_links'], r['unused_links_pct']))
    time.sleep(3)   # let the senders finish before the next permutation

  summary = {}
  for key in ('total_mbps', 'mean_flow_mbps', 'min_flow_mbps', 'max_link_util_pct',
              'jain_links', 'unused_links_pct'):
    xs = [r[key] for r in runs]
    summary[key] = {'mean': statistics.mean(xs), 'std': statistics.stdev(xs) if len(xs) > 1 else 0.0}
  return {'runs': runs, 'summary': summary, 'ideal_total_mbps': args.bw * len(hosts)}


def run_one(topo_name, builder, mode, args, run_dir):
  tag = '%s-%s' % (topo_name, mode)
  log('\n' + '=' * 70)
  log('[*] %s | %s' % (topo_name, mode))
  log('=' * 70)

  cleanup()
  topo, delays, labels = builder()
  for a, b, info in topo.links(withInfo=True):   # same bandwidth everywhere; delay on ISP links
    info['bw'] = args.bw
    d = delays.get((a, b), delays.get((b, a)))
    if d is not None and args.netem:
      info['delay'] = '%.2fms' % d
  switch = partial(OVSSwitch, datapath=args.datapath, protocols='OpenFlow10')
  net = Mininet(topo=topo, switch=switch, link=TCLink,
                controller=partial(LateStartController, ip='127.0.0.1', port=OF_PORT),
                autoSetMacs=True, waitConnected=False)
  topo_file = os.path.join(run_dir, '%s-topo.json' % topo_name)
  write_topology(net, topo_file, delays)
  weights = load_link_weights(topo_file)
  n_links = len(weights) // 2

  proc, stats_file = start_pox(mode, run_dir, tag, topo_file)
  rng = random.Random(args.seed)
  try:
    net.start()
    connected_at = time.time()
    if not net.waitConnected(timeout=30):
      raise RuntimeError("Switches did not connect to POX")
    csum = os.path.join(run_dir, 'tx_csum_off.py')
    with open(csum, 'w') as f:
      f.write(TX_CSUM_OFF)
    for h in net.hosts:
      h.cmd('sysctl -qw net.ipv6.conf.all.disable_ipv6=1 net.ipv6.conf.default.disable_ipv6=1')
      h.cmd('python3 %s %s' % (csum, h.defaultIntf().name))
    net.staticArp()

    result = {'topology': topo_name, 'mode': mode, 'hosts': len(net.hosts),
              'switches': len(net.switches), 'links': n_links, 'bw_mbps': args.bw,
              'has_delay': bool(delays), 'delay_emulated': bool(delays) and args.netem,
              'labels': labels}
    if mode == 'reactive':
      result['links_discovered'] = wait_for_spanning_tree(stats_file, n_links, connected_at)
      for h in net.hosts:   # host discovery: one broadcast per host, floods along the tree
        h.cmd('ping -n -b -c 1 -W 1 10.255.255.255 > /dev/null 2>&1')
      time.sleep(0.5)
    else:
      wait_for(lambda: sum(1 for s in read_stats(stats_file)['switches'].values()
                           if s['install_ms'] is not None) >= len(net.switches), 30)

    hosts = net.hosts
    ordered = [(a, b) for a in hosts for b in hosts if a is not b]
    pairs = rng.sample(ordered, min(args.pairs, len(ordered)))
    tracer = Tracer(net, topo_file)

    log('[A] Path stretch: %d host pairs x %d pings' % (len(pairs), args.count))
    a = experiment_paths(net, pairs, tracer, weights, bool(delays), args)
    result['paths'] = a
    msg = '    traced %d/%d | hop stretch mean %.2f max %.2f (%.0f%% of pairs longer than best)' % (
      a['traced'], len(pairs), a['hop_stretch']['mean'], a['hop_stretch']['max'],
      a['hop_stretch']['longer_than_best_pct'])
    if delays:
      msg += ' | delay stretch mean %.2f max %.2f | path RTT %.1f ms (best possible %.1f)' % (
        a['delay_stretch']['mean'], a['delay_stretch']['max'], a['path_rtt_ms'], a['best_path_rtt_ms'])
    log(msg + ' | lost %d' % a['lost_packets'])

    log('[B] Throughput and link balance: %d simultaneous TCP flows, %d s, %d permutations'
        % (len(hosts), args.flow_seconds, args.perms))
    result['throughput'] = experiment_throughput(net, run_dir, tag, rng, args)
  finally:
    net.stop()
    stop_pox(proc)

  result['controller'] = read_stats(stats_file)
  return result


# ---------------------------------------------------------------- output

MODE_LABEL = {'reactive': 'Reactive (learning + spanning tree)',
              'proactive': 'Proactive (one shortest path)',
              'proactive-ecmp': 'Proactive (ECMP)'}


def write_markdown(results, meta, run_dir):
  f = lambda x, p=2: '-' if x is None else ('%.*f' % (p, x))
  lines = ['# Path quality results (%s)' % os.path.basename(run_dir.rstrip('/')), '',
           'Testbed: %s | Python %s | %s | datapath=%s | every link %d Mbit/s' % (
             meta['uname'], meta['python'], meta['ovs'], meta['args']['datapath'], meta['args']['bw']), '',
           'Link delays emulated with netem: %s. Path RTT is computed from the map\'s link delays '
           'along the traced path; measured RTT is ping (it includes the delays only when emulated).'
           % ('yes' if meta['args']['netem'] else 'no (kernel has no netem)'), '',
           '## A: path stretch (1.00 = best possible path)', '',
           '| Network | Controller | Pairs traced | Hop stretch mean / max | Pairs on a longer path | '
           'Delay stretch mean / max | Path RTT (ms) | Best path RTT (ms) | Measured RTT (ms) |',
           '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
  for r in results:
    a = r['paths']
    hs, ds = a.get('hop_stretch', {}), a.get('delay_stretch', {})
    longer = ds.get('longer_than_best_pct') if r['has_delay'] else hs.get('longer_than_best_pct')
    lines.append('| %s | %s | %d / %d | %s / %s | %s%% | %s | %s | %s | %s |' % (
      r['topology'], MODE_LABEL[r['mode']], a['traced'], len(a['pairs']),
      f(hs.get('mean')), f(hs.get('max')), f(longer, 0),
      '%s / %s' % (f(ds.get('mean')), f(ds.get('max'))) if r['has_delay'] else '-',
      f(a.get('path_rtt_ms'), 1), f(a.get('best_path_rtt_ms'), 1),
      f(a.get('rtt_ms', {}).get('mean'), 2)))
  lines += ['', '## B: throughput and link balance (mean +/- std over permutations)', '',
            '| Network | Controller | Total Mbit/s (ideal) | Mean flow Mbit/s | Slowest flow Mbit/s | '
            'Busiest link % | Jain index over links | Links unused % |',
            '| --- | --- | --- | --- | --- | --- | --- | --- |']
  for r in results:
    s = r['throughput']['summary']
    pm = lambda k, p=1: '%s +/- %s' % (f(s[k]['mean'], p), f(s[k]['std'], p))
    lines.append('| %s | %s | %s (%d) | %s | %s | %s | %s | %s |' % (
      r['topology'], MODE_LABEL[r['mode']], pm('total_mbps'), r['throughput']['ideal_total_mbps'],
      pm('mean_flow_mbps', 2), pm('min_flow_mbps', 2), pm('max_link_util_pct'),
      pm('jain_links', 2), pm('unused_links_pct')))
  path = os.path.join(run_dir, 'paths.md')
  with open(path, 'w') as fh:
    fh.write('\n'.join(lines) + '\n')
  return path


def main():
  ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  ap.add_argument('--topos', nargs='+', default=list(pt.BUILTIN), choices=list(pt.BUILTIN))
  ap.add_argument('--gml', nargs='*', default=[], help='extra Internet Topology Zoo .gml files')
  ap.add_argument('--modes', nargs='+', default=MODES, choices=MODES)
  ap.add_argument('--pairs', type=int, default=40, help='host pairs for the path-stretch test')
  ap.add_argument('--count', type=int, default=6, help='pings per pair')
  ap.add_argument('--interval', default='0.1', help='seconds between pings')
  ap.add_argument('--bw', type=int, default=10, help='bandwidth of every link, Mbit/s')
  ap.add_argument('--flow-seconds', type=int, default=10)
  ap.add_argument('--perms', type=int, default=3, help='random traffic permutations')
  ap.add_argument('--datapath', default='kernel', choices=['kernel', 'user'])
  ap.add_argument('--seed', type=int, default=7)
  ap.add_argument('--quick', action='store_true', help='Abilene only, fewer pairs (smoke run)')
  ap.add_argument('--out', default=None, help='output directory')
  args = ap.parse_args()

  if os.geteuid() != 0:
    sys.exit("Mininet needs root: run with sudo")
  if not os.path.exists(os.path.join(POX_DIR, 'pox.py')):
    sys.exit("POX not found at %s (clone it there or set POX_DIR)" % POX_DIR)
  if args.flow_seconds < 4:
    sys.exit("--flow-seconds must be at least 4")
  if args.quick:
    args.topos, args.pairs, args.perms, args.flow_seconds = ['abilene'], 12, 1, 6

  args.netem = netem_available()
  if not args.netem:
    log('[!] This kernel has no netem: link delays are not emulated. Path delay is still '
        'computed from the map; pings show switching delay only.')
  topos = [(name, pt.BUILTIN[name]) for name in args.topos]
  topos += [(pt.gml_name(g), partial(pt.from_gml, g)) for g in args.gml]

  run_dir = args.out or os.path.join(REPO, 'results', 'measured', 'paths-' + time.strftime('%Y%m%d-%H%M%S'))
  os.makedirs(run_dir, exist_ok=True)
  setLogLevel('warning')

  results = []
  try:
    for name, builder in topos:
      for mode in args.modes:
        results.append(run_one(name, builder, mode, args, run_dir))
  finally:
    cleanup()
    meta = {'args': vars(args), 'started_by': os.environ.get('SUDO_USER'),
            'uname': ' '.join(os.uname()), 'python': sys.version.split()[0],
            'ovs': subprocess.run(['ovs-vsctl', '--version'], capture_output=True,
                                  text=True).stdout.split('\n')[0]}
    with open(os.path.join(run_dir, 'paths.json'), 'w') as fh:
      json.dump({'meta': meta, 'results': results}, fh, indent=2)

  md = write_markdown(results, meta, run_dir)
  log('\n[+] Raw results: %s' % os.path.join(run_dir, 'paths.json'))
  log('[+] Tables:      %s' % md)
  subprocess.run([sys.executable, os.path.join(HERE, 'plot_paths.py'), run_dir])

  uid, gid = os.environ.get('SUDO_UID'), os.environ.get('SUDO_GID')
  if uid and gid:   # files were created as root; hand them back to the user who ran sudo
    for root, dirs, files in os.walk(run_dir):
      for name in dirs + files:
        os.chown(os.path.join(root, name), int(uid), int(gid))
    os.chown(run_dir, int(uid), int(gid))


if __name__ == '__main__':
  main()
