#!/usr/bin/env python3
"""
Live demonstration: what happens to new connections when the controller freezes?
CS G525 Advanced Computer Networks - Project SA7

On the 4-host tree, for two controllers in turn:

  Part 1  REACTIVE (reactive_eval): every new connection asks the controller.
  Part 2  TAP (tap_eval): rules are in place before traffic; the switch forwards
          every packet itself and only sends a copy of each connection's
          SYN / FIN / RST to the controller.

In each part h1 opens a TCP connection to h4 three times:
  1. controller running        -> how long a connection takes normally
  2. controller frozen (SIGSTOP, as in a crash or a long pause)
  3. controller resumed         -> what it saw

Usage (needs root, like Mininet):
  sudo python3 demo/freeze_demo.py
  sudo python3 demo/freeze_demo.py --freeze 5 --pause 0 --datapath user
"""

import argparse
import os
import signal
import subprocess
import sys
import tempfile
import time
from functools import partial
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, 'experiments'))
sys.path.insert(0, HERE)

import run_experiments as rx  # noqa: E402
from run_demo import BLUE, BOLD, DIM, GREEN, ORANGE, RESET, command, heading, say, show_flows  # noqa: E402
from mininet.clean import cleanup  # noqa: E402
from mininet.log import setLogLevel  # noqa: E402
from mininet.net import Mininet  # noqa: E402
from mininet.node import OVSSwitch  # noqa: E402
from mininet.topolib import TreeTopo  # noqa: E402

PORT = 5001
SERVER = ("import socket,threading\n"
          "s=socket.socket();s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)\n"
          "s.bind(('',%d));s.listen(64)\n"
          "def h(c):\n"
          "  c.recv(65536);c.sendall(b'k');c.close()\n"
          "while True:\n"
          "  c,_=s.accept();threading.Thread(target=h,args=(c,),daemon=True).start()\n" % PORT)
# connect, send 1 KB, wait for the reply; prints the time in ms (or FAILED)
CLIENT = ("import socket,sys,time\n"
          "t=time.time()\n"
          "try:\n"
          "  c=socket.create_connection((sys.argv[1],%d),timeout=30);c.sendall(b'x'*1000)\n"
          "  ok=c.recv(1)==b'k';c.close()\n"
          "except OSError:\n"
          "  ok=False\n"
          "print('%%.1f' %% ((time.time()-t)*1000) if ok else 'FAILED',flush=True)\n" % PORT)


def start_tap(work, topo_file):
  stats_file = os.path.join(work, 'demo-tap-stats.json')
  flow_log = os.path.join(work, 'demo-tap-flowlog.jsonl')
  cmd = [sys.executable, os.path.join(rx.POX_DIR, 'pox.py'), 'openflow.of_01', '--port=%d' % rx.OF_PORT,
         'tap_eval', '--topo=%s' % topo_file, '--flow_log=%s' % flow_log, '--stats_file=%s' % stats_file]
  env = dict(os.environ)
  env['PYTHONPATH'] = rx.CONTROLLER_DIR + os.pathsep + env.get('PYTHONPATH', '')
  logf = open(os.path.join(work, 'demo-tap-pox.log'), 'w')
  proc = subprocess.Popen(cmd, cwd=rx.POX_DIR, env=env, stdout=logf, stderr=subprocess.STDOUT)
  if not rx.wait_for(lambda: rx.port_open(rx.OF_PORT) or proc.poll() is not None, 20) or proc.poll() is not None:
    raise RuntimeError('POX did not start - see %s' % logf.name)
  return proc, stats_file


def connect(h1, h4, client, label):
  command('mininet>', 'h1: open a TCP connection to h4, send 1 KB, wait for the reply   %s(%s)%s'
          % (DIM, label, RESET))
  return h1.popen(['python3', client, h4.IP()], stdout=subprocess.PIPE, universal_newlines=True)


def show_result(p, color):
  out = p.stdout.read().strip()
  p.wait()
  if out == 'FAILED':
    print('   %sconnection FAILED%s' % (BOLD + color, RESET), flush=True)
    return None
  ms = float(out)
  print('   %sconnection done in %.1f ms%s' % (BOLD + color, ms, RESET), flush=True)
  return ms


def run_mode(mode, args, work):
  color = ORANGE if mode == 'reactive' else BLUE
  title = ('Part 1: REACTIVE controller (controllers/reactive_eval.py)' if mode == 'reactive'
           else 'Part 2: TAP controller (controllers/tap_eval.py)')
  heading(title, color)
  cleanup()
  net = Mininet(topo=TreeTopo(depth=2, fanout=2),
                switch=partial(OVSSwitch, datapath=args.datapath, protocols='OpenFlow10'),
                controller=partial(rx.LateStartController, ip='127.0.0.1', port=rx.OF_PORT),
                autoSetMacs=True, waitConnected=False)
  topo_file = os.path.join(work, 'topo.json')
  rx.write_topology(net, topo_file)
  if mode == 'reactive':
    proc, stats_file = rx.start_pox('reactive', work, 'demo-reactive', topo_file,
                                    SimpleNamespace(reactive_match='exact', idle_timeout=10, hard_timeout=30))
  else:
    proc, stats_file = start_tap(work, topo_file)
  server, client = os.path.join(work, 'server.py'), os.path.join(work, 'client.py')
  for path, text in ((server, SERVER), (client, CLIENT)):
    with open(path, 'w') as f:
      f.write(text)
  frozen = False
  result = {}
  try:
    net.start()
    net.waitConnected(timeout=20)
    for h in net.hosts:
      h.cmd('sysctl -qw net.ipv6.conf.all.disable_ipv6=1 net.ipv6.conf.default.disable_ipv6=1')
    net.staticArp()
    if mode == 'reactive':
      for h in net.hosts:   # let the controller learn where hosts are
        h.cmd('ping -n -b -c 1 -W 1 10.255.255.255 > /dev/null 2>&1')
    else:
      rx.wait_for(lambda: len(rx.read_stats(stats_file)['switches']) == len(net.switches) and
                  all(s['install_ms'] is not None for s in rx.read_stats(stats_file)['switches'].values()), 20)
    time.sleep(1.2)
    h1, h4, s3 = net.get('h1'), net.get('h4'), net.get('s3')
    h4.cmd('python3 %s > /dev/null 2>&1 &' % server)
    time.sleep(0.5)

    if mode == 'tap':
      say("\nh4's switch s3 before any traffic: one rule per host, plus three tap rules per local host")
      say('(TCP SYN / FIN / RST: forward it AND send a copy to the controller):')
      show_flows(s3, args)
      time.sleep(args.pause)

    say('\nStep 1. Controller running:')
    result['normal'] = show_result(connect(h1, h4, client, 'controller running'), color)
    time.sleep(args.pause)

    say('\nStep 2. We freeze the controller (kill -STOP %d) and open a NEW connection:' % proc.pid, BOLD)
    os.kill(proc.pid, signal.SIGSTOP)
    frozen = True
    t0 = time.time()
    p = connect(h1, h4, client, 'controller frozen')
    while p.poll() is None and time.time() - t0 < args.freeze:
      time.sleep(0.1)
    if p.poll() is None:
      say('   ... still waiting after %.0f s: the first packet is stuck at the switch, waiting for a'
          % args.freeze, color)
      say('   controller that does not answer. Resuming the controller (kill -CONT):', color)
    else:
      say('   (the controller is still frozen)', DIM)
    os.kill(proc.pid, signal.SIGCONT)
    frozen = False
    result['frozen'] = show_result(p, color)
    time.sleep(args.pause)

    time.sleep(1.5)   # let the controller catch up on what arrived while it was frozen
    st = rx.read_stats(stats_file)
    if mode == 'tap':
      ex = st['extra']
      say('\nStep 3. What the controller saw: %d connections started, %d ended.'
          % (ex.get('flows_seen', 0), ex.get('flows_ended', 0)), BOLD)
      say('   Nothing was installed per connection (FLOW_MODs after start-up: 0); the copies told it.', DIM)
    else:
      say('\nStep 3. The controller installed %d rules on demand for these connections.'
          % st['totals']['flow_mod'], BOLD)
    result['seen'] = st['extra'].get('flows_seen') if mode == 'tap' else 'every flow (it had to set each one up)'
    time.sleep(args.pause)
    return result
  finally:
    if frozen:
      os.kill(proc.pid, signal.SIGCONT)
    net.stop()
    rx.stop_pox(proc)


def main():
  ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  ap.add_argument('--datapath', default='kernel', choices=['kernel', 'user'])
  ap.add_argument('--freeze', type=float, default=5.0, help='seconds the controller stays frozen')
  ap.add_argument('--pause', type=float, default=2.0, help='seconds between steps')
  ap.add_argument('--max-rules', type=int, default=8, help='rules shown in the flow-table dump')
  args = ap.parse_args()
  if os.geteuid() != 0:
    sys.exit('Mininet needs root: run with sudo')
  setLogLevel('error')
  print('%sCS G525 · Project SA7 · Freeze the controller: reactive vs tap%s' % (BOLD, RESET))
  results = {}
  with tempfile.TemporaryDirectory(prefix='sa7-freeze-') as work:
    try:
      for mode in ('reactive', 'tap'):
        results[mode] = run_mode(mode, args, work)
    finally:
      cleanup()
  heading('Side by side (one TCP connection h1 -> h4)', GREEN)
  fmt = '   %-10s %22s %26s'
  print(BOLD + fmt % ('Controller', 'Controller running', 'Controller frozen %.0f s' % args.freeze) + RESET)
  for mode, color in (('reactive', ORANGE), ('tap', BLUE)):
    r = results[mode]
    show = lambda v: 'FAILED' if v is None else '%.1f ms' % v
    print(color + fmt % (mode.capitalize(), show(r['normal']), show(r['frozen'])) + RESET, flush=True)
  say('\nReactive: a new connection cannot start until the controller answers.')
  say('Tap: the switch forwards on its own, and the controller still hears of every connection.')


if __name__ == '__main__':
  main()
