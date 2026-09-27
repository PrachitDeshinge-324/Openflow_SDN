"""
Reactive (on-demand) flow installation - instrumented
CS G525 Advanced Computer Networks - Project SA7

Behaves like POX's forwarding.l2_learning: every switch starts with an empty
flow table, so the first packet of a flow misses, is sent to the controller as
a PACKET_IN, and the controller answers with a FLOW_MOD (+ the buffered packet).
Host locations are learned from the source MAC of PACKET_INs.

Instrumentation: PACKET_IN / FLOW_MOD / PACKET_OUT counts per switch and the
controller's PACKET_IN processing time are written to --stats_file.

Usage (from the pox/ directory):
  PYTHONPATH=../controllers python3 pox.py reactive_eval \
      [--match=exact|pair|dst] [--idle_timeout=10] [--hard_timeout=30] \
      [--stats_file=/tmp/reactive_stats.json]

  --match=exact : 10-tuple match built from the packet (same as l2_learning);
                  every new transport flow gets its own rule
  --match=pair  : match on (source MAC, destination MAC)
  --match=dst   : match on destination MAC only
"""

import time

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet.ethernet import ethernet
from pox.lib.recoco import Timer
from pox.lib.util import dpid_to_str

from sa7_common import ControllerStats

log = core.getLogger("reactive_eval")


class ReactiveEval(object):

  def __init__(self, match_mode, idle_timeout, hard_timeout, stats):
    self.match_mode = match_mode
    self.idle_timeout = idle_timeout
    self.hard_timeout = hard_timeout
    self.stats = stats
    self.mac_to_port = {}    # dpid -> {EthAddr: port}
    core.openflow.addListeners(self)

  def _handle_ConnectionUp(self, event):
    self.mac_to_port[event.dpid] = {}
    self.stats.switch(event.dpid)['connected_at'] = time.time()
    self.stats.dirty = True
    log.info("Switch %s connected (reactive, match=%s)",
             dpid_to_str(event.dpid), self.match_mode)

  def _handle_ConnectionDown(self, event):
    self.mac_to_port.pop(event.dpid, None)

  def _match_for(self, packet, in_port):
    if self.match_mode == 'exact':
      return of.ofp_match.from_packet(packet, in_port)
    if self.match_mode == 'pair':
      return of.ofp_match(dl_src=packet.src, dl_dst=packet.dst)
    return of.ofp_match(dl_dst=packet.dst)

  def _flood(self, event):
    msg = of.ofp_packet_out(data=event.ofp, in_port=event.port)
    msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
    event.connection.send(msg)
    self.stats.count(event.dpid, 'packet_out')

  def _handle_PacketIn(self, event):
    t0 = time.perf_counter()
    dpid = event.dpid
    self.stats.count(dpid, 'packet_in')

    packet = event.parsed
    if not packet.parsed or packet.type == ethernet.LLDP_TYPE:
      return

    table = self.mac_to_port.setdefault(dpid, {})
    table[packet.src] = event.port   # learn where the sender is

    out_port = None if packet.dst.is_multicast else table.get(packet.dst)
    if out_port is None:
      # Broadcast or unknown destination: flood this packet, install nothing
      self._flood(event)
    elif out_port == event.port:
      pass   # would send the packet back where it came from: drop it
    else:
      msg = of.ofp_flow_mod()
      msg.match = self._match_for(packet, event.port)
      msg.idle_timeout = self.idle_timeout
      msg.hard_timeout = self.hard_timeout
      msg.actions.append(of.ofp_action_output(port=out_port))
      msg.data = event.ofp   # also forwards the packet that triggered this rule
      event.connection.send(msg)
      self.stats.count(dpid, 'flow_mod')

    self.stats.add_proc_time(time.perf_counter() - t0)


def launch(match='exact', idle_timeout='10', hard_timeout='30', stats_file=None):
  if match not in ('exact', 'pair', 'dst'):
    raise RuntimeError("--match must be exact, pair or dst")
  config = {'match': match, 'idle_timeout': int(idle_timeout),
            'hard_timeout': int(hard_timeout)}
  stats = ControllerStats('reactive', config, stats_file)

  def start():
    core.registerNew(ReactiveEval, match, int(idle_timeout), int(hard_timeout), stats)
    Timer(1, stats.dump, recurring=True)
    stats.dump(force=True)

  core.addListenerByName("GoingDownEvent", lambda e: stats.dump(force=True))
  core.call_when_ready(start, "openflow")
