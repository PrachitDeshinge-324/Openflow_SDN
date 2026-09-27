#!/usr/bin/env python3
"""
Plots for the measured SA7 experiments
CS G525 Advanced Computer Networks - Project SA7

Usage: python3 experiments/plot_results.py results/measured/<timestamp>
Reads results.json from that directory and writes three PNG figures next to it.
"""

import json
import os
import sys

os.environ.setdefault('MPLCONFIGDIR', '/tmp/matplotlib_cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

COLORS = {'reactive': '#d62728', 'proactive': '#1f77b4'}


def by_mode(results):
  out = {}
  for r in results:
    out.setdefault(r['mode'], []).append(r)
  for rs in out.values():
    rs.sort(key=lambda r: r['hosts'])
  return out


def plot_latency(modes, out_dir):
  fig, ax = plt.subplots(figsize=(9, 5))
  hosts = sorted({r['hosts'] for rs in modes.values() for r in rs})
  width = 0.2
  bars = [('reactive', 'pkt1', 'Reactive: packet 1'), ('reactive', 'steady', 'Reactive: steady state'),
          ('proactive', 'pkt1', 'Proactive: packet 1'), ('proactive', 'steady', 'Proactive: steady state')]
  for i, (mode, key, label) in enumerate(bars):
    rs = {r['hosts']: r for r in modes.get(mode, [])}
    xs = [j + (i - 1.5) * width for j, h in enumerate(hosts) if h in rs]
    ys = [rs[h]['latency'][key + '_mean_ms'] for h in hosts if h in rs]
    es = [rs[h]['latency'][key + '_std_ms'] for h in hosts if h in rs]
    ax.bar(xs, ys, width, yerr=es, capsize=3, label=label, color=COLORS[mode],
           alpha=1.0 if key == 'pkt1' else 0.45, edgecolor='black', linewidth=0.5)
  ax.set_xticks(range(len(hosts)))
  ax.set_xticklabels(['%d hosts' % h for h in hosts])
  ax.set_yscale('log')
  ax.yaxis.set_major_formatter(ScalarFormatter())
  ax.set_ylabel('Round-trip time (ms, log scale)')
  ax.set_title('Measured flow-setup latency: first packet vs steady state')
  ax.legend()
  ax.grid(axis='y', which='both', alpha=0.3)
  path = os.path.join(out_dir, 'measured_latency.png')
  fig.tight_layout()
  fig.savefig(path, dpi=150)
  return path


def plot_occupancy(modes, out_dir):
  fig, ax = plt.subplots(figsize=(9, 5))
  for mode, rs in modes.items():
    fracs = sorted({f for r in rs for f in r['occupancy']}, key=float)
    for f in fracs:
      xs = [r['hosts'] for r in rs if f in r['occupancy']]
      ys = [r['occupancy'][f]['total_rules'] for r in rs if f in r['occupancy']]
      if mode == 'proactive' and f != fracs[-1]:
        continue   # proactive tables do not depend on traffic; plot once
      label = 'Proactive (any traffic)' if mode == 'proactive' else \
              'Reactive (%d%% of pairs active)' % (float(f) * 100)
      ax.plot(xs, ys, marker='s' if mode == 'proactive' else 'o', color=COLORS[mode], label=label,
              linestyle='--' if mode == 'proactive' else '-', markersize=9 if mode == 'proactive' else 6,
              markerfacecolor='none' if mode == 'proactive' else None,
              alpha=1.0 if mode == 'proactive' else 0.35 + 0.65 * float(f))
  ax.set_xlabel('Hosts')
  ax.set_ylabel('Flow rules installed (all switches)')
  ax.set_title('Measured flow-table occupancy')
  ax.legend()
  ax.grid(alpha=0.3)
  path = os.path.join(out_dir, 'measured_flow_table.png')
  fig.tight_layout()
  fig.savefig(path, dpi=150)
  return path


def plot_churn(modes, out_dir):
  fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5))
  for mode, rs in modes.items():
    for r in rs:
      rates = [c['rate_flows_per_s'] for c in r['churn']]
      style = dict(marker='o', color=COLORS[mode], alpha=0.4 + 0.6 * r['hosts'] / 16,
                   label='%s, %d hosts' % (mode.capitalize(), r['hosts']))
      a1.plot(rates, [c['packet_in_per_s'] for c in r['churn']], **style)
      a2.plot(rates, [c['controller_cpu_pct'] for c in r['churn']], **style)
  a1.set_xlabel('New flows per second')
  a1.set_ylabel('PACKET_IN messages per second')
  a1.set_title('Controller signalling vs churn')
  a2.set_xlabel('New flows per second')
  a2.set_ylabel('POX process CPU (%)')
  a2.set_title('Controller CPU vs churn')
  for a in (a1, a2):
    a.grid(alpha=0.3)
    a.legend(fontsize=8)
  path = os.path.join(out_dir, 'measured_churn.png')
  fig.tight_layout()
  fig.savefig(path, dpi=150)
  return path


def main():
  if len(sys.argv) != 2:
    sys.exit(__doc__)
  out_dir = sys.argv[1]
  with open(os.path.join(out_dir, 'results.json')) as f:
    results = json.load(f)['results']
  if not results:
    sys.exit("No results to plot")
  modes = by_mode(results)
  for path in (plot_latency(modes, out_dir), plot_occupancy(modes, out_dir), plot_churn(modes, out_dir)):
    print('[+] Saved %s' % path)


if __name__ == '__main__':
  main()
