"""Figure for the paper: hit rate against network size, from docs/figures/scale_sim.json.

  python3 experiments/scale_sim.py            # writes docs/figures/scale_sim.json
  python3 docs/figures/make_scale_figure.py   # writes scale_hit_rate.pdf / .png next to this file,
                                              # and copies the PDF to paper/ and paper/sigcomm/

Sized for one column (3.33 in, the column width of both paper formats), so the 8 pt text stays
8 pt in print. Series differ by line style and marker as well as colour, so they stay apart in
grayscale.
"""
import json
import os
import shutil
import statistics

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER_DIRS = [os.path.join(HERE, '..', '..', 'paper'), os.path.join(HERE, '..', '..', 'paper', 'sigcomm')]
INK, MUTED, GRID = '#000000', '#555555', '#dddddd'
SERIES = [  # key, label, colour, marker, line style (style and marker alone tell the series apart)
  ('dst', 'Destination rules', '#1f4e9c', 'o', '-'),
  ('history+10', 'Pair rules + counter 10%', '#1a8a5f', 's', '--'),
  ('pair', 'Pair rules', '#d9541e', '^', ':'),
]

rows = json.load(open(os.path.join(HERE, 'scale_sim.json')))['rows']
loads = sorted({r['load'] for r in rows})
plt.rcParams.update({'font.size': 8, 'axes.titlesize': 8, 'axes.labelsize': 8, 'xtick.labelsize': 7.5,
                     'ytick.labelsize': 7.5, 'legend.fontsize': 7.5, 'axes.edgecolor': INK,
                     'axes.labelcolor': INK, 'xtick.color': INK, 'ytick.color': INK,
                     'font.family': 'DejaVu Sans', 'pdf.fonttype': 42})
fig, axes = plt.subplots(len(loads), 1, figsize=(3.33, 3.75), sharex=True)
for ax, load in zip(axes, loads):
  g = [r for r in rows if r['load'] == load]
  hosts = sorted({r['hosts'] for r in g})
  m = lambda key, h: statistics.mean(r[key] for r in g if r['hosts'] == h)
  ax.plot(hosts, [m('first_flow_ceiling', h) for h in hosts], color=MUTED, ls='-.', lw=1.0,
          label='Not first flow of pair')
  for key, label, color, marker, ls in SERIES:
    ax.plot(hosts, [m(key, h) for h in hosts], color=color, ls=ls, lw=1.6, marker=marker, ms=4.5,
            markerfacecolor=color if marker != 's' else 'white', markeredgecolor=color,
            markeredgewidth=1.1, label=label)
  ax.set_xscale('log')
  ax.set_xticks(hosts)
  ax.set_xticklabels([format(h, ',') for h in hosts])
  ax.minorticks_off()
  ax.set_ylim(40, 100)
  ax.grid(axis='y', color=GRID, lw=0.6)
  ax.set_axisbelow(True)
  for s in ('top', 'right'):
    ax.spines[s].set_visible(False)
  fpp = statistics.mean(r['flows_per_active_pair'] for r in g if r['hosts'] == hosts[-1])
  ax.set_title('%d%% load (%.1f flows per pair at %s hosts)'
               % (round(load * 100), fpp, format(hosts[-1], ',')), color=INK, loc='left')
  ax.set_ylabel('Hit rate (%)')
axes[-1].set_xlabel('Hosts (fat-tree, k = 4 to 16)')
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc='lower center', ncol=2, frameon=False, handlelength=2.6, columnspacing=1.0,
           bbox_to_anchor=(0.5, 0.0))
fig.tight_layout(rect=(0, 0.11, 1, 1), h_pad=0.8)
for ext in ('pdf', 'png'):
  fig.savefig(os.path.join(HERE, 'scale_hit_rate.' + ext), dpi=300)
print('wrote', os.path.join(HERE, 'scale_hit_rate.pdf'))
for d in PAPER_DIRS:
  if os.path.isdir(d):
    shutil.copy(os.path.join(HERE, 'scale_hit_rate.pdf'), os.path.join(d, 'scale_hit_rate.pdf'))
    print('copied to', os.path.normpath(os.path.join(d, 'scale_hit_rate.pdf')))
