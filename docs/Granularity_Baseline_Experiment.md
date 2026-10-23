# Wildcard reactive rules: does rule granularity explain the hybrid's gain?

CS G525 Advanced Computer Networks - Project SA7, Group 2.
Batch of 20-21 Oct 2026 (laptop, WSL2, Open vSwitch kernel datapath, Best performance mode).

## 1. Why this test

Until now every reactive controller in our traffic tests installed **exact-match** rules (one rule per TCP connection, as `l2_learning` does). A TCP connection uses a new source port, so a rule is almost never reused: the reactive hit rate is about 0% by construction. The hybrid's pre-installed rules are **pair rules** (source MAC + destination MAC), which cover every later flow of a pair. So the hybrid changed two things at once: *when* rules are installed and *how coarse* they are. The earlier tests could not tell which of the two produced the gain.

This test adds the missing baseline: a reactive controller that installs a **wildcard rule on the first miss**, with no prediction and no pre-installation.

| Mode | Behaviour |
| --- | --- |
| `reactive-sp` | reactive on shortest paths, exact-match rules (as before) |
| `reactive-pair` | the same, but each rule matches source MAC + destination MAC |
| `reactive-dst` | the same, but each rule matches the destination MAC only |

Code: `controllers/hybrid_eval.py` (`--match=exact|pair|dst`), modes in `experiments/run_traffic_experiments.py` (`--granularity-baselines`), batch script `experiments/night3_granularity.sh`. Rules keep the same timeouts as reactive (idle 10 s, hard 30 s). With ECMP on the fat-tree, a destination rule at a switch follows the next hop of its own shortest path, so packets never get stranded.

## 2. Setup

- 15 controllers per scenario, **all run for every seed (7 to 11)** in one batch, so counter, oracle, random and the new modes are interleaved (this also removes the "different nights" confound for counter vs random).
- 30 s of arrivals, 100 Mbit/s links, 30% load for web search, Zipf 1 pair popularity except the uniform control.
- Command: `sudo bash experiments/night3_granularity.sh`.
- Raw data:

| Scenario | Folder |
| --- | --- |
| University tree (16 hosts, 240 pairs), Zipf 1 | `results/measured/traffic-20261020-171718/` |
| Fat-tree k=4 (16 hosts, 240 pairs), web search | `results/measured/traffic-20261020-183215/` |
| Abilene ISP (11 hosts, 110 pairs) | `results/measured/traffic-20261021-050401/` |
| University tree, uniform pairs (control) | `results/measured/traffic-20261021-060910/` |

(`traffic-20261020-171300/` is an aborted first start and holds no results.)

## 3. Results (mean of 5 runs)

Hit rate = new connections whose first packet found a rule at the sender's switch. FCT = small flows (< 100 KB), median in ms, with the 95% interval. Rules = peak in all switches. Counter, oracle and random are at a 25% budget.

### University tree, Zipf pairs

| Controller | Hit rate % | Small-flow median (ms) | PACKET_IN/s | Peak rules |
| --- | --- | --- | --- | --- |
| Reactive, exact rules | 0 | 52.5 ± 5.0 | 2,352 | 10,987 |
| **Reactive, pair rules** | **97.9** | **1.49 ± 0.27** | **34** | **624** |
| **Reactive, destination rules** | **99.6** | **1.47 ± 0.22** | **8** | **80** |
| Counter, 25% | 60.6 | 12.0 ± 3.5 | 903 | 5,084 |
| Oracle, 25% | 68.2 | 6.3 ± 1.2 | 646 | 3,589 |
| Random, 25% | 23.9 | 35.1 ± 6.0 | 1,781 | 8,574 |
| Proactive | - | 1.49 ± 0.27 | 0 | 624 |

### Fat-tree, web search, Zipf pairs

| Controller | Hit rate % | Small-flow median (ms) | PACKET_IN/s | Peak rules |
| --- | --- | --- | --- | --- |
| Reactive, exact rules | 0 | see warning below | 507 | 3,765 |
| **Reactive, pair rules** | **86.1** | 39.2 ± 18.8 | 115 | 832 |
| **Reactive, destination rules** | **93.6** | 31.6 ± 4.3 | 69 | 280 |
| Counter, 25% | 65.7 | 42.6 ± 6.3 | 186 | 1,566 |
| Oracle, 25% | 73.7 | 36.8 ± 4.6 | 141 | 1,223 |
| Random, 25% | 19.3 | 60.4 ± 11.2 | 397 | 3,267 |
| Proactive (ECMP) | - | 28.7 ± 5.2 | 0 | 1,072 |

### Abilene ISP (real traffic matrices)

| Controller | Hit rate % | Small-flow median (ms) | PACKET_IN/s | Peak rules |
| --- | --- | --- | --- | --- |
| Reactive, exact rules | 0 | 56.5 ± 2.7 | 444 | 5,319 |
| **Reactive, pair rules** | **96.5** | **46.1 ± 1.5** | **15** | **380** |
| **Reactive, destination rules** | **97.8** | **46.1 ± 1.6** | **6** | **120** |
| Counter, 25% | 52.2 | 50.9 ± 2.5 | 207 | 2,621 |
| Oracle, 25% | 59.2 | 49.9 ± 3.0 | 168 | 2,419 |
| Random, 25% | 24.5 | 52.5 ± 2.3 | 330 | 4,013 |
| Proactive | - | 46.0 ± 1.5 | 0 | 386 |

### University tree, uniform pairs (control)

| Controller | Hit rate % | Small-flow median (ms) | PACKET_IN/s | Peak rules |
| --- | --- | --- | --- | --- |
| Reactive, exact rules | 0 | 24.8 ± 0.6 | 2,475 | 10,813 |
| **Reactive, pair rules** | **98.0** | **1.01 ± 0.27** | **20** | **624** |
| **Reactive, destination rules** | **99.6** | **0.96 ± 0.19** | **3** | **80** |
| Counter, 25% | 24.8 | 18.4 ± 0.5 | 1,952 | 8,369 |
| Oracle, 25% | 29.4 | 16.7 ± 0.4 | 1,660 | 7,854 |
| Random, 25% | 25.3 | 17.7 ± 0.7 | 1,763 | 8,204 |
| Proactive | - | 0.96 ± 0.20 | 0 | 624 |

**Warning: the fat-tree exact-match rows are contaminated.** The laptop slept during the batch. In folder `traffic-20261020-183215/`, `Reactive, long timeouts` shows 223 ± 600 failed flows (one run lost almost all its flows), `Reactive` shows 5 ± 14, and `Reactive on shortest paths` has an interval of ± 69 ms. Do not quote those rows. For exact-match reactive on the fat-tree use the clean 5-run results of the night of 17-18 Oct (`traffic-20261017-214330/`: small-flow median, mean of 5 runs, reactive 110.8 ms, reactive on shortest paths 59.3 ms, proactive ECMP 28.6 ms). The pair, destination, counter, oracle, random and proactive rows report 0 failed flows; pair rules have a wider interval (± 18.8) that should be checked against the per-run rows.

**Reproducibility.** Counter, oracle and random hit rates reproduce the earlier batches within 0.1 point (for example fat-tree counter 65.7 vs 65.8 at 25%; university random 23.9 vs 23.9).

## 4. What it shows

1. **Pair and destination rules close almost the whole reactive gap, with no prediction.** Hit rates are 86 to 98% (pair) and 94 to 100% (destination) in all four scenarios. In the university tree and on Abilene the small-flow median equals proactive's within the interval (1.49 vs 1.49 ms, 46.1 vs 46.0 ms).
2. **They need no more rules than proactive.** Pair rules end at 624 / 832 / 380 rules against proactive's 624 / 1,072 / 386; destination rules need only 80 / 280 / 120.
3. **The budgeted hybrid is dominated at this scale.** At 25% the counter and even the hindsight oracle have lower hit rates, more PACKET_INs and more rules than a plain reactive controller with pair rules. The hybrid's reactive fallback still installs exact-match rules, which is why its rule count stays high.
4. **Skew does not matter for pair rules.** With uniform pairs they still reach 98%, because every pair gets about 25 flows in 30 s (6,093 flows over 240 pairs). Skew only mattered for the counter.
5. **The T5 penalty belongs to exact-match rules.** Small flows are 2.2 to 28 times slower under exact-match reactive; with pair rules the university gap disappears (24.8 to 1.0 ms uniform, 52.5 to 1.5 ms Zipf), the Abilene gap shrinks to the path part (56.5 to 46.1 ms, floor 46.0), and the fat-tree gap shrinks (see the warning above).
6. **Proactive's rule count is also a granularity choice.** `proactive_eval --granularity=dst` needs O(N) rules per switch. A destination-rule proactive controller has not been run yet (`proactive-dst` is not a mode).

## 5. What it does not show

- **Not that wildcards are better in general.** Wildcard rules give up per-flow policy (access control, per-flow paths) and per-flow visibility, which is the reason for exact-match rules in Ethane-style designs. Our tests have no policy and no monitoring, so they cannot value that. State it as an argument, not a result.
- **Small networks only.** 11 to 16 hosts, 110 to 240 pairs, about 25 flows per pair in 30 s, so the first miss of a pair is amortised. At k=6 (2,862 pairs, about 640 flows in 30 s) most pairs appear once or twice, and pair rules should hit far less. That is the open test, and where a rule budget could still matter.
- **Idle timeout 10 s.** Pair rules were not given long timeouts; destination rules would also behave differently under a different routing policy.
- **One failed flow** in the oracle at 10% (university, seed 7); negligible (1 of 6,073).

## 6. Consequences for the other documents

| Claim | Status |
| --- | --- |
| "Reactive is 2.2 to 28 times slower" (T5) | holds for exact-match rules only |
| "Proactive costs memory, reactive costs time" (T1, T2) | granularity-dependent; pair-rule reactive matches proactive's rules and its speed |
| "A rule budget buys most of proactive's benefit" (T7) | true against exact-match reactive; **not** against pair-rule reactive at 11 to 16 hosts |
| "The oracle bounds what any predictor can add" (T8) | still a static hindsight bound only; ML has even less room because a rule with no prediction already hits 86 to 98% |

## 7. Next steps

1. **k=6 with the new modes** (where pairs far outnumber flows): `sudo python3 experiments/run_traffic_experiments.py --scenarios fattree-k6:websearch --budget-sweep --budgets 2 5 10 --load 0.05 --pair-zipf 1 --repeats 3 --granularity-baselines` (about 1 hour).
2. Add `proactive-dst` to complete the two-axis grid (when x how coarse).
3. Rerun the fat-tree exact-match rows (reactive, long timeouts, reactive on shortest paths) without the laptop sleeping, and check the pair-rule interval against the per-run rows.
4. A capped version of reactive-pair (a rule budget with LRU eviction) is the natural form of the hybrid if k=6 shows that pair rules overflow.
