"""
Shared helpers for the SA7 POX controller modules
CS G525 Advanced Computer Networks - Project SA7

- ControllerStats: counts OpenFlow messages per switch and periodically dumps
  them to a JSON file so the experiment harness can read them.
- load_topology / next_hop_ports / switch_path: static topology description
  (written by experiments/run_experiments.py) used by the proactive controller.
"""

import json
import os
import time
from collections import deque


class ControllerStats(object):
  """Message counters + PacketIn processing times, dumped to a JSON file."""

  def __init__(self, mode, config, stats_file=None):
    self.mode = mode
    self.config = config
    self.stats_file = stats_file
    self.started = time.time()
    self.switches = {}          # dpid -> per-switch counters
    self.proc_us = []           # PacketIn handler processing time (microseconds)
    self.dirty = True

  def switch(self, dpid):
    s = self.switches.get(dpid)
    if s is None:
      s = {'packet_in': 0, 'flow_mod': 0, 'packet_out': 0,
           'connected_at': None, 'rules_installed': 0, 'install_ms': None}
      self.switches[dpid] = s
    return s

  def count(self, dpid, field, n=1):
    self.switch(dpid)[field] += n
    self.dirty = True

  def add_proc_time(self, seconds):
    self.proc_us.append(seconds * 1e6)
    self.dirty = True

  def totals(self):
    t = {'packet_in': 0, 'flow_mod': 0, 'packet_out': 0, 'rules_installed': 0}
    for s in self.switches.values():
      for k in t:
        t[k] += s[k]
    return t

  def snapshot(self):
    proc = sorted(self.proc_us)
    n = len(proc)
    summary = {'count': n}
    if n:
      summary.update(mean=sum(proc) / n, p50=proc[n // 2],
                     p95=proc[min(n - 1, int(n * 0.95))], max=proc[-1])
    return {
      'mode': self.mode,
      'config': self.config,
      'pid': os.getpid(),
      'uptime_s': time.time() - self.started,
      'written_at': time.time(),
      'totals': self.totals(),
      'switches': {str(d): s for d, s in self.switches.items()},
      'packet_in_processing_us': summary,
    }

  def dump(self, force=False):
    if not self.stats_file or not (self.dirty or force):
      return
    tmp = self.stats_file + '.tmp'
    with open(tmp, 'w') as f:
      json.dump(self.snapshot(), f, indent=2)
    os.replace(tmp, self.stats_file)   # atomic, so readers never see half a file
    self.dirty = False


def load_topology(path):
  """
  Topology file format (JSON):
    {"switches": [1, 2, 3],
     "hosts": [{"name": "h1", "mac": "00:00:00:00:00:01", "ip": "10.0.0.1",
                "dpid": 2, "port": 1}, ...],
     "links": [{"dpid1": 1, "port1": 1, "dpid2": 2, "port2": 3}, ...]}
  """
  with open(path) as f:
    topo = json.load(f)
  adj = {int(d): {} for d in topo['switches']}   # dpid -> {neighbour dpid: local port}
  for l in topo['links']:
    adj[int(l['dpid1'])][int(l['dpid2'])] = int(l['port1'])
    adj[int(l['dpid2'])][int(l['dpid1'])] = int(l['port2'])
  return topo['hosts'], adj


def _bfs_parents(adj, root):
  parent = {root: None}
  q = deque([root])
  while q:
    u = q.popleft()
    for v in sorted(adj[u]):
      if v not in parent:
        parent[v] = u
        q.append(v)
  return parent


def switch_path(adj, src, dst):
  """Shortest switch path src -> dst (list of dpids, inclusive), or None."""
  parent = _bfs_parents(adj, dst)
  if src not in parent:
    return None
  path = [src]
  while path[-1] != dst:
    path.append(parent[path[-1]])
  return path


def next_hop_ports(adj, dpid):
  """For switch `dpid`: {destination dpid: local output port} along shortest paths."""
  ports = {}
  for dst in adj:
    if dst == dpid:
      continue
    path = switch_path(adj, dpid, dst)
    if path:
      ports[dst] = adj[dpid][path[1]]
  return ports
