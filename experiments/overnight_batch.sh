#!/bin/bash
# Overnight batch (22-23 Nov): two experiments that turn stated limitations into measurements.
#
#   A. Control-channel delay sweep (Paper_TODO 1.5; the reproducible stand-in for T9).
#      University tree, Zipf 1, modes reactive-sp reactive-dst proactive tap,
#      one-way OpenFlow delay 0 / 1 / 5 / 20 / 50 ms, seeds 7-9.
#      Question: how much does a distant controller cost each strategy?
#   B. Run length on the testbed (checks the 120 s replay result of the paper's limitations).
#      University tree, Zipf 1, modes reactive-pair reactive-dst hybrid-25 oracle-25,
#      30 s and 120 s of arrivals, seeds 7-9.
#      Question: does the measured hit rate move with run length as the replay model says?
#
# Fair by design: for each seed every delay (A) or length (B) runs in turn, so a slow drift of the
# machine during the night hits all of them equally, and a seed fixes the flows for all of them.
# Restartable: a run whose traffic.json exists is skipped, so after an interruption run it again.
#
# Run from the repo root, on the laptop of the paper's tables (Harikrushna):
#   sudo bash experiments/overnight_batch.sh            # about 3 hours
#   sudo bash experiments/overnight_batch.sh A          # only part A (about 1.5 h)
# Windows: power mode "Best performance", sleep "Never". Do not switch git branches while it runs.
# Then: python3 experiments/night_summary.py results/measured/night-<date>
set -u
cd "$(dirname "$0")/.."
PARTS="${1:-AB}"
NIGHT="results/measured/night-${NIGHT_TAG:-$(date +%Y%m%d)}"
mkdir -p "$NIGHT"
LOG="$NIGHT/batch.log"
SEEDS="7 8 9"
RUN="python3 experiments/run_traffic_experiments.py --scenarios tree-d2-f4:university --pair-zipf 1 --repeats 1"

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
  local out="$NIGHT/$1"; shift
  if complete "$out"; then say "skip $out (done)"; return 0; fi
  if [ -e "$out" ]; then   # an earlier, incomplete attempt: keep it aside, never delete
    mv "$out" "$out.incomplete-$(date +%H%M%S)"; say "moved aside an incomplete $out"
  fi
  say "run  $out: $*"
  if ! $RUN --out "$out" "$@" >> "$LOG" 2>&1; then
    say "FAILED $out (see $LOG); continuing"
    mv "$out" "$out.failed-$(date +%H%M%S)" 2>/dev/null
  fi
}

# --- self-checks: stop before spending the night on a broken setup
say "self-checks"
python3 experiments/test_tap_offline.py > /dev/null 2>&1 || { say "test_tap_offline FAILED: stop"; exit 1; }
python3 experiments/test_ctrl_delay.py >> "$LOG" 2>&1 || { say "test_ctrl_delay FAILED (see $LOG): stop"; exit 1; }
{ echo "git $(git -c safe.directory='*' rev-parse HEAD) dirty=$(git -c safe.directory='*' status --porcelain --untracked-files=no | wc -l)";
  uname -a; grep -m1 'model name' /proc/cpuinfo; nproc; ovs-vsctl --version | head -1; } > "$NIGHT/machine.txt"
mn -c > /dev/null 2>&1
# one real 10 s run through the same --out path style as the night's runs: stop now, not after 3 hours
CHECK="$NIGHT/selfcheck-$(date +%H%M%S)"
say "self-check: 10 s harness run with --ctrl-delay 5 into $CHECK"
if ! python3 experiments/run_traffic_experiments.py --quick --modes reactive-dst tap --ctrl-delay 5 \
     --out "$CHECK" >> "$LOG" 2>&1 || ! complete "$CHECK"; then
  say "harness self-check FAILED (see $LOG and $CHECK/*-pox.log): stop"; exit 1
fi
say "self-check passed"

if [[ "$PARTS" == *A* ]]; then
  say "A. control-channel delay sweep"
  for s in $SEEDS; do
    for d in 0 1 5 20 50; do
      run "ctrl-d$d-s$s" --seed "$s" --ctrl-delay "$d" --modes reactive-sp reactive-dst proactive tap
    done
  done
fi

if [[ "$PARTS" == *B* ]]; then
  say "B. run length 30 s vs 120 s"
  for s in $SEEDS; do
    for len in 30 120; do
      run "len$len-s$s" --seed "$s" --duration "$len" --modes reactive-pair reactive-dst hybrid-25 oracle-25
    done
  done
fi

say "done. Next: python3 experiments/night_summary.py $NIGHT"
