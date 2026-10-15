"""
Repeated runs: mean and 95% confidence interval of every metric
CS G525 Advanced Computer Networks - Project SA7

run_traffic_experiments.py --repeats N runs every (network, workload,
controller) N times, each time with a different seed, i.e. a new flow
schedule drawn from the same workload. aggregate() merges the N results of one
(network, workload, controller) into a single result whose metrics are the
mean of the N runs, with the half-width of the 95% confidence interval in
r['ci'] (Student's t, N - 1 degrees of freedom):

    mean +- t(0.975, N-1) * sd / sqrt(N)

So the interval covers both sources of variation: the random workload and
the noise of the machine (scheduling, controller CPU).
"""

import copy
import math
import statistics

# t(0.975, df) for df = 1..30; above 30 we use 1.96
T975 = [12.706, 4.303, 3.182, 2.776, 2.571, 2.447, 2.365, 2.306, 2.262, 2.228,
        2.201, 2.179, 2.160, 2.145, 2.131, 2.120, 2.110, 2.101, 2.093, 2.086,
        2.080, 2.074, 2.069, 2.064, 2.060, 2.056, 2.052, 2.048, 2.045, 2.042]

# Metrics that get a mean and a confidence interval (path into the result dict)
METRICS = [('fct', 'completed'), ('fct', 'failed'), ('fct', 'flows'),
           ('fct', 'small', 'mean_ms'), ('fct', 'small', 'p50_ms'), ('fct', 'small', 'p99_ms'),
           ('fct', 'medium', 'mean_ms'), ('fct', 'large', 'mean_ms'), ('fct', 'all', 'mean_ms'),
           ('control', 'packet_in_per_s'), ('control', 'flow_mod_per_s'),
           ('control', 'controller_cpu_pct'), ('control', 'peak_rules_total'),
           ('control', 'peak_rules_one_switch'),
           ('hybrid', 'hit_rate_pct'), ('hybrid', 'pair_installs'), ('hybrid', 'wasted_installs'),
           ('hybrid', 'syn_misses'),
           ('schedule', 'flows'), ('schedule', 'flows_per_s'), ('schedule', 'offered_mbps'),
           ('schedule', 'offered_load'), ('schedule', 'capped_flows'), ('schedule', 'off_rack_pct')]


def mean_ci(xs):
  """(mean, half-width of the 95% confidence interval); half-width is None for one value."""
  xs = [x for x in xs if x is not None]
  if not xs:
    return None, None
  m = statistics.mean(xs)
  if len(xs) < 2:
    return m, None
  t = T975[len(xs) - 2] if len(xs) - 1 <= len(T975) else 1.96
  return m, t * statistics.stdev(xs) / math.sqrt(len(xs))


def get(d, path):
  for k in path:
    if not isinstance(d, dict) or k not in d:
      return None
    d = d[k]
  return d


def _set(d, path, value):
  for k in path[:-1]:
    d = d.setdefault(k, {})
  d[path[-1]] = value


def aggregate(results):
  """One merged result per (network, workload, mode), in the order they first appear."""
  groups, order = {}, []
  for r in results:
    key = (r['network'], r['workload'], r['mode'])
    if key not in groups:
      groups[key] = []
      order.append(key)
    groups[key].append(r)
  merged = []
  for key in order:
    runs = groups[key]
    m = copy.deepcopy(runs[0])
    m['repeats'] = len(runs)
    m['seeds'] = [r.get('seed') for r in runs]
    m['ci'], m['values'] = {}, {}
    for path in METRICS:
      xs = [get(r, path) for r in runs]
      if all(x is None for x in xs):
        continue
      mean, half = mean_ci(xs)
      _set(m, path, mean)
      name = '.'.join(path)
      m['values'][name] = xs
      if half is not None:
        m['ci'][name] = half
    m['flows_detail'] = [x for r in runs for x in r.get('flows_detail', [])]   # pooled, for CDFs
    merged.append(m)
  return merged


def fmt(r, path, prec=1):
  """'12.3' for one run, '12.3 ± 0.4' for a merged result with a confidence interval."""
  v = get(r, path)
  if v is None:
    return '-'
  s = '%.*f' % (prec, v)
  half = r.get('ci', {}).get('.'.join(path))
  return s + (' ± %.*f' % (prec, half) if half is not None else '')
