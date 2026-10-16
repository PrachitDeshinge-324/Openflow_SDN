#!/usr/bin/env python3
"""
Summary figures for Step 4 (used in docs/Progress_Review_2.md)
CS G525 Advanced Computer Networks - Project SA7

The numbers below are copied from the laptop runs' traffic.md files: each is the
mean of 5 runs (seeds 7-11) with the half-width of its 95% confidence interval
(night of 15-16 Oct 2026, Windows power mode "Best performance"):
  university, Zipf 1   results/measured/traffic-20261015-225412/
  fat-tree, web search results/measured/traffic-20261015-233914/
  Abilene ISP          results/measured/traffic-20261016-004215/
  university, uniform  results/measured/traffic-20261016-012626/
Each run's own plots (traffic_budget.png etc.) are in those folders; this script
only puts the four scenarios side by side.

Usage: python3 docs/figures/make_step4_figures.py   (writes the PNGs next to itself)
"""

import os
import sys

os.environ.setdefault('MPLCONFIGDIR', '/tmp/matplotlib_cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'experiments'))
from plot_paths import GRID, INK, MUTED, style

COUNTER, ORACLE = '#6250d6', '#eda100'
SETUP, PATH, FLOOR = '#eb6834', '#6250d6', '#c9c8c0'

# Hit rate (%) at budgets 0 / 10 / 25 / 50 % of host pairs: (means, 95% CI half-widths)
HIT = [
  ('University tree, Zipf pairs', ([0, 30.8, 60.7, 78.9], [0, 10.2, 5.5, 1.8]),
   ([0, 49.3, 68.2, 84.7], [0, 6.0, 4.3, 2.1])),
  ('Fat-tree, web search, Zipf pairs', ([0, 51.1, 65.8, 77.4], [0, 1.6, 1.4, 1.8]),
   ([0, 56.2, 73.7, 88.3], [0, 1.3, 1.2, 0.7])),
  ('Abilene ISP, real traffic matrices', ([0, 26.6, 53.8, 77.2], [0, 2.3, 2.3, 1.8]),
   ([0, 33.1, 59.2, 83.0], [0, 1.0, 0.8, 1.0])),
  ('University tree, uniform pairs (control)', ([0, 9.6, 24.5, 48.4], [0, 0.2, 1.2, 0.2]),
   ([0, 12.5, 29.4, 55.4], [0, 0.2, 0.5, 0.6])),
]
BUDGETS = [0, 10, 25, 50]

# Small-flow median FCT (ms): reactive over a spanning tree, reactive on shortest
# paths (hybrid budget 0), proactive (ECMP on the fat-tree)
# (mean over 5 seeds of each run's median)
SPLIT = [
  ('University tree', 27.86, 27.29, 0.96),
  ('Fat-tree, web search', 110.83, 59.30, 28.62),
  ('Abilene ISP', 96.83, 55.62, 45.97),
]


def hit_rate():
  fig, axes = plt.subplots(1, len(HIT), figsize=(4.3 * len(HIT), 4.0), sharey=True)
  for ax, (name, counter, oracle) in zip(axes, HIT):
    ax.plot([0, 50], [0, 50], color=MUTED, linestyle='--', linewidth=1,
            label='Budget share (pairs picked at random)')
    for (ys, ci), color, label in ((oracle, ORACLE, 'Oracle (knows the future)'),
                                   (counter, COUNTER, 'Weighted counter')):
      ax.errorbar(BUDGETS, ys, yerr=ci, color=color, linewidth=2, marker='o', markersize=8,
                  markeredgecolor='white', markeredgewidth=1.5, capsize=4, elinewidth=1.2, label=label)
    # direct labels on the 10% and 50% points only
    for i in (1, 3):
      ax.annotate('%.0f' % oracle[0][i], (BUDGETS[i], oracle[0][i] + oracle[1][i]), xytext=(0, 5),
                  textcoords='offset points', ha='center', color=INK, fontsize=9)
      ax.annotate('%.0f' % counter[0][i], (BUDGETS[i], counter[0][i] - counter[1][i]), xytext=(0, -14),
                  textcoords='offset points', ha='center', color=INK, fontsize=9)
    ax.set_title(name, color=INK, fontsize=10)
    ax.set_xticks(BUDGETS)
    ax.set_xlim(-3, 55)
    ax.set_ylim(0, 100)
    ax.set_xlabel('Rule budget (% of host pairs)', color=INK)
    style(ax)
  axes[0].set_ylabel('Hit rate: new connections that\nfound a rule (%)', color=INK)
  axes[0].legend(frameon=False, fontsize=9, loc='upper left')
  fig.suptitle('Budgeted hybrid: hit rate against rule budget (laptop, mean of 5 runs, bars = 95% CI)',
               color=INK)
  fig.tight_layout()
  path = os.path.join(HERE, 'step4_hit_rate.png')
  fig.savefig(path, dpi=150)
  return path


def cost_split():
  fig, ax = plt.subplots(figsize=(9, 3.9))
  for i, (name, tree, sp, pro) in enumerate(SPLIT):
    y = len(SPLIT) - 1 - i
    path, setup = max(0.0, tree - sp), sp - pro
    left = 0
    for width, color in ((pro, FLOOR), (setup, SETUP), (path, PATH)):
      if width > 0:
        ax.barh(y, width, 0.55, left=left, color=color, edgecolor='white', linewidth=2)
      left += width
    ax.annotate('%.0f ms' % tree, (left, y), xytext=(6, 0), textcoords='offset points',
                va='center', color=INK, fontsize=9)
    if path >= 5:
      ax.annotate('+%.0f' % path, (pro + setup + path / 2, y), ha='center', va='center',
                  color='white', fontsize=9, fontweight='bold')
    ax.annotate('+%.0f' % setup, (pro + setup / 2, y), ha='center', va='center',
                color='white', fontsize=9, fontweight='bold')
  ax.set_yticks(range(len(SPLIT)))
  ax.set_yticklabels([s[0] for s in reversed(SPLIT)], color=INK)
  ax.set_xlabel('Small-flow completion time, median (ms)', color=INK)
  ax.set_xlim(0, 130)
  for side in ('top', 'right'):
    ax.spines[side].set_visible(False)
  for side in ('left', 'bottom'):
    ax.spines[side].set_color(MUTED)
  ax.tick_params(colors=MUTED, labelcolor=INK)
  ax.grid(axis='x', color=GRID, linewidth=0.8)
  ax.set_axisbelow(True)
  handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in (FLOOR, SETUP, PATH)]
  ax.legend(handles, ['Proactive (the floor)', 'Asking the controller (setup)',
                      'Spanning-tree detour (path)'],
            frameon=False, fontsize=9, loc='upper center', bbox_to_anchor=(0.45, -0.22), ncol=3)
  ax.set_title("Where reactive's extra time goes (mean of 5 runs; ECMP is part of the fat-tree's setup bar)",
               color=INK, fontsize=10)
  fig.tight_layout()
  path = os.path.join(HERE, 'step4_cost_split.png')
  fig.savefig(path, dpi=150)
  return path


if __name__ == '__main__':
  for p in (hit_rate(), cost_split()):
    print('[+] %s' % p)
