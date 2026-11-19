# Novelty plan: a model that predicts our testbed before we run it

CS G525 Advanced Computer Networks, Project SA7, Group 2. Written 19 Nov 2026 for the final presentation on 20 Nov.

**How to use this file:** open Claude Code in this repo with Opus 5.5 and paste the prompt in Section 7. Sections 3 to 5 are the work list it follows. Sections 1, 2 and 6 are for us.

---

## 1. The one point

> **A switch's flow table is a cache with a timeout. One 60-line model built on that idea reproduces all 46 of our measured wildcard runs to within 0.1 percentage points, so we used it to predict experiments before running them, and to answer the SA7 question at 1,024 hosts, which no laptop can emulate.**

What the professor sees, in order:

1. One scatter plot: predicted hit rate against measured hit rate, 46 runs, 5 networks and workloads, every point on the diagonal.
2. A git commit with tonight's predictions, time-stamped *before* the Mininet run, next to the measured values from that run.
3. One equation with no fitted parameters that gives the same answer to within about 3 points.
4. A map of which strategy wins from 16 to 1,024 hosts.

It also turns our negative result (the counter adds nothing over plain pair rules) into an explained one: the equation says why.

## 2. What is already checked (19 Nov, on the stored results)

`experiments/model_validate.py` replays the flow schedules stored in the result folders through a timeout cache (idle 10 s, hard 30 s). It needs no Mininet and runs in seconds.

| Scenario (folder) | Rules | Runs | Measured hit % | Model hit % |
| --- | --- | --- | --- | --- |
| University, Zipf (`traffic-20261020-171718`) | pair / dst | 5 | 97.9 / 99.6 | 97.9 / 99.6 |
| Fat-tree k=4, web search (`traffic-20261020-183215`) | pair / dst | 5 | 86.1 / 93.6 | 86.0 / 93.6 |
| Abilene ISP (`traffic-20261021-050401`) | pair / dst | 5 | 96.5 / 97.8 | 96.4 / 97.8 |
| University, uniform (`traffic-20261021-060910`) | pair / dst | 5 | 98.0 / 99.6 | 98.0 / 99.6 |
| Fat-tree k=6 (`traffic-20261023-070549`) | pair / dst | 3 | 50.8 / 59.3 | 50.8 / 59.3 |

Mean error per run is 0.0 to 0.1 points in every row.

Also checked with throwaway scripts (not in the repo; Step 1 rebuilds them properly):

- **The schedule regenerates exactly.** `workloads.make_schedule` with seed string `fattree-k6-websearch-<seed>` gives 613 / 618 / 695 flows for seeds 7 / 8 / 9, the same as the stored runs. So the model can generate traffic for networks we never ran.
- **Peak rules, k=6, pair rules:** model 1,252 / 1,276 / 1,410, measured 1,178 / 1,204 / 1,366. The model is 3 to 6% high.
- **Closed form (Section 3, Step 2) against the replay:** k=6 49.8 to 51.5 vs 48.5 to 52.6 (per seed, up to 3 points apart); k=8 46.9 vs 46.9; k=12 (432 hosts) 45.3 vs 45.5; k=6 at 30% load 76.7 vs 73.2.
- **Scale, 5% load, pair rules:** hit rate stays near 46% at k=8 and k=12, while proactive needs 76,672 rules at k=8 (128 hosts) against about 3,000 for pair rules.
- **Headroom:** a hindsight oracle on top of pair rules reaches 76 to 80% at a 5% budget at k=8. Online policies cannot see those pairs before their first flow.

**Be honest about what the 0.1 means.** The hit rate is almost a function of the schedule alone, so a replay should match. The finding is that nothing else matters: Open vSwitch timers, POX delay and TCP do not move the hit rate. The closed form, the rule counts and the blind runs are the harder tests, and they are less exact.

## 3. Work list for today (in this order)

Each step ends with something that can go on a slide. Stop after any step and the talk still works.

### Step 1. Turn the check into a model (`experiments/flow_table_model.py`)

Start from `experiments/model_validate.py`. Keep what is validated and add:

- **Schedule source:** either a result folder (`<tag>-sched-<host>.txt`, flow times from `flows_detail`) or `workloads.make_schedule` directly. The seed string is `'%s-%s-%d' % (network, workload, seed)`; hosts are `h1..hN` sorted by number; `edge_of` maps each host to its edge switch name (see `run_one` in `run_traffic_experiments.py`).
- **Topologies without Mininet:** fat-tree for any even k (k³/4 hosts, k/2 per edge switch; path length 1 / 3 / 5 switches for same edge / same pod / other pod), the depth-2 tree, and Abilene from a stored `*-topo.json`.
- **Outputs per run:** hit rate at the sender's switch, peak and mean rules over all switches, peak rules on one switch, misses per second over all switches (a lower bound on PACKET_IN/s).
- **Modes:** `pair`, `dst`, `exact` (hit rate 0 by construction), and a pre-installed set on top of pair rules (hindsight top-K, and the counter of `hybrid_eval.py` with a pair fallback).
- A rule for pair (a, b) is refreshed by flows a→b **and** b→a (the ACKs). For `dst` rules, every switch on the path is touched for both end hosts. This is already in `model_validate.py`; keep it.

**Done when:** `python3 experiments/flow_table_model.py --validate` prints the Section 2 table plus predicted and measured peak rules and PACKET_IN/s for every stored `reactive-pair` and `reactive-dst` run, and writes `docs/figures/model_vs_measured.png` (predicted on x, measured on y, diagonal line, one point per run, 46 points for the hit rate).

Say plainly in the output where the model is worse. PACKET_IN/s will be under-predicted when several packets of a flow arrive before the rule does; report the ratio.

### Step 2. The equation (`closed_form()` in the same file)

For a rule with refresh rate r (flows per second in both directions) and idle timeout T, Poisson arrivals:

- probability a new flow misses, steady state: `exp(-r T)`
- in a run of length D that starts with empty tables: `[(1 - exp(-r T)) / r + (D - T) exp(-r T)] / D`
- hit rate = `1 - Σ λ_i · miss_i / Σ λ_i`; expected rules in the table = `Σ (1 - exp(-r_i T)) × path length`

With Zipf popularity, `λ_i = Λ / (i^s · H)`. For the reverse direction use the mean pair rate (the ranking is random, so the reverse pair is an average pair).

**Done when:** a table in the write-up shows closed form vs replay vs measured for the five scenarios. Expect agreement within about 3 points.

Then write the two consequences, each in two sentences, with numbers from the model:

1. **Why the counter added nothing.** Pre-installing pair i saves `λ_i · exp(-r_i T)` misses per second. For a busy pair that is zero: its rule never expires. The budget went to pairs that were already cached.
2. **Where the misses are.** Pairs with `λ < 1/T` (fewer than one flow per timeout). A counter learns a pair from its first flow, and for most of these pairs there is no second flow in the run. Only knowledge from before the run can help, which is why only the oracle wins at k=6.

### Step 3. Blind prediction (start the Mininet run before the evening)

1. With the model, predict hit rate and peak rules for the runs below. Write them to `docs/Model_Blind_Predictions.md` as a table with an empty "Measured" column.
2. **Commit and push that file before starting Mininet.** The commit time is the proof.
3. Run on the usual laptop (Best performance mode, lid open, sleep off):

```bash
sudo python3 experiments/run_traffic_experiments.py --scenarios fattree-k6:websearch --modes reactive-pair reactive-dst --load 0.05 --pair-zipf 1 --seed 12 --repeats 3
```

```bash
sudo python3 experiments/run_traffic_experiments.py --scenarios fattree-k6:websearch --modes reactive-pair reactive-dst --load 0.10 --pair-zipf 1 --repeats 3
```

```bash
sudo python3 experiments/run_traffic_experiments.py --scenarios fattree-k4:datamining --modes reactive-pair reactive-dst --pair-zipf 1 --repeats 3
```

   - Run 1: new seeds (12 to 14) on a known setup. Safest; do it first.
   - Run 2: a load we never ran. If the laptop drops flows at 10%, report it and keep run 1.
   - Run 3: a workload never run with wildcard rules.
4. Fill in the "Measured" column in a second commit. Do not edit the predictions. If one misses, show the miss; that is the honest version and still a good slide.

Check first that `--modes` together with `--repeats` works with a 10-second smoke run (`--duration 10 --repeats 1`).

### Step 4. The scale map (`docs/figures/model_scale_map.png`)

Use the replay with generated schedules; 3 seeds each.

- Fat-tree k = 4, 6, 8, 10, 12, 16 (16 to 1,024 hosts), web search, Zipf 1, loads 5% and 30%. k=16 is slow in pure Python: use the closed form there if the replay takes more than a few minutes, and say so in the caption.
- Per size: hit rate for pair and dst rules; total rules and busiest-switch rules for pair, dst and proactive-pair (`Σ path length` over all ordered pairs).
- Draw a horizontal line at 1,500 rules per switch (the hardware table in DevoFlow, already cited in the Viva guide). The size where proactive crosses it is the headline number.

**Done when:** one figure with two panels (hit rate vs hosts; rules on the busiest switch vs hosts, log scale) and a 5-row table.

### Step 5. Write-up and pointers

- `docs/Flow_Table_Model.md`: same layout as the other experiment files (why, model, validation, blind test, scale map, what it does not show). Short sentences, every number traceable to a command.
- One row each in `README.md`, `docs/Test_Catalogue.md` (new T13), `docs/Viva_Guide.md` (cheat sheet + two questions from Section 6), `docs/Final_Report.md` (contribution 5 and a new 4.7).
- Run everything once from a clean clone before committing.

## 4. What the model does not cover (say this before being asked)

- **Flow completion time.** The model predicts hits, rules and control load, not milliseconds.
- **Exact-match reactive.** Its hit rate is 0 by construction; nothing to predict.
- **The counter hybrid with exact fallback** as measured in T7. Step 1 adds the counter with a pair fallback, which is a prediction with no measurement behind it unless there is time to run it.
- **Hardware.** Still emulation. The model inherits that.
- **The oracle uses hindsight** inside the same run, so "100% at a 10% budget" at k≥8 only means fewer than 10% of pairs ever appear. Do not quote it as achievable.

## 5. Prior work: check before presenting

The mathematics is not ours, and we must say so. From memory, to be verified today (find the PDF, add it to `docs/literature/`, cite the page):

- Che, Tung, Wang, "Hierarchical Web Caching Systems", IEEE JSAC 2002: the characteristic-time approximation.
- Fofack, Nain, Neglia, Towsley, "Analysis of TTL-based Cache Networks", ValueTools 2012.
- Metter et al., "Analytical Model for SDN Signaling Traffic and Flow Table Occupancy", IEEE TNSM 2017: a timeout model for flow tables.

**What we claim:** not the formula. We claim (a) the test of it on a real Open vSwitch + POX testbed with published traffic, at three rule granularities, to 0.1 points; (b) predictions committed before the measurement; (c) its use to explain why counter-based pre-installation fails and where prediction still has room. If a search finds a paper that did (a) to (c), change the wording to "we reproduce and extend".

## 6. The slide and the questions

**The slide (90 seconds).** Left: `model_vs_measured.png`. Right: the blind-prediction table with the two commit hashes. One line under it: "Flow table = timeout cache. Miss probability = exp(-rate × timeout)."

Say: "Until last week our model and our measurements were two separate things. Now one model predicts the testbed. We wrote down tonight's results before running them. Here is the commit, here is the measurement."

Then the scale map: "This is the experiment our laptops cannot run."

**Questions to expect.**

- *Is 0.1 points surprising?* Partly not: the hit rate is fixed by the schedule. The result is that the real switch and controller add nothing to it. The equation and the blind runs are the real tests.
- *Is this new?* The formula is from caching theory. The validation on a testbed, the pre-registered prediction and the explanation of the counter's failure are ours.
- *Why trust the 1,024-host numbers?* Same code that matched 46 runs, same traffic generator; and the closed form agrees with it at every size we could run both. It is still a prediction, and we label it so.
- *Does it predict delay?* No. Hits, rules and control load only.
- *Then which strategy should a network use?* Read it off the map: below the 1,500-rule line proactive fits and wins; above it, destination rules, and pre-installation only helps with knowledge from before the run.

**Do not say:** "our model is exact", "we invented the formula", "the hybrid reaches 80%" (that is hindsight), or any number that is not in a committed table.

## 7. Prompt to paste into Opus 5.5

```
Read docs/Novelty_Plan.md fully, then docs/Granularity_Baseline_Experiment.md,
experiments/model_validate.py, experiments/workloads.py and controllers/hybrid_eval.py.

Carry out Section 3 of docs/Novelty_Plan.md, Steps 1 to 5, in order. Rules:
- Run experiments/model_validate.py first and confirm it reproduces the table in Section 2.
- You have no Mininet here. For Step 3, produce the predictions file and commit it, then stop
  and give me the three commands to run on the laptop. When I paste the results folder names
  back, fill in the measured column in a new commit without touching the predictions.
- Every number in a document must come from a command you ran; print the command next to it.
- Report honestly where the model is off (rule counts, PACKET_IN/s). Do not tune anything to
  improve the fit: the model has no fitted parameters and must stay that way.
- Match the writing style of the existing docs (short plain sentences, tables, no hype).
- Commit after each step with a clear message.
The presentation is tomorrow, so finish Step 1 and Step 3's prediction commit first, then
Steps 2 and 4 while the laptop runs, then Step 5.
```

## 8. Timeline for today

| When | What | Who |
| --- | --- | --- |
| First 2 hours | Steps 1 and 3 (predictions committed, pushed) | Opus + one of us reviewing |
| Then | Start the three Mininet runs on the laptop | Whoever has the Best-performance laptop |
| While it runs | Steps 2 and 4 | Opus |
| Evening | Fill in measured values, Step 5, slide | All |
| Before sleeping | Rehearse the 90 seconds twice; rerun `--validate` on the presenting laptop | Presenter |
