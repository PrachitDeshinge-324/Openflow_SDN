# Step 4: Long Timeouts, Budgeted Hybrid, Oracle, Repeats and Two PCs

CS G525 Advanced Computer Networks, Project SA7, Group 2. This step covers the
comparisons that were still missing from `docs/Evaluation_Plan.md`:

| Plan item | What it asks | Where it is now |
| --- | --- | --- |
| #6 | Is "keep reactive rules longer" (SmartTime-style) enough? | mode `reactive-long` |
| #7 | What does a fixed budget of K pre-installed rules buy, chosen by a simple weighted counter? | modes `reactive-sp`, `hybrid-NN`, budget sweep |
| upper bound | How far is the counter from a perfect predictor? | mode `oracle-NN` |
| statistics | Are the differences larger than the run-to-run noise? | `--repeats N`: mean and 95% confidence interval |
| #9 / Review I point 3 | Does the controller sharing the PC with Mininet change the result? | `--controller-host`, see [Controller_On_Second_PC.md](Controller_On_Second_PC.md) |

The parameters, and the paper behind each, are in
[Realism_Sources.md](Realism_Sources.md).

## 1. The controllers compared

| Mode | Controller | Rules | What it tests |
| --- | --- | --- | --- |
| `reactive` | `reactive_eval` over a spanning tree; exact match; idle 10 s, hard 30 s | one per TCP connection per switch | the Review I baseline |
| `reactive-long` | same, but idle 60 s, hard 300 s | same | "just keep rules longer" (#6) |
| `reactive-sp` | `hybrid_eval --budget=0`: reactive, but on the shortest path (it knows the topology) | one per TCP connection per switch | the 0% point of the sweep; separates "reactive" from "spanning tree" |
| `hybrid-NN` | `hybrid_eval --budget=NN%`: reactive for everything, plus pair rules for the top NN% of host pairs chosen by a weighted counter | at most NN% of all host pairs × path length, plus the reactive rules | #7 |
| `oracle-NN` | `hybrid_eval --pairs_file`: pre-installs the NN% of pairs that **really** carry the most flows in this run, before the first flow | as `hybrid-NN` | the best any predictor (counter, ML, anything) could do with the same budget |
| `proactive` / `proactive-ecmp` | `proactive_eval`: every pair pre-installed | all pairs | the other end |

### The weighted counter (`controllers/hybrid_eval.py`)

Every second, for every (source, destination) host pair:

```
score = 0.97 * score + active        active = 1 if the pair was used in the last second, else 0
```

The controller learns that a pair was used in one of two ways:

- **Pair not pre-installed:** its new flow reached the controller as a
  PACKET_IN at the sender's switch.
- **Pair pre-installed:** its packets no longer reach the controller, so
  every second the controller asks the sender's switch for the packet
  counter of the pair rule. It counts as used if the counter went up.

Then the controller does three things:

1. **Keep the top K.** The K pairs with the highest score get a pair rule
   (match source MAC + destination MAC) on every switch of their shortest
   path. K = budget × all pairs; 240 pairs on the 16-host tree.
2. **Hysteresis.** A newcomer replaces the weakest kept pair only if its
   score is 1.5 times higher. Without this, pairs near the cut-off were
   swapped in and out every second.
3. **Removal.** A pair that drops out has its rules deleted. If its rule
   never matched a packet, it counts as a *wasted install*.

Everything not pre-installed is handled reactively, on the shortest path,
with exact-match rules. No flow is ever dropped because of the budget; a
miss only costs a trip to the controller.

Small example with a budget of 2 pairs (scores after each one-second tick):

| Second | h1→h2 | h3→h4 | h5→h6 | Installed |
| --- | --- | --- | --- | --- |
| 1 | used: 1.00 | used: 1.00 | - | h1→h2, h3→h4 (free budget) |
| 2 | used: 1.97 | idle: 0.97 | used: 1.00 | unchanged: h5→h6 needs more than 1.5 × 0.97 = 1.46 |
| 3 | used: 2.91 | idle: 0.94 | used: 1.97 | h5→h6 replaces h3→h4 (1.97 > 1.5 × 0.94) |

A pair used every second settles at a score of 1 / (1 − 0.97) ≈ 33. A pair
that stops being used loses half its score in about 23 s.

### The oracle: a controller that knows the future

The oracle cannot exist in a real network; it is a measuring stick. The
harness generates the whole flow schedule before the run, so it knows which
host pairs will be busiest:

1. It counts the flows of every pair in both directions, because the TCP
   reply needs the reverse rule.
2. It writes the K busiest pairs to a file.
3. `hybrid_eval --pairs_file` installs exactly those pairs before the first
   flow and never changes them.

Its hit rate is the best that any method choosing K pairs can reach: a
counter, logistic regression, XGBoost or anything else. So
**oracle − counter** is the most a smarter predictor could ever add at that
budget, measured without building one. This is the same idea as Belady's
optimal algorithm in caching (1966), which knows all future requests and
serves as the bound for real cache algorithms.

Limit: it is the best *fixed* set of pairs. Here pair popularity does not
change during a run, so a fixed set is the right bound. If popularity
shifted over time, an oracle that swaps pairs could do better.

**Hit rate** = the share of new TCP connections whose first packet (SYN)
found a rule at the sender's switch, i.e. did not go to the controller.

## 2. How to run (laptop)

```bash
# Budget sweep on the university tree, skewed pairs (about 25 minutes, 11 runs)
sudo python3 experiments/run_traffic_experiments.py --scenarios tree-d2-f4:university \
    --budget-sweep --pair-zipf 1
# The same with uniform pairs (pFabric's assumption): no pair is popular, so the counter
# should not beat its budget share. This is the control experiment.
sudo python3 experiments/run_traffic_experiments.py --scenarios tree-d2-f4:university \
    --budget-sweep --pair-zipf 0
# Data centre and ISP
sudo python3 experiments/run_traffic_experiments.py --scenarios fattree-k4:websearch --budget-sweep --pair-zipf 1
sudo python3 experiments/run_traffic_experiments.py --scenarios abilene:isp --budget-sweep
```

The ISP workload ignores `--pair-zipf`: its pairs come from the real Abilene
traffic matrices, which are already skewed.

Options:

- `--budgets 5 10 25 50` changes the budget points.
- `--decay` and `--hysteresis` change the counter.
- `--long-idle` and `--long-hard` change `reactive-long`.

**Repeats.** Add `--repeats 5` to any command. Every controller then runs 5
times, with seeds 7 to 11, so each run gets a new flow schedule from the same
workload. The tables then show the mean ± the half-width of the 95%
confidence interval (Student's t), plus an "Every run" table. The plots show
error bars, and the CDFs pool all runs. Use at least 5 repeats: with 2, the
t-multiplier is 12.7 and the intervals are meaninglessly wide. The repeats
are the outer loop (all controllers for seed 7, then all for seed 8, ...), so
a slow drift of the machine hits every controller equally.

Output: `results/measured/traffic-<timestamp>/`:

- `traffic.md`: tables, including "Budgeted hybrid" with hit rate and
  installs;
- `traffic.json`;
- `traffic_budget.png`: hit rate, small-flow median FCT, PACKET_IN/s and
  peak rules against the budget, for the counter and the oracle, with
  reactive, reactive-long and proactive as reference lines;
- the usual Step 2 plots.

## 3. First results: cloud test machine, NOT for the report

This run is only a check that everything works. It used the cloud box: a
4-CPU VM with userspace Open vSwitch (no kernel datapath) and no netem.
Userspace OVS makes every miss and every packet far slower than on the
laptop, so **absolute FCTs are 10–30× the laptop's**. Only the ordering and
the ratios mean anything. The laptop run replaces this table.

University traffic, `tree-d2-f4`, Zipf-1 pairs (the busiest 10% of pairs
carry 60% of the flows), 30 s, 6,088 flows, one run, no failed flows:

| Controller | Hit rate | Small-flow FCT median (ms) | Small p99 (ms) | PACKET_IN/s | CPU % | Peak rules |
| --- | --- | --- | --- | --- | --- | --- |
| Reactive (spanning tree, 10 s / 30 s) | - | 225.5 | 7,602 | 1,214 | 34.6 | 12,327 |
| Reactive, long timeouts (60 s / 300 s) | - | 220.6 | 10,270 | 1,199 | 32.7 | **32,325** |
| Reactive on shortest paths (budget 0%) | 0% | 205.0 | 8,411 | 1,212 | 33.4 | 12,717 |
| Hybrid counter, 10% of pairs | 35.7% | 133.0 | 6,778 | 722 | 24.7 | 6,937 |
| Hybrid counter, 25% | 63.8% | 62.5 | 2,789 | 441 | 18.8 | 4,829 |
| Hybrid counter, 50% | 81.0% | 32.9 | 1,107 | 241 | 14.1 | 2,636 |
| Oracle, 10% | 51.6% | 83.3 | 3,326 | 576 | 21.2 | 5,494 |
| Oracle, 25% | 70.6% | 34.8 | 1,135 | 360 | 16.7 | 3,304 |
| Oracle, 50% | 85.7% | 18.7 | 1,071 | 196 | 10.8 | 1,988 |
| Proactive (all pairs) | 100% | 7.7 | 1,055 | 0 | 0.0 | 624 |

Counter: 75 / 147 / 221 pair installs, 48 / 67 / 67 of them wasted (removed
before ever matching a packet).

What this run says, without sugar-coating:

1. **Long timeouts do nothing for this traffic except fill the tables.**
   Same PACKET_IN rate and the same FCT as normal reactive, with 2.6× the
   rules. The reason: the rules are exact matches, and every new TCP
   connection has a new source port, so a rule kept longer is never matched
   again. "Keep rules longer" only helps if rules are coarser (per pair) or
   if the same 5-tuple repeats. That is a real limit of the SmartTime-style
   approach for short-flow traffic.
2. **A small budget of pair rules beats reactive on every metric at once.**
   At 25% of pairs:
   - small-flow median 3.3× lower (62.5 vs 205 ms);
   - PACKET_IN/s 2.7× lower;
   - **2.6× fewer rules** than reactive.

   One pair rule replaces many per-connection rules.
3. **The counter is close to the oracle at 25–50% but clearly worse at
   10%.**
   - At 10%: 35.7% vs 51.6% hit rate. It wastes 48 of 75 installs while it
     is still learning which pairs are busy.
   - At 25%: 64% vs 71%.
   - At 50%: 81% vs 86%.

   This gap is the most a better predictor (ML or anything else) could add,
   and it is only large at a small budget.
4. **Even the oracle does not reach proactive.** Proactive has the fewest
   rules of all (624: 240 pairs, a few hops each). On a 16-host network,
   "pre-install everything" is cheap. The budget only matters when all
   pairs do not fit in the switches. That is true for large networks, not
   for ours: **be careful when presenting this**.

Not yet known: whether these hold on the laptop (kernel datapath), with
uniform pairs (`--pair-zipf 0`, where we expect the counter to gain only
about its budget share), on the fat-tree and Abilene, and with confidence
intervals (`--repeats 5`).

## 4. Laptop results

Setup:

- **Machine:** Mrudul's laptop: WSL2, Open vSwitch 3.7.1 with the kernel
  datapath, Python 3.14.
- **Controller:** POX on the same PC as Mininet.
- **Traffic:** university, `tree-d2-f4`, 16 hosts, 240 host pairs, every link
  100 Mbit/s.
- **Run:** 30 s of arrivals; host-pair popularity Zipf 1, so the busiest 10%
  of pairs carry 60% of the flows; one run (seed 7).
- **Result:** 6,088 flows, **0 failed in every run**.
- **Raw data:** `results/measured/traffic-20261015-204208/`.

### 4.1 University traffic, popular pairs (Zipf 1)

| Controller | Hit rate | Small-flow FCT median / p99 (ms) | PACKET_IN/s | Controller CPU % | Peak rules (all switches) |
| --- | --- | --- | --- | --- | --- |
| Reactive (spanning tree, 10 s / 30 s) | - | 53.4 / 137.2 | 2,371 | 83.6 | 11,170 |
| Reactive, long timeouts (60 s / 300 s) | - | 59.1 / 154.2 | 2,327 | 83.6 | **32,644** |
| Reactive on shortest paths (budget 0%) | 0% | 53.7 / 169.0 | 2,329 | 82.7 | 11,159 |
| Hybrid counter, 10% of pairs (24) | 24.5% | 32.5 / 99.4 | 1,685 | 74.4 | 7,588 |
| Hybrid counter, 25% (60) | 62.3% | 12.8 / 76.6 | 861 | 48.2 | 5,010 |
| Hybrid counter, 50% (120) | 80.5% | 4.1 / 61.9 | 365 | 28.3 | 2,340 |
| Oracle, 10% | 51.6% | 16.7 / 67.7 | 1,022 | 55.1 | 5,312 |
| Oracle, 25% | 70.6% | 7.4 / 67.6 | 572 | 39.7 | 3,287 |
| Oracle, 50% | 85.7% | 3.0 / 52.8 | 274 | 22.0 | 1,987 |
| Proactive (all 240 pairs) | 100% | 1.7 / 43.9 | 0 | 0.1 | 624 |

Counter installs and waste per budget:

| Budget | Pair installs | Wasted (removed without matching a packet) | Counter hit rate ÷ oracle hit rate |
| --- | --- | --- | --- |
| 10% | 80 | 53 (66%) | 0.47 |
| 25% | 153 | 71 (46%) | 0.88 |
| 50% | 206 | 55 (27%) | 0.94 |

The plot is `traffic_budget.png` in the same folder.

### 4.2 What the numbers say

1. **Long timeouts make reactive worse, not better.**
   - The small-flow median is 11% slower (59.1 vs 53.4 ms) and the tables
     hold 2.9× the rules.
   - The PACKET_IN rate is the same.
   - Why: reactive rules are exact matches, and every new TCP connection
     has a new source port. A rule that is kept longer is never matched
     again; it only takes space.
   - So "keep rules longer" (SmartTime-style timeout tuning) does not help
     short-flow traffic unless the rules are coarser.
2. **The 0% point equals normal reactive** (53.7 vs 53.4 ms, 2,329 vs
   2,371 PACKET_IN/s). On a tree, the spanning tree is the shortest path.
   So every gain in the hybrid rows comes from the pre-installed pair rules,
   not from better routing.
3. **A budget of 25% of pairs improves every metric at once** compared with
   reactive:
   - 4.2× faster small-flow median (12.8 vs 53.7 ms);
   - 2.7× fewer controller requests;
   - controller CPU down from 84% to 48%;
   - **2.2× fewer rules** (5,010 vs 11,159). One pair rule replaces the many
     exact rules its connections would otherwise create.

   At 50%: 13× faster median and 4.8× fewer rules.
4. **The counter is close to the oracle at 25–50%, far from it at 10%.**
   - It reaches 88% and 94% of the oracle's hit rate at 25% and 50%, but
     only 47% at 10%, wasting 66% of its installs.
   - So a better predictor (ML or anything else) could add at most 5–8
     points of hit rate at 25–50% of pairs, but up to 27 points at 10%.
   - Two candidate causes for the 10% gap:
     - **warm-up:** the counter's memory (about 33 s) is as long as the run;
     - **churn at the cut-off:** with 24 slots, many pairs have similar
       scores.

     Run B in Section 5 separates the two.
5. **Proactive is still best on this network.** It is the fastest (1.7 ms)
   and has the fewest rules of all (624 = 240 pairs × about 2.6 switches).
   With 16 hosts, every pair fits easily. A rule budget only pays off when
   all pairs do not fit in the switches' tables, which is the case in large
   networks, not in ours. **We must say this when we present the hybrid.**
6. **Reactive's controller load grows faster than its traffic.** It needs
   11.7 PACKET_INs per new flow (2,371/s for 203 flows/s). A connection
   misses at up to 3 switches in each direction, which already gives up to
   6. Under load, more packets of the same connection arrive before its
   rules are in, and each of them goes to the controller too. This is the
   same amplification as in Step 2.

**Laptop vs cloud test (Section 3).** The ordering of all ten controllers is
the same.

- **Oracle hit rates are identical** (51.6 / 70.6 / 85.7%), as they should
  be: the same schedule and the same pairs.
- **The counter's hit rate at 10% differs a lot:** 24.5% on the laptop,
  35.7% in the cloud. The counter depends on timing (which pairs happen to
  be active in each second), so single runs of it are noisy. This is why the
  final numbers need `--repeats 5`.

## 5. Runs still to do

| Run | Command (add `sudo python3 experiments/run_traffic_experiments.py`) | Question it answers | Status |
| --- | --- | --- | --- |
| A | `--scenarios tree-d2-f4:university --budget-sweep --pair-zipf 0` | Control: with no popular pairs, the counter should gain only about its budget share | running |
| B | `--scenarios tree-d2-f4:university --pair-zipf 1 --duration 120 --modes reactive-sp hybrid-10 oracle-10` | Is the counter's 10% gap warm-up (it closes in 120 s) or ranking (it stays)? | running |
| C1 | `--scenarios fattree-k4:websearch --budget-sweep --pair-zipf 1` | Data centre: fewer, bigger flows, many paths (ECMP) | running |
| C2 | `--scenarios abilene:isp --budget-sweep` | ISP: real traffic matrices, which are skewed on their own | running |
| D | Section 4.1 again with `--repeats 5` (about 2 h) | Confidence intervals for the main table | to do |
| E | Any of the above with `--controller-host` (two PCs) | Point 9: does a separate controller PC change the result? | to do (needs a second laptop) |
