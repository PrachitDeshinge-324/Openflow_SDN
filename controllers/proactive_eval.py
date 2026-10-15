"""
Proactive (pre-installed) flow installation - instrumented
CS G525 Advanced Computer Networks - Project SA7

The controller is given the topology in advance (--topo JSON file, written by
experiments/run_experiments.py). As soon as a switch connects, every rule it
will ever need is pushed to it, so data packets never miss the flow table and
the controller sees no traffic at runtime.

  --granularity=pair : one rule per (source host, destination host) pair on
                       every switch along that pair's shortest path
                       -> O(N^2) rules, the design the SA7 hypothesis models
  --granularity=dst  : one rule per destination host on every switch -> O(N)

Paths are the lowest-cost paths in the topology file (cost = link delay_ms if
given, else 1 per hop). When several paths tie (e.g. in a fat-tree):
  --paths=shortest : always the same one (the lowest switch numbers)
  --paths=ecmp     : each (source, destination) pair is hashed onto one of the
                     tied paths, like ECMP in real data centres (pair only)

A lowest-priority "drop" rule is installed as the table-miss entry (--miss=drop)
so unmatched packets (e.g. stray broadcasts) do not reach the controller. Use
--miss=controller to send them to the controller instead.

Instrumentation: rules installed and install time per switch (FEATURES_REPLY ->
BARRIER_REPLY), plus any PACKET_INs that still arrive, in --stats_file.

Usage (from the pox/ directory):
  PYTHONPATH=../controllers python3 pox.py proactive_eval --topo=/path/topo.json \
      [--granularity=pair|dst] [--paths=shortest|ecmp] [--miss=drop|controller] \
      [--stats_file=...]
"""

import time
import zlib

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import EthAddr
from pox.lib.recoco import Timer
from pox.lib.util import dpid_to_str

from sa7_common import ControllerStats, load_link_weights, load_topology, shortest_paths

log = core.getLogger("proactive_eval")

RULE_PRIORITY = 100


class ProactiveEval(object):

  def __init__(self, topo_file, granularity, paths, miss, stats):
    self.hosts, self.adj = load_topology(topo_file)
    self.weights = load_link_weights(topo_file)
    self.granularity = granularity
    self.paths = paths
    self.miss = miss
    self._path_cache = {}
    self.stats = stats
    self.pending_barrier = {}   # dpid -> (xid, t_start)
    core.openflow.addListeners(self)
    log.info("Loaded topology: %d switches, %d hosts", len(self.adj), len(self.hosts))

  def _tied_paths(self, a, b):
    key = (a, b)
    if key not in self._path_cache:
      self._path_cache[key] = shortest_paths(self.adj, self.weights, a, b)
    return self._path_cache[key]

  def pair_path(self, src, dst):
    """The switch path used by traffic from host src to host dst."""
    paths = self._tied_paths(src['dpid'], dst['dpid'])
    if not paths:
      return None
    if self.paths == 'ecmp':
      key = ('%s-%s' % (src['mac'], dst['mac'])).encode()
      return paths[zlib.crc32(key) % len(paths)]
    return paths[0]

  def _rules_for(self, dpid):
    """Yield (match, out_port) for every rule switch `dpid` needs."""
    if dpid not in self.adj:
      log.warning("Switch %s is not in the topology file", dpid_to_str(dpid))
      return

    def next_port(path, dst_host):
      i = path.index(dpid)
      if i == len(path) - 1:
        return dst_host['port']
      return self.adj[dpid][path[i + 1]]

    if self.granularity == 'dst':
      for h in self.hosts:
        paths = self._tied_paths(dpid, h['dpid'])
        if paths:
          yield of.ofp_match(dl_dst=EthAddr(h['mac'])), next_port(paths[0], h)
      return

    for src in self.hosts:
      for dst in self.hosts:
        if src is dst:
          continue
        path = self.pair_path(src, dst)
        if path and dpid in path:
          yield (of.ofp_match(dl_src=EthAddr(src['mac']), dl_dst=EthAddr(dst['mac'])),
                 next_port(path, dst))

  def _handle_ConnectionUp(self, event):
    dpid = event.dpid
    t0 = time.time()
    s = self.stats.switch(dpid)
    s['connected_at'] = t0

    n = 0
    for match, port in self._rules_for(dpid):
      msg = of.ofp_flow_mod(match=match, priority=RULE_PRIORITY)  # permanent: no timeouts
      msg.actions.append(of.ofp_action_output(port=port))
      event.connection.send(msg)
      n += 1

    miss = of.ofp_flow_mod(match=of.ofp_match(), priority=0)
    if self.miss == 'controller':
      miss.actions.append(of.ofp_action_output(port=of.OFPP_CONTROLLER))
    event.connection.send(miss)   # no actions = drop

    self.stats.count(dpid, 'flow_mod', n + 1)
    s['rules_installed'] = n
    barrier = of.ofp_barrier_request()
    self.pending_barrier[dpid] = (barrier.xid, t0)
    event.connection.send(barrier)
    log.info("Switch %s connected: pushed %d rules (granularity=%s, paths=%s)",
             dpid_to_str(dpid), n, self.granularity, self.paths)

  def _handle_BarrierIn(self, event):
    pending = self.pending_barrier.get(event.dpid)
    if pending and pending[0] == event.xid:
      del self.pending_barrier[event.dpid]
      s = self.stats.switch(event.dpid)
      s['install_ms'] = (time.time() - pending[1]) * 1000
      self.stats.dirty = True

  def _handle_PacketIn(self, event):
    # Should stay at zero with --miss=drop; counted to prove it
    self.stats.count(event.dpid, 'packet_in')


def launch(topo=None, granularity='pair', paths='shortest', miss='drop', stats_file=None):
  if not topo:
    raise RuntimeError("proactive_eval needs --topo=<topology.json>")
  if granularity not in ('pair', 'dst'):
    raise RuntimeError("--granularity must be pair or dst")
  if paths not in ('shortest', 'ecmp'):
    raise RuntimeError("--paths must be shortest or ecmp")
  if paths == 'ecmp' and granularity != 'pair':
    raise RuntimeError("--paths=ecmp needs --granularity=pair")
  if miss not in ('drop', 'controller'):
    raise RuntimeError("--miss must be drop or controller")
  config = {'granularity': granularity, 'paths': paths, 'miss': miss, 'topo': topo}
  stats = ControllerStats('proactive', config, stats_file)

  def start():
    core.registerNew(ProactiveEval, topo, granularity, paths, miss, stats)
    Timer(1, stats.dump, recurring=True)
    stats.dump(force=True)

  core.addListenerByName("GoingDownEvent", lambda e: stats.dump(force=True))
  core.call_when_ready(start, "openflow")
