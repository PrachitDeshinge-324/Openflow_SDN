"""
The tap comparison table, straight from the result folders
CS G525 Advanced Computer Networks - Project SA7

  python3 experiments/tap_summary.py results/measured/traffic-A/ [traffic-B/ ...]

For every scenario and controller in the folders: small-flow median and mean FCT
(mean of the runs, with the 95% interval), failed flows, PACKET_IN/s, controller
CPU, peak rules (total and busiest switch), and the share of new connections the
controller heard of:
  tap                       flows_seen / flows (from the SYN copies)
  reactive on shortest paths 100% (every connection asks it)
  reactive pair / dst rules  100 - hit rate (it only hears of connections that miss)
  proactive                  0%
"""

import json
import math
import os
import statistics
import sys

T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262}
ORDER = ['reactive', 'reactive-sp', 'reactive-pair', 'reactive-dst', 'proactive', 'proactive-ecmp', 'proactive-dst', 'tap']


def mean_ci(xs):
  xs = [x for x in xs if x is not None]
  if not xs:
    return None, None
  if len(xs) == 1:
    return xs[0], 0.0
  return statistics.mean(xs), T95.get(len(xs) - 1, 1.96) * statistics.stdev(xs) / math.sqrt(len(xs))


def heard(r):
  if r['mode'] == 'tap':
    return (r.get('tap') or {}).get('seen_pct')
  if r['mode'].startswith('proactive'):
    return 0.0
  if r['mode'] in ('reactive', 'reactive-sp', 'reactive-long'):
    return 100.0
  h = r.get('hybrid')
  return 100.0 - h['hit_rate_pct'] if h else None


def main(folders):
  rows = []
  for d in folders:
    with open(os.path.join(d, 'traffic.json')) as f:
      for r in json.load(f)['results']:
        r['_folder'] = os.path.basename(os.path.normpath(d))
        rows.append(r)
  for sc in sorted({(r['network'], r['workload']) for r in rows}):
    rs = [r for r in rows if (r['network'], r['workload']) == sc]
    print('\n### %s, %s (%s)\n' % (sc[0], sc[1], ', '.join(sorted({r['_folder'] for r in rs}))))
    print('| Controller | Runs | Small-flow median (ms) | Small-flow mean (ms) | Failed flows | PACKET_IN/s '
          '| Controller CPU % | Peak rules (busiest switch) | Connections the controller heard of % |')
    print('| --- | --- | --- | --- | --- | --- | --- | --- | --- |')
    modes = sorted({r['mode'] for r in rs}, key=lambda m: (ORDER.index(m) if m in ORDER else 99, m))
    for m in modes:
      mr = [r for r in rs if r['mode'] == m]
      f = lambda xs: '%.1f ± %.1f' % mean_ci(xs) if mean_ci(xs)[0] is not None else '-'
      med = f([r['fct']['small'].get('p50_ms') for r in mr])
      mean = f([r['fct']['small'].get('mean_ms') for r in mr])
      failed = sum(r['fct']['failed'] for r in mr)
      pin = statistics.mean(r['control']['packet_in_per_s'] for r in mr)
      cpu = statistics.mean(r['control']['controller_cpu_pct'] for r in mr)
      rules = max(r['control']['peak_rules_total'] for r in mr)
      one = max(r['control']['peak_rules_one_switch'] for r in mr)
      hv = [heard(r) for r in mr]
      hv = [x for x in hv if x is not None]
      print('| %s | %d | %s | %s | %d | %.0f | %.1f | %d (%d) | %s |'
            % (m, len(mr), med, mean, failed, pin, cpu, rules, one,
               '%.1f' % statistics.mean(hv) if hv else '-'))


if __name__ == '__main__':
  if len(sys.argv) < 2:
    sys.exit(__doc__)
  main(sys.argv[1:])
