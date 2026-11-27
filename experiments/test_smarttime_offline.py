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

def controller(match, policy='smarttime', cap=0, evict='auto'):
  return hybrid_eval.HybridEval(topo_file, 0.0, 0.97, 1, 1.5, 'shortest', 10, 0, ControllerStats('h', {}, None),
                                match=match, timeout_policy=policy, st_min=1, st_max=10,
                                table_cap=cap, evict=evict)

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
print('fixed policy: idle 10 s, no FLOW_REMOVED flag (as before)')

# 6. capped table, SmartTime: rule and packet sent separately; a random rule is evicted when full
class ErrIn(object):
  def __init__(self, xid):
    self.should_log = True
    self.ofp = of.ofp_error(type=of.OFPET_FLOW_MOD_FAILED, code=of.OFPFMFC_ALL_TABLES_FULL, xid=xid)
def miss_to(c, dst, sport=42000):
  ev = PktIn(a['dpid'], a['port'], syn(a, dst, sport)); c._handle_PacketIn(ev); return ev.connection.sent
c = controller('pair', cap=3)
for i, d in enumerate(hosts[1:4]):
  sent = miss_to(c, d, 42000 + i)
  fm = [m for m in sent if isinstance(m, of.ofp_flow_mod) and m.command == of.OFPFC_ADD][0]
  po = [m for m in sent if isinstance(m, of.ofp_packet_out)]
  assert fm.data is None and len(po) == 1 and fm.flags & of.OFPFF_SEND_FLOW_REM
assert len(c.table[a['dpid']]) == 3 and c.stats.extra['evictions'] == 0
sent = miss_to(c, hosts[4], 42010)   # table full: evict one, then install
dels = [m for m in sent if isinstance(m, of.ofp_flow_mod) and m.command == of.OFPFC_DELETE_STRICT]
assert len(dels) == 1 and c.stats.extra['evictions'] == 1 and c.stats.extra['table_full_events'] == 1
assert len(c.table[a['dpid']]) == 3
print('capped table, SmartTime: rule without the packet + PACKET_OUT; full table -> 1 random DELETE_STRICT')

# 7. capped table, fixed timeout: no eviction; a refusal (table full) is counted and leaves our view
c = controller('pair', 'fixed', cap=2)
miss_to(c, hosts[1]); miss_to(c, hosts[2])
sent = miss_to(c, hosts[3])
fm = [m for m in sent if isinstance(m, of.ofp_flow_mod)]
assert len(fm) == 1 and fm[0].command == of.OFPFC_ADD and c.stats.extra['evictions'] == 0
assert any(isinstance(m, of.ofp_packet_out) for m in sent)   # the packet still goes on
c._handle_ErrorIn(ErrIn(fm[0].xid))
assert c.stats.extra['refused_installs'] == 1 and len(c.table[a['dpid']]) == 2
# an idle expiry frees a slot in our view
c._handle_FlowRemoved(Removed(a['dpid'], fm[0].__class__(match=of.ofp_match(dl_src=EthAddr(a['mac']),
                      dl_dst=EthAddr(hosts[1]['mac']))), 11.0))
assert len(c.table[a['dpid']]) == 1
json.dumps(c.stats.extra)
print('capped table, fixed: no eviction, refused install counted, packet forwarded anyway')
for m in sent: m.pack()   # every message is valid OpenFlow 1.0
print('all SmartTime checks passed')
