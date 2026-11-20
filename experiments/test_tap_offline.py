"""Offline check of controllers/tap_eval.py: no switch needed. Run from the repo root."""
import json, os, sys, collections
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, 'pox')); sys.path.insert(0, os.path.join(REPO, 'controllers'))
import pox.core
pox.core.initialize()
import pox.openflow.libopenflow_01 as of
import pox.openflow.nicira as nx
from pox.lib.addresses import EthAddr, IPAddr
from pox.lib.packet.ethernet import ethernet
from pox.lib.packet.ipv4 import ipv4
from pox.lib.packet.tcp import tcp
from sa7_common import ControllerStats
import tap_eval

topo_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    REPO, 'results', 'measured', 'traffic-20261023-070549', 'fattree-k6-topo.json')
topo = json.load(open(topo_file))
stats = ControllerStats('tap', {}, None)
t = tap_eval.TapEval(topo_file, 'ecmp', 5, 30, None, stats, listen=False)

# 1. every rule packs, and the counts are as designed
fwd = collections.Counter(); taps = collections.Counter(); size = 0
table = {}
for dpid in t.adj:
  for kind, msg in t.rules_for(dpid):
    size += len(msg.pack())
    (fwd if kind == 'fwd' else taps)[dpid] += 1
    if kind == 'fwd':
      table[(dpid, str(msg.match.dl_dst))] = msg.actions[0].port
H, S = len(t.hosts), len(t.adj)
off = tap_eval.TapEval(topo_file, 'ecmp', 0, 30, None, ControllerStats('x', {}, None), listen=False, taps=False)
assert all(kind == 'fwd' for d in off.adj for kind, _ in off.rules_for(d))
assert sum(1 for d in off.adj for _ in off.rules_for(d)) == H * S
assert sum(fwd.values()) == H * S and sum(taps.values()) == 3 * H
print('rules: %d forwarding (%d hosts x %d switches) + %d tap = %d total; busiest switch %d'
      % (sum(fwd.values()), H, S, sum(taps.values()), sum(fwd.values()) + sum(taps.values()),
         max(fwd[d] + taps[d] for d in t.adj)))

# 2. forwarding is loop-free and reaches every host from every switch; links are all used
port_to = {(a, p): b for a, nb in t.adj.items() for b, p in nb.items()}
used = collections.Counter(); longest = 0
for h in t.hosts:
  for start in t.adj:
    d, hops = start, 0
    while d != h['dpid']:
      nxt = port_to[(d, table[(d, h['mac'])])]
      used[(d, nxt)] += 1
      d, hops = nxt, hops + 1
      assert hops <= S, 'loop towards %s from %s' % (h['name'], start)
    assert table[(d, h['mac'])] == h['port']
    longest = max(longest, hops)
links = sum(len(nb) for nb in t.adj.values())
print('forwarding: every switch reaches every host, no loops, longest path %d hops, %d of %d link directions used'
      % (longest, len(used), links))

# 3. the copies: SYN starts a flow, a repeated SYN is not a new flow, FIN from either side ends it
class Ev(object):
  def __init__(self, dpid, pkt): self.dpid, self.parsed = dpid, pkt
def pkt(src, dst, sport, dport, flags):
  tp = tcp(); tp.srcport, tp.dstport, tp.flags, tp.off, tp.win = sport, dport, flags, 5, 100
  ip = ipv4(); ip.srcip, ip.dstip, ip.protocol = IPAddr(src['ip']), IPAddr(dst['ip']), 6; ip.payload = tp
  e = ethernet(); e.src, e.dst, e.type = EthAddr(src['mac']), EthAddr(dst['mac']), 0x800; e.payload = ip
  return ethernet(e.pack()[:tap_eval.COPY_BYTES])      # as the switch sends it: parsed from bytes
a, b, c = t.hosts[0], t.hosts[len(t.hosts) // 2], t.hosts[-1]
t._handle_PacketIn(Ev(b['dpid'], pkt(a, b, 40000, 5001, 0x02)))
t._handle_PacketIn(Ev(b['dpid'], pkt(a, b, 40000, 5001, 0x02)))      # retransmission
t._handle_PacketIn(Ev(c['dpid'], pkt(a, c, 40001, 5001, 0x02)))
assert stats.extra['flows_seen'] == 2 and stats.extra['flows_active'] == 2
t._handle_PacketIn(Ev(a['dpid'], pkt(b, a, 5001, 40000, 0x11)))      # the server closes first
t._handle_PacketIn(Ev(b['dpid'], pkt(a, b, 40000, 5001, 0x11)))      # second FIN: already ended
t._handle_PacketIn(Ev(c['dpid'], pkt(a, c, 40001, 5001, 0x04)))      # reset
assert stats.extra['flows_ended'] == 2 and stats.extra['flows_active'] == 0
print('copies: 2 flows seen, 2 ended, 0 active after SYN / repeated SYN / FIN from the far side / RST')

# 4. the reactive decision: a source above --block_rate gets one drop rule at its own switch
sent = []
class Conn(object):
  def send(self, m): sent.append(m)
t.connections[a['dpid']] = Conn()
for i in range(8):
  t._handle_PacketIn(Ev(b['dpid'], pkt(a, b, 41000 + i, 5001, 0x02)))
assert len(sent) == 1 and sent[0].priority == tap_eval.BLOCK_PRIORITY and not sent[0].actions
assert str(sent[0].match.dl_src) == a['mac'] and len(sent[0].pack()) > 0
print('block: %s blocked after %d new flows in one second, one drop rule at its own switch'
      % (stats.extra['blocked'][0]['host'], stats.extra['blocked'][0]['flows_in_window']))
print('OK')
