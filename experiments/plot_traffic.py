#!/usr/bin/env python3
"""
Plots for the realistic-traffic experiment (run_traffic_experiments.py)
CS G525 Advanced Computer Networks - Project SA7

Usage: python3 experiments/plot_traffic.py results/measured/traffic-<timestamp>
Writes traffic_fct_cdf.png, traffic_small_fct.png and traffic_control.png, and
traffic_budget.png when the run includes the budget sweep (--budget-sweep).
With --repeats N, bars and points are the mean of the N runs with 95%
confidence intervals as error bars, and the CDFs pool the flows of all runs.
"""

import json
import os
import sys

os.environ.setdefault('MPLCONFIGDIR', '/tmp/matplotlib_cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plot_paths import COLORS, GRID, INK, LABELS, MODES, MUTED, style
from repeats import aggregate

SMALL = 100 * 1000


def scenarios(results):
  out = {}
  for r in results:
    out.setdefault('%s\n%s traffic' % (r['network'], r['workload']), {})[r['mode']] = r
  return out


def small_fcts(r):
  return sorted(x['fct_ms'] for x in r['flows_detail'] if x['ok'] and x['size'] < SMALL)


def plot_cdf(sc, out_dir):
  fig, axes = plt.subplots(1, len(sc), figsize=(5 * len(sc), 4.3), squeeze=False)
  for ax, (name, runs) in zip(axes[0], sc.items()):
    for m in MODES:
      if m not in runs:
        continue
      xs = small_fcts(runs[m])
      if xs:
        ax.plot(xs, [(i + 1) / len(xs) for i in range(len(xs))], color=COLORS[m], linewidth=2,
                label=LABELS[m].replace('\n', ' '))
    ax.set_xscale('log')
    ax.xaxis.set_major_formatter(ScalarFormatter())
    ax.set_xlabel('Flow completion time (ms, log scale)', color=INK)
    ax.set_title(name, color=INK, fontsize=11)
    ax.set_ylim(0, 1.02)
    style(ax)
    ax.grid(axis='x', color=GRID, linewidth=0.8)
  axes[0][0].set_ylabel('Fraction of small flows (< 100 KB) finished', color=INK)
  axes[0][-1].legend(frameon=False, fontsize=9, loc='lower right')
  fig.suptitle('Small flows: how long they take (further left = faster)', color=INK)
  fig.tight_layout()
  path = os.path.join(out_dir, 'traffic_fct_cdf.png')
  fig.savefig(path, dpi=150)
  return path


def bars(ax, runs, value, fmt, log=False, ci=None):
  """ci: name of the metric in r['ci'] (repeated runs) to draw as an error bar."""
  modes = [m for m in MODES if m in runs]
  ys = [value(runs[m]) for m in modes]
  errs = [runs[m].get('ci', {}).get(ci, 0) if ci else 0 for m in modes]
  floor = 0.5 if log else 0
  bs = ax.bar(range(len(modes)), [max(y, floor) for y in ys], 0.6, color=[COLORS[m] for m in modes],
              edgecolor='white', linewidth=2)
  if any(errs):
    ax.errorbar(range(len(modes)), [max(y, floor) for y in ys],
                yerr=[[min(e, max(y, floor) - floor * 0.99) for y, e in zip(ys, errs)], errs],
                fmt='none', ecolor=INK, elinewidth=1.2, capsize=4)
  for b, y, e in zip(bs, ys, errs):
    ax.annotate(fmt % y, (b.get_x() + b.get_width() / 2, max(y, floor) + e), xytext=(0, 4),
                textcoords='offset points', ha='center', color=INK, fontsize=10)
  ax.set_xticks(range(len(modes)))
  ax.set_xticklabels([LABELS[m] for m in modes], fontsize=8)
  if log:
    ax.set_yscale('log')
    ax.yaxis.set_major_formatter(ScalarFormatter())
  style(ax)


def plot_small(sc, out_dir):
  fig, axes = plt.subplots(2, len(sc), figsize=(5 * len(sc), 7.5), squeeze=False)
  for j, (name, runs) in enumerate(sc.items()):
    for i, (key, label) in enumerate((('p50_ms', 'median'), ('p99_ms', '99th percentile'))):
      ax = axes[i][j]
      bars(ax, runs, lambda r: r['fct']['small'].get(key, 0), '%.1f', log=True, ci='fct.small.' + key)
      top = max(r['fct']['small'].get(key, 1) for r in runs.values())
      ax.set_ylim(0.5, top * 4)
      ax.set_title('%s: %s' % (name.replace('\n', ', '), label), color=INK, fontsize=10)
    axes[0][0].set_ylabel('Small-flow FCT, median (ms, log)', color=INK)
    axes[1][0].set_ylabel('Small-flow FCT, 99th pct (ms, log)', color=INK)
  fig.suptitle('Small flows (< 100 KB): completion time', color=INK)
  fig.tight_layout()
  path = os.path.join(out_dir, 'traffic_small_fct.png')
  fig.savefig(path, dpi=150)
  return path


def plot_control(sc, out_dir):
  fig, axes = plt.subplots(2, len(sc), figsize=(5 * len(sc), 7.5), squeeze=False)
  for j, (name, runs) in enumerate(sc.items()):
    ax = axes[0][j]
    bars(ax, runs, lambda r: r['control']['packet_in_per_s'], '%.0f', ci='control.packet_in_per_s')
    ax.set_ylim(0, max(1, max(r['control']['packet_in_per_s'] for r in runs.values())) * 1.25)
    ax.set_title('%s: requests to the controller' % name.replace('\n', ', '), color=INK, fontsize=10)
    ax = axes[1][j]
    bars(ax, runs, lambda r: r['control']['peak_rules_total'], '%d', ci='control.peak_rules_total')
    ax.set_ylim(0, max(1, max(r['control']['peak_rules_total'] for r in runs.values())) * 1.25)
    ax.set_title('%s: rules in all switches (peak)' % name.replace('\n', ', '), color=INK, fontsize=10)
  axes[0][0].set_ylabel('PACKET_IN per second', color=INK)
  axes[1][0].set_ylabel('Rules (peak during the run)', color=INK)
  fig.suptitle('Controller load and flow-table size under realistic traffic', color=INK)
  fig.tight_layout()
  path = os.path.join(out_dir, 'traffic_control.png')
  fig.savefig(path, dpi=150)
  return path


COUNTER, ORACLE, RANDOM = '#6250d6', '#eda100', '#8a877c'


def _budget(mode):
  return float(mode.split('-', 1)[1])


def plot_budget(results, out_dir):
  """Hit rate, small-flow median FCT, PACKET_IN/s and rules against the rule budget."""
  sc = {}
  for r in results:
    sc.setdefault('%s, %s traffic' % (r['network'], r['workload']), {})[r['mode']] = r
  sc = {k: v for k, v in sc.items() if any(m.startswith(('hybrid-', 'oracle-', 'random-')) for m in v)}
  if not sc:
    return None
  metrics = [('Hit rate (% of new connections)', 'hybrid.hit_rate_pct',
              lambda r: r['hybrid']['hit_rate_pct'] if r.get('hybrid') else None),
             ('Small-flow FCT, median (ms)', 'fct.small.p50_ms', lambda r: r['fct']['small'].get('p50_ms')),
             ('PACKET_IN per second', 'control.packet_in_per_s', lambda r: r['control']['packet_in_per_s']),
             ('Rules in all switches (peak)', 'control.peak_rules_total',
              lambda r: r['control']['peak_rules_total'])]
  fig, axes = plt.subplots(len(sc), len(metrics), figsize=(4.4 * len(metrics), 3.8 * len(sc)), squeeze=False)
  for i, (name, runs) in enumerate(sc.items()):
    for j, (label, ci, get) in enumerate(metrics):
      ax = axes[i][j]
      base = runs.get('reactive-sp')
      for prefix, color, text in (('random-', RANDOM, 'Random'), ('hybrid-', COUNTER, 'Counter'),
                                  ('oracle-', ORACLE, 'Oracle')):
        pts = sorted((_budget(m), get(r), r.get('ci', {}).get(ci, 0)) for m, r in runs.items()
                     if m.startswith(prefix))
        if base is not None and get(base) is not None:
          pts = [(0.0, get(base), base.get('ci', {}).get(ci, 0))] + pts
        pts = [p for p in pts if p[1] is not None]
        if pts:
          ax.plot([p[0] for p in pts], [p[1] for p in pts], color=color, linewidth=2, marker='o',
                  markersize=7, markeredgecolor='white', label=text)
          if any(p[2] for p in pts):
            ax.errorbar([p[0] for p in pts], [p[1] for p in pts], yerr=[p[2] for p in pts], fmt='none',
                        ecolor=color, elinewidth=1.2, capsize=4)
      xmax = max([_budget(m) for m in runs if m.startswith(('hybrid-', 'oracle-', 'random-'))] + [10]) * 1.2
      # reactive-long's label goes under its line, so it does not sit on top of reactive's
      for mode, color, ls, dy in (('reactive', COLORS['reactive'], '--', 3),
                                  ('reactive-long', COLORS['reactive'], ':', -11),
                                  ('reactive-pair', COLORS['reactive'], '-.', 3),
                                  ('reactive-dst', COLORS['reactive'], '-.', -11),
                                  ('proactive', COLORS['proactive'], '--', 3),
                                  ('proactive-ecmp', COLORS['proactive-ecmp'], '--', 3)):
        if mode in runs and get(runs[mode]) is not None:
          ax.axhline(get(runs[mode]), color=color, linestyle=ls, linewidth=1.2)
          ax.annotate(mode, (xmax, get(runs[mode])), xytext=(-4, dy), textcoords='offset points',
                      ha='right', color=MUTED, fontsize=8)
      ax.set_xlim(-2, xmax)
      ax.set_ylim(bottom=0)
      ax.set_xlabel('Rule budget (% of all host pairs)', color=INK)
      ax.set_title('%s\n%s' % (name, label), color=INK, fontsize=10)
      style(ax)
  axes[0][0].legend(frameon=False, fontsize=9, loc='upper left')
  fig.suptitle('Budgeted hybrid: what a fraction of the rules buys (dashed lines: reactive / proactive)', color=INK)
  fig.tight_layout()
  path = os.path.join(out_dir, 'traffic_budget.png')
  fig.savefig(path, dpi=150)
  return path


def main():
  if len(sys.argv) != 2:
    sys.exit(__doc__)
  out_dir = sys.argv[1]
  with open(os.path.join(out_dir, 'traffic.json')) as f:
    results = aggregate(json.load(f)['results'])   # one entry per controller, also with --repeats
  sc = scenarios(results)
  if not sc:
    sys.exit('No results to plot')
  for p in (plot_cdf(sc, out_dir), plot_small(sc, out_dir), plot_control(sc, out_dir),
            plot_budget(results, out_dir)):
    if p:
      print('[+] Plot: %s' % p)


if __name__ == '__main__':
  main()
