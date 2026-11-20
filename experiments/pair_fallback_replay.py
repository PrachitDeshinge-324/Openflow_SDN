#!/usr/bin/env python3
"""
How much can pre-installing pairs add ON TOP OF pair rules? Replay of the stored testbed schedules.
CS G525 Advanced Computer Networks - Project SA7

The testbed hybrid pre-installs pairs on top of an exact-match fallback. A reviewer asks: what if the
fallback were pair rules? This answers it with the replay model of model_validate.py (validated to
within 0.1 points of hit rate on these same runs), on the flow schedules of the measured
reactive-pair runs, so no new testbed run is needed.

For each run and budget B (share of all ordered host pairs) it reports the hit rate of:
  pair          reactive pair rules only (the replay of the measured run)
  +busiest B    pair rules plus the B busiest pairs of the run pre-installed for the whole run
                (the testbed oracle's choice, moved onto a pair-rule fallback)
  +best B       pair rules plus the B pairs with the most pair-rule MISSES in the run. With no table
                limit a pair's misses at its ingress switch do not depend on other pairs, so this is
                the exact optimum over all fixed sets of B pairs: an upper bound for any predictor that
                pre-installs a fixed set (it is not a bound for a predictor that changes its set).
Limits: hit rate only (no timing); unlimited switch tables; pre-installed rules never expire.

  python3 experiments/pair_fallback_replay.py [--budgets 10 25] [--json F]
"""

import argparse
import json
import statistics
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model_validate import IDLE, HARD, load  # noqa: E402

RUNS = [('traffic-20261020-171718', (10, 25)), ('traffic-20261020-183215', (10, 25)),
        ('traffic-20261021-050401', (10, 25)), ('traffic-20261023-070549', (2, 5, 10))]


def misses_per_pair(flows, sw, path):
  """Pair-rule replay; returns (hit %, {pair: misses at its ingress switch})."""
  ev = []
  for i, (t, s, d, f) in enumerate(flows):
    ev.append((t, 0, i))
    ev.append((t + f, 1, i))
  ev.sort()
  last, inst, miss = {}, {}, {}

  def alive(k, t):
    return k in last and t - last[k] < IDLE and t - inst[k] < HARD

  def touch(k, t):
    if not alive(k, t):
      inst[k] = t
    last[k] = t

  for t, kind, i in ev:
    _, s, d, _ = flows[i]
    if kind == 0 and not alive((sw[s], (s, d)), t):
      miss[(s, d)] = miss.get((s, d), 0) + 1
    for S in path(sw[s], sw[d]):
      touch((S, (s, d)), t)
      touch((S, (d, s)), t)
  return 100.0 * (1 - sum(miss.values()) / len(flows)), miss


def hit_with(flows, miss, chosen):
  """Pre-installing a pair removes exactly its ingress misses (tables unlimited, pairs independent)."""
  return 100.0 * (1 - sum(m for p, m in miss.items() if p not in chosen) / len(flows))


def main():
  ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  ap.add_argument('--json', help='write the per-run rows to this file')
  args = ap.parse_args()
  rows = []
  print('| Folder | Network / workload | Runs | Pairs | Budget | Pair rules (replay) | Pair rules measured '
        '| + busiest B | + best fixed B (bound) | Room left by pair rules |')
  print('| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |')
  for folder, budgets in RUNS:
    runs = [x for x in load(folder) if x[0]['mode'] == 'reactive-pair']
    for B in budgets:
      res = []
      for r, flows, sw, path in runs:
        hosts = sorted(sw)
        n_pairs = len(hosts) * (len(hosts) - 1)
        k = int(round(n_pairs * B / 100.0))
        base, miss = misses_per_pair(flows, sw, path)
        count = {}
        for _, s, d, _ in flows:   # the testbed oracle counts a flow for both directions
          count[(s, d)] = count.get((s, d), 0) + 1
          count[(d, s)] = count.get((d, s), 0) + 1
        busiest = set(sorted(count, key=lambda p: -count[p])[:k])
        best = set(sorted(miss, key=lambda p: -miss[p])[:k])
        row = {'folder': folder, 'network': r['network'], 'workload': r['workload'], 'seed': r['seed'],
               'budget_pct': B, 'budget_pairs': k, 'pairs': n_pairs, 'flows': len(flows),
               'pair': base, 'measured_pair': r['hybrid']['hit_rate_pct'],
               'busiest': hit_with(flows, miss, busiest), 'best': hit_with(flows, miss, best)}
        res.append(row)
        rows.append(row)
      m = lambda key: statistics.mean(x[key] for x in res)
      print('| %s | %s / %s | %d | %d | %d%% (%d) | %.1f | %.1f | %.1f | %.1f | %.1f points |' % (
        folder, res[0]['network'], res[0]['workload'], len(res), res[0]['pairs'], B, res[0]['budget_pairs'],
        m('pair'), m('measured_pair'), m('busiest'), m('best'), m('best') - m('pair')))
  if args.json:
    with open(args.json, 'w') as f:
      json.dump(rows, f, indent=1)


if __name__ == '__main__':
  main()
