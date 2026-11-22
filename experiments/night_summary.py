#!/usr/bin/env python3
"""
Summary of experiments/overnight_batch.sh (control-channel delay sweep, run-length check).
CS G525 Advanced Computer Networks - Project SA7

  python3 experiments/night_summary.py results/measured/night-YYYYMMDD [--no-plot]

A. ctrl-d<D>-s<S>: per controller and one-way control delay D, the small-flow median (mean of seeds
   with 95% t interval), failed flows, PACKET_IN/s, and the paired per-seed increase over D = 0.
   Figure ctrl_delay.pdf / .png in the night folder.
B. len<L>-s<S>: per controller, the measured hit rate at 30 s and 120 s of arrivals and the paired
   change; for reactive-pair / reactive-dst also the replay model's prediction on the same stored
   schedules (tests the model at 120 s, and the paper's run-length statement on the testbed).
Pairing is by seed: a seed fixes the flows, and the batch interleaves delays / lengths per seed.
"""

import argparse
import glob
import json
import math
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447}
ORDER = ['reactive-sp', 'reactive-pair', 'reactive-dst', 'hybrid-25', 'oracle-25', 'proactive', 'tap']


def mean_ci(xs):
  xs = [x for x in xs if x is not None]
  if not xs:
    return None, None
  if len(xs) == 1:
    return xs[0], float('nan')
  return statistics.mean(xs), T975.get(len(xs) - 1, 1.96) * statistics.stdev(xs) / math.sqrt(len(xs))


def fmt(m, h, p=2):
  if m is None:
    return '-'
  return ('%.*f' % (p, m)) + ('' if h is None or h != h else ' ± %.*f' % (p, h))


def load(night, prefix):
  """{(key, seed): {mode: result}} for folders <prefix><key>-s<seed>."""
  out = {}
  for d in sorted(glob.glob(os.path.join(night, prefix + '*'))):
    m = re.match(re.escape(prefix) + r'([\d.]+)-s(\d+)$', os.path.basename(d))
    if not m or not os.path.isfile(os.path.join(d, 'traffic.json')):
      continue
    with open(os.path.join(d, 'traffic.json')) as f:
      data = json.load(f)
    out[(float(m.group(1)), int(m.group(2)))] = {r['mode']: dict(r, _folder=d) for r in data['results']}
  return out


def modes_of(runs):
  ms = {m for v in runs.values() for m in v}
  return sorted(ms, key=lambda m: (ORDER.index(m) if m in ORDER else 99, m))


def part_a(night, plot):
  runs = load(night, 'ctrl-d')
  if not runs:
    print('A: no ctrl-d* folders')
    return
  delays = sorted({k for k, _ in runs})
  seeds = sorted({s for _, s in runs})
  modes = modes_of(runs)
  print('## A. Control-channel delay (one way), university tree, seeds %s\n' % seeds)
  print('Small-flow median FCT, ms (mean of seeds ± 95% CI); [failed flows]; PACKET_IN/s\n')
  print('| Controller | ' + ' | '.join('%g ms' % d for d in delays) + ' |')
  print('| --- |' + ' --- |' * len(delays))
  series = {}
  for m in modes:
    cells, ys = [], []
    for d in delays:
      rs = [runs[(d, s)][m] for s in seeds if (d, s) in runs and m in runs[(d, s)]]
      mm, hh = mean_ci([r['fct']['small'].get('p50_ms') for r in rs])
      failed = sum(r['fct']['failed'] for r in rs)
      pin = statistics.mean(r['control']['packet_in_per_s'] for r in rs) if rs else None
      cells.append('%s [%d]; %s' % (fmt(mm, hh), failed, '-' if pin is None else '%.0f' % pin))
      ys.append((d, mm, hh))
    series[m] = ys
    print('| %s | %s |' % (m, ' | '.join(cells)))
  print('\nPaired increase over 0 ms (per seed, same flows), small-flow median, ms:\n')
  print('| Controller | ' + ' | '.join('+%g ms' % d for d in delays if d) + ' |')
  print('| --- |' + ' --- |' * (len(delays) - 1))
  for m in modes:
    cells = []
    for d in delays:
      if not d:
        continue
      diffs = [runs[(d, s)][m]['fct']['small']['p50_ms'] - runs[(0.0, s)][m]['fct']['small']['p50_ms']
               for s in seeds if (d, s) in runs and (0.0, s) in runs and m in runs[(d, s)] and m in runs[(0.0, s)]]
      mm, hh = mean_ci(diffs)
      cells.append('-' if mm is None else '%+.2f [%+.2f, %+.2f] (n=%d)' % (mm, mm - hh, mm + hh, len(diffs))
                   if hh == hh else '%+.2f (n=1)' % mm)
    print('| %s | %s |' % (m, ' | '.join(cells)))
  checked = [r.get('ctrl_delay_packets') for v in runs.values() for r in v.values() if r.get('ctrl_delay_ms')]
  print('\nDelay applied: %d delayed runs, OpenFlow packets delayed per run min %s (must be > 0)\n'
        % (len(checked), min(checked) if checked else '-'))
  if plot:
    try:
      import matplotlib
      matplotlib.use('Agg')
      import matplotlib.pyplot as plt
      fig, ax = plt.subplots(figsize=(5, 3.4))
      for m, ys in series.items():
        xs = [d for d, mm, _ in ys if mm is not None]
        ax.errorbar(xs, [mm for _, mm, _ in ys if mm is not None],
                    yerr=[0 if hh != hh else hh for _, mm, hh in ys if mm is not None],
                    marker='o', ms=4, capsize=3, label=m)
      ax.set_xscale('symlog', linthresh=1)
      from matplotlib.ticker import NullFormatter, ScalarFormatter
      ax.set_xticks(delays)
      ax.set_xticklabels(['%g' % d for d in delays])
      vals = [mm for ys in series.values() for _, mm, _ in ys if mm]
      if vals and max(vals) / min(vals) > 10:   # wide range (reactive under delay): log scale
        ax.set_yscale('log')
        ax.yaxis.set_major_formatter(ScalarFormatter())
        ax.yaxis.set_minor_formatter(NullFormatter())
      ax.set_xlabel('one-way control-channel delay (ms)')
      ax.set_ylabel('small-flow median FCT (ms)')
      ax.legend(frameon=False, fontsize=8)
      fig.tight_layout()
      for ext in ('pdf', 'png'):
        fig.savefig(os.path.join(night, 'ctrl_delay.' + ext), dpi=150)
      print('Figure: %s/ctrl_delay.pdf\n' % night)
    except ImportError:
      print('(matplotlib not installed: no figure)\n')


def part_b(night):
  runs = load(night, 'len')
  if not runs:
    print('B: no len* folders')
    return
  lengths = sorted({k for k, _ in runs})
  seeds = sorted({s for _, s in runs})
  modes = modes_of(runs)
  print('## B. Run length, university tree, seeds %s\n' % seeds)
  print('| Controller | ' + ' | '.join('hit %% at %g s' % L for L in lengths) +
        ' | paired change %g -> %g s (points) | replay model, same schedules: change |' % (lengths[0], lengths[-1]))
  print('| --- |' + ' --- |' * (len(lengths) + 2))
  try:
    from model_validate import load as mv_load, simulate
  except ImportError:
    mv_load = None
  for m in modes:
    cells = []
    for L in lengths:
      mm, hh = mean_ci([(runs[(L, s)][m].get('hybrid') or {}).get('hit_rate_pct')
                        for s in seeds if (L, s) in runs and m in runs[(L, s)]])
      cells.append(fmt(mm, hh, 1))
    lo, hi = lengths[0], lengths[-1]
    diffs = [runs[(hi, s)][m]['hybrid']['hit_rate_pct'] - runs[(lo, s)][m]['hybrid']['hit_rate_pct']
             for s in seeds if (lo, s) in runs and (hi, s) in runs and m in runs[(lo, s)] and m in runs[(hi, s)]
             and runs[(lo, s)][m].get('hybrid') and runs[(hi, s)][m].get('hybrid')]
    mm, hh = mean_ci(diffs)
    change = '-' if mm is None else ('%+.1f [%+.1f, %+.1f] (n=%d)' % (mm, mm - hh, mm + hh, len(diffs))
                                     if hh == hh else '%+.1f (n=1)' % mm)
    model = '-'
    if mv_load and m in ('reactive-pair', 'reactive-dst'):
      gran = 'pair' if m == 'reactive-pair' else 'dst'
      pred = {}
      for (L, s), v in runs.items():
        if m not in v:
          continue
        rel = os.path.relpath(os.path.dirname(v[m]['_folder']), os.path.join(HERE, '..', 'results', 'measured'))
        for r, flows, sw, path in mv_load(os.path.join(rel, os.path.basename(v[m]['_folder']))):
          if r['mode'] == m:
            pred[(L, s)] = (simulate(flows, sw, path, gran), r['hybrid']['hit_rate_pct'])
      pd = [pred[(hi, s)][0] - pred[(lo, s)][0] for s in seeds if (lo, s) in pred and (hi, s) in pred]
      err = [abs(p - meas) for p, meas in pred.values()]
      if pd:
        model = '%+.1f (model error per run at most %.1f points)' % (statistics.mean(pd), max(err))
    print('| %s | %s | %s | %s |' % (m, ' | '.join(cells), change, model))
  print()


def main():
  ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  ap.add_argument('night')
  ap.add_argument('--no-plot', action='store_true')
  args = ap.parse_args()
  machine = os.path.join(args.night, 'machine.txt')
  if os.path.isfile(machine):
    print('Machine and code:\n```\n' + open(machine).read().strip() + '\n```\n')
  part_a(args.night, not args.no_plot)
  part_b(args.night)


if __name__ == '__main__':
  main()
