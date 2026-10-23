# Index of measured results

Every folder in `results/measured/` has a timestamp for a name (`traffic-YYYYMMDD-HHMMSS`).
The documents refer to the folders by those names, so the folders are not renamed.
This file says which folder belongs to which test.

Test numbers (T1–T12) are those of `docs/Test_Catalogue.md`.
"Mode" is the Windows power mode on the laptop: **Balanced** (Review I, Steps 1–2 and the first single runs of Step 4) or **Best performance** (all the repeat runs, from the night of 15 Oct on).
"Runs" is the number of seeds; with 5 runs every value in the document is a mean with a 95% confidence interval.

## T1–T3: first packet, rules, controller load

| Folder | Test | What it holds | Runs | Mode |
|---|---|---|---|---|
| `20260927-152012/` | T1, T2, T3 | Reactive vs proactive on the three small trees (4, 8 and 16 hosts): ping delay, rule counts, churn. Laptop 1 | 1 | Balanced |
| `20261009-112228/` | T10 (and T1–T3 again) | The same experiment repeated on laptop 2 | 1 | Balanced |

## T4: path quality

| Folder | Test | What it holds | Runs | Mode |
|---|---|---|---|---|
| `paths-20261015-094800/` | T4 | Optimal vs haphazard paths on the fat-tree and Abilene: `paths.md`, `paths.json` and plots (`paths_stretch.png`, `paths_link_balance.png`, `paths_throughput.png`) | 1 | Balanced |

## T5, T6: realistic traffic, long timeouts

| Folder | Test | What it holds | Runs | Mode |
|---|---|---|---|---|
| `traffic-20261015-113417/` | T5 (first run) | University and data-centre workloads (web search, data mining), reactive vs proactive. Figures in Review II | 1 (seed 7) | Balanced |
| `traffic-20261015-122618/` | T5 (first run) | ISP workload on Abilene (SURGE sizes, Abilene matrices, netem delays) | 1 (seed 7) | Balanced |
| `traffic-20261017-214330/` | T5, T6, T11 | **The repeats**: all four scenarios, reactive / reactive-sp / reactive-long / proactive, uniform pairs | 5 (seeds 7–11) | Best performance |

## T7, T8: budgeted hybrid

Zipf pairs unless stated. The numbers in the report come from the 5-run folders.

| Folder | Test | What it holds | Runs | Mode |
|---|---|---|---|---|
| `traffic-20261015-204208/` | T7 | University tree, budget sweep, first single run | 1 | Balanced |
| `traffic-20261015-210056/` | T7 | University tree, uniform pairs (control), single run | 1 | Balanced |
| `traffic-20261015-211130/` | T7 | Warm-up check: 120 s instead of 30 s, 10% budget | 1 | Balanced |
| `traffic-20261015-213728/` | T7 | Fat-tree, web search, single run | 1 | Balanced |
| `traffic-20261015-215331/` | T7 | Abilene ISP, single run | 1 | Balanced |
| `traffic-20261015-225412/` | **T7** | **University, Zipf 1: counter, oracle, hybrid at 0 / 10 / 25 / 50%** | 5 | Best performance |
| `traffic-20261015-233914/` | **T7** | **Fat-tree, web search, budget sweep** | 5 | Best performance |
| `traffic-20261016-004215/` | **T7** | **Abilene ISP, budget sweep** | 5 | Best performance |
| `traffic-20261016-012626/` | **T7** | **University, uniform pairs (control)** | 5 | Best performance |
| `traffic-20261016-021112/` | T7 | Decay 0.9 instead of 0.97 (no change inside the intervals) | 1 | Best performance |
| `traffic-20261017-224052/` | **T7** | **Random pre-installation: university and fat-tree** | 5 | Best performance |
| `traffic-20261017-231017/` | **T7** | **Random pre-installation: Abilene** | 5 | Best performance |
| `traffic-20261018-001723/` | T7 | Decay 0.9, 5 runs (no change inside the intervals) | 5 | Best performance |

T8 (ML predictor) was not run; there is no folder for it.

## T11, T12

| Folder | Test | What it holds | Runs | Mode |
|---|---|---|---|---|
| `traffic-20261017-214330/` | **T11** | Path vs setup split: reactive, reactive-sp, proactive (same folder as the T5 repeats) | 5 | Best performance |
| `traffic-20261017-232237/` | **T12** | Fat-tree k = 6 (54 hosts, 2,862 pairs), budgets 0 / 2 / 5 / 10% | 3 (seeds 7–9) | Best performance |

## T9: controller on a second PC

No folder. Not run yet; it needs a second laptop (`docs/Controller_On_Second_PC.md`).

## Inside a folder

- `traffic.md`: the tables the documents quote (first line = folder name, second = the testbed).
- `traffic.json`: the numbers behind the tables.
- `traffic_*.png`: the folder's own plots (FCT distribution, controller load, budget curve).
- `<scenario>-<controller>-pox.log` and `-stats.json`: the controller's log and counters for each run.
- `*-fct-h*.txt` and `*-sched-h*.txt`: per-host flow completion times and flow schedules.

## Notes

- Some folders are on the laptop only until the user commits them; check with `ls results/measured`.
- Do not switch git branches while a batch is running: it deletes files the batch needs.
- If a document and this index disagree, the document's own raw-data line is the older one; fix this index.

## Granularity test (wildcard reactive rules, 20-21 Oct)

See `docs/Granularity_Baseline_Experiment.md`. `traffic-20261020-171300/` is an aborted start with no results.

| Folder | Test | What it holds | Runs | Mode |
|---|---|---|---|---|
| `traffic-20261020-171718/` | **Granularity** | **University, Zipf: reactive-pair / reactive-dst with counter, oracle, random (15 controllers)** | 5 | Best performance |
| `traffic-20261020-183215/` | **Granularity** | **Fat-tree, web search (exact-match reactive rows contaminated by laptop sleep)** | 5 | Best performance |
| `traffic-20261021-050401/` | **Granularity** | **Abilene ISP** | 5 | Best performance |
| `traffic-20261021-060910/` | **Granularity** | **University, uniform pairs (control)** | 5 | Best performance |
| `traffic-20261023-070549/` | **T12 + granularity** | **Fat-tree k=6 with reactive-pair / reactive-dst, counter, oracle, proactive (12 controllers)** | 3 (seeds 7-9) | Best performance |
