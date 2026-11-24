"""
Budgeted hybrid flow installation - weighted counter keeps the top-K pairs proactive
CS G525 Advanced Computer Networks - Project SA7

The controller knows the topology (--topo, as proactive_eval). Every new flow
that misses is handled reactively, but on the shortest path (not a spanning
tree): at each switch the PACKET_IN gets an exact-match rule towards the next
hop, like reactive_eval but with topology-aware forwarding.

On top of that, a weighted counter decides which host pairs get a pre-installed
pair rule (match source MAC + destination MAC on every switch of the pair's
path), within a budget of K pairs for the whole network:

  every --interval seconds, for every pair:
      score = decay * score + active
  where active = 1 if the pair started a flow that reached the controller in
  this interval, or if its pre-installed rule matched packets in this interval
  (read from the switch's flow counters, because pre-installed pairs no longer
  reach the controller). The K pairs with the highest score keep pair rules; a
  newcomer replaces the weakest kept pair only if its score is --hysteresis
  times higher. Pairs that drop out have their rules deleted.

  --budget=0    : pure reactive on shortest paths ("reactive-sp")
  --budget=0.25 : at most 25% of all (source, destination) host pairs pre-installed
  --budget=1    : every pair can be pre-installed once it has been seen
  --match=exact : the reactive rule matches the whole flow (default, as l2_learning)
  --match=pair  : the reactive rule matches source MAC + destination MAC, so later flows
                  of the same pair find it ("reactive with pair rules", no prediction)
  --match=dst   : the reactive rule matches the destination MAC only
  --timeout_policy=fixed     : every reactive rule gets --idle_timeout / --hard_timeout (default)
  --timeout_policy=smarttime : SmartTime-style adaptive idle timeout, reimplemented from
                  Vishnoi et al., "Effective switch memory management in OpenFlow networks",
                  ACM DEBS 2014 (policy "AdaptiveR"). Per switch and rule key (the --match key):
                    idle = min(st_min * 2^n, st_max), n = earlier installs of this key on this
                    switch (the paper's FlowRepeatCount: every PACKET_IN that installs counts,
                    with no time window); back to st_min if the last timeout was st_max and the
                    key's average hold factor (rule lifetime / active time, from FLOW_REMOVED)
                    is above 3. Paper values: 100 ms and 10 s; OpenFlow 1.0 timeouts are whole
                    seconds, so the defaults here are --st_min=1 --st_max=10. The paper uses no
                    hard timeout; the harness passes --hard_timeout=0. Eviction: see --table_cap
  --table_cap=N : the harness caps each switch's table at N data rules (Open vSwitch flow_limit,
                  overflow_policy=refuse). The controller then keeps its own view of each table
                  (FLOW_REMOVED on every reactive rule), sends the FLOW_MOD without the packet and
                  forwards the packet with a separate PACKET_OUT, so a refused rule (table full)
                  does not lose the packet. Counts: table_full_events (PACKET_INs that found the
                  table full), refused_installs (OFPFMFC_ALL_TABLES_FULL errors), evictions
  --evict=auto|none|random : what to do when a capped table is above 95% full (the SmartTime
                  rule: delete one random reactive rule of that switch). auto = random for
                  --timeout_policy=smarttime, none (the switch refuses) for fixed
  --pairs_file=F: "oracle" upper bound: pre-install exactly the pairs listed in F
                  (one "src_mac dst_mac" per line, e.g. the truly busiest pairs of the
                  coming traffic), keep them for the whole run, no counter

Statistics written to --stats_file (extra.*): pair installs, removals, wasted
installs (pairs removed without ever matching a packet), pairs installed now,
and ingress SYN misses (new TCP connections whose first packet found no rule
at the sender's switch) - the harness turns the last one into a hit rate.

Usage (from the pox/ directory):
  PYTHONPATH=../controllers python3 pox.py hybrid_eval --topo=/path/topo.json \\
      [--budget=0.25] [--decay=0.97] [--interval=1] [--hysteresis=1.5] [--pairs_file=F] \\
      [--paths=shortest|ecmp] [--match=exact|pair|dst] [--idle_timeout=10] [--hard_timeout=30] [--stats_file=...]
      [--timeout_policy=fixed|smarttime] [--st_min=1] [--st_max=10] [--table_cap=0] [--evict=auto]
"""

import os
import random
import time
import zlib

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import EthAddr
from pox.lib.packet.ethernet import ethernet
from pox.lib.recoco import Timer
from pox.lib.util import dpid_to_str

from sa7_common import ControllerStats, load_link_weights, load_topology, shortest_paths
from lstm_predictor import PairActivityLSTM

log = core.getLogger("hybrid_eval")

PAIR_PRIORITY = 100   # pre-installed pair rules; reactive rules are exact matches (always win in OF 1.0)


class HybridEval(object):

  def __init__(self, topo_file, budget, decay, interval, hysteresis, paths,
               idle_timeout, hard_timeout, stats, pairs_file=None, match='exact', strategy='counter',
               model_file=None, warmup_intervals=10, timeout_policy='fixed', st_min=1, st_max=10,
               table_cap=0, evict='auto'):
    self.hosts, self.adj = load_topology(topo_file)
    self.weights = load_link_weights(topo_file)
    self.by_mac = {EthAddr(h['mac']): h for h in self.hosts}
    self.paths = paths
    self.match_mode = match
    self.decay, self.hysteresis = decay, hysteresis
    self.idle_timeout, self.hard_timeout = idle_timeout, hard_timeout
    self.stats = stats
    n_pairs = len(self.hosts) * (len(self.hosts) - 1)
    self.budget = int(round(budget * n_pairs))
    self.static_pairs = None
    if pairs_file:
      with open(pairs_file) as f:
        self.static_pairs = [tuple(l.split()[:2]) for l in f if l.strip()]
      self.budget = len(self.static_pairs)
    self.score = {}        # (src mac, dst mac) -> weighted activity
    self.strategy = strategy
    self.predictor = PairActivityLSTM.load(model_file) if strategy == 'lstm' else None
    self.lstm_warmup_intervals = warmup_intervals
    self.lstm_intervals = 0
    self.lstm_warmup_started = False
    self.active = set()    # pairs active in the current interval
    self.installed = {}    # pair -> {'path': [...], 'used': bool, 'packets': int}
    self._path_cache = {}
    self.connections = {}
    self.timeout_policy, self.st_min, self.st_max = timeout_policy, st_min, st_max
    self.table_cap = table_cap
    self.evict = (('random' if timeout_policy == 'smarttime' else 'none') if evict == 'auto' else evict)
    self.table = {}        # capped tables: dpid -> {rule key: match} of the reactive rules in the switch
    self.pending = {}      # capped tables: FLOW_MOD xid -> (dpid, rule key), to match refusals
    self.rnd = random.Random(1)
    self.st = {}           # SmartTime: (dpid, key) -> {'n': installs, 'live': timeout or None,
                           #            'prev': last timeout, 'holds': [hold factors]}
    stats.extra.update(budget_pairs=self.budget, total_pairs=n_pairs, pair_installs=0,
                       pair_removals=0, wasted_installs=0, pairs_installed=0,
                       ingress_syn_misses=0, ingress_new_flows=0)
    if timeout_policy == 'smarttime':
      stats.extra.update(st_installs=0, st_resets=0, st_duplicates=0, st_removed=0,
                         st_timeouts={})   # idle timeout (s) -> installs with it
    if table_cap:
      stats.extra.update(table_cap=table_cap, evict_policy=self.evict, table_full_events=0,
                         refused_installs=0, evictions=0, reactive_installs=0)
    if self.predictor:
      stats.extra.update(lstm_warmup_intervals=warmup_intervals, lstm_intervals=0)
    core.openflow.addListeners(self)
    Timer(interval, self._tick, recurring=True)
    log.info("Hybrid: %d hosts, budget %d of %d pairs, decay %.2f, every %.1f s",
             len(self.hosts), self.budget, n_pairs, decay, interval)

  # ------------------------------------------------------------ paths

  def _path(self, src, dst):
    key = (src['mac'], dst['mac'])
    if key not in self._path_cache:
      tied = shortest_paths(self.adj, self.weights, src['dpid'], dst['dpid'])
      if not tied:
        self._path_cache[key] = None
      elif self.paths == 'ecmp':
        self._path_cache[key] = tied[zlib.crc32(('%s-%s' % key).encode()) % len(tied)]
      else:
        self._path_cache[key] = tied[0]
    return self._path_cache[key]

  def _path_from(self, dpid, src, dst):
    tied = shortest_paths(self.adj, self.weights, dpid, dst['dpid'])
    if not tied:
      return None
    if self.paths == 'ecmp':
      return tied[zlib.crc32(('%s-%s' % (src['mac'], dst['mac'])).encode()) % len(tied)]
    return tied[0]

  def _out_port(self, path, dpid, dst):
    i = path.index(dpid)
    return dst['port'] if i == len(path) - 1 else self.adj[dpid][path[i + 1]]

  # ------------------------------------------------------------ OpenFlow events

  def _handle_ConnectionUp(self, event):
    self.connections[event.dpid] = event.connection
    self.stats.switch(event.dpid)['connected_at'] = time.time()
    self.stats.dirty = True

  def _handle_ConnectionDown(self, event):
    self.connections.pop(event.dpid, None)

  def _handle_PacketIn(self, event):
    t0 = time.perf_counter()
    packet = event.parsed
    if not packet.parsed or packet.type == ethernet.LLDP_TYPE:
      return
    dpid = event.dpid
    self.stats.count(dpid, 'packet_in')
    src, dst = self.by_mac.get(packet.src), self.by_mac.get(packet.dst)
    if src is None or dst is None:
      return   # broadcast or unknown host: static ARP is used, so drop
    path = self._path(src, dst)
    if self.match_mode == 'dst' and path and dpid not in path:
      # a destination rule at an earlier switch may have sent the packet along another
      # shortest path (the first sender's), so route from here
      path = self._path_from(dpid, src, dst)
    if not path or dpid not in path:
      return
    pair = (src['mac'], dst['mac'])
    if dpid == src['dpid']:   # the sender's own switch: this is where a flow starts
      self.active.add(pair)
      tcp = packet.find('tcp')
      if tcp is not None and tcp.SYN and not tcp.ACK:
        self.stats.extra['ingress_syn_misses'] += 1
      self.stats.extra['ingress_new_flows'] += 1
      self.stats.dirty = True
    msg = of.ofp_flow_mod()
    if self.match_mode == 'pair':
      msg.match = of.ofp_match(dl_src=packet.src, dl_dst=packet.dst)
    elif self.match_mode == 'dst':
      msg.match = of.ofp_match(dl_dst=packet.dst)
    else:
      msg.match = of.ofp_match.from_packet(packet, event.port)
    msg.idle_timeout, msg.hard_timeout = self.idle_timeout, self.hard_timeout
    if self.timeout_policy == 'smarttime':
      msg.idle_timeout = self._smarttime_idle(dpid, msg.match)
      msg.flags |= of.OFPFF_SEND_FLOW_REM   # FLOW_REMOVED tells us when it expired, and its hold factor
    out = of.ofp_action_output(port=self._out_port(path, dpid, dst))
    msg.actions.append(out)
    if self.table_cap:
      self._capped_install(event, dpid, msg, out)
    else:
      msg.data = event.ofp
      event.connection.send(msg)
      self.stats.count(dpid, 'flow_mod')
    self.stats.add_proc_time(time.perf_counter() - t0)

  # ------------------------------------------------------------ capped tables

  def _capped_install(self, event, dpid, msg, out):
    table = self.table.setdefault(dpid, {})
    key = self._rule_key(msg.match)
    msg.flags |= of.OFPFF_SEND_FLOW_REM   # so the controller's view of the table stays right
    if key not in table:
      if len(table) >= self.table_cap:
        self.stats.extra['table_full_events'] += 1
      if self.evict == 'random' and table and (len(table) >= self.table_cap or
                                               len(table) > 0.95 * self.table_cap):
        victim = self.rnd.choice(sorted(table))
        vmatch = table.pop(victim)
        event.connection.send(of.ofp_flow_mod(command=of.OFPFC_DELETE_STRICT, match=vmatch,
                                              priority=of.OFP_DEFAULT_PRIORITY))
        self.stats.count(dpid, 'flow_mod')
        self.stats.extra['evictions'] += 1
        rec = self.st.get((dpid, victim))
        if rec is not None:
          rec['live'] = None
      table[key] = msg.match
    # The rule and the packet go separately: if the switch refuses the rule (table full), the
    # packet is still forwarded, instead of waiting ~1 s for a TCP retransmission
    msg.xid = of.generate_xid()
    self.pending[msg.xid] = (dpid, key)
    if len(self.pending) > 20000:
      for x in list(self.pending)[:10000]:
        del self.pending[x]
    event.connection.send(msg)
    self.stats.count(dpid, 'flow_mod')
    self.stats.extra['reactive_installs'] += 1
    po = of.ofp_packet_out(in_port=event.port, action=of.ofp_action_output(port=out.port))
    po.data = event.ofp   # POX uses the switch's buffer if there is one, else the packet bytes
    event.connection.send(po)
    self.stats.dirty = True

  def _handle_ErrorIn(self, event):
    if not self.table_cap:
      return
    err = event.ofp
    if err.type != of.OFPET_FLOW_MOD_FAILED or err.code != of.OFPFMFC_ALL_TABLES_FULL:
      return
    event.should_log = False
    self.stats.extra['refused_installs'] += 1
    self.stats.dirty = True
    where = self.pending.pop(err.xid, None)
    if where is None:
      return
    dpid, key = where
    self.table.get(dpid, {}).pop(key, None)
    rec = self.st.get((dpid, key))
    if rec is not None:
      rec['live'] = None

  # ------------------------------------------------------------ SmartTime-style adaptive timeout

  def _rule_key(self, match):
    if self.match_mode == 'pair':
      return (str(match.dl_src), str(match.dl_dst))
    if self.match_mode == 'dst':
      return str(match.dl_dst)
    return (str(match.dl_src), str(match.dl_dst), match.dl_type, match.nw_proto,
            str(match.nw_src), str(match.nw_dst), match.tp_src, match.tp_dst)

  def _smarttime_idle(self, dpid, match):
    rec = self.st.setdefault((dpid, self._rule_key(match)),
                             {'n': 0, 'live': None, 'prev': None, 'holds': []})
    if rec['live'] is not None:
      # The rule is still in the switch (no FLOW_REMOVED yet): a second packet of the same
      # flow reached us before the first FLOW_MOD took effect. Not a repeat: same timeout.
      self.stats.extra['st_duplicates'] += 1
      return rec['live']
    idle = min(self.st_min * 2 ** rec['n'], self.st_max)
    if (rec['prev'] == self.st_max and rec['holds'] and
        sum(rec['holds']) / len(rec['holds']) > 3):
      idle = self.st_min
      self.stats.extra['st_resets'] += 1
    rec['n'] += 1
    rec['live'] = rec['prev'] = idle
    self.stats.extra['st_installs'] += 1
    hist = self.stats.extra['st_timeouts']
    hist[str(idle)] = hist.get(str(idle), 0) + 1
    return idle

  def _handle_FlowRemoved(self, event):
    ofp = event.ofp
    if ofp.priority == PAIR_PRIORITY:
      return
    if self.table_cap and ofp.reason != of.OFPRR_DELETE:   # an evicted rule has already left our view
      self.table.get(event.dpid, {}).pop(self._rule_key(ofp.match), None)
    if self.timeout_policy != 'smarttime':
      return
    rec = self.st.get((event.dpid, self._rule_key(ofp.match)))
    if rec is None:
      return
    life = ofp.duration_sec + ofp.duration_nsec / 1e9
    active = life - ofp.idle_timeout if ofp.reason == of.OFPRR_IDLE_TIMEOUT else life
    rec['holds'].append(life / active if active > 0 else float('inf'))
    rec['live'] = None
    self.stats.extra['st_removed'] += 1
    self.stats.dirty = True

  def _handle_FlowStatsReceived(self, event):
    # Packet counters of our pre-installed pair rules at the sender's switch
    for st in event.stats:
      if st.priority != PAIR_PRIORITY:
        continue
      pair = (str(st.match.dl_src), str(st.match.dl_dst))
      rec = self.installed.get(pair)
      if rec is None:
        continue
      if st.packet_count > rec['packets']:
        self.active.add(pair)
        rec['used'] = True
      rec['packets'] = st.packet_count

  # ------------------------------------------------------------ pair rules

  def _pair_rule(self, pair, path, dpid, command):
    src, dst = self.by_mac[EthAddr(pair[0])], self.by_mac[EthAddr(pair[1])]
    msg = of.ofp_flow_mod(command=command, priority=PAIR_PRIORITY,
                          match=of.ofp_match(dl_src=EthAddr(pair[0]), dl_dst=EthAddr(pair[1])))
    if command == of.OFPFC_ADD:
      msg.actions.append(of.ofp_action_output(port=self._out_port(path, dpid, dst)))
    return msg

  def _install(self, pair):
    src, dst = self.by_mac[EthAddr(pair[0])], self.by_mac[EthAddr(pair[1])]
    path = self._path(src, dst)
    if not path or any(d not in self.connections for d in path):
      return False
    for d in reversed(path):   # far end first, so the path is complete when the first hop goes in
      self.connections[d].send(self._pair_rule(pair, path, d, of.OFPFC_ADD))
      self.stats.count(d, 'flow_mod')
    self.installed[pair] = {'path': path, 'used': False, 'packets': 0}
    self.stats.extra['pair_installs'] += 1
    return True

  def _remove(self, pair):
    rec = self.installed.pop(pair)
    for d in rec['path']:
      if d in self.connections:
        self.connections[d].send(self._pair_rule(pair, rec['path'], d, of.OFPFC_DELETE_STRICT))
        self.stats.count(d, 'flow_mod')
    self.stats.extra['pair_removals'] += 1
    if not rec['used']:
      self.stats.extra['wasted_installs'] += 1

  def _tick(self):
    if self.static_pairs is not None:   # oracle: install the given pairs once switches are up
      for pair in self.static_pairs:
        if pair not in self.installed:
          self._install(pair)
      self.active = set()
      self.stats.extra['pairs_installed'] = len(self.installed)
      self.stats.dirty = True
      return
    # 1. Rank pairs using recent activity or the online next-interval forecast.
    if self.predictor:
      warming_up = self.lstm_intervals < self.lstm_warmup_intervals
      ranking = self.predictor.update(set(self.score) | self.active, self.active, learn=warming_up)
      if warming_up:
        for pair in set(self.score) | self.active:
          self.score[pair] = self.decay * self.score.get(pair, 0.0) + (1.0 if pair in self.active else 0.0)
      else:
        self.score.update({pair: probability / max(1.0 - probability, 1e-6)
                           for pair, probability in ranking.items()})
      self.lstm_warmup_started = self.lstm_warmup_started or bool(self.active)
      if self.lstm_warmup_started and self.lstm_intervals < self.lstm_warmup_intervals:
        self.lstm_intervals += 1
      self.stats.extra['lstm_intervals'] = self.lstm_intervals
      self.stats.extra['lstm_warmup_complete'] = self.lstm_intervals >= self.lstm_warmup_intervals
    else:
      for pair in set(self.score) | self.active:
        self.score[pair] = self.decay * self.score.get(pair, 0.0) + (1.0 if pair in self.active else 0.0)
    self.active = set()
    for pair in [p for p, s in self.score.items() if s < 1e-3 and p not in self.installed]:
      del self.score[pair]
    # 2. keep the top K within the budget, with hysteresis
    if self.budget > 0:
      ranked = sorted(self.score, key=lambda p: -self.score[p])
      for pair in ranked[:self.budget]:
        if pair in self.installed:
          continue
        if len(self.installed) < self.budget:
          self._install(pair)
          continue
        weakest = min(self.installed, key=lambda p: self.score.get(p, 0.0))
        if self.score[pair] > self.hysteresis * max(self.score.get(weakest, 0.0), 1e-9):
          self._remove(weakest)
          self._install(pair)
    # 3. ask the senders' switches how much each pre-installed pair was used
    #    (one request per pair, matching only that pair, so the reply stays small)
    for pair, rec in self.installed.items():
      d = rec['path'][0]
      if d in self.connections:
        m = of.ofp_match(dl_src=EthAddr(pair[0]), dl_dst=EthAddr(pair[1]))
        self.connections[d].send(of.ofp_stats_request(body=of.ofp_flow_stats_request(match=m)))
    self.stats.extra['pairs_installed'] = len(self.installed)
    self.stats.dirty = True


def launch(topo=None, budget='0.25', decay='0.97', interval='1', hysteresis='1.5',
           paths='shortest', idle_timeout='10', hard_timeout='30', stats_file=None, pairs_file=None,
           match='exact', strategy='counter', model_file=None, warmup_intervals='10',
           timeout_policy='fixed', st_min='1', st_max='10', table_cap='0', evict='auto'):
  if not topo:
    raise RuntimeError("hybrid_eval needs --topo=<topology.json>")
  if paths not in ('shortest', 'ecmp'):
    raise RuntimeError("--paths must be shortest or ecmp")
  if match not in ('exact', 'pair', 'dst'):
    raise RuntimeError("--match must be exact, pair or dst")
  if timeout_policy not in ('fixed', 'smarttime'):
    raise RuntimeError("--timeout_policy must be fixed or smarttime")
  if not 1 <= int(st_min) <= int(st_max) <= 65535:
    raise RuntimeError("--st_min / --st_max: whole seconds, 1 <= st_min <= st_max (OpenFlow 1.0)")
  if int(table_cap) < 0 or evict not in ('auto', 'none', 'random'):
    raise RuntimeError("--table_cap must be >= 0 and --evict auto, none or random")
  if strategy not in ('counter', 'lstm'):
    raise RuntimeError("--strategy must be counter or lstm")
  if strategy == 'lstm' and (not model_file or not os.path.isfile(model_file)):
    raise RuntimeError("--strategy=lstm requires --model_file=<trained .npz file>")
  if int(warmup_intervals) < 0:
    raise RuntimeError("--warmup_intervals must be non-negative")
  config = {'budget': float(budget), 'decay': float(decay), 'interval': float(interval),
            'hysteresis': float(hysteresis), 'paths': paths, 'idle_timeout': int(idle_timeout),
            'hard_timeout': int(hard_timeout), 'topo': topo, 'pairs_file': pairs_file, 'match': match,
            'strategy': strategy, 'model_file': model_file,
            'warmup_intervals': int(warmup_intervals), 'timeout_policy': timeout_policy,
            'st_min': int(st_min), 'st_max': int(st_max), 'table_cap': int(table_cap), 'evict': evict}
  stats = ControllerStats('hybrid', config, stats_file)

  def start():
    core.registerNew(HybridEval, topo, float(budget), float(decay), float(interval),
                     float(hysteresis), paths, int(idle_timeout), int(hard_timeout), stats,
                     pairs_file, match, strategy, model_file, int(warmup_intervals),
                     timeout_policy, int(st_min), int(st_max), int(table_cap), evict)
    Timer(1, stats.dump, recurring=True)
    stats.dump(force=True)

  core.addListenerByName("GoingDownEvent", lambda e: stats.dump(force=True))
  core.call_when_ready(start, "openflow")
