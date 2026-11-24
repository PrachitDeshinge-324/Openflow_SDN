#!/bin/bash
# SmartTime batch: a published adaptive-timeout method (Vishnoi et al., DEBS 2014) against
# reactive pair / destination rules, on the same seeds. See docs/SmartTime_Port.md.
#
#   A. No table cap, 3 scenarios x 5 seeds:
#      reactive-pair reactive-dst smarttime-exact smarttime-pair proactive(-ecmp)        ~1-1.5 h
#   B. Capped tables (Open vSwitch flow_limit, overflow_policy=refuse; SmartTime evicts a random
#      rule above 95%), university tree and fat-tree, caps 20 / 12 / 6 rules per switch
#      (above, below and well below one rule per destination: 16 hosts), 3 seeds:
#      reactive-pair reactive-dst smarttime-pair smarttime-dst                          ~1 h
#
# Run from the repo root, inside tmux:   sudo bash experiments/smarttime_batch.sh
# Power mode: Best performance; sleep off. Safe to re-run: finished folders are skipped.
#   PART=A or PART=B runs only that part (e.g. if time runs out:  sudo PART=A bash ...)
# Results: results/measured/smarttime-<date>/A-*, B-cap*-*. Summary: see the end of this file.
set -u
cd "$(dirname "$0")/.."
OUT="results/measured/smarttime-${TAG:-$(date +%Y%m%d)}"
mkdir -p "$OUT"
LOG="$OUT/batch.log"
PART="${PART:-AB}"
RUN="python3 experiments/run_traffic_experiments.py --pair-zipf 1"

say() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"; }
complete() {   # complete <folder>: traffic.json holds one result for every mode asked for
  python3 - "$1/traffic.json" <<'PY' 2>/dev/null
import json, sys
d = json.load(open(sys.argv[1]))
a = d['meta']['args']
sys.exit(0 if d['results'] and len(d['results']) == len(a['modes']) * a['repeats']
         and all(r.get('fct') for r in d['results']) else 1)
PY
}
run() {   # run <folder> <args...>: skip if already complete
  local out="$OUT/$1"; shift
  if complete "$out"; then say "skip $out (done)"; return 0; fi
  if [ -e "$out" ]; then mv "$out" "$out.incomplete-$(date +%H%M%S)"; say "moved aside an incomplete $out"; fi
  say "run  $out: $*"
  if ! $RUN --out "$out" "$@" >> "$LOG" 2>&1; then
    say "FAILED $out (see $LOG); continuing"
    mv "$out" "$out.failed-$(date +%H%M%S)" 2>/dev/null
  fi
}

# --- self-checks: stop before spending hours on a broken setup
say "self-checks"
python3 experiments/test_smarttime_offline.py >> "$LOG" 2>&1 || { say "test_smarttime_offline FAILED: stop"; exit 1; }
{ echo "git $(git -c safe.directory='*' rev-parse HEAD) dirty=$(git -c safe.directory='*' status --porcelain --untracked-files=no | wc -l)";
  uname -a; grep -m1 'model name' /proc/cpuinfo; nproc; ovs-vsctl --version | head -1; } > "$OUT/machine.txt"
mn -c > /dev/null 2>&1
if [[ "$PART" == *B* ]]; then
  # The cap must really be enforced by Open vSwitch: refusals seen, no switch above the cap
  rm -rf "$OUT/check-cap"
  $RUN --quick --table-cap 6 --modes reactive-pair smarttime-pair --out "$OUT/check-cap" >> "$LOG" 2>&1
  python3 - "$OUT/check-cap/traffic.json" <<'PY' >> "$LOG" 2>&1 || { say "table-cap self-check FAILED (see $LOG): stop"; exit 1; }
import json, sys
rs = {r['mode']: r for r in json.load(open(sys.argv[1]))['results']}
fixed, st = rs['reactive-pair'], rs['smarttime-pair']
print('check-cap:', {m: (r['table'], r['control']['peak_rules_one_switch']) for m, r in rs.items()})
assert fixed['table']['refused_installs'] > 0, 'no install was refused: the cap is not enforced'
assert st['table']['evictions'] > 0, 'SmartTime never evicted'
assert all(r['control']['peak_rules_one_switch'] <= 6 for r in rs.values()), 'a switch went above the cap'
PY
  say "table-cap self-check passed"
fi

# --- A: no cap
if [[ "$PART" == *A* ]]; then
  M="reactive-pair reactive-dst smarttime-exact smarttime-pair"
  run A-tree    --repeats 5 --scenarios tree-d2-f4:university --modes $M proactive
  run A-fattree --repeats 5 --scenarios fattree-k4:websearch  --modes $M proactive-ecmp
  run A-abilene --repeats 5 --scenarios abilene:isp           --modes $M proactive
fi

# --- B: capped tables
if [[ "$PART" == *B* ]]; then
  M="reactive-pair reactive-dst smarttime-pair smarttime-dst"
  for cap in 20 12 6; do
    run B-cap$cap-tree    --repeats 3 --table-cap $cap --scenarios tree-d2-f4:university --modes $M
    run B-cap$cap-fattree --repeats 3 --table-cap $cap --scenarios fattree-k4:websearch  --modes $M
  done
fi
uid=${SUDO_UID:-}; gid=${SUDO_GID:-}
[ -n "$uid" ] && chown -R "$uid:$gid" "$OUT"
say "done: $OUT"

# Summary for the paper (paired, seed by seed):
#   python3 experiments/paired_stats.py results/measured/smarttime-*/A-* \
#       --pairs smarttime-pair:reactive-dst smarttime-pair:reactive-pair smarttime-exact:reactive-dst \
#       --metrics hit_rate small_p50 packet_in peak_rules
#   python3 experiments/paired_stats.py results/measured/smarttime-*/B-* \
#       --pairs smarttime-pair:reactive-dst smarttime-pair:reactive-pair smarttime-dst:reactive-dst \
#       --metrics hit_rate small_p50 packet_in refused evictions st_cost full_pct
