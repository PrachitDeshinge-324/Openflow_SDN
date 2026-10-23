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

### Fat-tree k=6 (54 hosts, 2,862 pairs), added 23 Oct

Same traffic as T12 (web search, 5% load, Zipf 1, about 640 flows per run), **3 seeds (7 to 9)**, 12 controllers per seed, 0 failed flows. Folder: `results/measured/traffic-20261023-070549/`. The counter and oracle numbers reproduce the earlier T12 run (counter 40.0 / 46.9 / 51.1%, oracle 50.3 / 65.5 / 77.8%, proactive 13,230 rules).

| Controller | Hit rate % | Small-flow median (ms) | PACKET_IN/s | Peak rules |
| --- | --- | --- | --- | --- |
| Reactive (spanning tree), exact | 0 | 86.0 ± 39.7 | 345 | 2,977 |
| Reactive on shortest paths, exact | 0 | 52.5 ± 22.4 | 371 | 2,165 |
| **Reactive, pair rules** | **50.8 ± 5.0** | 21.5 ± 11.3 | 213 | 1,249 |
| **Reactive, destination rules** | **59.3 ± 2.4** | 13.4 ± 7.4 | 153 | 766 |
| Counter, 2% | 40.0 ± 7.0 | 29.1 ± 18.7 | 231 | 1,583 |
| Counter, 5% | 46.9 ± 9.5 | 24.7 ± 12.3 | 212 | 1,840 |
| Counter, 10% | 51.1 ± 7.2 | 22.6 ± 9.6 | 189 | 2,368 |
| Oracle, 2% | 50.3 ± 7.1 | 22.0 ± 9.5 | 194 | 1,363 |
| Oracle, 5% | 65.5 ± 9.6 | 13.4 ± 18.6 | 141 | 1,430 |
| Oracle, 10% | 77.8 ± 8.1 | 8.1 ± 4.2 | 94 | 2,028 |
| Proactive (ECMP) | - | 4.95 ± 0.8 | 0 | 13,230 |

What it shows:
- **The wildcard hit rate falls with size**: 86 to 98% at 11 to 16 hosts, 51% (pair) and 59% (destination) at 54 hosts. About 640 flows over 2,862 pairs means most pairs appear once or twice, so a rule installed on the first miss is rarely reused.
- **The counter still adds nothing over plain pair rules.** At a 10% budget it has the same hit rate (51.1 vs 50.8) and speed (22.6 vs 21.5 ms), with 1.9 times the rules (2,368 vs 1,249) and 43% of its installs wasted (214 of 500).
- **Only the oracle, which knows the future, beats wildcard rules** (65.5% at 5%, 77.8% at 10%). So prediction has room at this size, but our counter does not capture it.
- **Proactive is still the fastest** (4.95 ms) but needs 10.6 times the rules of pair rules and 17 times those of destination rules.
- Destination rules are the best non-oracle trade-off: 59% hit rate and 13.4 ms with 766 rules.
- With 3 seeds most speed differences between pair, destination, counter and the 2 to 5% oracle are not significant; the hit rates are tighter.

**Warning: the fat-tree exact-match rows (k=4) are contaminated.** The laptop slept during the batch. In folder `traffic-20261020-183215/`, `Reactive, long timeouts` shows 223 ± 600 failed flows (one run lost almost all its flows), `Reactive` shows 5 ± 14, and `Reactive on shortest paths` has an interval of ± 69 ms. Do not quote those rows. For exact-match reactive on the fat-tree use the clean 5-run results of the night of 17-18 Oct (`traffic-20261017-214330/`: small-flow median, mean of 5 runs, reactive 110.8 ms, reactive on shortest paths 59.3 ms, proactive ECMP 28.6 ms). The pair, destination, counter, oracle, random and proactive rows report 0 failed flows; pair rules have a wider interval (± 18.8) that should be checked against the per-run rows.

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
- **Small networks (k=4, Abilene) amortise the first miss.** 110 to 240 pairs and about 25 flows per pair in 30 s. At k=6 the hit rate of pair rules falls to 51% (see above), so the k=4 result must not be extrapolated to large networks. Only 3 seeds at k=6, 5% load, web search only.
- **Idle timeout 10 s.** Pair rules were not given long timeouts; destination rules would also behave differently under a different routing policy.
- **One failed flow** in the oracle at 10% (university, seed 7); negligible (1 of 6,073).

## 6. Consequences for the other documents

| Claim | Status |
| --- | --- |
| "Reactive is 2.2 to 28 times slower" (T5) | holds for exact-match rules only |
| "Proactive costs memory, reactive costs time" (T1, T2) | granularity-dependent; pair-rule reactive matches proactive's rules and its speed |
| "A rule budget buys most of proactive's benefit" (T7) | true against exact-match reactive; **not** against pair-rule reactive at 11 to 16 hosts; at 54 hosts the counter equals pair rules, only the oracle is better |
| "The oracle bounds what any predictor can add" (T8) | still a static hindsight bound only; ML has even less room because a rule with no prediction already hits 86 to 98% |

## 7. Next steps

1. **A counter on top of a wildcard fallback** (untested idea): pre-install the busiest pairs as now, but let every miss install a pair rule instead of an exact-match rule. At k=6 this might close part of the gap between pair rules (51%) and the oracle (65 to 78%). It is a prediction, not a result.
2. Add `proactive-dst` to complete the two-axis grid (when x how coarse).
3. Rerun the k=4 fat-tree exact-match rows without the laptop sleeping (optional; the earlier clean results exist).
4. Emulated control-channel delay and the second-PC run (T9), since every result so far uses a loopback control channel.
