#!/usr/bin/env python3
"""
Real Abilene traffic matrices -> hourly city-to-city traffic for one day
CS G525 Advanced Computer Networks - Project SA7

Source: the public Abilene traffic matrices of Y. Zhang et al. (Network
Anomography, IMC 2005), https://www.cs.utexas.edu/~yzhang/research/AbileneTM/
Format (data/abilene/readme-AbileneTM.txt): each X*.gz file is one week of
2016 five-minute matrices; each line has 144 x 5 values, five per
(source, destination) router pair, the first being the real measured value,
in units of 100 bytes per 5 minutes (NetFlow sampled 1 in 100). The 12
routers are in the order of data/abilene/topo-2003-04-10.txt.

What this script does:
  - keeps the real values only (not the 4 estimates)
  - merges the two Atlanta routers (ATLA-M5 carries under 1% of the traffic)
  - drops traffic that enters and leaves at the same city (it never crosses
    the backbone)
  - averages the 12 matrices of each hour -> 24 hourly matrices in Mbit/s

Usage:
  python3 experiments/abilene_tm.py X01.gz            # day 1 of the week (2004-03-01)
  python3 experiments/abilene_tm.py X01.gz --day 2    # day 3
Writes data/abilene/tm-<date>.json (used by the 'isp' workload).
"""

import argparse
import datetime
import gzip
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Router order of the dataset (topo-2003-04-10.txt) and the city each one is in,
# named as in experiments/path_topologies.py
ROUTERS = ['ATLA-M5', 'ATLAng', 'CHINng', 'DNVRng', 'HSTNng', 'IPLSng', 'KSCYng',
           'LOSAng', 'NYCMng', 'SNVAng', 'STTLng', 'WASHng']
CITY = {'ATLA-M5': 'Atlanta', 'ATLAng': 'Atlanta', 'CHINng': 'Chicago', 'DNVRng': 'Denver',
        'HSTNng': 'Houston', 'IPLSng': 'Indianapolis', 'KSCYng': 'Kansas City',
        'LOSAng': 'Los Angeles', 'NYCMng': 'New York', 'SNVAng': 'Sunnyvale',
        'STTLng': 'Seattle', 'WASHng': 'Washington DC'}
WEEK_START = {'X01': '2004-03-01', 'X02': '2004-03-08', 'X03': '2004-04-02', 'X04': '2004-04-09',
              'X05': '2004-04-22', 'X06': '2004-05-01', 'X07': '2004-05-08', 'X08': '2004-05-15',
              'X09': '2004-05-22', 'X10': '2004-05-29', 'X11': '2004-06-05', 'X12': '2004-06-12',
              'X13': '2004-06-19', 'X14': '2004-06-26', 'X15': '2004-07-03', 'X16': '2004-07-10',
              'X17': '2004-07-17', 'X18': '2004-07-24', 'X19': '2004-07-31', 'X20': '2004-08-07',
              'X21': '2004-08-13', 'X22': '2004-08-21', 'X23': '2004-08-28', 'X24': '2004-09-04'}
UNIT_BITS_PER_S = 100 * 8 / 300.0   # one unit = 100 bytes per 5 minutes
BACKBONE_BPS = 9.92e9               # OC-192 links (topo-2003-04-10.txt); IPLS-ATLA is 2.48e9


def hourly_matrices(xfile, day):
  with gzip.open(xfile, 'rt') as f:
    lines = [l for l in f if l.strip()]
  per_day = 12 * 24
  if len(lines) < (day + 1) * per_day:
    raise SystemExit("%s has only %d matrices" % (xfile, len(lines)))
  hours = []
  for h in range(24):
    acc = {}
    for line in lines[day * per_day + h * 12: day * per_day + (h + 1) * 12]:
      v = line.split()
      for k in range(144):
        src, dst = CITY[ROUTERS[k // 12]], CITY[ROUTERS[k % 12]]
        if src == dst:
          continue   # enters and leaves at the same city: never crosses the backbone
        acc[(src, dst)] = acc.get((src, dst), 0.0) + float(v[5 * k])   # real value only
    hours.append({'%s>%s' % p: x / 12 * UNIT_BITS_PER_S / 1e6 for p, x in acc.items()})  # Mbit/s
  return hours


def main():
  ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  ap.add_argument('xfile', help='X01.gz ... X24.gz from the AbileneTM dataset')
  ap.add_argument('--day', type=int, default=0, help='day of the week in the file, 0-6')
  ap.add_argument('--out', default=None)
  args = ap.parse_args()

  week = os.path.basename(args.xfile).split('.')[0]
  start = WEEK_START.get(week)
  date = ((datetime.date.fromisoformat(start) + datetime.timedelta(days=args.day)).isoformat()
          if start else '%s-day%d' % (week, args.day))
  hours = hourly_matrices(args.xfile, args.day)
  totals = [sum(h.values()) for h in hours]
  out = args.out or os.path.join(REPO, 'data', 'abilene', 'tm-%s.json' % date)
  os.makedirs(os.path.dirname(out), exist_ok=True)
  with open(out, 'w') as f:
    json.dump({'source': 'Abilene traffic matrices, Zhang et al. IMC 2005 (AbileneTM %s, day %d)'
                         % (week, args.day),
               'date': date, 'unit': 'Mbit/s, hourly mean of the real measured values',
               'backbone_link_bps': BACKBONE_BPS,
               'hourly_total_mbps': totals, 'hours': hours}, f, indent=1)
  print('Wrote %s: %s, total %.0f-%.0f Mbit/s over the day (mean %.0f), %d city pairs'
        % (out, date, min(totals), max(totals), sum(totals) / 24, len(hours[0])))


if __name__ == '__main__':
  main()
