"""
Realistic traffic workloads, each taken from a published measurement
CS G525 Advanced Computer Networks - Project SA7

Every workload = a flow-size distribution + a flow-arrival process.
Sources are listed in docs/Realism_Sources.md.

  university  Benson et al., IMC 2010 ("Network Traffic Characteristics of
              Data Centers in the Wild"), university data centres:
              - flow sizes: read off Fig. 4(a), curves EDU1/EDU3 (80% of
                flows < 10 KB; most bytes in the largest 10%)
              - arrivals, per edge switch: 80% of gaps between new flows are
                4-40 ms (Sec. 5); Table 4 fits a Weibull to the university
                arrival process, so we use a Weibull with 10th/90th
                percentiles at 4 ms and 40 ms (shape 1.34, scale 21.5 ms)
  websearch   DCTCP (Alizadeh et al., SIGCOMM 2010) production search
              cluster, as the "web search" workload of pFabric (SIGCOMM
              2013). CDF file CDF_dctcp.tcl from the PIAS simulator
              (github.com/HKUST-SING/PIAS-NS2), in 1460-byte packets.
              Poisson arrivals, random source/destination (as in pFabric).
  datamining  VL2 (Greenberg et al., SIGCOMM 2009) data-mining cluster, as
              the "data mining" workload of pFabric. CDF file CDF_vl2.tcl
              from the same repository. Poisson arrivals.

For websearch/datamining the arrival rate is set by the offered load:
  flows/s = load x (hosts x link speed) / mean flow size
Flows larger than max_bytes are capped so that a run on 10 Mbit/s links
finishes in minutes (3% of websearch flows and 5% of datamining flows are
above 10 MB). The number of flows of each size, which is what the controller
sees, is unchanged below the cap.
"""

import bisect
import math
import random

MSS = 1460   # bytes per packet in the PIAS/pFabric CDF files

# (size, cumulative probability); sizes in packets of MSS bytes
WEBSEARCH_PKTS = [(6, 0.0), (6, 0.15), (13, 0.2), (19, 0.3), (33, 0.4), (53, 0.53), (133, 0.6),
                  (667, 0.7), (1333, 0.8), (3333, 0.9), (6667, 0.97), (20000, 1.0)]
DATAMINING_PKTS = [(1, 0.0), (1, 0.5), (2, 0.6), (3, 0.7), (7, 0.8), (267, 0.9), (2107, 0.95),
                   (66667, 0.99), (666667, 1.0)]
# Benson Fig. 4(a), university curves (EDU1/EDU3), read by eye; sizes in bytes,
# log-scale x axis, so we interpolate in log(size)
UNIVERSITY_BYTES = [(60, 0.0), (100, 0.05), (300, 0.25), (500, 0.35), (1000, 0.47), (2000, 0.62),
                    (4000, 0.75), (10000, 0.87), (30000, 0.92), (100000, 0.96), (1000000, 0.99),
                    (10000000, 1.0)]

UNIV_GAP_WEIBULL = (1.34, 0.0215)   # shape, scale (s): P10 = 4 ms, P90 = 40 ms


class EmpiricalCDF(object):
  """Inverse-CDF sampling with linear (or log-linear) interpolation, like ns-2."""

  def __init__(self, points, unit=1, log=False):
    self.x = [p[0] * unit for p in points]
    self.p = [p[1] for p in points]
    self.log = log

  def sample(self, rng):
    u = rng.random()
    i = bisect.bisect_left(self.p, u)
    i = min(max(i, 1), len(self.p) - 1)
    p0, p1, x0, x1 = self.p[i - 1], self.p[i], self.x[i - 1], self.x[i]
    f = 0.0 if p1 == p0 else (u - p0) / (p1 - p0)
    if self.log:
      return math.exp(math.log(x0) + f * (math.log(x1) - math.log(x0)))
    return x0 + f * (x1 - x0)

  def mean(self, cap=None, steps=400):
    m = 0.0
    for i in range(1, len(self.p)):
      w = self.p[i] - self.p[i - 1]
      for k in range(steps):
        f = (k + 0.5) / steps
        if self.log:
          x = math.exp(math.log(self.x[i - 1]) + f * (math.log(self.x[i]) - math.log(self.x[i - 1])))
        else:
          x = self.x[i - 1] + f * (self.x[i] - self.x[i - 1])
        m += w / steps * (min(x, cap) if cap else x)
    return m


WORKLOADS = {
  'university': {'sizes': EmpiricalCDF(UNIVERSITY_BYTES, log=True), 'arrivals': 'benson-edge',
                 'source': 'Benson et al., IMC 2010 (university data centres)'},
  'websearch': {'sizes': EmpiricalCDF(WEBSEARCH_PKTS, unit=MSS), 'arrivals': 'poisson',
                'source': 'DCTCP, SIGCOMM 2010 / pFabric web search workload'},
  'datamining': {'sizes': EmpiricalCDF(DATAMINING_PKTS, unit=MSS), 'arrivals': 'poisson',
                 'source': 'VL2, SIGCOMM 2009 / pFabric data mining workload'},
}


def make_schedule(workload, hosts, edge_of, duration, load, bw_mbps, max_bytes, seed):
  """
  hosts:   list of host names
  edge_of: {host: name of its edge switch}
  Returns (flows, info): flows = [(start_s, src, dst, size_bytes)], sorted by start.
  The same seed gives the same flows for every controller.
  """
  wl = WORKLOADS[workload]
  rng = random.Random(seed)
  flows = []

  def flow(t, src):
    dst = rng.choice([h for h in hosts if h != src])   # uniform destination, as in pFabric
    size = max(1, int(min(wl['sizes'].sample(rng), max_bytes)))
    flows.append((t, src, dst, size))

  mean_size = wl['sizes'].mean(cap=max_bytes)
  if wl['arrivals'] == 'benson-edge':
    # One arrival process per edge switch (Benson measured at edge switches);
    # each new flow starts at a random host under that switch
    shape, scale = UNIV_GAP_WEIBULL
    edges = sorted(set(edge_of.values()))
    for e in edges:
      under = [h for h in hosts if edge_of[h] == e]
      t = rng.weibullvariate(scale, shape)
      while t < duration:
        flow(t, rng.choice(under))
        t += rng.weibullvariate(scale, shape)
    rate = len(flows) / duration
  else:
    rate = load * len(hosts) * bw_mbps * 1e6 / 8 / mean_size   # flows per second, whole network
    t = rng.expovariate(rate)
    while t < duration:
      flow(t, rng.choice(hosts))
      t += rng.expovariate(rate)
  flows.sort()
  offered = sum(f[3] for f in flows) * 8 / duration / 1e6
  info = {'workload': workload, 'source': wl['source'], 'flows': len(flows),
          'flows_per_s': len(flows) / duration, 'target_rate': rate,
          'mean_size_bytes': mean_size, 'max_bytes': max_bytes,
          'offered_mbps': offered, 'offered_load': offered / (len(hosts) * bw_mbps),
          'capped_flows': sum(1 for f in flows if f[3] >= max_bytes),
          'off_rack_pct': 100.0 * sum(1 for f in flows if edge_of[f[1]] != edge_of[f[2]]) / max(1, len(flows))}
  return flows, info
