#!/usr/bin/env python3
"""
Plots for the realistic-traffic experiment (run_traffic_experiments.py)
CS G525 Advanced Computer Networks - Project SA7

Usage: python3 experiments/plot_traffic.py results/measured/traffic-<timestamp>
Writes traffic_fct_cdf.png, traffic_small_fct.png and traffic_control.png.
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


def bars(ax, runs, value, fmt, log=False):
  modes = [m for m in MODES if m in runs]
  ys = [value(runs[m]) for m in modes]
  floor = 0.5 if log else 0
  bs = ax.bar(range(len(modes)), [max(y, floor) for y in ys], 0.6, color=[COLORS[m] for m in modes],
              edgecolor='white', linewidth=2)
  for b, y in zip(bs, ys):
    ax.annotate(fmt % y, (b.get_x() + b.get_width() / 2, max(y, floor)), xytext=(0, 4),
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
      bars(ax, runs, lambda r: r['fct']['small'].get(key, 0), '%.1f', log=True)
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
    bars(ax, runs, lambda r: r['control']['packet_in_per_s'], '%.0f')
    ax.set_ylim(0, max(1, max(r['control']['packet_in_per_s'] for r in runs.values())) * 1.25)
    ax.set_title('%s: requests to the controller' % name.replace('\n', ', '), color=INK, fontsize=10)
    ax = axes[1][j]
    bars(ax, runs, lambda r: r['control']['peak_rules_total'], '%d')
    ax.set_ylim(0, max(1, max(r['control']['peak_rules_total'] for r in runs.values())) * 1.25)
    ax.set_title('%s: rules in all switches (peak)' % name.replace('\n', ', '), color=INK, fontsize=10)
  axes[0][0].set_ylabel('PACKET_IN per second', color=INK)
  axes[1][0].set_ylabel('Rules (peak during the run)', color=INK)
  fig.suptitle('Controller load and flow-table size under realistic traffic', color=INK)
  fig.tight_layout()
  path = os.path.join(out_dir, 'traffic_control.png')
  fig.savefig(path, dpi=150)
  return path


def main():
  if len(sys.argv) != 2:
    sys.exit(__doc__)
  out_dir = sys.argv[1]
  with open(os.path.join(out_dir, 'traffic.json')) as f:
    sc = scenarios(json.load(f)['results'])
  if not sc:
    sys.exit('No results to plot')
  for p in (plot_cdf(sc, out_dir), plot_small(sc, out_dir), plot_control(sc, out_dir)):
    print('[+] Plot: %s' % p)


if __name__ == '__main__':
  main()
