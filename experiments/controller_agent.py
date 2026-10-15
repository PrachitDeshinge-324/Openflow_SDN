#!/usr/bin/env python3
"""
Controller agent: lets the experiment harness run POX on a second PC
CS G525 Advanced Computer Networks - Project SA7

PC A (Mininet, switches, traffic)          PC B (controller)
  run_traffic_experiments.py                 controller_agent.py
    --controller-host <PC B's IP>   -->        starts / stops POX, reports its
                                               stats and CPU time
  OVS switches  ---- OpenFlow, TCP 6633 ---->  POX

Run on PC B (no root needed, Mininet not needed; Python 3 and the repo with
pox/ are enough):
  python3 experiments/controller_agent.py            # listens on TCP 6000
Then on PC A:
  sudo python3 experiments/run_traffic_experiments.py --controller-host 192.168.1.20 ...

Protocol: one JSON request per TCP connection, one JSON reply.
  {"cmd": "info"}                                   -> host name, CPU, Python
  {"cmd": "start", "tag": T, "args": [...], "files": {name: text}}
        writes the files into the agent's run directory, replaces "{dir}" in the
        arguments with that directory, starts POX with the arguments, waits for
        it to listen on the OpenFlow port
  {"cmd": "stats"}                                  -> the latest stats dump
  {"cmd": "fresh"}                                  -> waits for a dump written after
        the request arrived (dumps happen every second), so the two PCs' clocks
        never have to agree
  {"cmd": "cpu"}                                    -> POX's CPU seconds (user + system)
  {"cmd": "stop"}                                   -> stops POX, returns its log and final stats

Only the POX modules used by this project can be started (ALLOWED_MODULES),
so the agent cannot be used to run anything else. Still: run it only on a
lab network you trust, and stop it (Ctrl-C) when the experiments are done.
"""

import argparse
import json
import os
import platform
import socket
import socketserver
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POX_DIR = os.environ.get('POX_DIR', os.path.join(REPO, 'pox'))
CONTROLLER_DIR = os.path.join(REPO, 'controllers')
OF_PORT = 6633
ALLOWED_MODULES = {'openflow.of_01', 'openflow.discovery', 'openflow.spanning_tree',
                   'reactive_eval', 'proactive_eval', 'hybrid_eval'}

state = {'proc': None, 'stats_file': None, 'log_file': None, 'dir': None}


def port_open(port):
  try:
    with socket.create_connection(('127.0.0.1', port), timeout=0.5):
      return True
  except OSError:
    return False


def read_stats():
  for _ in range(20):
    try:
      with open(state['stats_file']) as f:
        return json.load(f)
    except (OSError, ValueError, TypeError):
      time.sleep(0.1)
  raise RuntimeError('could not read the stats file %s' % state['stats_file'])


def cpu_seconds():
  with open('/proc/%d/stat' % state['proc'].pid) as f:
    fields = f.read().rsplit(')', 1)[1].split()
  return (int(fields[11]) + int(fields[12])) / os.sysconf('SC_CLK_TCK')


def stop():
  proc = state['proc']
  if proc is None:
    return
  proc.send_signal(2)   # SIGINT: POX shuts down cleanly and writes final stats
  try:
    proc.wait(timeout=5)
  except subprocess.TimeoutExpired:
    proc.kill()
    proc.wait()
  state['proc'] = None


def cpu_model():
  try:
    with open('/proc/cpuinfo') as f:
      for line in f:
        if line.startswith('model name'):
          return line.split(':', 1)[1].strip()
  except OSError:
    pass
  return platform.processor()


def start(req, run_root):
  stop()
  tag = os.path.basename(req['tag'])
  run_dir = os.path.join(run_root, tag)
  os.makedirs(run_dir, exist_ok=True)
  for name, text in req.get('files', {}).items():
    with open(os.path.join(run_dir, os.path.basename(name)), 'w') as f:
      f.write(text)
  args = [a.replace('{dir}', run_dir) for a in req['args']]
  modules = [a for a in args if not a.startswith('-')]
  bad = [m for m in modules if m not in ALLOWED_MODULES]
  if bad:
    raise RuntimeError('module(s) not allowed: %s' % ', '.join(bad))
  state['stats_file'] = os.path.join(run_dir, 'stats.json')
  state['log_file'] = os.path.join(run_dir, 'pox.log')
  cmd = [sys.executable, os.path.join(POX_DIR, 'pox.py'), 'openflow.of_01', '--port=%d' % OF_PORT]
  cmd += args + ['--stats_file=%s' % state['stats_file']]
  env = dict(os.environ)
  env['PYTHONPATH'] = CONTROLLER_DIR + os.pathsep + env.get('PYTHONPATH', '')
  logf = open(state['log_file'], 'w')
  state['proc'] = subprocess.Popen(cmd, cwd=POX_DIR, env=env, stdout=logf, stderr=subprocess.STDOUT)
  end = time.time() + 20
  while time.time() < end and not port_open(OF_PORT) and state['proc'].poll() is None:
    time.sleep(0.2)
  if state['proc'].poll() is not None or not port_open(OF_PORT):
    with open(state['log_file']) as f:
      raise RuntimeError('POX did not start:\n' + f.read()[-2000:])
  print('[agent] %s: POX started (pid %d)' % (tag, state['proc'].pid), flush=True)
  return {'pid': state['proc'].pid, 'dir': run_dir}


def handle(req, run_root):
  cmd = req.get('cmd')
  if cmd == 'info':
    return {'host': socket.gethostname(), 'cpu': cpu_model(), 'cpus': os.cpu_count(),
            'python': sys.version.split()[0], 'uname': ' '.join(os.uname()),
            'pox_found': os.path.exists(os.path.join(POX_DIR, 'pox.py'))}
  if cmd == 'start':
    return start(req, run_root)
  if cmd == 'stats':
    return {'stats': read_stats()}
  if cmd == 'fresh':
    asked = time.time()
    end = asked + 5
    while time.time() < end:
      st = read_stats()
      if st['written_at'] > asked:
        return {'stats': st}
      time.sleep(0.1)
    return {'stats': read_stats()}
  if cmd == 'cpu':
    return {'cpu_seconds': cpu_seconds()}
  if cmd == 'stop':
    stop()
    out = {'stats': None, 'log': ''}
    if state['stats_file'] and os.path.exists(state['stats_file']):
      out['stats'] = read_stats()
    if state['log_file'] and os.path.exists(state['log_file']):
      with open(state['log_file']) as f:
        out['log'] = f.read()
    print('[agent] POX stopped', flush=True)
    return out
  raise RuntimeError('unknown command %r' % cmd)


def main():
  ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  ap.add_argument('--port', type=int, default=6000, help='TCP port the harness connects to')
  ap.add_argument('--bind', default='0.0.0.0', help='address to listen on')
  ap.add_argument('--out', default=os.path.join(REPO, 'results', 'agent'),
                  help='where POX logs and stats are kept')
  args = ap.parse_args()
  if not os.path.exists(os.path.join(POX_DIR, 'pox.py')):
    sys.exit('POX not found at %s (set POX_DIR)' % POX_DIR)

  class Handler(socketserver.StreamRequestHandler):
    def handle(self):
      try:
        req = json.loads(self.rfile.readline().decode())
        reply = {'ok': True, 'result': handle(req, args.out)}
      except Exception as e:   # report every error to the harness instead of dying
        reply = {'ok': False, 'error': '%s: %s' % (type(e).__name__, e)}
      self.wfile.write((json.dumps(reply) + '\n').encode())

  socketserver.TCPServer.allow_reuse_address = True
  server = socketserver.TCPServer((args.bind, args.port), Handler)
  print('[agent] %s: waiting for the harness on TCP %d; POX will listen on TCP %d. Ctrl-C to stop.'
        % (socket.gethostname(), args.port, OF_PORT), flush=True)
  try:
    server.serve_forever()
  except KeyboardInterrupt:
    pass
  finally:
    stop()
    server.server_close()


if __name__ == '__main__':
  main()
