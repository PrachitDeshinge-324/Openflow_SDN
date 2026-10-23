# Test Catalogue: Every Test, Its Closest Paper, and What We Found

CS G525 Advanced Computer Networks, Project SA7, Group 2. Status: 16 October 2026.

**One section per test, always in the same order:**
1. **Question:** what the test answers.
2. **Configuration:** hosts, switches, links, link speed and delay, controllers and their parameters, traffic, runs and seeds, power mode, the exact command. The parts common to every test (machines, software versions, controller options, network sizes) are in **Testbed** below.
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

## Testbed (common to every test)

### Machines

| Machine | Used for | OS / kernel | CPU | Open vSwitch datapath |
| --- | --- | --- | --- | --- |
| **Laptop 1** ("Harikrushna", Mrudul) | every test | Windows 11 + WSL2 Ubuntu, kernel 6.18.33.2-microsoft-standard-WSL2 | 16 hardware threads | kernel |
| **Laptop 2** ("Nisarg") | T1, T2 reproduction (9 Oct) | Windows 11 + WSL2 Ubuntu, kernel 6.18.40.1-microsoft-standard-WSL2 | – | kernel |
| **Cloud VM** | T10 checks only (never in a results table) | Linux 6.18, Python 3.11.15 | 4 vCPUs | userspace (OVS 3.3.9, no netem) |

### Software (laptops)

| Component | Version |
| --- | --- |
| Emulator | Mininet 2.3.0 |
| Switch | Open vSwitch 3.7.1, kernel datapath, OpenFlow 1.0 |
| Controller | POX 0.7.0 (`gar`, commit 5f82461), stored in `pox/`; single-threaded Python |
| Python | 3.14.4 |
| Our code | `controllers/` (POX modules), `experiments/` (harnesses), on GitHub `main` |

### Settings that are the same in every test

- **Controller placement:** the controller runs on the same machine, at `127.0.0.1:6633`, except T9.
- **Addressing:** Mininet assigns MAC and IP addresses in order (h1 = 10.0.0.1, 00:00:00:00:00:01, ...).
- **ARP:** static ARP tables on every host (`net.staticArp()`), so ARP never reaches the controller and does not distort the timings.
- **IPv6:** turned off on every host, so no IPv6 neighbour traffic is generated.
- **Seeds:** default seed 7. With repeats, the seeds are 7, 8, 9, 10, 11; each seed gives a new flow schedule, and the same seed gives the same schedule for every controller.
- **Power mode:**
  - Windows "Balanced": Review I, Step 1, Step 2 and the first Step 4 single runs;
  - "Best performance": every 5-run repeat (16 Oct onwards).
  - Compare absolute times only within one batch. The same configuration measured on two nights gave different reactive times (see T10), so a confidence interval covers run-to-run noise within a night, not drift between nights.

### Controllers

| Name in tables | Module and options | Rules it installs | Used in |
| --- | --- | --- | --- |
| Reactive (Review I) | `reactive_eval --match=exact --idle_timeout=10 --hard_timeout=30` (POX `l2_learning` logic) | one exact-match rule (in_port, MACs, IPs, protocol, ports) per new flow per switch, on the first packet; floods unknown destinations | T1, T2 |
| Reactive (Steps 1, 2, 4) | the same, plus POX `openflow.discovery` + `openflow.spanning_tree --no-flood --hold-down`, on every network (on a tree the spanning tree is the whole tree) | as above, along the spanning tree only | T3–T7, T11, T12 |
| Reactive, long timeouts | as Reactive, `--idle_timeout=60 --hard_timeout=300` | as Reactive | T6 |
| Reactive on shortest paths | `hybrid_eval --budget=0` (knows the topology) | exact-match rules, hop by hop, on the lowest-delay path (ECMP on fat-trees) | T7, T11 |
| Hybrid counter NN% | `hybrid_eval --budget=0.NN --decay=0.97 --hysteresis=1.5 --interval=1` | Reactive on shortest paths, plus pair rules (source MAC + destination MAC, priority 100) on every switch of the path, for the top-K pairs by score | T7 |
| Oracle NN% | `hybrid_eval --pairs_file=...` | pair rules for the K busiest pairs of the run (both directions), installed before the first flow; the rest reactive | T7, T8 |
| Random NN% | `hybrid_eval --pairs_file=...` | pair rules for K random pairs (both directions), before the first flow; the rest reactive | T7 |
| Proactive | `proactive_eval --granularity=pair --paths=shortest --miss=drop` | one pair rule per ordered host pair on every switch of its lowest-delay path, installed when the switch connects; table-miss rule drops | all |
| Proactive ECMP | `proactive_eval --paths=ecmp` | as Proactive, with pairs hashed (CRC32 of the two MACs) over the equal-cost paths | T4, T5, T7, T11, T12 |

### Networks

| Name | What it models | Hosts | Switches | Links (switch–switch + host) | Host pairs (ordered) | Link speed | Link delay |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `tree-d2-f2` | small campus tree | 4 | 3 | 2 + 4 | 12 | unshaped (T1, T2) | none |
| `tree-d3-f2` | deeper tree | 8 | 7 | 6 + 8 | 56 | unshaped (T1, T2) | none |
| `tree-d2-f4` | campus tree | 16 | 5 | 4 + 16 | 240 | unshaped (T1, T2); 100 Mbit/s (T3, T5–T7) | none |
| `fattree-k4` | data centre (Al-Fares 2008) | 16 | 20 (4 core, 8 aggregation, 8 edge) | 32 + 16 | 240 | 10 Mbit/s (T4); 100 Mbit/s (T3, T5–T7) | none |
| `abilene` | US research backbone, 11 cities | 11 (one per city) | 11 | 14 + 11 | 110 | 10 Mbit/s (T4); 100 Mbit/s (T3, T5–T7), Atlanta–Indianapolis at ¼ | one-way 1.33–11.03 ms per link (city distance ÷ 200 km/ms, netem) |
| `fattree-k6` | larger data centre | 54 | 45 (9 core, 18 aggregation, 18 edge) | 108 + 54 | 2,862 | 100 Mbit/s | none |

"Unshaped" means Mininet's default virtual Ethernet links, with no bandwidth limit and no added delay.

---

## Index

| # | Test | Closest paper(s) | Status |
| --- | --- | --- | --- |
| T1 | First-packet delay, reactive vs proactive | DIFANE, Ethane | Done (2 laptops) |
| T2 | Rules in the switches: all pairs, and under churn | DevoFlow, CacheFlow | Done |
| T3 | Controller load under realistic arrivals | Tootoonchian et al., DevoFlow | Done (5 runs) |
| T4 | Path quality: optimal vs haphazard path | Al-Fares, Hedera | Done |
| T5 | Flow completion time under realistic traffic | pFabric / PIAS workloads, Batista et al. | Done (5 runs) |
| T6 | Reactive with long timeouts | SmartTime, AH-IHTA | Done (4 scenarios × 5 runs) |
| T7 | Budgeted hybrid + oracle + random baseline + uniform control | CacheFlow, PARD, Kim et al. | Done (4 scenarios × 5 runs; random baseline × 5 runs) |
| T8 | ML predictor vs counter | Batista et al., Rouf & Yuksel | Bounded by the oracle; no ML model built |
| T9 | Controller on a separate PC | Kandoo, Ethane | Tool ready; run pending |
| T10 | Reproducibility on several machines | most papers above | Done |
| T11 | Reactive's cost split: path vs setup | DIFANE (setup), Al-Fares / Hedera (path) | Done (3 networks × 5 runs) |
| T12 | A larger network (fat-tree k = 6) | DevoFlow, CacheFlow | Done (3 runs) |

---

## T1. First-packet delay: reactive vs proactive

**Question.** How much longer does the first packet of a new flow take when the rule must come from the controller, and does this grow with network size?

**Configuration.**

| Item | Value |
| --- | --- |
| Networks | `tree-d2-f2` (4 hosts, 3 switches), `tree-d3-f2` (8 hosts, 7 switches), `tree-d2-f4` (16 hosts, 5 switches) |
| Links | unshaped (no bandwidth limit, no added delay) |
| Controllers | Reactive (Review I): exact match, idle 10 s / hard 30 s, no spanning tree (trees have no loops); Proactive: pair rules, installed when each switch connects |
| Traffic | 20 random host pairs (all 6 on the 4-host tree), 10 pings per pair, 0.1 s apart; packet 1 = new flow, packet 2, then the median of packets 3–10 = steady state |
| Runs | one run per laptop, seed 7: laptop 1 (27 Sep), laptop 2 (9 Oct); Balanced power mode |
| Command | `sudo python3 experiments/run_experiments.py` (defaults: `--pairs 20 --count 10 --interval 0.1`) |

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

**Configuration.**

| Item | Value |
| --- | --- |
| Networks and controllers | as T1 (4, 8 and 16 hosts; Reactive (Review I) and Proactive) |
| Links | unshaped |
| Traffic, case 1 ("occupancy") | 25%, 50% and 100% of all host pairs made active (3 pings each), reactive rules cleared before each step; rules counted 1.5 s later |
| Traffic, case 2 ("churn") | h1 sends single UDP packets to random other hosts (UDP port 9) at 10, 50, 100 and 200 new flows/s, 5 s per rate. Each packet uses a new socket, so a new source port, so a new flow. Reactive rules cleared before each rate |
| Runs | one run per laptop, seed 7, two laptops; Balanced power mode |
| Command | `sudo python3 experiments/run_experiments.py` (defaults: `--fractions 0.25 0.5 1.0 --rates 10 50 100 200 --churn-duration 5`) |

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

**Configuration.**

| Scenario | Network | Hosts | Switches | Host pairs | Link speed / delay |
| --- | --- | --- | --- | --- | --- |
| University | `tree-d2-f4` | 16 | 5 | 240 | 100 Mbit/s, no delay |
| Web search | `fattree-k4` | 16 | 20 | 240 | 100 Mbit/s, no delay |
| Data mining | `fattree-k4` | 16 | 20 | 240 | 100 Mbit/s, no delay |
| ISP | `abilene` | 11 | 11 | 110 | 100 Mbit/s (Atlanta–Indianapolis 25 Mbit/s), city delays 1.33–11.03 ms |

| Item | Value |
| --- | --- |
| Controllers | Reactive (Steps 1, 2, 4), Proactive, and Proactive ECMP on the fat-tree |
| Traffic | the four published workloads of T5, 30 s of flow arrivals each |
| Measurement window | the 30 s of arrivals; controller counters read from POX's own stats; CPU from `/proc` for the POX process; rules sampled every 5 s (`ovs-ofctl dump-aggregate`, data rules only) |
| Runs | **5 runs, seeds 7–11**, uniform host pairs, Best performance mode (night of 17–18 Oct); the first single runs (seed 7, Balanced) are in `traffic-20261015-113417/` and `-122618/` |
| Command | `sudo python3 experiments/run_traffic_experiments.py` (defaults: `--duration 30 --bw 100 --load 0.3 --max-mb 20 --flow-timeout 30`) |

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

**Our results** (reactive, mean of 5 runs ± 95% CI):

| Scenario | New flows/s | PACKET_IN/s | PACKET_INs per new flow | Controller CPU | Rules: reactive vs proactive |
| --- | --- | --- | --- | --- | --- |
| University | 203.1 | 2,417 ± 47 | 11.9 | 72.2 ± 4.8% | 10,836 ± 196 vs 624 (17×) |
| Web search | 37.9 | 489 ± 22 | 12.9 | 36.5 ± 4.5% | 4,329 ± 419 vs 1,072 (4.0×) |
| Data mining | 56.3 | 684 ± 29 | 12.1 | 47.0 ± 4.1% | 5,862 ± 218 vs 1,072 (5.5×) |
| ISP | 58.3 | 611 ± 20 | 10.5 | 31.9 ± 3.5% | 7,332 ± 160 vs 386 (19×) |

The first single runs (Balanced mode) gave 2,379 PACKET_IN/s at 86.4% CPU on university traffic; the faster power mode lowered the CPU share, not the request rate.

**What it means.**
- **POX is busy but not saturated:** 72% of one core at 203 new flows/s (86% in the first, slower-mode run). The request rate is the same in both, so the load is set by the traffic, not by the machine.
- **Amplification:** one new flow caused **10.5–12.9 PACKET_INs** in every scenario, although it needs at most about 6 (up to 3 switches in each direction). While the controller is slow, more packets of the same flow reach the switch before its rule does, and each one asks again. In a lighter 10-s run (54% CPU) it was 7.4 per flow. This is a feedback loop towards overload.

**Limits.** POX is single-threaded Python, so absolute capacity is POX's, not a production controller's.

**Data and details.**
- **Raw data:** as T5.
- **Detailed documents:** `docs/Realistic_Traffic_Experiment.md`; Review II Section 5.

**If asked.**
- **"Isn't POX just slow?"** Yes, and we say so. The trend matters: requests per flow grow with load. That holds for any controller near its own limit.

---

## T4. Path quality: optimal vs haphazard path

**Question.** On networks with many paths, which paths do the controllers actually use, and what does that cost in delay and throughput?

**Configuration.**

| Item | Value |
| --- | --- |
| Networks | `fattree-k4` (16 hosts, 20 switches, 48 links, up to 4 equal paths between pods); `abilene` (11 hosts, 11 switches, 25 links, one-way delays 1.33–11.03 ms) |
| Links | **10 Mbit/s** on every link, so the links (not the laptop) are the bottleneck |
| Controllers | Reactive over the spanning tree ("haphazard"), Proactive shortest path ("optimal"), Proactive ECMP |
| Traffic A (paths) | 40 random host pairs (the same for every controller), 6 pings each, 0.1 s apart; the real path is read from the flow tables (`ovs-ofctl dump-flows`) and compared with the best possible path |
| Traffic B (throughput) | every host sends one TCP flow to another at the same time (random permutation with no host sending to itself): 16 flows on the fat-tree, 11 on Abilene; 3 permutations × 10 s |
| Runs | single run, seed 7 (the paths are deterministic; throughput is mean ± std over the 3 permutations); Balanced power mode |
| Command | `sudo python3 experiments/run_path_experiments.py` (defaults: `--pairs 40 --count 6 --bw 10 --flow-seconds 10 --perms 3`) |

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

> **Update, 21 Oct 2026.** All reactive numbers in this test use exact-match rules. A reactive controller with pair or destination rules removes most of the penalty (university: 52.5 to 1.5 ms; Abilene: 56.5 to 46.1 ms, proactive 46.0). See `docs/Granularity_Baseline_Experiment.md`.

**Configuration.** Networks as in T3: 16 hosts on the tree and the fat-tree, 11 on Abilene. All links 100 Mbit/s; Abilene's Atlanta–Indianapolis link 25 Mbit/s, with city delays.

| Scenario | Flow sizes | Flow arrivals | Flows per 30 s run | Source |
| --- | --- | --- | --- | --- |
| University (`tree-d2-f4`) | Benson Fig. 4(a), university curves: 60 B to 10 MB, 87% < 10 KB | per edge switch (4 of them), Weibull gaps (shape 1.34, scale 21.5 ms: 80% between 4 and 40 ms); a random host under that switch starts each flow | about 6,100 (203/s) | Benson et al., IMC 2010 [p.2, p.6, p.7] |
| Web search (`fattree-k4`) | `CDF_dctcp.tcl` (in 1,460-byte packets), mean 1.67 MB | Poisson; rate set by 30% load of host capacity | about 1,160 (39/s) | DCTCP via pFabric / PIAS |
| Data mining (`fattree-k4`) | `CDF_vl2.tcl`, mean 7.47 MB | Poisson, 30% load | about 1,710 (57/s) | VL2 via pFabric / PIAS |
| ISP (`abilene`) | SURGE: lognormal body μ = 9.357, σ = 1.318; Pareto tail above 133 KB, α = 1.1; 7% in the tail | real hourly city-to-city volumes of 1 Mar 2004, 24 h replayed in 30 s, scaled by 100 Mbit/s ÷ 9.92 Gbit/s; Poisson within each hour | about 1,760 (59/s) | Zhang et al., IMC 2005; Barford & Crovella 1998 (Table 1, Section 4) |

| Item | Value |
| --- | --- |
| Destination choice | uniform random (pFabric's choice) for university, web search and data mining in Step 2; the real matrices for ISP |
| One flow | open a TCP connection, send N bytes, wait for a 1-byte reply; flow completion time = connect to reply; a flow without a reply in 30 s counts as failed |
| Cap | flows above 20 MB are cut to 20 MB (0% of university, about 1% of web search, about 4% of data-mining flows) |
| Same flows for everyone | the schedule (start time, source, destination, size) is computed from the seed before the controller starts |
| Controllers | Reactive (Steps 1, 2, 4), Proactive, Proactive ECMP (fat-tree) |
| Runs | **5 runs, seeds 7–11**, uniform host pairs, Best performance mode (night of 17–18 Oct); the first single runs (seed 7, Balanced) are in `traffic-20261015-113417/` and `-122618/` |
| Command | `sudo python3 experiments/run_traffic_experiments.py` |

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

**Our results** (mean of 5 runs ± 95% CI; small-flow median / p99 in ms; large-flow mean in s):

| Scenario | Reactive | Proactive | Proactive ECMP |
| --- | --- | --- | --- |
| University | **32.0 ± 4.5** / 92.1 ± 25.5 | **1.15 ± 0.24** / 41.4 ± 4.4 | - |
| Web search | 115.5 ± 16.9 / 308.5 ± 34.9; large 10.3 ± 3.3 s | 57.3 ± 8.0 / 243.9 ± 20.3; large 10.5 ± 3.4 s | **17.0 ± 3.4** / 194.0 ± 39.3; large **3.19 ± 0.62 s** |
| Data mining | 80.5 ± 12.6 / 183.3 ± 30.3; large 9.85 ± 0.77 s | 26.2 ± 2.0 / 99.5 ± 22.6; large 9.98 ± 0.66 s | **9.6 ± 2.4** / 67.3 ± 9.3; large **3.56 ± 0.45 s** |
| ISP | **101.5 ± 4.5** / 350.0 ± 16.9; large 1.61 ± 0.06 s | **46.3 ± 1.2** / 206.5 ± 37.3; large 1.46 ± 0.40 s | - |

Flows per run: 6,093 ± 101 (university), 1,136 ± 49 (web search), 1,689 ± 40 (data mining), 1,749 ± 43 (ISP). 0 failed flows in every run.

The first single runs (Balanced mode) gave medians of 55.7 / 155 / 113 / 120 ms for reactive. Reactive got faster in the faster power mode; proactive barely changed, so the ratios shrank a little.

**What it means.**
- **University:** small flows are **28× slower** with reactive (32.0 vs 1.15 ms; 44× in the first single run). The network is only 6% loaded, so the whole difference is the setup cost.
- **Data centre:** small flows are **6.8× (web search) and 8.4× (data mining) faster** with ECMP than with reactive. Large flows depend on load balance, not on the controller: 9.9–10.5 s with reactive or one shortest path, **3.2–3.6 s with ECMP**.
- **ISP:** reactive is **2.2× slower** (101.5 vs 46.3 ms); T11 splits this into path and setup.

**Limits.** Generated traffic, not replayed packets (except the ISP volumes, which are real). The university size curve was read from a plot.

**Data and details.**
- **Raw data:** the repeats are in `results/measured/traffic-20261017-214330/`; the first single runs in `traffic-20261015-113417/` and `-122618/`.
- **Detailed documents:** `docs/Realistic_Traffic_Experiment.md`; `docs/Realism_Sources.md` (the paper behind every parameter).

**If asked.**
- **"How do you know every controller saw the same traffic?"** The schedule is computed before the controller starts, from a seed (`experiments/workloads.py`).

---

## T6. Reactive with long timeouts

**Question.** Is "just keep reactive rules longer" enough to get most of proactive's benefit?

> **Update, 21 Oct 2026.** Long timeouts keep exact-match rules that are never reused. A reactive controller with pair or destination rules gets 86 to 98% hit rate with the normal timeouts (`docs/Granularity_Baseline_Experiment.md`).

**Configuration.**

| Item | Value |
| --- | --- |
| Scenarios | university (`tree-d2-f4`, 16 hosts), Zipf pairs; web search (`fattree-k4`, 16 hosts), Zipf pairs; ISP (`abilene`, 11 hosts), real matrices; university, uniform pairs (control) |
| Links | 100 Mbit/s (Abilene: Atlanta–Indianapolis 25 Mbit/s, city delays) |
| Traffic | the T5 workloads, 30 s; host-pair popularity Zipf with exponent 1 (`--pair-zipf 1`) where stated |
| Controllers compared | Reactive (idle 10 s / hard 30 s) vs Reactive, long timeouts (idle 60 s / hard 300 s), both over the spanning tree; plus the others of the sweep (T7) |
| Runs | **5 runs, seeds 7–11**, Best performance mode (night of 15–16 Oct) |
| Command | `sudo python3 experiments/run_traffic_experiments.py --scenarios <scenario> --budget-sweep --pair-zipf 1 --repeats 5` |

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

> **Update, 21 Oct 2026.** A reactive controller that installs a pair rule on the first miss (no prediction) reaches 86 to 98% hit rate in all four scenarios, above the counter and the hindsight oracle at 25%, with no more rules than proactive. At 11 to 16 hosts most of the hybrid's gain is rule granularity. The open test is k=6, where pairs far outnumber flows. See `docs/Granularity_Baseline_Experiment.md`.

**Configuration.**

| Item | Value |
| --- | --- |
| Scenarios | as T6: university Zipf (16 hosts, 240 pairs), fat-tree web search Zipf (16 hosts, 240 pairs), Abilene (11 hosts, 110 pairs), university uniform |
| Links | 100 Mbit/s (Abilene as T5) |
| Budgets | 10%, 25%, 50% of all ordered host pairs: 24 / 60 / 120 pairs on 240, 11 / 28 / 55 on 110 |
| Counter | every 1 s: `score = 0.97 × score + 1` if the pair was used in that second, else `0.97 × score`. "Used" = a PACKET_IN of the pair at the sender's switch, or (if pre-installed) its rule's packet counter went up (one stats request per installed pair per second). The top-K scores keep pair rules; a newcomer must score 1.5× the weakest kept pair (hysteresis) |
| Pair rules | match source MAC + destination MAC, priority 100, on every switch of the pair's shortest path (ECMP-hashed on the fat-tree), installed far end first |
| Everything else | reactive on shortest paths, exact match, idle 10 s / hard 30 s |
| Oracle | counts each pair's flows in the run's schedule in both directions and pre-installs the top K before the first flow; never changes them |
| Random | pre-installs K random pairs (each in both directions) before the first flow, chosen with no knowledge of the traffic (seeded per run) |
| Hit rate | new TCP connections whose SYN found a rule at the sender's switch ÷ all connections |
| Runs | **5 runs, seeds 7–11**, Best performance mode, for counter, oracle, random and decay 0.9; one extra single run: 120 s warm-up (Balanced). The random runs and the decay runs were on the night of 17–18 Oct, the counter and oracle runs on 15–16 Oct: hit rates compare directly (they depend only on the flow schedule), times only loosely |
| Command | `sudo python3 experiments/run_traffic_experiments.py --scenarios <scenario> --budget-sweep --pair-zipf 1 --repeats 5` |

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

**Random baseline: pre-installing a random K pairs, no knowledge** (mean of 5 runs ± 95% CI; hit rate %):

| Scenario | Random 10 / 25 / 50% | Counter 10 / 25 / 50% | Oracle 10 / 25 / 50% | Share of the oracle's gain over random that the counter gets |
| --- | --- | --- | --- | --- |
| University, Zipf | 9.8 ± 7.1 / 23.9 ± 7.8 / 49.8 ± 12.3 | 30.8 / 60.7 / 78.9 | 49.3 / 68.2 / 84.7 | 0.53 / 0.83 / 0.83 |
| Fat-tree, web search | 8.4 ± 3.2 / 19.3 ± 9.0 / 43.5 ± 6.7 | 51.1 / 65.8 / 77.4 | 56.2 / 73.7 / 88.3 | 0.89 / 0.85 / 0.76 |
| Abilene | 9.6 ± 4.8 / 24.5 ± 4.8 / 54.1 ± 5.4 | 26.6 / 53.8 / 77.2 | 33.1 / 59.2 / 83.0 | 0.72 / 0.84 / 0.80 |

At a 25% budget, against reactive on shortest paths (University / Fat-tree / Abilene):

| Controller | PACKET_IN/s | Peak rules | Small-flow median (ms) |
| --- | --- | --- | --- |
| Reactive on shortest paths | 2,549 / 492 / 447 | 10,983 / 3,752 / 5,321 | 27.3 / 59.3 / 55.6 |
| **Random 25%** | 1,872 / 389 / 334 | 8,556 / 3,282 / 4,012 | 19.2 / 55.3 / 53.3 |
| Counter 25% | 936 / 180 / 198 | 5,278 / 1,569 / 2,615 | 8.4 / 38.2 / 50.0 |
| Oracle 25% | 658 / 139 / 169 | 3,586 / 1,221 / 2,418 | 5.0 / 34.0 / 49.4 |

**Other extra runs.**
- **Warm-up check** (120 s instead of 30 s, university, 10%, single run): the counter's hit rate rose from 24.5% to 38.1%; the oracle stayed at 51.5%.
- **Decay 0.9 instead of 0.97** (university, Zipf, 5 runs): hit rate 34.9 ± 6.8% (10%) and 62.1 ± 4.5% (25%), against 30.8 ± 10.2% and 60.7 ± 5.5% with 0.97. Small-flow median 15.5 / 7.0 ms against 17.7 / 8.4 ms; wasted installs 50 / 64 against 40 / 64. Every difference is inside the confidence intervals: **a shorter memory does not help.**

**What it means.**
1. **With skewed traffic, a quarter of the pairs removes most of the setup cost.** 54–66% of new connections skip the controller, with **fewer** rules than reactive: one pair rule replaces many per-connection rules.
2. **The gain comes from skew.** With uniform pairs, a budget of B% buys about B%.
   - **Random pre-installation confirms it:** with skewed traffic, a random K pairs also buys only about its budget share (8–10% / 19–25% / 44–54% at 10 / 25 / 50%), with very wide intervals (a lucky pick can catch a busy pair).
   - **Choosing well is worth a lot:** at 25%, random cuts the rules by only 12–25% and the controller requests by 21–27%; the counter cuts the rules by 51–58% and the requests by 56–63%.
   - **The counter does most of the oracle's job:** it gets 72–89% of the oracle's advantage over random (53% for university at 10%).
3. **The simple counter reaches 0.88–0.93 of a perfect predictor** at 25–50% budgets.
4. **Its weak spot is small budgets with many flows per pair** (university, 10%). The counter scores "busy seconds", not flows, so pairs with 1.4 and 0.8 flows/s look alike.
5. **Proactive still wins on these small networks** (see T12 for a larger one).

**Limits.**
- The hybrid is close to CacheFlow and PARD, and it is not a new algorithm.
- Zipf popularity is an assumption (from CacheFlow), except for Abilene.
- The oracle is the best **fixed** set: right for our traffic, whose popularity does not change during a run.

**Data and details.**
- **Raw data:** as T6, plus `traffic-20261015-211130/` (warm-up), `traffic-20261017-224052/` (random: university and fat-tree), `traffic-20261017-231017/` (random: Abilene) and `traffic-20261018-001723/` (decay 0.9).
- **Detailed documents:** `docs/Budgeted_Hybrid_Experiment.md` (Sections 1 and 4.0); Review II Section 6; figure `docs/figures/step4_hit_rate.png`.

**If asked.**
- **"What is the oracle, and isn't it cheating?"** It cheats on purpose. It knows the future flow schedule, so it gives the best hit rate any predictor could reach with the same budget. Same idea as Belady's optimal algorithm in caching.
- **"Why is CacheFlow's hit rate higher?"** CacheFlow counts packets of policy rules on traces with a strong skew. We count new connections between host pairs, on 110–240 pairs. Same direction, smaller effect.

---

## T8. ML predictor vs counter

**Question.** Would a machine-learning predictor choose the pre-installed pairs better than a simple counter?

**Configuration.** No separate run: the bound comes from the T7 runs (same scenarios, networks, budgets and 5 seeds). No ML model was built. The oracle gives the best possible choice for each budget, and the gap between the oracle and the counter bounds what *any* predictor could add.

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
- **10% budget:** the gap is larger (university: 18.5 points). A shorter counter memory (decay 0.9, 5 runs) did not close it, so the cause is likely the counter's 0/1 scoring, not its memory length.
- **At scale (k = 6, T12):** the gap to the oracle is wider (the counter reaches 0.65–0.80 of it). With few flows per pair, there is more to learn, so a better predictor has more to gain there.

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

**Configuration.**

| Item | Value |
| --- | --- |
| PC A | Mininet, Open vSwitch and the traffic; runs `run_traffic_experiments.py --controller-host <PC B's IP>` |
| PC B | POX, started and stopped per run by `experiments/controller_agent.py` (listens on TCP 6000; POX listens on TCP 6633) |
| Network between them | the same LAN (Ethernet preferred); on WSL2, mirrored networking plus two firewall rules (`docs/Controller_On_Second_PC.md`) |
| Scenarios | any of T5–T7; planned: the university Zipf sweep and Abilene, 5 seeds, same seeds as T7 |
| Power mode | Best performance on both PCs |
| Status | tested only with the agent on the same machine (127.0.0.1); the two-laptop run is pending |

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

**Configuration.**

| Run | Machine | Datapath | What was compared |
| --- | --- | --- | --- |
| Review I (T1, T2) | laptop 1 (27 Sep) and laptop 2 (9 Oct) | kernel | latency pattern, rule counts, controller load |
| Step 1 (T4) | laptop 1 and the cloud VM | kernel / userspace | the traced paths |
| Step 4 (T7) | laptop 1 and the cloud VM | kernel / userspace | the ranking of the ten controllers |
| Step 4 repeats (T6, T7, T11) | laptop 1, 5 seeds | kernel | mean ± 95% confidence interval |

**Closest papers.** Most papers above report one testbed and do not repeat on different machines.

**Our results.**
- **Review I:** the same patterns on two laptops; **identical rule counts**; the 8-host tree slowest on both.
- **Step 1:** **identical paths** on the laptop and a cloud VM.
- **Step 4:** the same ranking of all ten controllers on the laptop and the cloud VM. Absolute times differ: the cloud VM uses a slower userspace datapath.
- **Within one laptop:** 5 seeds per configuration give 95% confidence intervals (T6, T7, T11).

**Night-to-night variation (found on 17 Oct).** The same configuration (university, uniform pairs, 5 seeds, Best performance) was measured twice:

| | Reactive small-flow median | Proactive | Ratio | Controller CPU |
| --- | --- | --- | --- | --- |
| Night of 15–16 Oct | 23.6 ± 0.7 ms | 0.96 ms | 25× | 64.2% |
| Night of 17–18 Oct | 32.0 ± 4.5 ms | 1.15 ms | 28× | 72.2% |

The intervals do not overlap, so a confidence interval covers noise *within* a night, not the machine's state *between* nights (background load, temperature). The ratio held. **Therefore: compare controllers only within one batch, and quote ratios more than absolute times.**

**Limits.** All machines ran Mininet + Open vSwitch; no hardware switch.

**Data and details.**
- **Raw data:** `results/measured/` (laptop runs); `results/validation_*` (cloud runs).

---

## T11. Reactive's cost split: path vs setup

**Question.** When reactive is slower, how much of that is asking the controller (**setup**), and how much is the spanning tree's longer paths (**path**)?

**Configuration.**

| Item | Value |
| --- | --- |
| Scenarios | university (`tree-d2-f4`, 16 hosts), web search (`fattree-k4`, 16 hosts), Abilene (11 hosts); traffic as T5, with Zipf pairs on the tree and the fat-tree |
| Links | 100 Mbit/s (Abilene as T5) |
| The three controllers | Reactive over the spanning tree; Reactive on shortest paths (`hybrid_eval --budget=0`: the same exact-match reactive logic, but routed on the known topology); Proactive (ECMP on the fat-tree) |
| Calculation | path cost = Reactive − Reactive on shortest paths; setup cost = Reactive on shortest paths − Proactive (small-flow medians) |
| Runs | **5 runs, seeds 7–11** (the same runs as T6/T7), Best performance mode |

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

> **Update, 23 Oct 2026.** Rerun with wildcard baselines (`traffic-20261023-070549/`, 3 seeds): reactive with pair rules gets 51% hit rate and destination rules 59% at this size, down from 86 to 98% at 11 to 16 hosts. The counter at 10% gets the same 51% with 1.9 times the rules; only the oracle (65 to 78% at 5 to 10%) is better. See `docs/Granularity_Baseline_Experiment.md`.

**Configuration.**

| Item | Value |
| --- | --- |
| Network | `fattree-k6`: 54 hosts, 45 switches (9 core, 18 aggregation, 18 edge), 162 links, 2,862 ordered host pairs, up to 9 equal paths between pods |
| Links | 100 Mbit/s, no delay |
| Traffic | web search (as T5), Zipf pairs, **5% load** (the laptop's limit: about 21 new flows/s, about 280 Mbit/s offered), 30 s |
| Controllers | the full sweep: Reactive, Reactive with long timeouts, Reactive on shortest paths, counter / oracle at **2 / 5 / 10%** (57 / 143 / 286 pairs), Proactive ECMP |
| Runs | **3 runs, seeds 7–9**, Best performance mode (night of 17–18 Oct); an earlier smoke test (1 run, 20 s, Proactive ECMP and Reactive on shortest paths) gave 13,230 and 2,058 rules |
| Command | `sudo python3 experiments/run_traffic_experiments.py --scenarios fattree-k6:websearch --budget-sweep --budgets 2 5 10 --load 0.05 --pair-zipf 1 --repeats 3` |

**Closest papers.**
- **DevoFlow:** a real switch holds 16K exact-match and 1,500 wildcard rules [p.4].
- **CacheFlow:** 84–97% hits with 2–10% of rules [p.9].

**Our results** (mean of 3 runs, seeds 7–9, ± 95% CI with 2 degrees of freedom, so the intervals are wide; 642 ± 114 flows per run, **0 failed**):

| Controller | Hit rate % | Small-flow median (ms) | PACKET_IN/s | Peak rules, all switches | Peak rules, busiest switch |
| --- | --- | --- | --- | --- | --- |
| Reactive (spanning tree) | - | 99.6 ± 48.5 | 344 ± 29 | 3,012 ± 660 | 406 |
| Reactive, long timeouts | - | 93.7 ± 33.0 | 354 ± 47 | 8,023 ± 1,003 | 1,061 |
| Reactive on shortest paths | 0 | 51.5 ± 7.1 | 367 ± 50 | 2,160 ± 406 | 138 |
| Counter 2% (57 pairs) | 40.0 ± 6.8 | 31.3 ± 7.9 | 229 ± 59 | 1,589 ± 283 | 69 |
| Counter 5% (143) | 47.1 ± 9.6 | 26.9 ± 8.2 | 204 ± 60 | 1,819 ± 385 | 77 |
| Counter 10% (286) | 50.9 ± 7.8 | 25.0 ± 15.5 | 189 ± 59 | 2,374 ± 329 | 89 |
| Oracle 2% | 50.3 ± 7.1 | 23.0 ± 9.4 | 195 ± 45 | 1,370 ± 312 | 54 |
| Oracle 5% | 65.5 ± 9.6 | 13.5 ± 17.6 | 143 ± 45 | 1,430 ± 241 | 56 |
| Oracle 10% | 77.8 ± 8.1 | 8.0 ± 4.9 | 96 ± 46 | 2,019 ± 113 | 68 |
| Proactive ECMP | 100 | 4.9 ± 0.6 | 0 | **13,230** | 312 |

**What it means.**
- **Proactive's rule count explodes with size:** 13,230 rules in total against 1,072 on the 16-host fat-tree (12× more rules for 3.4× the hosts), and 6.1× the reactive-on-shortest-paths count.
- **A 2% budget already changes the picture:** 57 pre-installed pairs give a 40% hit rate, 1.6× lower small-flow median than reactive on shortest paths (31 vs 51 ms) and 38% fewer controller requests, with **8× fewer rules than proactive** (1,589 vs 13,230) and fewer than reactive. It does not reach proactive's 4.9 ms.
- **Path and setup, here:** reactive's extra over proactive is about 48 ms of path (99.6 − 51.5) and 47 ms of setup (51.5 − 4.9).
- **The counter is weaker at this scale:** 0.80 / 0.72 / 0.65 of the oracle's hit rate at 2 / 5 / 10% (0.88–0.93 on the 16-host networks), and 43–46% of its installs are wasted (51 of 118, 125 of 273, 214 of 500). With only about 640 flows over 2,862 pairs in 30 s, most pairs appear once or twice, so the counter spends many installs on pairs that do not come back.
- **At 10% the hybrid holds more rules than pure reactive** (2,374 vs 2,160): the pair rules are added on top of the exact-match rules of the misses.
- **The per-switch view is unchanged:** proactive's busiest switch holds 312 rules, which still fits a hardware table (see the calculation below).

**Per switch it still fits.** A switch's capacity is per switch, and proactive's busiest switch holds 312 pair rules. Pair rules match only MAC addresses, so on hardware they would sit in the TCAM. That is within the 1,500 wildcard rules of DevoFlow's switch. An edge switch of a k-ary fat-tree needs about k × N pair rules (N = k³/4 hosts). At k = 10 (250 hosts) that is about 2,500, above the 1,500. So the budget becomes necessary at a few hundred hosts: larger than we can emulate, and small for a real data centre.

**Limits.**
- Only 3 seeds, so many differences between neighbouring rows (for example counter 5% vs 10%) are not significant.
- 5% load, not 30%: the laptop cannot carry more at this size.
- Web search traffic only.

**Data and details.** `results/measured/traffic-20261017-232237/`; `docs/Budgeted_Hybrid_Experiment.md` Section 4.8.

---

## Not yet tested (and why)

- **Hardware switches:** none available. The limit is stated in every report.
- **Adaptive timeouts (SmartTime's algorithm itself):** T6 shows that even the best-case fixed long timeout gives no gain on short-flow traffic.
- **ML predictor:** bounded by the oracle (T8).
- **Microservice call-chain traffic:** needs hundreds of hosts (T8).
