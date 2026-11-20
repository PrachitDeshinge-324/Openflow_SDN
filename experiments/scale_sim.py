"""
Scale sweep by trace replay: wildcard hit rate, and the most prediction could add, on fat-trees
far larger than the laptop can emulate.
CS G525 Advanced Computer Networks - Project SA7

Uses the replay model of experiments/model_validate.py, which reproduces the hit rate of all 46
measured reactive-pair / reactive-dst runs to within 0.1 percentage points per run. Flow
schedules come from the same workload code as the testbed (web search sizes, Poisson arrivals,
Zipf pair popularity), generated here without Mininet.

For each fat-tree size k, load and seed it reports the hit rate (share of new connections whose
first packet finds a rule at the sender's switch) of:
  pair      reactive, one rule per (source, destination) pair on the first miss
  dst       reactive, one rule per destination on the first miss
  history+B pair rules, plus the B% busiest pairs of the PREVIOUS window pre-installed
            (a frequency counter with history: a predictor that could be built)
  oracle+B  pair rules, plus the B% busiest pairs of the run pre-installed for its whole length
            (a hindsight bound on what any pair predictor can add on top of pair rules)
first_flow_ceiling = share of flows that are not the first flow of their pair (the most a
rule installed on the first miss can ever hit), and flows per active pair, the quantity that decides whether a first-miss rule is reused.

  python3 experiments/scale_sim.py [--ks 4 6 8 12 16] [--loads 0.05 0.3] [--seeds 7 8 9] [--zipf 1] [--out F]
"""

import argparse
import json
import os
import random
import statistics
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import workloads as wl
from model_validate import simulate

BW_MBPS, MAX_BYTES = 100, 20 * 1000 * 1000


def fattree(k):
  """Hosts {name: edge dpid}, and a shortest-path function over the switch graph."""
  half = k // 2
  core = [('c', i) for i in range(half * half)]
  adj = {}

  def link(a, b):
    adj.setdefault(a, set()).add(b)
    adj.setdefault(b, set()).add(a)
  host_sw = {}
  h = 0
  for p in range(k):
    aggs = [('a', p, i) for i in range(half)]
    edges = [('e', p, i) for i in range(half)]
    for i, a in enumerate(aggs):
      for j in range(half):
        link(a, core[i * half + j])
      for e in edges:
        link(a, e)
    for e in edges:
      for _ in range(half):
        h += 1
        host_sw['h%d' % h] = e
  ids = {s: n for n, s in enumerate(sorted(adj))}
  graph = {ids[s]: sorted(ids[t] for t in nb) for s, nb in adj.items()}
  cache = {}

  def path(a, b):   # BFS, lowest neighbour first: deterministic, like shortest_paths()[0]
    if (a, b) not in cache:
      prev, frontier = {a: None}, [a]
      while b not in prev:
        nxt = []
        for u in frontier:
          for v in graph[u]:
            if v not in prev:
              prev[v] = u
              nxt.append(v)
        frontier = nxt
      p = [b]
      while p[-1] != a:
        p.append(prev[p[-1]])
      cache[(a, b)] = p[::-1]
    return cache[(a, b)]
  return {n: ids[s] for n, s in host_sw.items()}, path


def schedule(hosts, duration, load, seed, zipf=1.0, rank_seed=None):
  """workloads.make_schedule for 'websearch', with the Zipf pair choice precomputed (fast at 1,000 hosts)."""
  rng = random.Random(seed)
  sizes = wl.WORKLOADS['websearch']['sizes']
  n = len(hosts)
  rank = list(range(n * (n - 1)))
  random.Random('%s-pair-ranking' % (seed if rank_seed is None else rank_seed)).shuffle(rank)
  w, i = {}, 0
  for a in hosts:
    w[a] = []
    for b in hosts:
      if a != b:
        w[a].append((b, 1.0 / (rank[i] + 1) ** zipf))
        i += 1
  src_w = [sum(x for _, x in w[a]) for a in hosts]
  cum = {a: [] for a in hosts}
  for a in hosts:
    t = 0.0
    for _, x in w[a]:
      t += x
      cum[a].append(t)
  rate = load * n * BW_MBPS * 1e6 / 8 / sizes.mean(cap=MAX_BYTES)
  flows, t = [], rng.expovariate(rate)
  srcs = rng.choices(hosts, weights=src_w, k=int(rate * duration * 1.5) + 10)
  si = 0
  while t < duration:
    a = srcs[si]
    si += 1
    import bisect
    j = bisect.bisect_left(cum[a], rng.random() * cum[a][-1])
    b = w[a][min(j, len(w[a]) - 1)][0]
    size = max(1, int(min(sizes.sample(rng), MAX_BYTES)))
    fct = size * 8 / (BW_MBPS * 1e6) + 0.005   # unloaded transfer time + 5 ms; only moves rule refreshes
    flows.append((t, a, b, fct))
    t += rng.expovariate(rate)
  return flows


def main():
  ap = argparse.ArgumentParser()
  ap.add_argument('--ks', nargs='+', type=int, default=[4, 6, 8, 12, 16])
  ap.add_argument('--loads', nargs='+', type=float, default=[0.05, 0.3])
  ap.add_argument('--seeds', nargs='+', type=int, default=[7, 8, 9])
  ap.add_argument('--duration', type=float, default=30.0)
  ap.add_argument('--budgets', nargs='+', type=float, default=[2, 10])
  ap.add_argument('--zipf', type=float, default=1.0, help='pair-popularity Zipf exponent (0 = uniform)')
  ap.add_argument('--out', default=os.path.join(HERE, '..', 'docs', 'figures', 'scale_sim.json'))
  args = ap.parse_args()
  rows = []
  for k in args.ks:
    sw, path = fattree(k)
    hosts = sorted(sw, key=lambda h: int(h[1:]))
    n_pairs = len(hosts) * (len(hosts) - 1)
    for load in args.loads:
      for seed in args.seeds:
        t0 = time.time()
        flows = schedule(hosts, args.duration, load, seed, zipf=args.zipf)
        counts = {}
        for _, a, b, _ in flows:
          counts[(a, b)] = counts.get((a, b), 0) + 1
        row = {'k': k, 'hosts': len(hosts), 'pairs': n_pairs, 'load': load, 'seed': seed,
               'flows': len(flows), 'active_pairs': len(counts),
               'flows_per_active_pair': len(flows) / max(1, len(counts)),
               'pair': simulate(flows, sw, path, 'pair'), 'dst': simulate(flows, sw, path, 'dst')}
        ranked = sorted(counts, key=lambda p: -counts[p])
        for b in args.budgets:
          top = ranked[:int(round(b / 100.0 * n_pairs))]
          pre = {(sw[a], (a, d)) for a, d in top}
          row['oracle+%g' % b] = simulate(flows, sw, path, 'pair', pre=pre)
        # a realisable predictor: count pairs in the previous window (same pair popularity,
        # new arrivals) and pre-install the busiest B% of pairs; pair rules for the rest
        past = schedule(hosts, args.duration, load, seed + 1000, zipf=args.zipf, rank_seed=seed)
        pc = {}
        for _, a, d, _ in past:
          pc[(a, d)] = pc.get((a, d), 0) + 1
        past_ranked = sorted(pc, key=lambda p: -pc[p])
        for b in args.budgets:
          top = past_ranked[:int(round(b / 100.0 * n_pairs))]
          row['history+%g' % b] = simulate(flows, sw, path, 'pair', pre={(sw[a], (a, d)) for a, d in top})
        row['first_flow_ceiling'] = 100.0 * (1 - len(counts) / float(len(flows)))
        rows.append(row)
        print('k=%2d hosts=%4d load=%.2f seed=%d flows=%6d flows/pair=%5.2f  pair %5.1f  dst %5.1f  %s  (%.0f s)'
              % (k, len(hosts), load, seed, len(flows), row['flows_per_active_pair'], row['pair'], row['dst'],
                 '  '.join('hist+%g %5.1f oracle+%g %5.1f' % (b, row['history+%g' % b], b, row['oracle+%g' % b])
                           for b in args.budgets),
                 time.time() - t0), flush=True)
  with open(args.out, 'w') as f:
    json.dump({'args': vars(args), 'rows': rows}, f, indent=1)
  print('\nmean over seeds:')
  keys = (['first_flow_ceiling', 'pair', 'dst'] + ['history+%g' % b for b in args.budgets]
          + ['oracle+%g' % b for b in args.budgets])
  for k in args.ks:
    for load in args.loads:
      g = [r for r in rows if r['k'] == k and r['load'] == load]
      print('k=%2d load=%.2f flows/pair %5.2f  ' % (k, load, statistics.mean(r['flows_per_active_pair'] for r in g)) +
            '  '.join('%s %5.1f' % (c, statistics.mean(r[c] for r in g)) for c in keys))


if __name__ == '__main__':
  main()
