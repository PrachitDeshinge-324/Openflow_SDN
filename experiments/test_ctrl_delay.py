#!/usr/bin/env python3
"""
Self-test for --ctrl-delay (needs root, about 10 s; no Mininet, no POX).
CS G525 Advanced Computer Networks - Project SA7

Applies the control-channel delay of run_traffic_experiments.py, then measures real TCP round trips
over the loopback device to the OpenFlow port (6633) and to a control port (6634):
  - 6633 must be slower by about 2 x DELAY (both directions are delayed),
  - 6634 must not be delayed,
  - the netem band must have counted the packets,
  - after removal, lo must be back to its normal state and 6633 fast again.

  sudo python3 experiments/test_ctrl_delay.py [--delay 20]
"""

import argparse
import os
import socket
import statistics
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_traffic_experiments as rt  # noqa: E402


def echo_server(port, stop):
  srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  srv.bind(('127.0.0.1', port))
  srv.listen(1)
  srv.settimeout(0.5)
  while not stop.is_set():
    try:
      conn, _ = srv.accept()
    except socket.timeout:
      continue
    conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    while True:
      b = conn.recv(1)
      if not b:
        break
      conn.sendall(b)
    conn.close()
  srv.close()


def rtt_ms(port, n=15):
  c = socket.create_connection(('127.0.0.1', port), timeout=5)
  c.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
  out = []
  for _ in range(n):
    t = time.perf_counter()
    c.sendall(b'x')
    c.recv(1)
    out.append(1000 * (time.perf_counter() - t))
  c.close()
  return statistics.median(out)


def main():
  ap = argparse.ArgumentParser()
  ap.add_argument('--delay', type=float, default=20.0, help='one-way delay to test, ms')
  args = ap.parse_args()
  if os.geteuid() != 0:
    sys.exit('run with sudo')
  of, other = rt.OF_PORT, rt.OF_PORT + 1
  stop = threading.Event()
  for p in (of, other):
    threading.Thread(target=echo_server, args=(p, stop), daemon=True).start()
  time.sleep(0.3)
  ok = True
  try:
    base_of, base_other = rtt_ms(of), rtt_ms(other)
    rt.ctrl_delay_on(args.delay)
    d_of, d_other = rtt_ms(of), rtt_ms(other)
    pkts = rt.ctrl_delay_packets()
  finally:
    rt.ctrl_delay_off()
  after_of = rtt_ms(of)
  after_qdisc = rt._tc('qdisc show dev lo', check=False).stdout.strip()
  stop.set()

  want = 2 * args.delay
  checks = [
    ('port %d RTT +%.1f ms (want about +%.0f)' % (of, d_of - base_of, want), abs((d_of - base_of) - want) < 0.25 * want + 2),
    ('port %d RTT +%.1f ms (want about 0)' % (other, d_other - base_other), abs(d_other - base_other) < 2),
    ('netem counted %s packets (want > 0)' % pkts, bool(pkts)),
    ('after removal port %d RTT %.2f ms (want < 2)' % (of, after_of), after_of < 2),
    ('after removal lo qdisc: %r (ours gone)' % after_qdisc, rt.CTRL_QDISC not in after_qdisc),
  ]
  for text, passed in checks:
    print('[%s] %s' % ('PASS' if passed else 'FAIL', text))
    ok = ok and passed
  print('OK' if ok else 'FAILED')
  sys.exit(0 if ok else 1)


if __name__ == '__main__':
  main()
