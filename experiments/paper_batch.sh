#!/bin/bash
# Paper batch: the fair baseline for the tap controller.
#
# proactive-dst = tap_eval --taps=off: the same destination rules on the same paths as tap,
# without the SYN/FIN/RST copies. It answers two questions about T13:
#   1. Does tap need fewer rules than proactive because it taps, or only because its
#      forwarding rules are per destination instead of per pair?  (rules: tap - proactive-dst)
#   2. Is tap's slowdown on the k=4 fat-tree caused by per-destination path choice?
#      If proactive-dst is as slow as tap there, yes.
# Proactive (pair rules), tap and reactive-dst run in the same batch, for every seed,
# so all rows compare within one night.
#
# Run from the repo root:   sudo bash experiments/paper_batch.sh
# About 1.5-2 hours. Power mode: Best performance; stop the laptop from sleeping.
# Then:  python3 experiments/tap_summary.py $(ls -d results/measured/traffic-* | tail -4)
set -u
cd "$(dirname "$0")/.."
RUN="python3 experiments/run_traffic_experiments.py --pair-zipf 1"

echo "[*] 1/4 university tree";  $RUN --repeats 5 --scenarios tree-d2-f4:university \
    --modes reactive-dst proactive proactive-dst tap
echo "[*] 2/4 fat-tree k=4, web search"; $RUN --repeats 5 --scenarios fattree-k4:websearch \
    --modes reactive-dst proactive-ecmp proactive-dst tap
echo "[*] 3/4 Abilene ISP"; $RUN --repeats 5 --scenarios abilene:isp \
    --modes reactive-dst proactive proactive-dst tap
echo "[*] 4/4 fat-tree k=6, web search, 5% load"; $RUN --repeats 3 --load 0.05 --scenarios fattree-k6:websearch \
    --modes reactive-dst proactive-ecmp proactive-dst tap
echo "[*] done: results/measured/traffic-* (newest four folders)"
