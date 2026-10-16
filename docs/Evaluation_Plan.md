# Evaluation Plan: What We Measure, Next to the Closest Prior Work

CS G525, Project SA7, Group 2.

**Our contribution is evidence, not a new algorithm.** The main rule-installation strategies are compared side by side, on the same testbed, the same realistic traffic and the same networks. Setup cost and path quality are measured together.

**Status (15 Oct 2026):**
- **Done:** measured on the laptop testbed.
- **Tool ready:** implemented and tested; the measurement itself is still to run.
- **Planned:** for the final submission (20 Nov).

Results so far are summarised in Section 3; details are in `docs/Progress_Review_2.md` and `docs/Budgeted_Hybrid_Experiment.md`.

**What the paper gives / misses** describes the paper as we read it: full text where we have it, otherwise its abstract (marked *abstract*).

---

## 1. Comparisons

| # | Our comparison | Status | Closest paper | What the paper gives | What the paper misses | What we add |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | First-packet delay, reactive vs proactive, 4 / 8 / 16 hosts | Done | **DIFANE** (SIGCOMM 2010); **Ethane** (SIGCOMM 2007) | First-packet RTT of reactive NOX vs DIFANE on Click software switches. Ethane: setup delay in a real 300-host deployment | Only one network size; no link between delay and path length; old software stack | Three network sizes. Delay grows with the number of switches on the path. A modern Open vSwitch stack, including its cache effect. Reproduced on 2 laptops |
| 2 | Rules in the switches: all pairs active, and under churn | Done | **DevoFlow** (SIGCOMM 2011); **CacheFlow** (SOSR 2016) | DevoFlow: table and setup-rate limits of a real HP switch, then simulation. CacheFlow: caching popular rules on a real Pica8 switch | No direct count of how reactive exact-match rules pile up against proactive under churn | Measured count: up to **83× more rules** for reactive under churn; equal to proactive when every pair talks |
| 3 | Controller load under realistic flow arrivals | Done | **Tootoonchian et al.** (Hot-ICE 2012, cbench) | Maximum flows/s of several controllers under **synthetic** load from emulated switches | Realistic traffic; how load changes requests per flow | Load under university, data-centre and ISP traffic, plus the **amplification effect**: 7.4 → ~12 requests per flow as POX CPU rose from 54% to 86% |
| 4 | Path quality: reactive vs proactive shortest path vs ECMP | Done | **Al-Fares** (SIGCOMM 2008); **Hedera** (NSDI 2010) | Fat-tree design; ECMP and flow scheduling for throughput | Not about how rules are installed. The reactive-vs-proactive papers do not measure paths | **Links installation mode to path quality**: stretch, delay, throughput, link balance, on a fat-tree and the real Abilene map |
| 5 | Flow completion time under realistic traffic | Done | **pFabric** (SIGCOMM 2013) / **PIAS** (NSDI 2015) workloads; **Batista et al.** 2024 | pFabric/PIAS: published web-search and data-mining workloads, used to test transport protocols. Batista: response time, reactive vs LSTM pre-install, on IoT | These workloads never used to compare rule-installation strategies; Batista only on periodic IoT | Reactive vs proactive vs ECMP under university, web-search, data-mining and **real Abilene ISP** traffic |
| 6 | Reactive with long timeouts | **Done** (4 scenarios, 5 runs each) | **SmartTime** (DEBS 2014); **AH-IHTA** (*Electronics* 2020) | Adaptive vs fixed timeouts: fewer misses and less controller load. SmartTime on Benson's real university traces | No comparison against proactive or a hybrid on the same traffic; no flow completion times or path quality | Long timeouts vs proactive vs hybrid on the same workloads and networks, with all metrics |
| 7 | **Budgeted hybrid**: a counter keeps the top-K pairs pre-installed, budget 10 / 25 / 50%, plus an **oracle** upper bound and a uniform-traffic control | **Done** (4 scenarios, 5 runs each) | **CacheFlow** (SOSR 2016); **PARD** (*JNSM* 2020, abstract); **Kim et al.** (*Electronics* 2022) | CacheFlow: hit rate of caching popular rules. PARD: hybrid that cuts first-packet latency. Kim: per-flow hybrid choice, in simulation | How much of proactive's benefit a **fraction of its rules** buys; realistic traffic in emulation | Flow completion time, PACKET_IN and hit rate against the rule budget, on realistic traffic and three networks |
| 8 | *(Optional)* ML predictor vs counter at the same budget | Optional; bounded by the oracle (Section 3) | **Batista et al.** 2024; **Rouf & Yuksel** (arXiv 2025, abstract) | Batista: LSTM pre-install, 51% faster than reactive (IoT). Rouf & Yuksel: DQN eviction, ~8% better than LFU (IoT traces) | Batista compares only with reactive. Rouf & Yuksel do eviction, not pre-installation | Pre-installation: ML **vs a simple counter** at the same budget, on non-IoT realistic traffic |
| 9 | Controller on a separate PC | **Tool ready** (run needs a second laptop) | **Kandoo** (HotSDN 2012); most papers above | Emulation or simulation on one machine | The effect of a real network between controller and switches | Measured effect of control-channel delay on reactive's cost |
| 10 | Reproducibility on several machines | Done | Most papers above | Results from one testbed | Repeats on different machines | The same patterns on 2 laptops and a cloud VM; identical paths and rule counts |
| 11 | Reactive's cost split into **path** (spanning tree) and **setup** (controller) | **Done** (3 networks, 5 runs) | **Path quality** papers (Al-Fares, Hedera) and **setup cost** papers (DIFANE, DevoFlow) | Each side measured separately | No paper separates the two for the same reactive controller and traffic | Reactive with and without the spanning tree on the same traffic. On Abilene, about 41 ms of reactive's extra delay is path and 10 ms is setup |

## 2. Measurements (metrics)

| Group | Metric | Used in |
| --- | --- | --- |
| Latency | First-packet RTT; packet 2; steady-state RTT | 1 |
| Latency | Flow completion time of small (< 100 KB), medium and large (> 10 MB) flows: mean, median, 99th percentile | 5, 6, 7, 8, 9 |
| Reliability | Failed / unfinished flows | 5–9 |
| Controller | PACKET_IN/s, FLOW_MOD/s, controller CPU %, PACKET_INs per new flow | 2, 3, 5–9 |
| Switch tables | Rules in all switches, peak rules in one switch | 2, 5–8 |
| Hybrid | Hit rate (% of new flows that found a pre-installed rule); wasted pre-installs | 7, 8 |
| Paths | Hop stretch, delay stretch, % of pairs on a longer path, path RTT | 4 |
| Throughput | Total throughput vs ideal; slowest flow; busiest link; Jain index over links; % of links unused | 4 |
| Control channel | Effect of controller-to-switch delay on all of the above | 9 |
| Rigour | 5 repeats, mean and 95% confidence interval (done for Step 4; Step 2 to repeat) | All |

---

## 3. Results so far (laptop; Step 4 rows: mean of 5 runs, 16 Oct 2026)

| # | Result |
| --- | --- |
| 6 | Long timeouts (60 s / 300 s) gave **no fewer controller requests and no faster flows** in 4 of 4 scenarios (significantly slower in one), with 2.2–3.0× the rules. Exact-match rules are never reused by new connections. |
| 7 | 25% of host pairs pre-installed: **54–66% hit rate**, 2.3–2.7× fewer PACKET_INs, 2.0–2.4× fewer rules than reactive on shortest paths. With uniform pairs, a budget buys only its own share. |
| 7 (oracle) | The counter reaches **0.88–0.93 of the oracle's hit rate** at 25–50% budgets, and 0.62–0.91 at 10%. |
| 8 | Not built. The oracle shows how much any predictor, ML included, could add: at most 5–11 points of hit rate at 25–50% budgets; more only at a 10% budget with many flows per pair. |
| 11 | Path vs setup, small-flow median: university 0.6 / 26 ms, fat-tree 52 / 31 ms (setup includes ECMP), Abilene 41 / 10 ms. A faster CPU shrank only the setup part. |

---

## 4. How to state the contribution

> "Each rule-installation idea has been tested on its own, on its own traffic and setup: timeouts on university traces (SmartTime), hybrids in simulation (PARD, Kim), predictors on IoT traffic (Batista), and ECMP without considering how rules are installed (Al-Fares, Hedera). We compare reactive, long-timeout reactive, proactive, proactive ECMP and a budgeted popularity hybrid side by side, on one testbed, with university, data-centre and ISP traffic from published measurements, on tree, fat-tree and Abilene networks. We measure both flow-setup cost and path quality."

**Limits to state:**
- the testbed is emulated (no hardware switch);
- POX is single-threaded;
- the budgeted hybrid is not a new algorithm (it is close to CacheFlow and PARD); the contribution is the comparison;
- our networks are small (11–16 hosts), so proactive's rules always fit and proactive stays the best choice; a rule budget matters only for larger networks.
