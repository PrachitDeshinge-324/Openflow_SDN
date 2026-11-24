"""Offline check of the SmartTime-style timeout in controllers/hybrid_eval.py: no switch needed.
Run from the repo root:  python3 experiments/test_smarttime_offline.py"""
import json, os, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, 'pox')); sys.path.insert(0, os.path.join(REPO, 'controllers'))
import pox.core
pox.core.initialize()
from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import EthAddr, IPAddr
from pox.lib.packet.ethernet import ethernet
from pox.lib.packet.ipv4 import ipv4
from pox.lib.packet.tcp import tcp
from sa7_common import ControllerStats
import hybrid_eval

class _OF(object):
  def addListeners(self, *a, **k): pass
core.register('openflow', _OF())
hybrid_eval.Timer = lambda *a, **k: None

topo_file = os.path.join(REPO, 'results', 'measured', 'traffic-20261119-114525', 'tree-d2-f4-topo.json')
hosts = json.load(open(topo_file))['hosts']

class Conn(object):
  def __init__(self): self.sent = []
  def send(self, m): self.sent.append(m)
class PktIn(object):
  def __init__(self, dpid, port, pkt):
    self.dpid, self.port, self.parsed, self.connection = dpid, port, pkt, Conn()
    self.ofp = of.ofp_packet_in(in_port=port, data=pkt.pack())
class Removed(object):
  def __init__(self, dpid, msg, life):
    self.dpid = dpid
    self.ofp = of.ofp_flow_removed(match=msg.match, priority=msg.priority, idle_timeout=msg.idle_timeout,
                                   reason=of.OFPRR_IDLE_TIMEOUT, duration_sec=int(life),
                                   duration_nsec=int((life % 1) * 1e9))

def syn(src, dst, sport):
  tp = tcp(); tp.srcport, tp.dstport, tp.flags, tp.off, tp.win = sport, 5001, 0x02, 5, 100
  ip = ipv4(); ip.srcip, ip.dstip, ip.protocol = IPAddr(src['ip']), IPAddr(dst['ip']), 6; ip.payload = tp
  e = ethernet(); e.src, e.dst, e.type = EthAddr(src['mac']), EthAddr(dst['mac']), 0x800; e.payload = ip
  return ethernet(e.pack())

def controller(match, policy='smarttime'):
  return hybrid_eval.HybridEval(topo_file, 0.0, 0.97, 1, 1.5, 'shortest', 10, 0, ControllerStats('h', {}, None),
                                match=match, timeout_policy=policy, st_min=1, st_max=10)

a, b = hosts[0], hosts[-1]
def miss(c, sport=40000):
  ev = PktIn(a['dpid'], a['port'], syn(a, b, sport)); c._handle_PacketIn(ev)
  return ev.connection.sent[-1]

# 1. pair rules: 1, 2, 4, 8, 10, 10 s on successive installs; FLOW_REMOVED flag set; no hard timeout
c = controller('pair'); seen = []
for i in range(6):
  m = miss(c, 40000 + i)
  assert m.flags & of.OFPFF_SEND_FLOW_REM and m.hard_timeout == 0
  seen.append(m.idle_timeout)
  c._handle_FlowRemoved(Removed(a['dpid'], m, m.idle_timeout + 20.0))   # active 20 s: hold ~1.5
assert seen == [1, 2, 4, 8, 10, 10], seen
print('pair rules: idle timeouts', seen)

# 2. a second PACKET_IN while the rule is still in the switch is not a repeat
c = controller('pair'); m1 = miss(c); m2 = miss(c, 40001)
assert (m1.idle_timeout, m2.idle_timeout) == (1, 1) and c.stats.extra['st_duplicates'] == 1
print('duplicate PACKET_IN before FLOW_REMOVED: same timeout, not counted as a repeat')

# 3. back to the minimum after a 10 s rule whose flows were mostly idle (hold factor > 3)
c = controller('pair'); seen = []
for i in range(6):
  m = miss(c, 40000 + i); seen.append(m.idle_timeout)
  c._handle_FlowRemoved(Removed(a['dpid'], m, m.idle_timeout + 0.5))    # active 0.5 s: hold > 3
assert seen == [1, 2, 4, 8, 10, 1], seen
assert c.stats.extra['st_resets'] == 1
print('reset rule: idle timeouts', seen)

# 4. exact-match rules: a new source port is a new key, so every connection starts at 1 s
c = controller('exact'); seen = []
for i in range(4):
  m = miss(c, 41000 + i); seen.append(m.idle_timeout)
  c._handle_FlowRemoved(Removed(a['dpid'], m, m.idle_timeout + 5.0))
assert seen == [1, 1, 1, 1], seen
print('exact-match rules: every new connection gets', seen[0], 's')

# 5. the fixed policy is unchanged
c = controller('pair', 'fixed'); m = miss(c)
assert (m.idle_timeout, m.hard_timeout, m.flags) == (10, 0, 0)
json.dumps(c.stats.extra); json.dumps(controller('pair').stats.extra)
print('fixed policy: idle 10 s, no FLOW_REMOVED flag (as before)\nall SmartTime checks passed')
