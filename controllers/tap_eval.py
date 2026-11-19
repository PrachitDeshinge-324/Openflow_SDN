"""
Forward first, tell the controller in parallel ("tap")
CS G525 Advanced Computer Networks - Project SA7

Reactive rules make the first packet wait for the controller. Proactive rules
do not, but the controller never learns which flows exist. This module separates
the two things a PACKET_IN does today: it forwards without asking, and it still
tells the controller about every TCP connection.

  Forwarding  one destination rule per host on every switch, installed when the
              switch connects (as proactive_eval --granularity=dst). With
              --paths=ecmp each switch picks among its equal-cost next hops by a
              hash of the destination, so the fat-tree's paths are all used.
  Tap         at the switch a host is attached to, three more rules per host,
              with a higher priority. They match TCP packets to that host with
              SYN (and not ACK), FIN or RST set, and have two actions: output to
              the host, and send a 128-byte copy to the controller.

So a connection's first packet is forwarded by the switch at once, and the
controller receives one PACKET_IN when the connection starts and one or two when
it ends. No rule is installed per flow. If the controller is slow or stopped,
forwarding is not affected; only the copies are late or lost.

Matching TCP flags is not in OpenFlow 1.0. It is the Open vSwitch extension field
NXM_NX_TCP_FLAGS (Open vSwitch 2.1 and later), sent with a Nicira flow-mod. The
connection to the switch stays OpenFlow 1.0.

What the controller can still do, because it knows every flow as it starts:
  --block_rate=N   a source that opens more than N connections in one second gets
                   a drop rule at its own switch for --block_s seconds (a reactive
                   decision, taken after the first packets have passed)

Limits (see docs/Novelty_Plan.md): TCP only; no byte counts per flow; a decision
that must be taken before the first packet (an access list) has to be a
pre-installed rule, as in any proactive design.

Statistics written to --stats_file (extra.*): flows_seen (SYN copies),
flows_ended, flows_active, tap_rules, blocked (list). ingress_syn_misses is
always 0: no connection waits for the controller.

Usage (from the pox/ directory):
  PYTHONPATH=../controllers python3 pox.py tap_eval --topo=/path/topo.json \\
      [--paths=shortest|ecmp] [--block_rate=0] [--block_s=30] [--flow_log=F] [--stats_file=...]
"""

import json
import time
import zlib

from pox.core import core
import pox.openflow.libopenflow_01 as of
import pox.openflow.nicira as nx
from pox.lib.addresses import EthAddr
from pox.lib.recoco import Timer
from pox.lib.util import dpid_to_str

from sa7_common import ControllerStats, load_link_weights, load_topology, shortest_paths

log = core.getLogger("tap_eval")

FWD_PRIORITY = 100     # destination rules
TAP_PRIORITY = 200     # the same forwarding, plus a copy to the controller
BLOCK_PRIORITY = 300   # drop rules decided by the controller
COPY_BYTES = 128       # enough for Ethernet + IPv4 + TCP headers

TCP_FIN, TCP_SYN, TCP_RST, TCP_ACK = 0x001, 0x002, 0x004, 0x010
# (flag value, flag mask): SYN without ACK; any FIN; any RST
TAPS = ((TCP_SYN, TCP_SYN | TCP_ACK), (TCP_FIN, TCP_FIN), (TCP_RST, TCP_RST))


class TapEval(object):

  def __init__(self, topo_file, paths, block_rate, block_s, flow_log, stats, listen=True):
    self.hosts, self.adj = load_topology(topo_file)
    self.weights = load_link_weights(topo_file)
    self.by_mac = {EthAddr(h['mac']): h for h in self.hosts}
    self.paths = paths
    self.block_rate, self.block_s = block_rate, block_s
    self.flow_log = open(flow_log, 'w') if flow_log else None
    self.stats = stats
    self.connections = {}
    self.pending_barrier = {}
    self.flows = {}          # (src ip, dst ip, src port, dst port) -> start time
    self.recent = {}         # source MAC -> start times within the last second
    self.blocked = {}        # source MAC -> time of the drop rule
    stats.extra.update(flows_seen=0, flows_ended=0, flows_active=0, tap_rules=0, blocked=[],
                       ingress_syn_misses=0, ingress_new_flows=0,   # read by the harness:
                       budget_pairs=0, total_pairs=len(self.hosts) * (len(self.hosts) - 1),
                       pair_installs=0, pair_removals=0, wasted_installs=0, pairs_installed=0)
    if listen:
      core.openflow.addListeners(self)
    log.info("Tap: %d switches, %d hosts, paths=%s, block above %s new flows/s",
             len(self.adj), len(self.hosts), paths, block_rate or 'never')

  # ------------------------------------------------------------ rules

  def out_port(self, dpid, host):
    """Port of switch `dpid` towards `host` (a next hop on a lowest-cost path), or None."""
    if dpid == host['dpid']:
      return host['port']
    tied = shortest_paths(self.adj, self.weights, dpid, host['dpid'])
    if not tied:
      return None
    path = tied[zlib.crc32(host['mac'].encode()) % len(tied)] if self.paths == 'ecmp' else tied[0]
    return self.adj[dpid][path[1]]

  def rules_for(self, dpid):
    """Flow-mods for switch `dpid`: (kind, message), kind 'fwd' or 'tap'."""
    for h in self.hosts:
      port = self.out_port(dpid, h)
      if port is None:
        continue
      fwd = of.ofp_flow_mod(match=of.ofp_match(dl_dst=EthAddr(h['mac'])), priority=FWD_PRIORITY)
      fwd.actions.append(of.ofp_action_output(port=port))
      yield 'fwd', fwd
      if dpid != h['dpid']:
        continue
      for value, mask in TAPS:   # the host's own switch: every flow to it passes here once
        tap = nx.nx_flow_mod(priority=TAP_PRIORITY)
        tap.match.of_eth_dst = EthAddr(h['mac'])
        tap.match.of_eth_type = 0x0800
        tap.match.of_ip_proto = 6
        tap.match.nx_tcp_flags = value
        tap.match.nx_tcp_flags_mask = mask
        tap.actions.append(of.ofp_action_output(port=port))
        tap.actions.append(of.ofp_action_output(port=of.OFPP_CONTROLLER, max_len=COPY_BYTES))
        yield 'tap', tap

  def _handle_ConnectionUp(self, event):
    dpid, t0 = event.dpid, time.time()
    self.connections[dpid] = event.connection
    s = self.stats.switch(dpid)
    s['connected_at'] = t0
    if dpid not in self.adj:
      log.warning("Switch %s is not in the topology file", dpid_to_str(dpid))
      return
    n = taps = 0
    for kind, msg in self.rules_for(dpid):
      event.connection.send(msg)
      n += 1
      taps += kind == 'tap'
    event.connection.send(of.ofp_flow_mod(match=of.ofp_match(), priority=0))   # anything else: drop
    self.stats.count(dpid, 'flow_mod', n + 1)
    s['rules_installed'] = n
    self.stats.extra['tap_rules'] += taps
    barrier = of.ofp_barrier_request()
    self.pending_barrier[dpid] = (barrier.xid, t0)
    event.connection.send(barrier)
    log.info("Switch %s: %d forwarding rules, %d tap rules", dpid_to_str(dpid), n - taps, taps)

  def _handle_ConnectionDown(self, event):
    self.connections.pop(event.dpid, None)

  def _handle_BarrierIn(self, event):
    pending = self.pending_barrier.get(event.dpid)
    if pending and pending[0] == event.xid:
      del self.pending_barrier[event.dpid]
      self.stats.switch(event.dpid)['install_ms'] = (time.time() - pending[1]) * 1000
      self.stats.dirty = True

  def _handle_ErrorIn(self, event):
    log.error("Switch %s refused a message: %s (does this Open vSwitch match tcp_flags? "
              "needs 2.1 or later)", dpid_to_str(event.dpid), event.asString())
    self.stats.extra['switch_errors'] = self.stats.extra.get('switch_errors', 0) + 1
    self.stats.dirty = True

  # ------------------------------------------------------------ what the copies tell us

  def _handle_PacketIn(self, event):
    t0 = time.perf_counter()
    now = time.time()
    self.stats.count(event.dpid, 'packet_in')
    packet = event.parsed
    ip, tcp = packet.find('ipv4'), packet.find('tcp')
    if ip is None or tcp is None:
      return
    key = (str(ip.srcip), str(ip.dstip), tcp.srcport, tcp.dstport)
    extra = self.stats.extra
    if tcp.SYN and not tcp.ACK:
      if key not in self.flows:        # a retransmitted SYN is the same connection
        self.flows[key] = now
        extra['flows_seen'] += 1
        extra['ingress_new_flows'] += 1
        if self.flow_log:
          self.flow_log.write(json.dumps({'event': 'start', 'at': now, 'src': key[0], 'dst': key[1],
                                          'sport': key[2], 'dport': key[3]}) + '\n')
        self._watch_source(packet.src, now)
    elif tcp.FIN or tcp.RST:
      for k in (key, (key[1], key[0], key[3], key[2])):   # either side may close first
        start = self.flows.pop(k, None)
        if start is not None:
          extra['flows_ended'] += 1
          if self.flow_log:
            self.flow_log.write(json.dumps({'event': 'end', 'start': start, 'end': now, 'src': k[0], 'dst': k[1],
                                            'sport': k[2], 'dport': k[3]}) + '\n')
          break
    extra['flows_active'] = len(self.flows)
    self.stats.add_proc_time(time.perf_counter() - t0)

  def _watch_source(self, mac, now):
    """A reactive decision without a reactive delay: block a source that opens too many flows."""
    if not self.block_rate or mac in self.blocked:
      return
    times = [t for t in self.recent.get(mac, ()) if now - t < 1.0] + [now]
    self.recent[mac] = times
    host = self.by_mac.get(mac)
    if len(times) <= self.block_rate or host is None or host['dpid'] not in self.connections:
      return
    msg = of.ofp_flow_mod(match=of.ofp_match(dl_src=mac), priority=BLOCK_PRIORITY,
                          hard_timeout=self.block_s)   # no actions = drop
    self.connections[host['dpid']].send(msg)
    self.stats.count(host['dpid'], 'flow_mod')
    self.blocked[mac] = now
    self.stats.extra['blocked'].append({'mac': str(mac), 'host': host['name'], 'at': now,
                                        'first_flow_at': times[0], 'flows_in_window': len(times)})
    log.warning("Blocked %s (%s): %d new flows in one second", host['name'], mac, len(times))

  def _expire(self):
    """Forget connections whose end we never saw (a lost copy), and blocks that timed out."""
    now = time.time()
    for k in [k for k, t in self.flows.items() if now - t > 300]:
      del self.flows[k]
    for m in [m for m, t in self.blocked.items() if now - t > self.block_s]:
      del self.blocked[m]
    if self.flow_log:
      self.flow_log.flush()


def launch(topo=None, paths='shortest', block_rate='0', block_s='30', flow_log=None, stats_file=None):
  if not topo:
    raise RuntimeError("tap_eval needs --topo=<topology.json>")
  if paths not in ('shortest', 'ecmp'):
    raise RuntimeError("--paths must be shortest or ecmp")
  config = {'topo': topo, 'paths': paths, 'block_rate': int(block_rate), 'block_s': int(block_s)}
  stats = ControllerStats('tap', config, stats_file)

  def start():
    tap = core.registerNew(TapEval, topo, paths, int(block_rate), int(block_s), flow_log, stats)
    # dump every second even when nothing changed: the harness waits for a fresh dump to take
    # its "before the first flow" baseline, and with no traffic yet nothing would be written
    Timer(1, lambda: stats.dump(force=True), recurring=True)
    Timer(5, tap._expire, recurring=True)
    stats.dump(force=True)

  core.addListenerByName("GoingDownEvent", lambda e: stats.dump(force=True))
  core.call_when_ready(start, "openflow")
