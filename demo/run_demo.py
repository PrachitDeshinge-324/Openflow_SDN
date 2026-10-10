#!/usr/bin/env python3
"""
Live Demonstration: Reactive vs. Proactive Flow Installation
CS G525 Advanced Computer Networks - Project SA7

One command that walks through the demo with on-screen captions, so it can be
run live or screen-recorded. On the 4-host tree (h1 ... h4, switches s1-s3):

  Part 1  REACTIVE  - s1 starts empty; h1 pings h4; the first packet waits for
                      the controller; rules appear on s1 only after traffic.
  Part 2  PROACTIVE - s1 already holds every rule before any traffic; the first
                      packet is fast; the controller receives no PACKET_IN.
  Part 3  Side-by-side summary.

Usage (needs root, like Mininet):
  sudo python3 demo/run_demo.py                  # kernel datapath
  sudo python3 demo/run_demo.py --datapath user  # if 'modprobe openvswitch' fails
  sudo python3 demo/run_demo.py --pause 0        # no pauses between steps
"""

import argparse
import os
import re
import statistics
import subprocess
import sys
import tempfile
import time
from functools import partial
from types import SimpleNamespace

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, 'experiments'))

import run_experiments as rx   # reuses its POX/topology helpers  # noqa: E402
from mininet.clean import cleanup  # noqa: E402
from mininet.log import setLogLevel  # noqa: E402
from mininet.net import Mininet  # noqa: E402
from mininet.node import OVSSwitch  # noqa: E402
from mininet.topolib import TreeTopo  # noqa: E402

BOLD, DIM, RESET = '\033[1m', '\033[2m', '\033[0m'
ORANGE, BLUE, GREEN, CYAN = '\033[38;5;209m', '\033[38;5;111m', '\033[38;5;114m', '\033[38;5;80m'

PING_RE = re.compile(r'icmp_seq=(\d+) ttl=\d+ time=([\d.]+) ms')


def say(text, color=CYAN):
  print('%s%s%s' % (color, text, RESET), flush=True)


def heading(text, color):
  print('\n%s%s%s\n%s%s%s' % (BOLD + color, text, RESET, color, '─' * len(text), RESET), flush=True)


def command(prompt, cmd):
  print('%s%s%s %s' % (DIM, prompt, RESET, cmd), flush=True)


def wait(args, seconds=None):
  time.sleep(args.pause if seconds is None else seconds * (args.pause > 0))


def compact_flow(line):
  """One dump-flows line, without the fields that do not matter for the demo."""
  line = re.sub(r'\s*(cookie|duration|table|n_bytes|hard_timeout)=[^,\s]+,?', '', line.strip())
  line = re.sub(r'(vlan_tci=0x0000|nw_tos=0|icmp_code=0|priority=65535),?', '', line)
  if 'nw_src=' in line:   # IP addresses already identify the hosts
    line = re.sub(r'dl_(src|dst)=[0-9a-f:]+,?', '', line)
  return re.sub(r',\s*actions', ' actions', line).strip()


def show_flows(sw, args):
  command('mininet>', 'sh ovs-ofctl dump-flows %s   %s(trimmed to the key fields)%s' % (sw.name, DIM, RESET))
  lines = [l for l in sw.dpctl('dump-flows').splitlines() if 'cookie=' in l]
  rules = [l for l in lines if not re.search(r'priority=0[ ,]', l)]
  if not rules:
    say('   (no rules: the flow table is empty)', DIM)
  for l in rules[:args.max_rules]:
    print('   ' + compact_flow(l), flush=True)
  if len(rules) > args.max_rules:
    say('   ... and %d more' % (len(rules) - args.max_rules), DIM)
  return len(rules)


def live_ping(src, dst, count):
  command('mininet>', '%s ping -c %d %s' % (src.name, count, dst.name))
  p = src.popen(['ping', '-n', '-c', str(count), '-i', '0.5', dst.IP()],
                stdout=subprocess.PIPE, universal_newlines=True)
  rtts = []
  for line in p.stdout:
    m = PING_RE.search(line)
    if m:
      rtts.append(float(m.group(2)))
      tag = ''
      if m.group(1) == '1':
        tag = '<- packet 1'
      elif m.group(1) == '2':
        tag = '<- packet 2'
      print('   %s%s%s' % (line.rstrip().ljust(56), BOLD, tag) + RESET, flush=True)
  p.wait()
  return rtts


def counters(stats_file):
  t = rx.read_stats(stats_file)['totals']
  say('   controller counters: PACKET_IN = %d, FLOW_MOD = %d' % (t['packet_in'], t['flow_mod']), BOLD)
  return t


def run_mode(mode, args, work):
  color = ORANGE if mode == 'reactive' else BLUE
  part = 'Part 1: REACTIVE' if mode == 'reactive' else 'Part 2: PROACTIVE'
  heading('%s controller (controllers/%s_eval.py)' % (part, mode), color)

  cleanup()
  net = Mininet(topo=TreeTopo(depth=2, fanout=2),
                switch=partial(OVSSwitch, datapath=args.datapath, protocols='OpenFlow10'),
                controller=partial(rx.LateStartController, ip='127.0.0.1', port=rx.OF_PORT),
                autoSetMacs=True, waitConnected=False)
  topo_file = os.path.join(work, 'topo.json')
  rx.write_topology(net, topo_file)
  pox_args = SimpleNamespace(reactive_match='exact', idle_timeout=10, hard_timeout=30, granularity='pair')
  proc, stats_file = rx.start_pox(mode, work, 'demo-' + mode, topo_file, pox_args)
  try:
    net.start()
    net.waitConnected(timeout=20)
    for h in net.hosts:
      h.cmd('sysctl -qw net.ipv6.conf.all.disable_ipv6=1 net.ipv6.conf.default.disable_ipv6=1')
    net.staticArp()
    if mode == 'reactive':
      for h in net.hosts:   # let the controller learn where hosts are (installs no rules)
        h.cmd('ping -n -b -c 1 -W 1 10.255.255.255 > /dev/null 2>&1')
    else:
      rx.wait_for(lambda: all(s['install_ms'] is not None
                              for s in rx.read_stats(stats_file)['switches'].values())
                  and len(rx.read_stats(stats_file)['switches']) == len(net.switches), 20)
    time.sleep(1.2)
    h1, h4, s1 = net.get('h1'), net.get('h4'), net.get('s1')

    say('\n4-host tree: h1 and h4 are on different edge switches, so the path is s2 -> s1 -> s3.')
    if mode == 'reactive':
      say('Step 1. Before any traffic, the core switch s1 has no rules:')
    else:
      say('Step 1. Before any traffic, s1 already holds every rule it will need:')
    wait(args)
    before = show_flows(s1, args)
    t0 = counters(stats_file)
    if mode == 'reactive':
      say('   (these PACKET_INs are the hosts announcing themselves once; they install no rules)', DIM)
    else:
      say('   (all FLOW_MODs were sent when the switches connected: %d rules + 1 table-miss entry per switch)'
          % (t0['flow_mod'] - len(net.switches)), DIM)
    wait(args)

    say('\nStep 2. h1 pings h4. Watch packet 1 against the rest:')
    wait(args, 1)
    rtts = live_ping(h1, h4, args.count)
    wait(args)

    if mode == 'reactive':
      say('\nPacket 1 waited for the controller at every switch on the path (PACKET_IN -> FLOW_MOD).')
      say('Packet 2 is the first one Open vSwitch forwards itself, so it fills its datapath cache.')
    else:
      say('\nNo controller round trip: the rules were already there. Packet 1 only fills the')
      say('Open vSwitch datapath cache, so it is a little slower than the steady state.')
    wait(args)

    say('\nStep 3. The flow table and the controller after the ping:')
    wait(args, 1)
    after = show_flows(s1, args)
    t = counters(stats_file)
    if mode == 'reactive':
      say('This ping caused %d PACKET_INs and %d FLOW_MODs: 3 switches on the path x 2 directions.'
          % (t['packet_in'] - t0['packet_in'], t['flow_mod'] - t0['flow_mod']))
      say('Rules were created on demand by the traffic: %d before, %d after on s1.' % (before, after))
    else:
      say('Same %d rules as before the ping, and the controller received no PACKET_IN.' % after)
    wait(args)
    return {'rtts': rtts, 'rules_s1': after, 'packet_in': t['packet_in'] - t0['packet_in']}
  finally:
    net.stop()
    rx.stop_pox(proc)


def summary(results, args):
  heading('Part 3: Side by side (this run, h1 -> h4)', GREEN)
  fmt = '   %-11s %10s %10s %13s %12s %18s'
  print(BOLD + fmt % ('Mode', 'Packet 1', 'Packet 2', 'Steady (med)', 'Rules on s1', 'PACKET_INs (ping)') + RESET)
  for mode, color in (('reactive', ORANGE), ('proactive', BLUE)):
    r = results[mode]
    rt = r['rtts']
    steady = statistics.median(rt[2:]) if len(rt) > 2 else float('nan')
    print(color + fmt % (mode.capitalize(),
                         '%.3f ms' % rt[0] if rt else '-', '%.3f ms' % rt[1] if len(rt) > 1 else '-',
                         '%.3f ms' % steady, r['rules_s1'], r['packet_in']) + RESET, flush=True)
  say('\nReactive pays a controller round trip on the first packet of every flow and builds its')
  say('table from traffic. Proactive pays in table space up front and keeps the controller idle.')
  say('Full measurements: sudo python3 experiments/run_experiments.py   (results in results/measured/)')


def main():
  ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  ap.add_argument('--datapath', default='kernel', choices=['kernel', 'user'])
  ap.add_argument('--count', type=int, default=6, help='pings per mode')
  ap.add_argument('--pause', type=float, default=2.0, help='seconds between steps (0 = none)')
  ap.add_argument('--max-rules', type=int, default=6, help='rules shown per flow-table dump')
  args = ap.parse_args()
  if os.geteuid() != 0:
    sys.exit('Mininet needs root: run with sudo')
  if not os.path.exists(os.path.join(rx.POX_DIR, 'pox.py')):
    sys.exit('POX not found at %s (run setup.sh, or set POX_DIR)' % rx.POX_DIR)

  setLogLevel('error')
  print('%sCS G525 · Project SA7 · Reactive vs. Proactive Flow Installation: live demo%s' % (BOLD, RESET))
  ovs = subprocess.run(['ovs-vsctl', '--version'], capture_output=True, text=True).stdout.split('\n')[0]
  say('Mininet + %s (%s datapath) + POX, OpenFlow 1.0' % (ovs.replace('ovs-vsctl ', ''), args.datapath), DIM)
  wait(args)

  results = {}
  with tempfile.TemporaryDirectory(prefix='sa7-demo-') as work:
    try:
      for mode in ('reactive', 'proactive'):
        results[mode] = run_mode(mode, args, work)
    finally:
      cleanup()
  summary(results, args)


if __name__ == '__main__':
  main()
