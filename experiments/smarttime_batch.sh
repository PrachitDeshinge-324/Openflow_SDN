#!/bin/bash
# SmartTime batch: a published adaptive-timeout method (Vishnoi et al., DEBS 2014) against
# reactive pair / destination rules, on the same seeds. See docs/SmartTime_Baseline.md.
#
#   smarttime-exact : SmartTime-style timeout on exact-match rules, as in the paper
#   smarttime-pair  : the same on pair rules (the fair comparison with reactive-pair / -dst)
#
# Run from the repo root, inside tmux:   sudo bash experiments/smarttime_batch.sh
# About 1-1.5 hours (5 modes x 5 seeds x 3 scenarios). Power mode: Best performance; sleep off.
# Then:  python3 experiments/paired_stats.py $(ls -d results/measured/traffic-* | tail -3) \
#            --pairs smarttime-pair:reactive-dst smarttime-pair:reactive-pair smarttime-exact:reactive-dst \
#            --metrics hit_rate small_p50 packet_in peak_rules
set -u
cd "$(dirname "$0")/.."
python3 experiments/test_smarttime_offline.py > /dev/null || { echo "[!] offline SmartTime check failed"; exit 1; }
RUN="python3 experiments/run_traffic_experiments.py --pair-zipf 1 --repeats 5"
M="reactive-pair reactive-dst smarttime-exact smarttime-pair"

echo "[*] 1/3 university tree";           $RUN --scenarios tree-d2-f4:university --modes $M proactive
echo "[*] 2/3 fat-tree k=4, web search";  $RUN --scenarios fattree-k4:websearch  --modes $M proactive-ecmp
echo "[*] 3/3 Abilene ISP";               $RUN --scenarios abilene:isp           --modes $M proactive
echo "[*] done: results/measured/traffic-* (newest three folders)"
