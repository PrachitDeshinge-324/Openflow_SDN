# Paper TODO: from course project to a benchmarking paper

**Target claim:** published flow-rule predictors (ML and heuristic) are mostly compared against exact-match reactive only. A reactive controller with pair or destination rules, with no prediction, gets most of that gain. We give the benchmark, the trivial baseline and a hindsight reference (the best fixed set, not an upper bound) that a predictor must be judged against, and we map where prediction has real room.

**Status, 20 Nov 2026 (today's submission version):**
- Draft written: `paper/paper.tex` (IEEE conference format, now about 5,900 words with tables; compile on Overleaf with `paper/scale_hit_rate.pdf`).
- Done 20 Nov: paired per-seed statistics (Table IV, 4.2 in part), oracle reworded as a hindsight reference, 120 s run-length check (3.3 by replay), Zipf 0 / 0.5 / 1.5 sweep (3.2 in part: the regime depends on skew), bound for fixed sets on a pair-rule fallback (1.1 by replay; the testbed version is not fair in our controller), LSTM in the paper (2.1, hit rate and installs only), `docs/Reproduce.md` (5.1 in part).
- 1.2 done: harness mode `proactive-dst` (`tap_eval --taps=off`), batch run 21 Nov on Harikrushna (`traffic-20261121-*`); the paper has no `\pending{}` marks left.
- 3.1 done by simulation: `experiments/scale_sim.py` (fat-tree k = 4 to 16, 16 to 1,024 hosts), on the replay model that reproduces all 46 measured wildcard runs (mean absolute error at most 0.1 points). Figure: `docs/figures/scale_hit_rate.pdf`.
- 0.1 partly: the paper counts the 11 pre-installation papers of the survey; full text of the 9 abstract-only ones is still to read.
- Before submission: author block, repository URL, check the two references marked TODO in the bibliography (Kim 2022, Rouf and Yuksel 2025).

**Order matters.** Phase 0 decides whether the claim holds. Do not spend machine time on later phases before it is done.

Each task lists what to do, how it helps the paper, and when it counts as done.

---

## Phase 0: check the claim (no machine time)

### 0.1 Table of the 28 prediction papers
- **Do:** from `docs/literature/ML_Rule_Prediction_Survey.md`, one row per paper: baseline compared against, rule granularity of that baseline, traffic used, network size, emulation or simulation, upper bound given or not, code released or not.
- **Helps:** this is the motivation of the paper. If most rows say "exact-match reactive, no bound", the claim is supported by evidence a reviewer can check. If they do not, we change the angle before wasting weeks.
- **Done when:** the table is complete and we can state a count, for example "N of 28 compare only against exact-match reactive".

### 0.2 Position against DevoFlow and CacheFlow
- **Do:** one paragraph each on what DevoFlow (wildcards cut controller load) and CacheFlow (caching popular rules) already showed, and what they did not: neither evaluates predictors against a wildcard baseline or an oracle.
- **Helps:** answers the first reviewer objection, "wildcards helping is known since 2011", before it is raised.
- **Done when:** the related-work section states our difference in two sentences.

---

## Phase 1: complete the design grid (code)

### 1.1 Counter and LSTM on top of a pair-rule fallback
- **Do:** let `hybrid_eval` combine `--budget > 0` with `--match=pair` as a harness mode (today hybrid modes always use an exact-match fallback).
- **Helps:** separates the two things the hybrid changes at once (when rules are installed, how coarse they are). Without this cell a reviewer says the predictor was handicapped by its fallback.
- **Done when:** modes such as `hybrid-pair-10` run in `run_traffic_experiments.py`.

### 1.2 Proactive with destination rules
- **Do:** add `proactive-dst` as a harness mode (`proactive_eval --granularity=dst` already exists).
- **Helps:** completes the timing x granularity grid, and gives the fair rule-count figure for proactive: O(N) per switch, not O(N^2).
- **Done when:** it appears in the same tables as the other modes.

### 1.3 Hit rate for every mode
- **Do:** report hit rate (new connections whose SYN found a rule) for all controllers, not only those built on `hybrid_eval`.
- **Helps:** hit rate is the headline metric and does not depend on POX or on the laptop. It must be measured the same way everywhere.
- **Done when:** `reactive` and `proactive` rows have a measured hit rate.

### 1.4 Switch table limit
- **Do:** add a `--table-limit` option that caps rules per switch (Open vSwitch flow-table limit with eviction, or refusal).
- **Helps:** today proactive always fits, so it always wins and the trade-off never binds. With a limit, the benchmark tests the situation the paper is about.
- **Done when:** a run with a limit below proactive's need shows proactive failing or degrading, and the other modes adapting.

### 1.5 Emulated control-channel delay
- **Do:** add `--control-delay MS` (netem on the controller connection).
- **Helps:** every result so far uses loopback. A delay sweep shows how a miss gets more expensive with a distant controller, and replaces the pending second-PC test (T9) with something reproducible.
- **Done when:** a sweep of 0 / 1 / 5 / 20 ms runs for one scenario.

---

## Phase 2: predictors as benchmark entries

### 2.1 Report the LSTM
- **Do:** run the existing `lstm_predictor.py` (`--lstm-baseline`) in the standard batches. The docs currently say no ML model was built; fix that either way.
- **Helps:** a benchmark of predictors with no learned predictor in it is not credible. This is the cheapest one to add because the code exists.
- **Done when:** LSTM rows sit next to counter, oracle, random and pair rules, with how it was trained stated.

### 2.2 Reimplement one or two published predictors
- **Do:** pick from the Phase 0 table the methods that are simple to reproduce (for example an LSTM in the style of Batista et al., and an LFU or DQN-style eviction policy).
- **Helps:** turns "our counter loses to pair rules" into "published methods lose to pair rules", which is the publishable statement.
- **Done when:** each has a mode, a short description of what was reproduced and what was simplified.

### 2.3 Predictor interface
- **Do:** one small documented interface: given per-interval pair activity, return a ranking. Counter, LSTM, oracle and random all implement it.
- **Helps:** makes the repo a benchmark others can add to, which is what reviewers of benchmark papers check first.
- **Done when:** adding a new predictor needs one file and no harness change.

---

## Phase 3: scale and traffic

### 3.1 Sweep flows per pair and network size
- **Do:** fat-tree k = 4, 6, 8 and one larger Topology Zoo map (`--gml`), each at several loads, so flows per pair ranges from below 1 to above 20.
- **Helps:** flows per pair decides whether a wildcard rule is reused. The sweep produces the regime map (where pair rules are enough, where prediction has room), which is the main figure of the paper. It also answers "11 to 54 hosts is too small".
- **Done when:** one plot shows hit rate of pair rules, best predictor and oracle against flows per pair.

### 3.2 Pair popularity from real data
- **Do:** add at least one trace-derived pair distribution besides Abilene (for example a public data-centre or campus trace), and keep Zipf as a sensitivity test with several exponents.
- **Helps:** removes the weakest assumption. Today the hybrid result rests on an assumed Zipf exponent of 1.
- **Done when:** the main result is shown on two real pair distributions plus a Zipf sweep.

### 3.3 Longer runs
- **Do:** 120 s or more of arrivals for the predictor comparison.
- **Helps:** 30 s is too short for a learned predictor to warm up and for timeouts (idle 10 s, hard 30 s) to cycle, so a reviewer can dismiss the predictor results as start-up effects.
- **Done when:** results are reported after a stated warm-up period.

---

## Phase 4: measurement rigour

### 4.1 One clean batch on bare-metal Linux
- **Do:** rerun every table in the paper in a single batch, one machine, sleep disabled, fixed power mode, all modes interleaved per seed.
- **Helps:** removes WSL2 noise, the power-mode difference between batches and the contaminated fat-tree rows. A reviewer cannot attack numbers as coming from different nights.
- **Done when:** every number in the paper comes from that batch and the machine is described (CPU, cores, kernel).

### 4.2 Enough seeds, and paired statistics
- **Do:** 10 seeds for the main tables (at least 5 at the largest size). Compare modes per seed (paired differences), since they share the same flows.
- **Helps:** k = 6 has 3 seeds and intervals too wide to separate modes. Paired tests use the same-flows design and tighten the intervals without more runs.
- **Done when:** every claimed difference has an interval that excludes zero, or is stated as not significant.

### 4.3 Second controller for the timing numbers
- **Do:** port the reactive and pair-rule modes to Ryu (or another maintained controller) and rerun one scenario.
- **Helps:** shows that the ordering of strategies is not a POX artefact. Hit rate and rule counts should match exactly; only latency and CPU should move.
- **Done when:** one table compares the two controllers. Lower priority than 4.1 and 4.2.

---

## Phase 5: artefact

### 5.1 One entry point, one results format
- **Do:** a single scenario file (network, workload, modes, seeds) and one JSON schema for all output.
- **Helps:** needed for artefact evaluation, and it makes Phase 3 and 4 batches less error-prone.
- **Done when:** one command reproduces each table of the paper.

### 5.2 Clean the repository
- **Do:** move course material (viva guide, progress reviews, analytical model, demo) out of the released tree; keep the vendored POX with its licence; add a licence for our code.
- **Helps:** a reviewer who opens the repo should see a benchmark, not a course submission.
- **Done when:** the README describes only the benchmark.

---

## Phase 6: writing

### 6.1 Restructure around the grid
- **Do:** rewrite `docs/Final_Report.md` as: motivation (Phase 0 table), benchmark design, baselines and bounds, regime map, predictor results, limits.
- **Helps:** the current T1 to T12 order tells the history of the project, not the argument.

### 6.2 Cut or shrink
- **Do:** T1, T2 (tree delay and rule counts) to one sanity paragraph; T6 (long timeouts) to one sentence; T11 (path vs setup) to a short section or a separate paper.
- **Helps:** these are known results or a different story, and they dilute the claim.

### 6.3 State the limits ourselves
- **Do:** emulation, no hardware table-update rate, no per-flow policy (the real reason for exact-match rules), one or two controllers.
- **Helps:** reviewers are easier on limits the paper names than on ones they find.

---

## Minimum set for a submission

0.1, 0.2, 1.1, 1.3, 1.4, 2.1, 2.2, 3.1, 3.2, 4.1, 4.2, 5.1, 6.1.
The rest strengthens the paper but is not required for the core claim.
