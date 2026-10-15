#!/usr/bin/env python3
"""
Plots for the path-quality experiment (run_path_experiments.py)
CS G525 Advanced Computer Networks - Project SA7

Usage: python3 experiments/plot_paths.py results/measured/paths-<timestamp>
Writes paths_stretch.png, paths_throughput.png and paths_link_balance.png.
"""

import json
import os
import sys

os.environ.setdefault('MPLCONFIGDIR', '/tmp/matplotlib_cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

MODES = ['reactive', 'proactive', 'proactive-ecmp']
COLORS = {'reactive': '#eb6834', 'proactive': '#2a78d6', 'proactive-ecmp': '#1baf7a'}
LABELS = {'reactive': 'Reactive\n(learning + tree)', 'proactive': 'Proactive\n(one shortest path)',
          'proactive-ecmp': 'Proactive\n(ECMP)'}
INK, MUTED, GRID = '#1f1f1e', '#6b6a63', '#e4e3dc'


def style(ax):
  for side in ('top', 'right'):
    ax.spines[side].set_visible(False)
  for side in ('left', 'bottom'):
    ax.spines[side].set_color(MUTED)
  ax.tick_params(colors=MUTED, labelcolor=INK)
  ax.grid(axis='y', color=GRID, linewidth=0.8)
  ax.set_axisbelow(True)


def by_topology(results):
  out = {}
  for r in results:
    out.setdefault(r['topology'], {})[r['mode']] = r
  return out


def bar_panel(ax, runs, value, fmt, error=None):
  modes = [m for m in MODES if m in runs]
  ys = [value(runs[m]) for m in modes]
  es = [error(runs[m]) for m in modes] if error else [0] * len(modes)
  bars = ax.bar(range(len(modes)), ys, 0.6, color=[COLORS[m] for m in modes],
                edgecolor='white', linewidth=2, yerr=es if error else None,
                error_kw={'ecolor': MUTED, 'capsize': 4, 'elinewidth': 1})
  for b, y, e in zip(bars, ys, es):
    ax.annotate(fmt % y, (b.get_x() + b.get_width() / 2, y + e), xytext=(0, 4),
                textcoords='offset points', ha='center', color=INK, fontsize=10)
  ax.set_xticks(range(len(modes)))
  ax.set_xticklabels([LABELS[m] for m in modes], fontsize=9)
  style(ax)


def stretch(r):
  a = r['paths']
  key = 'delay_stretch' if r['has_delay'] else 'hop_stretch'
  return a.get(key, {}).get('mean', float('nan'))


def plot_stretch(topos, out_dir):
  fig, axes = plt.subplots(1, len(topos), figsize=(5 * len(topos), 4.5), squeeze=False)
  for ax, (name, runs) in zip(axes[0], topos.items()):
    bar_panel(ax, runs, stretch, '%.2f')
    any_r = next(iter(runs.values()))
    ax.axhline(1.0, color=MUTED, linestyle='--', linewidth=1)
    ax.set_ylim(0, max(stretch(r) for r in runs.values()) * 1.25)
    ax.set_title('%s: %s' % (name, 'path delay' if any_r['has_delay'] else 'path hops'),
                 color=INK, fontsize=11)
  axes[0][0].set_ylabel('Path used / best possible path\n(1.00 = best, dashed)', color=INK)
  fig.suptitle('Experiment A: how much longer than the best path?', color=INK)
  fig.tight_layout()
  path = os.path.join(out_dir, 'paths_stretch.png')
  fig.savefig(path, dpi=150)
  return path


def plot_throughput(topos, out_dir):
  fig, axes = plt.subplots(1, len(topos), figsize=(5 * len(topos), 4.5), squeeze=False)
  for ax, (name, runs) in zip(axes[0], topos.items()):
    total = lambda r, k: r['throughput']['summary']['total_mbps'][k]
    bar_panel(ax, runs, lambda r: total(r, 'mean'), '%.0f', lambda r: total(r, 'std'))
    ideal = next(iter(runs.values()))['throughput']['ideal_total_mbps']
    ax.axhline(ideal, color=MUTED, linestyle='--', linewidth=1)
    ax.annotate('every host at full speed: %d' % ideal, (ax.get_xlim()[0], ideal), xytext=(4, 4),
                textcoords='offset points', color=MUTED, fontsize=9)
    ax.set_ylim(0, ideal * 1.2)
    ax.set_title(name, color=INK, fontsize=11)
  axes[0][0].set_ylabel('Total throughput, all flows (Mbit/s)', color=INK)
  fig.suptitle('Experiment B: total throughput, every host sending at once (mean +/- std)', color=INK)
  fig.tight_layout()
  path = os.path.join(out_dir, 'paths_throughput.png')
  fig.savefig(path, dpi=150)
  return path


def plot_link_balance(topos, out_dir):
  fig, axes = plt.subplots(1, len(topos), figsize=(5 * len(topos), 4.5), squeeze=False)
  for ax, (name, runs) in zip(axes[0], topos.items()):
    for m in MODES:
      if m not in runs:
        continue
      first = runs[m]['throughput']['runs'][0]['link_mbps']
      ys = sorted(first.values(), reverse=True)
      ax.plot(range(1, len(ys) + 1), ys, color=COLORS[m], linewidth=2,
              label=LABELS[m].replace('\n', ' '))
    ax.set_xlabel('Switch links, busiest to idlest (each direction)', color=INK)
    ax.set_title(name, color=INK, fontsize=11)
    ax.set_ylim(bottom=0)
    style(ax)
  axes[0][0].set_ylabel('Traffic on the link (Mbit/s)', color=INK)
  axes[0][-1].legend(frameon=False, fontsize=9)
  fig.suptitle('Experiment B: how evenly the links are used (first permutation)', color=INK)
  fig.tight_layout()
  path = os.path.join(out_dir, 'paths_link_balance.png')
  fig.savefig(path, dpi=150)
  return path


def main():
  if len(sys.argv) != 2:
    sys.exit(__doc__)
  out_dir = sys.argv[1]
  with open(os.path.join(out_dir, 'paths.json')) as f:
    topos = by_topology(json.load(f)['results'])
  if not topos:
    sys.exit('No results to plot')
  for p in (plot_stretch(topos, out_dir), plot_throughput(topos, out_dir),
            plot_link_balance(topos, out_dir)):
    print('[+] Plot: %s' % p)


if __name__ == '__main__':
  main()
