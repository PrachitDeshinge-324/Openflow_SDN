#!/usr/bin/env python3
"""
Paired comparisons between controllers, from existing result folders.
CS G525 Advanced Computer Networks - Project SA7

Every controller of a batch runs on the same seeds, and a seed fixes the flow schedule, so two
controllers can be compared seed by seed. For each pair of modes (A, B) and each metric this prints
the mean of the per-seed differences A - B and its 95% confidence interval (Student's t with n - 1
degrees of freedom on the n differences), and in how many seeds A was below B.

How to read it:
  - an interval that excludes 0 is a difference in the direction of its sign;
  - an interval that contains 0 is NOT evidence that A and B are equal. It only bounds the
    difference: the data are compatible with any value inside it. No equivalence test is made,
    because no equivalence margin was fixed before the runs.
With n = 5 (or 3) the t quantile is large (2.776, or 4.303), so intervals are wide.

  python3 experiments/paired_stats.py results/measured/traffic-20261119-114525 [...] [--pairs tap:proactive ...]
  python3 experiments/paired_stats.py --paper      # every comparison quoted in paper/paper.tex
"""

import argparse
import json
import math
import os
import statistics
import sys

T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262}

METRICS = {   # name -> (path in a result, unit)
  'small_p50': (('fct', 'small', 'p50_ms'), 'ms'),
  'small_mean': (('fct', 'small', 'mean_ms'), 'ms'),
  'hit_rate': (('hybrid', 'hit_rate_pct'), 'pp'),
  'packet_in': (('control', 'packet_in_per_s'), '/s'),
}

HERE = os.path.dirname(os.path.abspath(__file__))
M = os.path.join(HERE, '..', 'results', 'measured')
# The comparisons the paper makes, per table: (folder, A, B, metrics)
PAPER = [
  # Table 2: granularity (university, fat-tree k=4, Abilene; 5 seeds each)
  *[(f, a, b, ['hit_rate', 'small_p50'])
    for f in ('traffic-20261020-171718', 'traffic-20261020-183215', 'traffic-20261021-050401')
    for a, b in (('reactive-pair', 'hybrid-25'), ('reactive-dst', 'hybrid-25'),
                 ('reactive-pair', 'oracle-25'), ('reactive-dst', 'oracle-25'),
                 ('oracle-25', 'hybrid-25'), ('hybrid-25', 'random-25'))],
  *[(f, a, p, ['small_p50'])
    for f, p in (('traffic-20261020-171718', 'proactive'), ('traffic-20261020-183215', 'proactive-ecmp'),
                 ('traffic-20261021-050401', 'proactive'))
    for a in ('reactive-pair', 'reactive-dst')],
  # Section IV-A: long timeouts against plain reactive (T6 folders, 5 seeds each)
  *[(f, 'reactive-long', 'reactive', ['packet_in', 'small_p50'])
    for f in ('traffic-20261015-225412', 'traffic-20261015-233914', 'traffic-20261016-004215',
              'traffic-20261016-012626')],
  # Section V: 54 hosts (3 seeds)
  ('traffic-20261023-070549', 'hybrid-10', 'reactive-pair', ['hit_rate']),
  ('traffic-20261023-070549', 'oracle-10', 'reactive-pair', ['hit_rate']),
  ('traffic-20261023-070549', 'reactive-dst', 'reactive-pair', ['hit_rate']),
  # Table 3: tap (four networks)
  *[(f, 'tap', p, ['small_p50', 'small_mean'])
    for f, p in (('traffic-20261119-114525', 'proactive'), ('traffic-20261119-120616', 'proactive-ecmp'),
                 ('traffic-20261119-123520', 'proactive'), ('traffic-20261119-125611', 'proactive-ecmp'))],
  *[(f, 'tap', 'reactive-dst', ['small_p50', 'packet_in'])
    for f in ('traffic-20261119-114525', 'traffic-20261119-120616', 'traffic-20261119-123520',
              'traffic-20261119-125611')],
  # Section VI, second batch (21 Nov): proactive-dst = tap without its copy rules
  *[(f, 'tap', 'proactive-dst', ['small_p50', 'small_mean'])
    for f in ('traffic-20261121-073853', 'traffic-20261121-075657', 'traffic-20261121-082609',
              'traffic-20261121-084548')],
  *[(f, 'proactive-dst', p, ['small_p50'])
    for f, p in (('traffic-20261121-073853', 'proactive'), ('traffic-20261121-075657', 'proactive-ecmp'),
                 ('traffic-20261121-082609', 'proactive'), ('traffic-20261121-084548', 'proactive-ecmp'))],
]


def get(r, path):
  for k in path:
    if not isinstance(r, dict) or r.get(k) is None:
      return None
    r = r[k]
  return r


def paired(rows, a, b, metric):
  path = METRICS[metric][0]
  va = {r['seed']: get(r, path) for r in rows if r['mode'] == a}
  vb = {r['seed']: get(r, path) for r in rows if r['mode'] == b}
  seeds = sorted(s for s in set(va) & set(vb) if va[s] is not None and vb[s] is not None)
  if not seeds:
    return None
  d = [va[s] - vb[s] for s in seeds]
  n = len(d)
  mean = statistics.mean(d)
  half = T975.get(n - 1, 1.96) * statistics.stdev(d) / math.sqrt(n) if n > 1 else float('nan')
  return {'n': n, 'mean': mean, 'lo': mean - half, 'hi': mean + half,
          'a_below': sum(1 for x in d if x < 0), 'b_mean': statistics.mean(vb[s] for s in seeds),
          'a_mean': statistics.mean(va[s] for s in seeds)}


def load(folder):
  with open(os.path.join(folder, 'traffic.json')) as f:
    return json.load(f)['results']


def verdict(s):
  if s['lo'] > 0:
    return 'A > B'
  if s['hi'] < 0:
    return 'A < B'
  return 'not resolved'


def main():
  ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  ap.add_argument('folders', nargs='*')
  ap.add_argument('--pairs', nargs='+', default=[], metavar='A:B')
  ap.add_argument('--metrics', nargs='+', default=['small_p50', 'hit_rate'], choices=sorted(METRICS))
  ap.add_argument('--paper', action='store_true', help='every comparison quoted in the paper')
  ap.add_argument('--json', help='also write the rows to this file')
  args = ap.parse_args()

  jobs = []
  if args.paper:
    jobs += [(os.path.join(M, f), a, b, ms) for f, a, b, ms in PAPER]
  for f in args.folders:
    for p in args.pairs:
      a, b = p.split(':')
      jobs.append((f, a, b, args.metrics))
  if not jobs:
    sys.exit('give result folders and --pairs A:B, or --paper')

  print('Paired per-seed differences A - B: mean and 95% CI (t, n - 1 df). '
        '"not resolved" = the interval contains 0 (no equivalence is claimed).\n')
  print('| Folder | Network / workload | A | B | Metric | n | A mean | B mean | A - B | 95% CI | Seeds A < B | Result |')
  print('| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |')
  cache, out = {}, []
  for folder, a, b, metrics in jobs:
    rows = cache.setdefault(folder, load(folder))
    for metric in metrics:
      s = paired(rows, a, b, metric)
      if s is None:
        continue
      sc = '%s / %s' % (rows[0]['network'], rows[0]['workload'])
      unit = METRICS[metric][1]
      print('| %s | %s | %s | %s | %s (%s) | %d | %.2f | %.2f | %+.2f | [%+.2f, %+.2f] | %d of %d | %s |' % (
        os.path.basename(os.path.normpath(folder)), sc, a, b, metric, unit, s['n'], s['a_mean'],
        s['b_mean'], s['mean'], s['lo'], s['hi'], s['a_below'], s['n'], verdict(s)))
      out.append(dict(s, folder=os.path.basename(os.path.normpath(folder)), scenario=sc, a=a, b=b,
                      metric=metric, unit=unit, result=verdict(s)))
  if args.json:
    with open(args.json, 'w') as f:
      json.dump(out, f, indent=1)


if __name__ == '__main__':
  main()
