#!/bin/bash
# Night 3: does reactive with wildcard rules (pair / destination) explain the hybrid's gain?
# Every invocation runs ALL controllers of a scenario for each seed (7..11), so the counter,
# oracle, random and the new reactive-pair / reactive-dst runs are interleaved in one batch.
# Run from the repo root:   sudo bash experiments/night3_granularity.sh
# Do not switch git branches while it runs. Power mode: Best performance.
set -u
cd "$(dirname "$0")/.."
RUN="python3 experiments/run_traffic_experiments.py --budget-sweep --random-baseline --granularity-baselines --repeats 5"

echo "[*] 1/4 university, Zipf pairs";   $RUN --scenarios tree-d2-f4:university --pair-zipf 1
echo "[*] 2/4 fat-tree, web search, Zipf pairs"; $RUN --scenarios fattree-k4:websearch --pair-zipf 1
echo "[*] 3/4 Abilene ISP";              $RUN --scenarios abilene:isp --pair-zipf 1
echo "[*] 4/4 university, uniform pairs (control)"; $RUN --scenarios tree-d2-f4:university --pair-zipf 0
echo "[*] done: results/measured/traffic-* (newest four folders)"
