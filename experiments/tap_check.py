"""
Which flows did the tap controller not hear of, and when?
CS G525 Advanced Computer Networks - Project SA7

  python3 experiments/tap_check.py results/measured/traffic-<timestamp>/

For every 'tap' run in the folder, matches the flows the hosts started (the
schedule files) with the SYN copies the controller logged (<tag>-flowlog.jsonl,
'start' records), and prints how many were missed and in which second of the run.
Misses bunched at the very end point to the measurement window; misses spread
over the run point to copies lost on the way to the controller.

  python3 experiments/tap_check.py <folder> [WINDOW_S]

A copy counts for a scheduled flow if it reaches the controller within WINDOW_S seconds
(default 1). With a frozen controller (--pause-controller) the copies queue and are read
when it resumes, up to the pause length late, so use a window longer than the pause
(e.g. 6 for a 5 s pause); with the default, those late copies are reported as missed.
"""

import collections
import glob
import json
import os
import statistics
import sys


def main(folder, window=1.0):
  topo = {}
  for f in glob.glob(os.path.join(folder, '*-topo.json')):
    for h in json.load(open(f))['hosts']:
      topo[h['name']] = h['ip']
  logs = sorted(glob.glob(os.path.join(folder, '*-tap*-flowlog.jsonl')))
  if not logs:
    sys.exit('No tap flow logs in %s' % folder)
  for log in logs:
    tag = os.path.basename(log)[:-len('-flowlog.jsonl')]
    starts = collections.defaultdict(list)   # (src ip, dst ip) -> controller times
    n_old = 0
    for line in open(log):
      r = json.loads(line)
      if r.get('event') == 'start':
        starts[(r['src'], r['dst'])].append(r['at'])
      elif 'event' not in r:
        n_old += 1
    sched = collections.defaultdict(list)    # (src ip, dst ip) -> schedule times (s from run start)
    for f in glob.glob(os.path.join(folder, '%s-sched-h*.txt' % tag)):
      host = f.rsplit('-sched-', 1)[1][:-4]
      for line in open(f):
        p = line.split()
        if p:
          sched[(topo[host], p[1])].append(float(p[0]))
    total = sum(len(v) for v in sched.values())
    if not any(starts.values()):
      print('%s: this log has no start records (%d end records): rerun with the updated tap_eval.py'
            % (tag, n_old))
      continue
    # clock offset between the schedule and the controller: median over pairs of first-flow gaps
    offset = statistics.median(min(starts[k]) - min(v) for k, v in sched.items() if starts.get(k))
    missed = []
    for k, times in sched.items():
      seen = sorted(starts.get(k, []))
      for t in sorted(times):   # greedy: each scheduled flow takes the first copy within the window
        hit = next((i for i, s in enumerate(seen) if -0.2 < s - offset - t < window), None)
        if hit is None:
          missed.append(t)
        else:
          seen.pop(hit)
    dur = max(max(v) for v in sched.values())
    by_s = collections.Counter(int(t) for t in missed)
    print('%s: %d flows started, %d heard of (%.1f%%), %d missed' %
          (tag, total, total - len(missed), 100.0 * (total - len(missed)) / max(1, total), len(missed)))
    print('    missed per second of the run: %s' % ', '.join('%d s: %d' % (s, by_s[s]) for s in range(int(dur) + 1)))
    last = sum(1 for t in missed if t > dur - 1)
    print('    in the last second: %d of %d missed' % (last, len(missed)))


if __name__ == '__main__':
  if len(sys.argv) not in (2, 3):
    sys.exit(__doc__)
  main(sys.argv[1], float(sys.argv[2]) if len(sys.argv) == 3 else 1.0)
