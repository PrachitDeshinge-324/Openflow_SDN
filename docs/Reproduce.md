# Reproducing the paper (`paper/paper.tex`)

Every number in the paper comes from a result folder in `results/measured/` or from a script that
reads those folders. This file says, for each table and figure: the command, the folders, and the
machine. Commands run from the repository root; testbed commands need root (Mininet).

Setup first: `bash setup.sh`, then `python3 smoke_test.py` (see `INSTALL.md`).

## Machines

| Name | What it is | Used for |
|---|---|---|
| **Harikrushna** | Laptop, Windows 11 + WSL2 (Ubuntu), x86_64, 16 hardware threads, Open vSwitch 3.7.1 (kernel datapath), Python 3.14.4, POX 0.7.0. Windows power mode "Best performance", sleep off. WSL2 kernel 6.18.33.2 for the October batches, **6.18.58.1** for the November batches | Every testbed table and number in the paper |
| **prachit (VM)** | Ubuntu VM (kernel 7.3) on an Apple-silicon Mac, aarch64, 4 virtual CPUs, Open vSwitch 4.0.0, Python 3.14.8 | LSTM batch only (branch `lstm-baseline`); replay model and statistics (no timing) |

The CPU of Harikrushna is an AMD Ryzen 7 8840HS (16 threads), recorded by the 21 Nov batch; the October and 19 Nov batches did not record it. Batches started
from 20 Nov 2026 on record it, with the git commit of the code, in `traffic.json` (`meta.cpu_model`,
`meta.git_commit`, `meta.git_dirty`) and in the `CPU:` line of `traffic.md`.

**Absolute times are compared only within one batch.** The same controller gives different times in
different batches (proactive on the campus tree: 1.49 ms in Table II, 0.94 ms in Table III; the
WSL2 kernel was updated between the two). Hit rates, rule counts and PACKET_IN counts do not depend
on timing to the same degree; the replay model reproduces measured hit rates within 0.1 points.

## Testbed tables

All use 30 s of arrivals, load 30% (5% at k=6), Zipf 1 pair popularity, seeds 7-11 (7-9 at k=6),
every controller for every seed in one batch.

| Paper | Folder(s) | Command | Machine |
|---|---|---|---|
| Table II (granularity), campus tree | `traffic-20261020-171718` | `sudo python3 experiments/run_traffic_experiments.py --scenarios tree-d2-f4:university --budget-sweep --budgets 10 25 50 --random-baseline --granularity-baselines --pair-zipf 1 --repeats 5` | Harikrushna (Oct) |
| Table II, fat-tree k=4 | `traffic-20261020-183215` | same, `--scenarios fattree-k4:websearch`. Exact-match reactive rows disturbed by the laptop sleeping; not used | Harikrushna (Oct) |
| Table II, Abilene | `traffic-20261021-050401` | same, `--scenarios abilene:isp` | Harikrushna (Oct) |
| §IV-B "skew is not required" (uniform pairs) | `traffic-20261021-060910` | as campus tree, without `--pair-zipf` | Harikrushna (Oct) |
| §V, 54 hosts (counter, oracle, coarse rules) | `traffic-20261023-070549` | `sudo python3 experiments/run_traffic_experiments.py --scenarios fattree-k6:websearch --load 0.05 --budget-sweep --budgets 2 5 10 --granularity-baselines --pair-zipf 1 --repeats 3` | Harikrushna (Oct) |
| Table III (tap), campus tree | `traffic-20261119-114525` | `sudo python3 experiments/run_traffic_experiments.py --scenarios tree-d2-f4:university --modes reactive-sp reactive-pair reactive-dst proactive tap --pair-zipf 1 --repeats 5` | Harikrushna (Nov) |
| Table III, fat-tree k=4 | `traffic-20261119-120616` | same, `--scenarios fattree-k4:websearch`, `proactive-ecmp` instead of `proactive` | Harikrushna (Nov) |
| Table III, Abilene | `traffic-20261119-123520` | same as campus tree, `--scenarios abilene:isp` | Harikrushna (Nov) |
| Table III, fat-tree k=6 | `traffic-20261119-125611` | `... --scenarios fattree-k6:websearch --load 0.05 --modes reactive-sp reactive-pair reactive-dst proactive-ecmp tap --pair-zipf 1 --repeats 3` | Harikrushna (Nov) |
| §VI frozen controller | `traffic-20261119-175235` | `sudo python3 experiments/run_traffic_experiments.py --scenarios tree-d2-f4:university --modes reactive-sp reactive-dst proactive tap --pause-controller 10:5 --pair-zipf 1 --repeats 3` | Harikrushna (Nov) |
| §VI second tap batch (proactive-dst; k=4 explanation, cost of the copies, Table IV last rows) | `traffic-20261121-073853` (tree), `-075657` (k=4), `-082609` (Abilene), `-084548` (k=6) | `sudo bash experiments/paper_batch.sh` | Harikrushna (Nov; AMD Ryzen 7 8840HS, 16 threads, code commit 369b32d2, recorded in each folder) |

Visibility ("heard") for tap: `python3 experiments/tap_check.py <folder>`.
Table III summary rows: `python3 experiments/tap_summary.py <folders>`.

## Analysis (no testbed, any machine)

| Paper | Command | Output |
|---|---|---|
| Table IV (paired differences) and every "paired difference" in the text | `python3 experiments/paired_stats.py --paper` | printed table; method in the script's docstring |
| §V replay model validation (46 runs, error at most 0.1 points) | `python3 experiments/model_validate.py` | printed per folder |
| Fig. 1 and §V scale sweep (k = 4 to 16; Fig. 2 in `paper/sigcomm/`) | `python3 experiments/scale_sim.py`, then `python3 docs/figures/make_scale_figure.py` | `docs/figures/scale_sim.json`, `scale_hit_rate.pdf` (also copied to `paper/` and `paper/sigcomm/`) |
| §IV-B "Prediction on top of pair rules" (bound for fixed sets on a pair-rule fallback) | `python3 experiments/pair_fallback_replay.py` | printed table (replay of the stored schedules of the measured reactive-pair runs) |
| §V "Skew matters as much as scale" (Zipf 0, 0.5, 1.5) | `for z in 0 0.5 1.5; do python3 experiments/scale_sim.py --zipf $z --out docs/figures/scale_sim_zipf$z.json; done` | `docs/figures/scale_sim_zipf{0,0.5,1.5}.json` (Zipf 1 is `scale_sim.json`) |
| §IV-A long timeouts vs plain reactive (paired PACKET_IN/s and small-flow median) | `python3 experiments/paired_stats.py --paper` (rows `reactive-long` - `reactive`, T6 folders `traffic-20261015-225412`, `-233914`, `traffic-20261016-004215`, `-012626`) | printed table |
| Tap visibility in the frozen-controller runs | `python3 experiments/tap_check.py results/measured/traffic-20261119-175235 6` (a window longer than the 5 s pause; with the default 1 s window the copies read after the pause count as missed) | printed per run: 18,269 of 18,269 |
| §VII (limitations) run-length check (120 s of arrivals) | `python3 experiments/scale_sim.py --ks 4 6 8 --duration 120 --out docs/figures/scale_sim_duration120.json` | `docs/figures/scale_sim_duration120.json` (compare with the k = 4-8 rows of `scale_sim.json`) |

The replay and statistics scripts are deterministic: re-running them gives the committed outputs
exactly (checked 20 Nov 2026).

## LSTM predictor (§IV-B "A learned predictor")

| Paper | Folder(s) | Command | Machine |
|---|---|---|---|
| LSTM vs counter, campus tree, 25% | `traffic-20261022-101219` (5 seeds); re-check `traffic-20261120-151236` (seed 7) | `sudo python3 experiments/run_traffic_experiments.py --scenarios tree-d2-f4:university --modes hybrid-25 lstm-25 --duration 60 --pair-zipf 1 --repeats 5 --lstm-model results/lstm_datacenter.npz` | prachit (VM) |
| Model | `results/lstm_datacenter.npz` | `python3 experiments/train_lstm.py --workloads university websearch datamining --out results/lstm_datacenter.npz` (seeds 101-110 by default) | any |
| Paired numbers | | `python3 experiments/paired_stats.py results/measured/traffic-20261022-101219 --pairs lstm-25:hybrid-25 --metrics hit_rate` | any |

Only hit rate and installs are reported for this batch (see `results/measured/INDEX.md`).

## Distant controller and run length (`paper/sigcomm/paper.tex` only: §4.2 "Longer runs", §4.3, Table 3, Fig. 1)

One overnight batch, 24 Nov 2026, folder `results/measured/night-20261124/` (machine and code in its
`machine.txt`: Harikrushna, WSL2 kernel 6.18.58.1, AMD Ryzen 7 8840HS, code commit 2d767423, clean).

| Paper | Folder(s) | Command | Machine |
|---|---|---|---|
| §4.3 control-channel delay, Table 3 | `night-20261124/ctrl-d<D>-s<S>/` (D = 0, 1, 5, 20, 50 ms one way; seeds 7-9) | `sudo bash experiments/overnight_batch.sh A` (university tree, reactive-sp / reactive-dst / proactive / tap, delays interleaved per seed) | Harikrushna (Nov) |
| Fig. 1 (`paper/sigcomm/ctrl_delay.pdf`) | same | `python3 experiments/night_summary.py results/measured/night-20261124` writes `night-20261124/ctrl_delay.pdf`; copied unchanged to `paper/sigcomm/` | any (needs matplotlib) |
| §4.2 "Longer runs" (30 s vs 120 s) | `night-20261124/len<L>-s<S>/` (L = 30, 120; seeds 7-9) | `sudo bash experiments/overnight_batch.sh B` (reactive-pair / reactive-dst / hybrid-25 / oracle-25) | Harikrushna (Nov) |
| Medians, paired increases, hit rates, model error | | `python3 experiments/night_summary.py results/measured/night-20261124 --no-plot` | any |
| "30.4 points below pair rules at 120 s" | | `paired_stats.paired()` on the rows of `len120-s7/8/9` pooled (pairs `reactive-pair:hybrid-25`); `paired_stats.py` itself pairs within one folder | any |
| Destination rules' tail at 50 ms (small-flow mean, p99), PACKET_INs per flow of reactive-sp | | per-seed differences from `ctrl-d<D>-s<S>/traffic.json` (`fct.small.mean_ms`, `fct.small.p99_ms`) and `*-reactive-sp-stats.json` (`totals.packet_in` / flows), same t interval as `night_summary.py` | any |

Before trusting a delay run: `sudo python3 experiments/test_ctrl_delay.py` (the batch runs it first and stops if it fails;
its output is at the top of `night-20261124/batch.log`).

## Not in the paper

- T9 (controller on a second PC): not run; see the paper's limitations.
