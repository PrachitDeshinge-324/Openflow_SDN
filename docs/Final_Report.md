# Reactive, Proactive and In Between: An Empirical Comparison of OpenFlow Rule Installation Under Realistic Traffic

**CS G525 Advanced Computer Networks, Research Project SA7, Group 2**
**Members:** N. Nisarg Vagh, D. Dhaduk Mrudul Hiteshbhai, Prachit Suresh Deshinge, Mukul Saini
**Submission:** 20 November 2026
**Code and raw data:** <https://github.com/PrachitDeshinge-324/Openflow_SDN>

> **Status of this draft (15 Oct 2026).** This is the structure of the final report.
> - **Sections that will not change** are written: introduction, related work, testbed and method, and the Review I and Step 1 results.
> - **`TODO (data)`** marks a place that waits for a measurement still to run:
>   - the two-PC run;
>   - the larger fat-tree;
>   - Step 2 with repeats.
> - **Step 4 now uses the repeat means (16 Oct).**
> - **Numbers marked *(single run)*** are from one run and will be replaced by the repeat means.

---

## Abstract

*TODO (final numbers).* Draft:

In OpenFlow, a switch can only forward a packet that matches a rule. A **reactive** controller installs rules when the first packet of a flow arrives; a **proactive** controller installs them in advance. Published work has proposed many strategies between the two (longer timeouts, caches of popular rules, hybrids, ML predictors), but each was evaluated on its own traffic and setup.

We compare them **side by side on one testbed** (Mininet, Open vSwitch, POX):
- **networks:** a campus tree, a data-centre fat-tree and the real Abilene backbone;
- **traffic:** university, data-centre and ISP traffic taken from published measurements and real traffic matrices.

**What we find:**
1. **Reactive pays twice.** Its small flows are 2.5–44× slower than proactive's, because of the setup delay and, on networks with loops, the spanning tree's detours. On Abilene the detours cost more than the setup.
2. **Long timeouts give no benefit** for short-flow traffic.
3. **A budgeted hybrid helps when traffic is skewed.** Pre-installing the busiest 25% of host pairs, chosen by a simple counter, removes 54–66% of controller trips, with 2.0–2.4× fewer rules than reactive.
4. **A perfect predictor would add only 5–11 percentage points** of hit rate at those budgets. This bounds what ML prediction could gain on this traffic.

---

## 1. Introduction

### 1.1 The problem
- **Reactive installation** keeps switch tables small but delays the first packet of every new flow. It also loads the controller with one request (PACKET_IN) per new flow per switch.
- **Proactive installation** removes the delay and the controller load at run time, but it needs a rule for every host pair: O(N²) table entries.
- **Real switch tables are small.** The HP switch studied in DevoFlow holds about 16K exact-match rules. So the trade-off matters in practice.

### 1.2 What is missing in the literature
Each in-between idea has been shown to beat plain reactive, but always on its own terms:
- **Timeouts:** SmartTime and AH-IHTA, on university traces.
- **Rule caching:** CacheFlow, on policy rules.
- **Hybrids:** PARD and Kim et al., in simulation.
- **Predictors:** Batista et al., on periodic IoT traffic.

None of these compared their idea, on the same testbed and traffic, against the others, against a simple frequency counter, or against an upper bound. And the papers that study path quality (ECMP, Hedera) do not look at how rules are installed. (`docs/Evaluation_Plan.md` lists each comparison next to the closest paper.)

### 1.3 Our contribution
**An empirical comparison, not a new algorithm.** On one testbed, with the same flows for every controller, we measure:

1. **First-packet delay, rule counts and controller load**, from 4 to 16 hosts (Review I).
2. **Path quality:** reactive (spanning tree) against proactive shortest paths and ECMP, on a fat-tree and the real Abilene map (Step 1).
3. **Flow completion times and controller load under realistic traffic:** university, web search, data mining, and real ISP traffic matrices (Step 2).
4. **The in-between strategies:** long timeouts, a budgeted popular-pair hybrid, and an oracle that bounds any predictor. We also split reactive's cost into a **path** part and a **setup** part (Step 4).
5. *TODO (data):* the effect of running the controller on a separate machine.

---

## 2. Background and related work

*Source: `docs/literature/Literature_Review_IdleHybrid.md` (14 papers, 11 read in full) and `docs/literature/ML_Rule_Prediction_Survey.md` (28 papers). Condense to about one page.*

| Theme | Key papers | What they show | What we take or test |
| --- | --- | --- | --- |
| Reactive setup is expensive | Ethane (SIGCOMM 2007), DIFANE (SIGCOMM 2010), DevoFlow (SIGCOMM 2011), Tootoonchian et al. (Hot-ICE 2012) | Setup delay of ms to tens of ms; controllers and switch control paths are limited | We measure delay, PACKET_IN rate and controller CPU under realistic traffic |
| Path quality in multi-path networks | Al-Fares et al. (SIGCOMM 2008), Hedera (NSDI 2010) | Fat-trees need ECMP / flow scheduling | We link the installation mode to path quality |
| Caching popular rules | CacheFlow (SOSR 2016) | 90% hits with < 5% of rules on Zipf traffic | Our budgeted hybrid, on host pairs |
| Timeouts and eviction | SmartTime (DEBS 2014), AH-IHTA (2020) | Tuned timeouts cut controller load | Our long-timeout baseline |
| Hybrid installation | PARD (2020), Kim et al. (2022) | Hybrids cut first-packet delay | Our budgeted hybrid |
| Prediction / ML | Batista et al. (2024), others in our survey | Predictors beat plain reactive, mostly on IoT traffic; rarely compared with a simple counter | Our oracle bound instead of an ML model |
| Realistic traffic | Benson et al. (IMC 2010), DCTCP, VL2, pFabric, Abilene TMs (Zhang et al., IMC 2005) | Published workloads and real matrices | Our four workloads (`docs/Realism_Sources.md`) |

---

## 3. Testbed and method

### 3.1 Testbed
| Item | Value |
| --- | --- |
| Emulator / switch / controller | Mininet 2.3.0, Open vSwitch 3.7.1 (kernel datapath), POX 0.7.0 (`gar`), OpenFlow 1.0 |
| Machines | Laptops with Windows 11 + WSL2 (Ubuntu, kernel 6.18), Python 3.14. *TODO: CPU model and core count.* |
| Power mode | Review I, Step 1, Step 2: Windows "Balanced". Step 4 repeats onwards: "Best performance". Absolute times are compared only within one batch; see Section 6. |
| Second machine | *TODO (data):* the two-PC setup (`docs/Controller_On_Second_PC.md`) |

### 3.2 Controllers
| Name | Behaviour |
| --- | --- |
| Reactive | POX learning switch (`reactive_eval`), exact-match rules, idle 10 s / hard 30 s; over POX discovery + spanning tree on networks with loops |
| Reactive, long timeouts | The same, idle 60 s / hard 300 s |
| Reactive on shortest paths | `hybrid_eval` with budget 0: reactive, exact-match, but routes on the shortest path from the known topology |
| Budgeted hybrid | `hybrid_eval`: the above, plus pair rules for the top-K host pairs by a decaying counter (decay 0.97/s, hysteresis 1.5) |
| Oracle | `hybrid_eval --pairs_file`: pre-installs the K pairs that really carry the most flows in the run (both directions), before the first flow |
| Proactive / Proactive ECMP | `proactive_eval`: one rule per host pair on the lowest-delay path; ECMP hashes pairs over equal-cost paths |

### 3.3 Networks
- **Trees:** 4, 8 and 16 hosts.
- **Fat-tree k = 4:** 20 switches, 16 hosts.
- **Abilene:** 11 cities, 14 links, real link speeds, and city-to-city delays from fibre distance.
- *TODO (data):* fat-tree k = 6 (45 switches, 54 hosts).

### 3.4 Traffic
| Workload | Flow sizes | Arrivals | Source |
| --- | --- | --- | --- |
| University | Benson Fig. 4(a): 87% < 10 KB | Weibull gaps per edge switch, 80% within 4–40 ms | Benson et al., IMC 2010 |
| Web search | `CDF_dctcp.tcl` (mean 1.67 MB) | Poisson, 30% load | DCTCP via pFabric / PIAS |
| Data mining | `CDF_vl2.tcl` (mean 7.47 MB) | Poisson, 30% load | VL2 via pFabric / PIAS |
| ISP | SURGE file sizes (lognormal body μ = 9.357, σ = 1.318; Pareto tail k = 133 KB, α = 1.1, 7% of files in the tail; from the paper's Table 1 and Section 4) | Real Abilene hourly traffic matrices, 1 Mar 2004 | Zhang et al., IMC 2005 |
| Pair popularity (Step 4) | – | Zipf with exponent 1 over host pairs, or uniform (control); real matrices for ISP | CacheFlow's Zipf assumption |

### 3.5 Fairness and statistics
- **Identical flows:** the flow schedule is computed in advance from a seed, so every controller gets exactly the same flows (start time, source, destination, size).
- **Repeats:** 5 seeds per configuration; mean ± half-width of the 95% confidence interval (Student's t, 4 degrees of freedom). Done for Step 4. *TODO (data):* Step 2.
- **Measured, not modelled:**
  - paths are read from the switches' flow tables;
  - controller load comes from counters inside our controllers;
  - flow completion time is measured per flow by the traffic generator.

---

## 4. Results

### 4.1 Setup cost and table size on trees (Review I)
*Final. Source: `docs/Progress_Review_1.md`, reproduced on a second laptop.*

- **First packet:** reactive takes 3.8–6.6 ms (laptop 1) and 7.2–11.4 ms (laptop 2); proactive takes 0.7–1.5 ms. Later packets are equal (0.06–0.09 ms).
- **Rules when every pair is active:** identical (28 / 216 / 624).
- **Rules under 200 new flows/s:** reactive accumulates 4–83× more.

*Figure: `results/measured/20260927-152012/measured_latency.png`.*

### 4.2 Path quality (Step 1)
*Final. Source: `docs/Path_Quality_Experiment.md`.*

- **Abilene, reactive:** 70% of pairs are on a slower path; delay stretch is 1.58 on average and up to 4.47. Ping RTT is 40.5 ms against 26.9 ms.
- **Fat-tree, total throughput:** ECMP 95 Mbit/s, reactive 64 Mbit/s, one shortest path 62 Mbit/s. Unused links: 16% with ECMP, 59% with reactive.

*Figures: `results/measured/paths-20261015-094800/`.*

### 4.3 Realistic traffic (Step 2)
*Source: `docs/Realistic_Traffic_Experiment.md`.* *(single run, Balanced mode)* *TODO: decide whether to re-run with `--repeats 5` in performance mode.*

| Scenario | Reactive small-flow median | Proactive (ECMP) small-flow median |
| --- | --- | --- |
| University | 55.7 ms | 1.3 ms |
| Web search | 155 ms | 19 ms (ECMP) |
| Data mining | 113 ms | 11.5 ms (ECMP) |
| ISP | 120 ms | 48 ms |

Further findings:
- **Controller load:** 2,379 PACKET_IN/s at 86% CPU for 203 new flows/s.
- **Amplification:** 7.4 to 12 requests per flow as the controller's load rises.

### 4.4 Between reactive and proactive (Step 4)
*Source: `docs/Budgeted_Hybrid_Experiment.md`, Section 4.0. Every value is the mean of 5 runs (seeds 7–11) ± 95% CI, in "Best performance" mode. Full tables are in Section 6 of `docs/Progress_Review_2.md`; copy and condense them here.*

1. **Long timeouts:**
   - no gain in 4 of 4 scenarios, with 2.2–3.0× the rules;
   - with uniform pairs, significantly slower (25.7 ± 0.8 vs 23.6 ± 0.7 ms).
2. **Path vs setup split** (reactive's extra small-flow median over proactive):

   | Scenario | Path | Setup |
   | --- | --- | --- |
   | University tree | 0.6 ms | 26 ms |
   | Fat-tree | 52 ms (wide interval) | 31 ms |
   | Abilene | **41 ms** | **10 ms** |

   Against the Balanced-mode single runs, a faster CPU shrank only the setup part.
3. **Budget of 25% of pairs**, compared with reactive on shortest paths:
   - 54–66% hit rate;
   - 2.3–2.7× fewer PACKET_INs;
   - 2.0–2.4× fewer rules;
   - small-flow median 3.3× lower (university), 1.6× (fat-tree) and 1.1× (Abilene).

   With uniform pairs, a budget buys only its own share.
4. **Counter vs oracle:** 0.88–0.93 at 25–50% budgets, 0.62–0.91 at 10%. The university 10% point is the noisiest (30.8 ± 10.2%).
5. **Counter decay 0.9 vs 0.97:** one run, inconclusive. *TODO (data):* `--decay 0.9 --repeats 5`.

*Figures: `docs/figures/step4_hit_rate.png` and `docs/figures/step4_cost_split.png` (both from the repeat means).*

### 4.5 Controller on a separate machine
**TODO (data).** The question: does a real network between switches and controller, and a controller with its own CPU, change reactive's cost? Tool: `experiments/controller_agent.py` + `--controller-host`.

### 4.6 A larger network
**TODO (data).** Fat-tree k = 6 (54 hosts, 2,862 pairs): does the rule budget start to matter when proactive needs thousands of rules?

---

## 5. Discussion

### 5.1 When each strategy wins
*TODO (final numbers).* Draft:

| Situation | What decides performance | Best choice |
| --- | --- | --- |
| Small network, any traffic | Setup cost | Proactive (ECMP on multi-path networks) |
| Multi-path network | Path choice as much as setup | Anything topology-aware; reactive over a spanning tree is worst |
| Skewed traffic, limited table space | Which pairs get the scarce rules | Budgeted hybrid with a simple counter |
| Uniform traffic, limited table space | Nothing to learn | Budget buys only its own share |
| Short flows | New 5-tuples every time | Long timeouts do not help |

### 5.2 What this means for ML-based rule prediction
- **What the oracle shows:** a perfect predictor of which host pairs will be busy would add only 5–11 percentage points of hit rate over a simple counter at 25–50% budgets on our traffic.
- **Where ML could add more:**
  - small budgets with many flows per pair;
  - traffic where flows on one pair predict flows on *other* pairs (microservice call chains), at a scale where most pairs are idle.

  The second case needs hundreds of hosts and is beyond a laptop emulation.

### 5.3 Threats to validity
- **Emulation, not hardware:** Open vSwitch in software, so there is no TCAM limit and no hardware table-update rate.
- **Controller:** POX is single-threaded, so absolute controller numbers are POX's, not a production controller's.
- **Scale:** our networks are small (11–16 hosts; *TODO:* 54), so proactive's rules always fit.
- **Traffic:** generated from published distributions, not replayed packets. The university size curve was read from a plot. SURGE models web files from the late 1990s (its parameters are checked against the paper). Pair popularity (Zipf) is an assumption, except for ISP.
- **Machine state:** WSL2 timing noise, and the power mode differed between batches (Section 3.1).
- **Counter design:** the counter scores "busy seconds", not flows. This understates what a counter can do at small budgets.

---

## 6. Conclusion
*TODO (final).* Three to five sentences: reactive pays for both setup and path; long timeouts do not help short flows; a small, counter-chosen budget of pair rules recovers most of proactive's benefit when traffic is skewed; and the room left for smarter prediction is small.

## 7. Future work
- Run the comparison on a hardware switch, or at a larger scale.
- A counter that counts flows instead of busy seconds; adaptive timeouts.
- Cross-pair (dependency) prediction for microservice traffic at data-centre scale.

## References
*TODO:* merge the references of `docs/Realism_Sources.md` and the two literature documents into one numbered list.

## Appendix: How to reproduce
See `README.md`, Section 2. All raw data (each flow, each path, POX logs) is in `results/measured/`.
