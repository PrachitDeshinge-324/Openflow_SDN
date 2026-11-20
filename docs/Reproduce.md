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

The CPU model of Harikrushna was not recorded by the October and November batches. Batches started
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
| §VI k=4 fat-tree: proactive-dst (**pending**) | (to be added) | `sudo bash experiments/paper_batch.sh` (four networks: reactive-dst, proactive or proactive-ecmp, proactive-dst, tap) | Harikrushna |

Visibility ("heard") for tap: `python3 experiments/tap_check.py <folder>`.
Table III summary rows: `python3 experiments/tap_summary.py <folders>`.

## Analysis (no testbed, any machine)

| Paper | Command | Output |
|---|---|---|
| Table IV (paired differences) and every "paired difference" in the text | `python3 experiments/paired_stats.py --paper` | printed table; method in the script's docstring |
| §V replay model validation (46 runs, error at most 0.1 points) | `python3 experiments/model_validate.py` | printed per folder |
| Fig. 1 and §V scale sweep (k = 4 to 16) | `python3 experiments/scale_sim.py`, then `python3 docs/figures/make_scale_figure.py` | `docs/figures/scale_sim.json`, `scale_hit_rate.pdf` |
| §VII (limitations) run-length check (120 s of arrivals) | `python3 experiments/scale_sim.py --ks 4 6 8 --duration 120 --out docs/figures/scale_sim_duration120.json` | `docs/figures/scale_sim_duration120.json` (compare with the k = 4-8 rows of `scale_sim.json`) |

The replay and statistics scripts are deterministic: re-running them gives the committed outputs
exactly (checked 20 Nov 2026).

## Not in the paper

- LSTM predictor (`lstm-NN` modes): branch `lstm-baseline`, folder `traffic-20261022-101219`, VM; see
  `results/measured/INDEX.md`.
- T9 (controller on a second PC): not run; see the paper's limitations.
