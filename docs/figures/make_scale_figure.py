"""Figure for the paper: hit rate against network size, from docs/figures/scale_sim.json.

  python3 experiments/scale_sim.py            # writes docs/figures/scale_sim.json
  python3 docs/figures/make_scale_figure.py   # writes scale_hit_rate.pdf / .png next to this file
"""
import json
import os
import statistics

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
INK, MUTED, GRID, SURFACE = '#0b0b0b', '#52514e', '#e4e3dc', '#fcfcfb'
SERIES = [  # key, label, colour (fixed categorical order), marker, line style
  ('dst', 'Reactive, destination rules', '#2a78d6', 'o', '-'),
  ('history+10', 'Pair rules + counter from past window (10%)', '#1baf7a', 's', '-'),
  ('pair', 'Reactive, pair rules', '#eb6834', '^', '-'),
]

rows = json.load(open(os.path.join(HERE, 'scale_sim.json')))['rows']
loads = sorted({r['load'] for r in rows})
plt.rcParams.update({'font.size': 8, 'axes.edgecolor': MUTED, 'axes.labelcolor': INK,
                     'xtick.color': MUTED, 'ytick.color': MUTED, 'font.family': 'DejaVu Sans'})
fig, axes = plt.subplots(1, len(loads), figsize=(7.0, 2.5), sharey=True, facecolor=SURFACE)
for ax, load in zip(axes, loads):
  ax.set_facecolor(SURFACE)
  g = [r for r in rows if r['load'] == load]
  hosts = sorted({r['hosts'] for r in g})
  m = lambda key, h: statistics.mean(r[key] for r in g if r['hosts'] == h)
  ax.plot(hosts, [m('first_flow_ceiling', h) for h in hosts], color=MUTED, ls='--', lw=1.2,
          label='Flows that are not the first of their pair')
  for key, label, color, marker, ls in SERIES:
    ax.plot(hosts, [m(key, h) for h in hosts], color=color, ls=ls, lw=2, marker=marker, ms=5,
            markeredgecolor=SURFACE, markeredgewidth=1, label=label)
  ax.set_xscale('log')
  ax.set_xticks(hosts)
  ax.set_xticklabels([str(h) for h in hosts])
  ax.minorticks_off()
  ax.set_ylim(40, 100)
  ax.grid(axis='y', color=GRID, lw=0.8)
  ax.set_axisbelow(True)
  for s in ('top', 'right'):
    ax.spines[s].set_visible(False)
  ax.set_xlabel('Hosts (fat-tree k = 4 ... 16)')
  fpp = statistics.mean(r['flows_per_active_pair'] for r in g if r['hosts'] == hosts[-1])
  ax.set_title('Web search, %d%% load (%.1f flows per pair at %d hosts)' % (round(load * 100), fpp, hosts[-1]),
               color=INK, fontsize=8)
axes[0].set_ylabel('Hit rate (%)')
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc='lower center', ncol=2, frameon=False, fontsize=7, bbox_to_anchor=(0.5, -0.02))
fig.tight_layout(rect=(0, 0.17, 1, 1))
for ext in ('pdf', 'png'):
  fig.savefig(os.path.join(HERE, 'scale_hit_rate.' + ext), dpi=200, facecolor=SURFACE)
print('wrote', os.path.join(HERE, 'scale_hit_rate.pdf'))
