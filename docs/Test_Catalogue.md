# Test Catalogue: Every Test, Its Closest Paper, and What We Found

CS G525 Advanced Computer Networks, Project SA7, Group 2. Status: 16 October 2026.

**One section per test, always in the same order:**
1. **Question:** what the test answers.
2. **Setup:** network, traffic, controllers, the command, number of runs.
3. **Measured:** the metrics.
4. **Closest paper(s):** what they did and found, with the page of the PDF; what they did not measure.
5. **What we add.**
6. **Our results:** the numbers, labelled *single run* or *mean of 5 runs ± 95% CI*.
7. **What it means.**
8. **Limits.**
9. **Data and details:** the raw-data folder and the detailed document.
10. **If asked:** one or two likely questions, with answers.

**Where the paper facts come from:**
- **[p.N]:** checked in the full text (PDFs in `docs/literature/papers/`).
- **[Abstract]:** abstract only.
- **[not page-checked]:** standard result, but the PDF is not in our folder yet.

Details of every paper: `docs/literature/Literature_Review_IdleHybrid.md` and `docs/literature/ML_Rule_Prediction_Survey.md`.

**Power mode.**
- **Balanced:** Review I, Step 1, Step 2 and the first Step 4 runs.
- **Best performance:** the Step 4 repeats.
- Absolute times differ between the two (up to 2×), so compare numbers only within one batch.

## Index

| # | Test | Closest paper(s) | Status |
| --- | --- | --- | --- |
| T1 | First-packet delay, reactive vs proactive | DIFANE, Ethane | Done (2 laptops) |
| T2 | Rules in the switches: all pairs, and under churn | DevoFlow, CacheFlow | Done |
| T3 | Controller load under realistic arrivals | Tootoonchian et al., DevoFlow | Done (single runs; repeats tonight) |
| T4 | Path quality: optimal vs haphazard path | Al-Fares, Hedera | Done |
| T5 | Flow completion time under realistic traffic | pFabric / PIAS workloads, Batista et al. | Done (single runs; repeats tonight) |
| T6 | Reactive with long timeouts | SmartTime, AH-IHTA | Done (4 scenarios × 5 runs) |
| T7 | Budgeted hybrid + oracle + uniform control | CacheFlow, PARD, Kim et al. | Done (4 scenarios × 5 runs) |
| T8 | ML predictor vs counter | Batista et al., Rouf & Yuksel | Bounded by the oracle; no ML model built |
| T9 | Controller on a separate PC | Kandoo, Ethane | Tool ready; run pending |
| T10 | Reproducibility on several machines | most papers above | Done |
| T11 | Reactive's cost split: path vs setup | DIFANE (setup), Al-Fares / Hedera (path) | Done (3 networks × 5 runs) |
| T12 | A larger network (fat-tree k = 6) | DevoFlow, CacheFlow | Smoke test done; sweep tonight |

---

## T1. First-packet delay: reactive vs proactive

**Question.** How much longer does the first packet of a new flow take when the rule must come from the controller, and does this grow with network size?

**Setup.**
- **Networks:** Mininet trees with 4, 8 and 16 hosts (`tree-d2-f2`, `tree-d3-f2`, `tree-d2-f4`).
- **Controllers:** `reactive_eval` (POX learning switch, exact-match rules, idle 10 s / hard 30 s) and `proactive_eval` (one rule per host pair, installed when a switch connects).
- **Traffic:** host pairs ping 6–10 times each, and packet 1 is compared with the later packets.
- **Command:** `sudo python3 experiments/run_experiments.py`.
- **Runs:** one run per laptop, two laptops.

**Measured.** Packet-1 RTT, packet-2 RTT, steady-state RTT.

**Closest papers.**
- **DIFANE** (Yu et al., SIGCOMM 2010):
  - **did:** a Click-based OpenFlow prototype against the NOX controller;
  - **found:** the first packet takes **10 ms with NOX against 0.4 ms with DIFANE**, and later packets 0.3 ms in both [p.9];
  - **missed:** one network size only, old software switches, and no link between the delay and the number of switches on the path.
- **Ethane** (Casado et al., SIGCOMM 2007):
  - **did:** a real 300-host deployment;
  - **found:** flows set up in **under 1.5 ms worst case** at up to 11,000 flows/s [p.9];
  - **missed:** it measures the controller's setup time, not the end-to-end first packet in networks of different sizes.

**What we add.** Three network sizes on a current Open vSwitch + POX stack, reproduced on two laptops, and the link between delay and path length.

**Our results** (single runs per laptop):

| | 4 hosts | 8 hosts | 16 hosts |
| --- | --- | --- | --- |
| Packet 1, reactive (laptop 1 / laptop 2) | 3.81 / 7.2 ms | 6.60 / 11.4 ms | 5.44 / 8.7 ms |
| Packet 1, proactive (laptop 1 / laptop 2) | 0.67 / 1.0 ms | 0.86 / 1.5 ms | 0.77 / 1.0 ms |
| Later packets, both | 0.06–0.09 ms | 0.07–0.09 ms | 0.09 ms |

**What it means.**
- Reactive's first packet is 5–8× slower; later packets are equal.
- The 8-host tree is the slowest because it has the longest paths: reactive sets the rule up switch by switch.
- Same trend as DIFANE; our absolute numbers are lower because our software stack is newer and faster.

**Limits.** Ping, not real flows (T5 covers real flows). Software switches only.

**Data and details.**
- **Raw data:** `results/measured/20260927-152012/` (laptop 1), `results/measured/20261009-112228/` (laptop 2).
- **Detailed document:** `docs/Progress_Review_1.md`; Review II Section 2.

**If asked.**
- **"Why is proactive's packet 1 still slower than packet 2?"** Open vSwitch fills its datapath cache on the first packet. No controller is involved.

---

## T2. Rules in the switches: all pairs, and under churn

**Question.** Does proactive really use more switch memory than reactive?

**Setup.**
- **Networks and controllers:** as T1.
- **Two traffic cases:**
  - every host pair active;
  - **churn:** new single-packet UDP flows at 10–200 per second, cbench-style.
- **Command:** `sudo python3 experiments/run_experiments.py`.

**Measured.** Rules per switch and in total (`ovs-ofctl dump-aggregate`); controller PACKET_IN/s and CPU under churn.

**Closest papers.**
- **DevoFlow** (Curtis et al., SIGCOMM 2011):
  - **did:** measured a real HP 5406zl switch, then simulated;
  - **found:** the switch holds "**16K exact-match rules and the 1500 wild-card rules**" [p.4] and completes only "roughly **275 flow setups per second**" [p.4];
  - **missed:** no direct count of how reactive exact-match rules pile up against proactive rules under churn.
- **CacheFlow** (Katta et al., SOSR 2016):
  - **did:** treated the table as a cache of popular rules;
  - **missed:** it does not compare against reactive installation.

**What we add.** A measured count, on the same network, of reactive vs proactive rules in both cases.

**Our results** (laptop 1, single runs):

| | 4 hosts | 8 hosts | 16 hosts |
| --- | --- | --- | --- |
| Rules, every pair active (proactive = reactive) | 28 | 216 | 624 |
| Rules after 5 s at 200 new flows/s: reactive vs proactive | 2,321 vs 28 (83×) | 3,857 vs 216 (18×) | 2,631 vs 624 (4×) |
| Controller at 200 new flows/s (reactive): PACKET_IN/s, CPU | 465, 20.8% | 786, 36.4% | 544, 31.6% |

**What it means.** "Proactive costs memory" is only half true:
- when every pair talks, both need the same rules;
- under churn, reactive's per-connection exact-match rules pile up to 4–83× more.

**Limits.** Synthetic churn (single packets); T5 repeats this with realistic traffic. Our networks are small, so proactive's N² rules stay small (see T12).

**Data and details.**
- **Raw data:** as T1.
- **Detailed document:** `docs/Progress_Review_1.md`.

**If asked.**
- **"Why does reactive have more rules than proactive?"** Exact-match rules: every new connection, with a new source port, gets its own rule on every switch of its path. A proactive pair rule covers all connections between two hosts.

---

## T3. Controller load under realistic flow arrivals

**Question.** How busy does the controller get with real traffic patterns, and does its load grow faster than the traffic?

**Setup.** The four Step 2 scenarios (see T5), reactive vs proactive.
- **Command:** `sudo python3 experiments/run_traffic_experiments.py`.
- **Runs:** single runs, Balanced mode. Repeats are scheduled tonight.

**Measured.** PACKET_IN/s, FLOW_MOD/s, controller CPU %, PACKET_INs per new flow.

**Closest papers.**
- **Tootoonchian et al.** (Hot-ICE 2012):
  - **did:** benchmarked controllers with cbench, using **synthetic** load from emulated switches;
  - **found:** NOX handles about **30k** flows/s; NOX-MT **1.6 M requests/s at 2 ms** on 8 cores [p.1, p.6];
  - **missed:** realistic traffic, and how load changes the number of requests per flow.
- **DevoFlow:**
  - **found:** a real switch completes only about 275 setups/s [p.4];
  - **missed:** the controller side under realistic traffic.

**What we add.** Controller load under university, data-centre and ISP traffic, and the **amplification effect**.

**Our results** (single runs):

| Scenario | New flows/s | PACKET_IN/s (reactive) | Controller CPU | Rules: reactive vs proactive |
| --- | --- | --- | --- | --- |
| University | 203 | 2,379 | 86.4% | 10,928 vs 624 |
| Data centre, web search | 39 | 514 | 44.3% | 4,623 vs 1,072 |
| Data centre, data mining | 57 | 738 | 56.3% | 6,083 vs 1,072 |
| ISP | 59 | 624 | 44.0% | 7,176 vs 386 |

**What it means.**
- **POX nears saturation:** 86% CPU at 203 new flows/s on university traffic.
- **Amplification:** one new flow caused about **12 PACKET_INs**, although it needs at most about 6 (up to 3 switches in each direction). While the controller is slow, more packets of the same flow reach the switch before its rule does, and each one asks again. In a lighter 10-s run (54% CPU) it was 7.4 per flow. This is a feedback loop towards overload.

**Limits.** POX is single-threaded Python, so absolute capacity is POX's, not a production controller's.

**Data and details.**
- **Raw data:** `results/measured/traffic-20261015-113417/`, `traffic-20261015-122618/`.
- **Detailed documents:** `docs/Realistic_Traffic_Experiment.md` Section 7; Review II Section 5.

**If asked.**
- **"Isn't POX just slow?"** Yes, and we say so. The trend matters: requests per flow grow with load. That holds for any controller near its own limit.

---

## T4. Path quality: optimal vs haphazard path

**Question.** On networks with many paths, which paths do the controllers actually use, and what does that cost in delay and throughput?

**Setup.**
- **Networks:**
  - **fat-tree k = 4:** 20 switches, 16 hosts, up to 4 equal paths;
  - **Abilene:** the real US backbone, 11 cities, 14 links, delays from fibre distance.
- **Links:** 10 Mbit/s, so only the path matters.
- **Controllers:**
  - reactive over POX's spanning tree ("haphazard");
  - proactive shortest path ("optimal");
  - proactive ECMP.
- **Traffic:**
  - **A:** 40 host pairs, pinged; the real path is read from the flow tables;
  - **B:** permutation traffic (every host sends one TCP flow at once), 3 permutations × 10 s.
- **Command:** `sudo python3 experiments/run_path_experiments.py`.

**Measured.** Hop stretch, delay stretch, share of pairs on a longer path, ping RTT, total throughput, Jain index over links, unused links.

**Closest papers.**
- **Al-Fares et al.** (SIGCOMM 2008):
  - **did / found:** the fat-tree design, and ECMP to use its many paths [not page-checked];
  - **missed:** how rules are installed.
- **Hedera** (Al-Fares et al., NSDI 2010):
  - **did / found:** scheduling large flows, because ECMP hash collisions waste capacity [not page-checked];
  - **missed:** the reactive vs proactive question.
- **The reactive vs proactive papers (T1, T2):** do not measure paths at all.

**What we add.** We link the installation mode to path quality, on a data-centre network and on a real ISP map.

**Our results** (single run; paths are deterministic):

| Network | Controller | Delay stretch mean / max | Pairs on a longer path | Ping RTT | Throughput (ideal) | Unused links |
| --- | --- | --- | --- | --- | --- | --- |
| Fat-tree | Reactive | hop stretch 1.11 / 1.50 | 22% | 0.14 ms | 63.6 Mbit/s (160) | 59% |
| Fat-tree | Proactive | 1.00 | 0% | 0.13 ms | 61.7 | 63% |
| Fat-tree | Proactive ECMP | 1.00 | 0% | 0.13 ms | **95.3** | **16%** |
| Abilene | Reactive | **1.58 / 4.47** | **70%** | **40.5 ms** | 42.1 (110) | 29% |
| Abilene | Proactive | 1.00 | 0% | 26.9 ms | **60.7** | 20% |

**What it means.**
- **ISP:** reactive's spanning tree switches off 4 of Abilene's 14 links, so 70% of pairs take a slower path.
  - Example: Atlanta → Washington has a direct link (4.4 ms), but reactive goes through Houston, Kansas City, Indianapolis, Chicago and New York (about 23 ms).
- **Data centre:** one shortest path is no better than reactive; only ECMP uses the extra paths (+50% throughput).

**Limits.** Straight-line delays are a lower bound (real cables are longer). ECMP is per host pair, not per flow.

**Data and details.**
- **Raw data:** `results/measured/paths-20261015-094800/`.
- **Detailed documents:** `docs/Path_Quality_Experiment.md`; Review II Section 4.

**If asked.**
- **"Isn't this unfair to reactive?"** A plain learning switch needs the spanning tree, or broadcasts loop. T11 also measures reactive on shortest paths.

---

## T5. Flow completion time under realistic traffic

**Question.** With real traffic patterns (mostly tiny flows, a few huge ones), how much slower are flows under reactive?

**Setup.**
- **Scenarios** (each network carries the traffic measured in that kind of network):

  | Scenario | Network | Traffic | Source |
  | --- | --- | --- | --- |
  | University | tree, 16 hosts | Benson Fig. 4(a) sizes; Weibull gaps, 80% within 4–40 ms | Benson et al., IMC 2010 [p.2, p.6, p.7] |
  | Web search | fat-tree k = 4 | `CDF_dctcp.tcl`, Poisson, 30% load | DCTCP via pFabric / PIAS |
  | Data mining | fat-tree k = 4 | `CDF_vl2.tcl`, Poisson, 30% load | VL2 via pFabric / PIAS |
  | ISP | Abilene | real hourly traffic matrices (1 Mar 2004); SURGE sizes (checked against the paper's Table 1 and Section 4) | Zhang et al., IMC 2005; Barford & Crovella 1998 |

- **Links:** 100 Mbit/s; flows capped at 20 MB.
- **Fairness:** the same flow schedule for every controller.
- **Command:** `sudo python3 experiments/run_traffic_experiments.py`.
- **Runs:** single runs, Balanced mode; repeats are scheduled tonight.

**Measured.** Flow completion time (FCT) of small (< 100 KB), medium and large (> 10 MB) flows: mean, median, 99th percentile; failed flows.

**Closest papers.**
- **pFabric / PIAS:**
  - **did:** published the web-search and data-mining workloads, to test transport protocols;
  - **missed:** never used them to compare rule-installation strategies.
- **Batista et al.** (Discover IoT 2024):
  - **did:** reactive vs LSTM pre-installation, on Mininet + POX/Ryu;
  - **found:** **about 51% lower response time** [p.3];
  - **missed:** only periodic IoT traffic.

**What we add.** Reactive vs proactive vs ECMP flow completion times under university, data-centre and real ISP traffic.

**Our results** (single runs; small-flow median / p99 in ms; large-flow mean in s):

| Scenario | Reactive | Proactive | Proactive ECMP |
| --- | --- | --- | --- |
| University | **55.7** / 126.0 | **1.3** / 37.9 | - |
| Web search | 155.3 / 343.5; large 12.2 s | 62.6 / 242.0; large 12.8 s | **19.2** / 170.8; large **3.5 s** |
| Data mining | 113.0 / 244.2; large 10.9 s | 24.9 / 111.0; large 10.7 s | **11.5** / 67.7; large **3.6 s** |
| ISP | **120.0** / 405.7 | **48.1** / 198.4 | - |

0 failed flows in every run.

**What it means.**
- **University:** small flows are 44× slower with reactive. The network is only 6% loaded, so the whole difference is the setup cost.
- **Data centre:** small flows are 8–10× faster with ECMP. Large flows depend on load balance, not on the controller.
- **ISP:** 2.5× slower; T11 splits this into path and setup.

**Limits.** Generated traffic, not replayed packets (except the ISP volumes, which are real). The university size curve was read from a plot.

**Data and details.**
- **Raw data:** as T3.
- **Detailed documents:** `docs/Realistic_Traffic_Experiment.md`; `docs/Realism_Sources.md` (the paper behind every parameter).

**If asked.**
- **"How do you know every controller saw the same traffic?"** The schedule is computed before the controller starts, from a seed (`experiments/workloads.py`).

---

## T6. Reactive with long timeouts

**Question.** Is "just keep reactive rules longer" enough to get most of proactive's benefit?

**Setup.**
- **Controller:** reactive with idle 60 s / hard 300 s, against the default 10 s / 30 s.
- **Traffic:** all four Step 4 scenarios: university Zipf, fat-tree web search, Abilene, university uniform.
- **Command:** `--budget-sweep` (it includes `reactive-long`).
- **Runs:** **5 runs, seeds 7–11, Best performance mode.**

**Measured.** Small-flow FCT, PACKET_IN/s, peak rules.

**Closest papers.**
- **SmartTime** (Vishnoi et al., DEBS 2014):
  - **did:** adaptive idle timeouts plus proactive eviction, on real data-centre traces;
  - **found:** up to **58% lower total cost** than the best static timeout [p.1];
  - **missed:** no comparison against proactive or a hybrid on the same traffic; no flow completion times; no path quality.
- **AH-IHTA** (Isyaku et al., 2020):
  - **found:** **28% fewer flow-setup requests** and 39% fewer evictions [p.1];
  - **missed:** the same gaps as SmartTime.

**What we add.** Long timeouts against reactive, proactive and a hybrid, on the same realistic traffic, with all metrics.

**Our results** (mean of 5 runs ± 95% CI; small-flow median):

| Scenario | Reactive | Reactive, long timeouts | Rules: long vs normal |
| --- | --- | --- | --- |
| University, Zipf | 27.9 ± 2.4 ms | 29.6 ± 4.1 ms | 32,363 vs 10,965 (3.0×) |
| Fat-tree | 110.8 ± 38.0 ms | 111.7 ± 36.1 ms | 10,643 vs 4,406 (2.4×) |
| Abilene | 96.8 ± 6.8 ms | 97.3 ± 6.2 ms | 16,332 vs 7,339 (2.2×) |
| University, uniform | 23.6 ± 0.7 ms | **25.7 ± 0.8 ms** (significantly slower) | 31,644 vs 10,836 (2.9×) |

PACKET_IN/s is the same within the intervals in every scenario.

**What it means.**
- No gain anywhere, and 2.2–3.0× the rules.
- **Why:** reactive rules are exact matches, and every new TCP connection has a new source port, so a rule kept longer is never matched again. Timeouts only help when the same 5-tuple repeats, or when the rules are coarser.
- This does not contradict SmartTime: their gains come from traces where rules do get reused, and from eviction under a full table.

**Limits.** We tested one fixed long timeout, not SmartTime's adaptive algorithm.

**Data and details.**
- **Raw data:** `results/measured/traffic-20261015-225412/`, `-233914/`, `traffic-20261016-004215/`, `-012626/`.
- **Detailed documents:** `docs/Budgeted_Hybrid_Experiment.md` Section 4.0; Review II Section 6.

**If asked.**
- **"Why didn't you implement SmartTime itself?"** The fixed long timeout is the best case for "keep rules longer": it never evicts a useful rule. If even that gives no gain on short-flow traffic, an adaptive timeout cannot give one either, because the rules are never reused.

---

## T7. Budgeted hybrid, oracle and uniform control

**Question.** If only a fraction of the host pairs may have pre-installed rules, how much of proactive's benefit does that buy, and how close is a simple counter to the best possible choice?

**Setup.**
- **Controller** (`controllers/hybrid_eval.py`): reactive on shortest paths, plus pair rules (source MAC + destination MAC) for the top-K pairs by a decaying counter:
  - every second, `score = 0.97 × score + (1 if used this second)`;
  - hysteresis 1.5.
- **Budgets:** 10 / 25 / 50% of all host pairs.
- **Oracle:** pre-installs the K pairs that really carry the most flows in the run, before the first flow (it reads the flow schedule).
- **Traffic:**
  - university and fat-tree with Zipf pair popularity (exponent 1);
  - Abilene with its real matrices;
  - a control run with uniform pairs.
- **Command:** `--budget-sweep --pair-zipf 1`.
- **Runs:** **5 runs, seeds 7–11.**

**Measured.**
- **Hit rate:** the share of new TCP connections whose first packet found a rule at the sender's switch.
- **Also:** pair installs, wasted installs, small-flow FCT, PACKET_IN/s, peak rules.

**Closest papers.**
- **CacheFlow** (Katta et al., SOSR 2016):
  - **did:** caches the most popular policy rules in hardware, on Zipf traffic;
  - **found:** **90% hits with < 5% of rules** [p.2]; real REANNZ trace: **84% with 2%, 97% with 10%** [p.9];
  - **missed:** no comparison against reactive or proactive installation, and no flow completion times.
- **PARD** (Rzepka et al., 2020):
  - **did:** coarse proactive plus detailed reactive entries;
  - **found:** "significantly reduces" first-packet latency [Abstract];
  - **missed:** no popularity, no budget.
- **Kim et al.** (Electronics 2022):
  - **did:** per-flow proactive or reactive choice, using an LSTM-predicted controller delay; simulation on the Abilene topology;
  - **found:** better hit ratio and install delay than earlier schemes [p.1, p.11];
  - **missed:** simulation only, and graphs without headline numbers.

**What we add.** Hit rate, flow completion time, controller load and rules against the rule budget, on realistic traffic and three networks, compared with an **oracle** upper bound and a **uniform-traffic control**.

**Our results** (mean of 5 runs ± 95% CI):

| Scenario | Counter hit rate, 10 / 25 / 50% | Oracle hit rate, 10 / 25 / 50% | Counter ÷ oracle |
| --- | --- | --- | --- |
| University, Zipf | 30.8 ± 10.2 / 60.7 ± 5.5 / 78.9 ± 1.8 | 49.3 ± 6.0 / 68.2 ± 4.3 / 84.7 ± 2.1 | 0.62 / 0.89 / 0.93 |
| Fat-tree, web search | 51.1 ± 1.6 / 65.8 ± 1.4 / 77.4 ± 1.8 | 56.2 ± 1.3 / 73.7 ± 1.2 / 88.3 ± 0.7 | 0.91 / 0.89 / 0.88 |
| Abilene | 26.6 ± 2.3 / 53.8 ± 2.3 / 77.2 ± 1.8 | 33.1 ± 1.0 / 59.2 ± 0.8 / 83.0 ± 1.0 | 0.80 / 0.91 / 0.93 |
| University, uniform | 9.6 ± 0.2 / 24.5 ± 1.2 / 48.4 ± 0.2 | 12.5 ± 0.2 / 29.4 ± 0.5 / 55.4 ± 0.6 | – |

At a 25% budget, against reactive on shortest paths:

| Scenario | PACKET_IN/s | Peak rules | Small-flow median |
| --- | --- | --- | --- |
| University | 2,549 → 936 (2.7×) | 10,983 → 5,278 (2.1×) | 27.3 → 8.4 ms |
| Fat-tree | 492 → 180 (2.7×) | 3,752 → 1,569 (2.4×) | 59.3 → 38.2 ms |
| Abilene | 447 → 198 (2.3×) | 5,321 → 2,615 (2.0×) | 55.6 → 50.0 ms |

Proactive, for reference: 0 PACKET_IN/s; 624 / 1,072 / 386 rules; median 0.96 / 28.6 / 46.0 ms.

**Extra runs.**
- **Warm-up check** (120 s instead of 30 s, university, 10%, single run): the counter's hit rate rose from 24.5% to 38.1%; the oracle stayed at 51.5%.
- **Decay 0.9** (single run): 36.7% at 10%, which is inside the 0.97 spread. Inconclusive; repeats are scheduled tonight.

**What it means.**
1. **With skewed traffic, a quarter of the pairs removes most of the setup cost.** 54–66% of new connections skip the controller, with **fewer** rules than reactive: one pair rule replaces many per-connection rules.
2. **The gain comes from skew.** With uniform pairs, a budget of B% buys about B%.
3. **The simple counter reaches 0.88–0.93 of a perfect predictor** at 25–50% budgets.
4. **Its weak spot is small budgets with many flows per pair** (university, 10%). The counter scores "busy seconds", not flows, so pairs with 1.4 and 0.8 flows/s look alike.
5. **Proactive still wins on these small networks** (see T12 for a larger one).

**Limits.**
- The hybrid is close to CacheFlow and PARD, and it is not a new algorithm.
- Zipf popularity is an assumption (from CacheFlow), except for Abilene.
- The oracle is the best **fixed** set: right for our traffic, whose popularity does not change during a run.

**Data and details.**
- **Raw data:** as T6, plus `traffic-20261015-211130/` (warm-up) and `traffic-20261016-021112/` (decay).
- **Detailed documents:** `docs/Budgeted_Hybrid_Experiment.md` (Sections 1 and 4.0); Review II Section 6; figure `docs/figures/step4_hit_rate.png`.

**If asked.**
- **"What is the oracle, and isn't it cheating?"** It cheats on purpose. It knows the future flow schedule, so it gives the best hit rate any predictor could reach with the same budget. Same idea as Belady's optimal algorithm in caching.
- **"Why is CacheFlow's hit rate higher?"** CacheFlow counts packets of policy rules on traces with a strong skew. We count new connections between host pairs, on 110–240 pairs. Same direction, smaller effect.

---

## T8. ML predictor vs counter

**Question.** Would a machine-learning predictor choose the pre-installed pairs better than a simple counter?

**Setup.** No ML model was built. The oracle from T7 gives the best possible choice for each budget, and the gap between the oracle and the counter bounds what *any* predictor could add.

**Closest papers.**
- **Batista et al.** (2024):
  - **did:** LSTM pre-installation, on Mininet + POX/Ryu;
  - **found:** 51% faster than reactive [p.3];
  - **missed:** compared only with plain reactive, on periodic IoT traffic.
- **Rouf & Yuksel** (arXiv 2025):
  - **did:** DQN-based rule eviction, on IoT traces;
  - **found:** about **8% better than LFU** [Abstract];
  - **missed:** it is eviction, not pre-installation.
- **Our survey of 28 papers:** we found no paper that compared ML pre-installation with a simple frequency counter at the same rule budget (`docs/literature/ML_Rule_Prediction_Survey.md`, Section D).

**What we add.** A measured upper bound on what prediction can gain, on non-IoT realistic traffic.

**Our results** (from T7):
- **25–50% budgets:** a perfect predictor would add only **5–11 percentage points** of hit rate over the counter.
- **10% budget:** the gap is larger (university: 18.5 points), and part of it is our counter's design.

**What it means.** On this traffic, ML has little room.
- **Where ML could matter:** traffic where flows on one pair predict flows on *other* pairs (microservice call chains), at a scale where most pairs are idle.
- **Why we did not test that:** it needs hundreds of hosts, beyond a laptop emulation.

**Limits.**
- An upper bound, not a measured ML model.
- The oracle is the best fixed set; with traffic whose popularity changes over time, a predictor that adapts could gain more.

**Data and details.** As T7.

**If asked.**
- **"Why not just try XGBoost?"** On our traffic the oracle already shows the most it could gain. A model that at best ties a counter adds cost (training, inference on every decision) and no evidence.

---

## T9. Controller on a separate PC

**Question.** Does a real network between the switches and the controller, and a controller with its own CPU, change reactive's cost?

**Setup.**
- POX runs on PC B, started remotely by `experiments/controller_agent.py`. Mininet and the traffic run on PC A, with `--controller-host <PC B>`.
- On WSL2 this needs mirrored networking and two firewall rules (`docs/Controller_On_Second_PC.md`).

**Measured.** All T5/T7 metrics, plus the round-trip time between the PCs (median of 20 TCP handshakes).

**Closest papers.**
- **Kandoo** (HotSDN 2012):
  - **did:** two layers of controllers;
  - **found:** the root controller's load drops 5× in packets [p.4];
  - **missed:** emulation; it does not measure the effect of the switch-to-controller delay itself.
- **Ethane:** a real deployment [p.1, p.9], but an older stack, and no comparison of strategies.
- **Most papers above:** run controller and switches on one machine, or in simulation.

**What we add.** The effect of a real control channel on reactive's cost, with the same traffic as T5 and T7.

**Our results.** **Pending.**
- **Done so far:** the tool is tested end to end on one machine (agent at 127.0.0.1): start and stop POX, stats, CPU time, log copy-back, and repeats.
- **Needed:** a second laptop for one evening.

**What we expect.**
- **Reactive:** gets slower by about one control-channel round trip per switch on the path.
- **Proactive:** no change, because it does not talk to the controller during the run.
- **The hybrid:** in between, in proportion to its miss rate.

**Data and details.** `docs/Controller_On_Second_PC.md`.

---

## T10. Reproducibility on several machines

**Question.** Are the results specific to one laptop?

**Setup.** The same commands on laptop 1, laptop 2 (Review I) and a cloud VM (Steps 1 and 4).

**Closest papers.** Most papers above report one testbed and do not repeat on different machines.

**Our results.**
- **Review I:** the same patterns on two laptops; **identical rule counts**; the 8-host tree slowest on both.
- **Step 1:** **identical paths** on the laptop and a cloud VM.
- **Step 4:** the same ranking of all ten controllers on the laptop and the cloud VM. Absolute times differ: the cloud VM uses a slower userspace datapath.
- **Within one laptop:** 5 seeds per configuration give 95% confidence intervals (T6, T7, T11).

**Limits.** All machines ran Mininet + Open vSwitch; no hardware switch.

**Data and details.**
- **Raw data:** `results/measured/` (laptop runs); `results/validation_*` (cloud runs).

---

## T11. Reactive's cost split: path vs setup

**Question.** When reactive is slower, how much of that is asking the controller (**setup**), and how much is the spanning tree's longer paths (**path**)?

**Setup.** The same reactive logic run two ways, on the same traffic:
- over the spanning tree (`reactive`);
- on shortest paths (`reactive-sp` = `hybrid_eval` with budget 0).

So: path cost = reactive − reactive-sp; setup cost = reactive-sp − proactive. Three networks, **5 runs each**.

**Measured.** Small-flow median FCT.

**Closest papers.**
- **The setup-cost papers** (DIFANE [p.9], DevoFlow [p.4]): measure setup without path effects.
- **The path papers** (Al-Fares, Hedera): measure paths without installation effects.
- **We found no paper** that separates the two for the same reactive controller and traffic.

**What we add.** The split itself, measured, and how it changes with controller speed.

**Our results** (mean of 5 runs; small-flow median):

| Scenario | Reactive | Reactive, shortest paths | Proactive | **Path** | **Setup** |
| --- | --- | --- | --- | --- | --- |
| University tree | 27.9 ms | 27.3 ms | 0.96 ms | 0.6 ms (noise) | **26 ms** |
| Fat-tree | 110.8 ± 38.0 ms | 59.3 ± 6.6 ms | 28.6 ms (ECMP) | **52 ms** | 31 ms (includes ECMP) |
| Abilene | 96.8 ± 6.8 ms | 55.6 ± 2.0 ms | 46.0 ms | **41 ms** | 10 ms |

In the earlier Balanced-mode single runs, the setup parts were 52 / 78 / 26 ms and the path parts about the same (0 / 39 / 44 ms).

**What it means.**
- **On a tree, reactive's whole cost is setup.** On networks with loops, a large part is the spanning tree; on Abilene, 81%.
- **A faster CPU shrinks only the setup part.** A faster controller can hide setup cost, never path cost.
- Review II Section 5's first estimate for the ISP (27 ms path, 40 ms setup) had the two the wrong way round; this measurement corrects it.

**Limits.** The fat-tree's reactive median varies a lot (± 38 ms), so its path number is the least certain.

**Data and details.**
- **Raw data:** as T6.
- **Detailed documents:** figure `docs/figures/step4_cost_split.png`; Review II Section 6, finding 2.

**If asked.**
- **"Why does the CPU change only the setup part?"** Path delay is propagation and queueing on the links. CPU speed changes how fast POX answers a PACKET_IN, not how long a packet travels.

---

## T12. A larger network: fat-tree k = 6

**Question.** Does the picture change when proactive needs thousands of rules?

**Setup.**
- **Network:** fat-tree k = 6: 45 switches, 54 hosts, 2,862 host pairs.
- **Traffic:** web search at 5% load (the laptop's limit).
- **Budgets:** 2 / 5 / 10% (the range CacheFlow studied).
- **Command:** `--scenarios fattree-k6:websearch --budget-sweep --budgets 2 5 10 --load 0.05 --pair-zipf 1 --repeats 3` (tonight).

**Closest papers.**
- **DevoFlow:** a real switch holds 16K exact-match and 1,500 wildcard rules [p.4].
- **CacheFlow:** 84–97% hits with 2–10% of rules [p.9].

**Our results so far** (smoke test, single run, 0 failed flows):

| Controller | Small-flow mean | Peak rules, all switches | Peak rules, busiest switch |
| --- | --- | --- | --- |
| Proactive ECMP | 9.8 ms | **13,230** | 312 |
| Reactive, shortest paths | 47.4 ms | **2,058** | 80 |

**What it means.**
- **On 16 hosts, proactive had the fewest rules; on 54 hosts it has 6.4× more than reactive.** This is the N² cost.
- **Per switch it still fits.** A switch's capacity is per switch, and proactive's busiest switch holds 312 pair rules. Pair rules match only MAC addresses, so on hardware they would sit in the TCAM. That is within the 1,500 wildcard rules of DevoFlow's switch.
- **Where it stops fitting:** an edge switch of a k-ary fat-tree needs about k × N pair rules (N = k³/4 hosts). At k = 10 (250 hosts) that is about 2,500, above the 1,500. So the budget becomes necessary at a few hundred hosts: larger than we can emulate, and small for a real data centre.

**Status.** The budget sweep runs tonight.

---

## Not yet tested (and why)

- **Hardware switches:** none available. The limit is stated in every report.
- **Adaptive timeouts (SmartTime's algorithm itself):** T6 shows that even the best-case fixed long timeout gives no gain on short-flow traffic.
- **ML predictor:** bounded by the oracle (T8).
- **Microservice call-chain traffic:** needs hundreds of hosts (T8).
