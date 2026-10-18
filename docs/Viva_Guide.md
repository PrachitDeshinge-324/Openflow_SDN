# Viva and Review Guide: How to Explain SA7

CS G525 Advanced Computer Networks, Project SA7, Group 2.

**Who this is for:** all four of us, before Review II (30 Oct) and the final viva.

**What it gives you:**
- the story in one minute;
- where each answer lives in the repo;
- the numbers worth memorising;
- the questions we are likely to get, with short honest answers.

**Rule for the viva:** every number we say must be in a table in the repo, and we must know which one. If you do not know an answer, say which document has it and open it. That is better than guessing.

---

## 1. The project in one minute

**The question.** In OpenFlow, a switch can only forward a packet that matches a rule. There are two ways to get the rule:
- **reactive:** ask the controller when the first packet of a new flow arrives;
- **proactive:** install every rule in advance.

Published papers propose many things in between, but each was tested on its own traffic and setup.

**What we did.** We built one testbed (Mininet + Open vSwitch + POX) and ran every strategy on it, side by side:
- **the same flows for every controller:** the flow schedule is computed in advance from a seed;
- **three networks:** a campus tree, a data-centre fat-tree and the real Abilene ISP backbone;
- **published traffic:** university (Benson 2010), web search (DCTCP), data mining (VL2), and real Abilene traffic matrices;
- **repeats:** 5 runs per configuration, with 95% confidence intervals.

**What we found (five sentences):**
1. **Reactive pays twice: setup delay and bad paths.** On the ISP map, the spanning tree's detours cost more than asking the controller: about 41 ms against 10 ms.
2. **Long timeouts do not help** short-flow traffic. New TCP connections never reuse an exact-match rule, so the switch tables just grow 2–3×.
3. **Pre-installing the busiest 25% of host pairs works.** A simple counter picks the pairs, and 54–66% of new connections then skip the controller, with 2–2.4× fewer rules than reactive.
4. **A perfect predictor (the oracle) would add only 5–11 percentage points** at those budgets. So ML prediction has little room on this traffic.
5. **On our small networks, proactive is still best.** On a larger fat-tree (54 hosts) it needs 13,230 rules in total against reactive's 2,058. Per switch that still fits a hardware table; at a few hundred hosts it stops fitting, and then a budget is needed.

**What we do not claim:**
- the hybrid is not a new algorithm: it is close to CacheFlow and PARD;
- it does not beat proactive on small networks;
- we did not use real hardware switches.

---

## 2. Where everything is: open this when asked that

| If someone asks... | Open | Section |
| --- | --- | --- |
| "Give us the overview" | `docs/Progress_Review_2.pdf` (or `.md`) | 0. At a glance |
| "What did you change after Review I?" | `docs/Progress_Review_2.md` | 1. Response to the feedback (table, one row per point) |
| "What were the Review I results?" | `docs/Progress_Review_1.md`, or Section 2 of Review II | tables at the top |
| "How is the testbed built? Which versions?" | `docs/Progress_Review_2.md` | 3. Testbed and method |
| "Optimal path vs haphazard path?" | `docs/Path_Quality_Experiment.md` | 6. Results; 3. "Which links the spanning tree switches off" |
| "What traffic did you use, and why is it realistic?" | `docs/Realistic_Traffic_Experiment.md` | 2–3; and `docs/Realism_Sources.md` for the paper behind each choice |
| "Where does this parameter come from?" | `docs/Realism_Sources.md` | find the parameter in the tables; each row names the paper and says "checked in PDF / online / data file" |
| "What is your hybrid? How does the counter work?" | `docs/Budgeted_Hybrid_Experiment.md` | 1. The controllers compared; "The weighted counter" (with a worked example) |
| "What is the oracle?" | `docs/Budgeted_Hybrid_Experiment.md` | 1. "The oracle: a controller that knows the future" |
| "Show the hybrid results with error bars" | `docs/Budgeted_Hybrid_Experiment.md` (4.0) or Review II Section 6 | figures `docs/figures/step4_hit_rate.png` and `step4_cost_split.png` |
| "Walk us through one test: what, closest paper, what it missed, your result" | `docs/Test_Catalogue.md` | one section per test (T1–T12), always in the same order |
| "How do you compare with previous papers?" | `docs/Test_Catalogue.md` (per test) or `docs/Evaluation_Plan.md` (one table) | |
| "Did you read the literature?" | `docs/literature/Literature_Review_IdleHybrid.md` (14 papers, page refs) and `ML_Rule_Prediction_Survey.md` (28 papers) | PDFs in `docs/literature/papers/` |
| "Why not ML?" | `docs/literature/ML_Rule_Prediction_Survey.md` | D. What this means for our project; and the oracle results |
| "Multiple PCs?" | `docs/Controller_On_Second_PC.md` | status line at the top, then 1–3 |
| "How do I run it myself?" | `README.md` | 1. Setup, 2. Measured evaluation; `INSTALL.md` for a fresh laptop |
| "Show me the raw data" | `results/measured/<run>/` | `traffic.md` (tables), `traffic.json` (every flow), `*-pox.log` |
| "What is still missing?" | `docs/Progress_Review_2.md` (9. Plan) and `docs/Final_Report.md` (`TODO (data)` markers) | |

---

## 3. Code tour (what each file does)

| File | What it does | Who should know it |
| --- | --- | --- |
| `controllers/reactive_eval.py` | The reactive controller: POX learning switch with exact-match rules (idle 10 s, hard 30 s), plus counters for PACKET_IN, FLOW_MOD and CPU | Everyone |
| `controllers/proactive_eval.py` | The proactive controller: reads the topology, installs one rule per host pair on the lowest-delay path (or ECMP) when a switch connects | Everyone |
| `controllers/hybrid_eval.py` | Step 4: reactive on shortest paths, plus pair rules for the top-K pairs by a decaying counter; or a fixed oracle list | Whoever presents Step 4 |
| `controllers/sa7_common.py` | Shared helpers: stats file, topology loading, Dijkstra | |
| `experiments/run_experiments.py` | Review I: first-packet latency, rule counts, churn | Review I presenter |
| `experiments/run_path_experiments.py` | Step 1: path stretch (reads the real path from the flow tables), throughput, link balance | Step 1 presenter |
| `experiments/run_traffic_experiments.py` | Steps 2 and 4: builds the network, generates the flow schedule, starts POX, runs TCP flows on every host, measures FCT and controller load; `--budget-sweep`, `--repeats`, `--controller-host` | Steps 2 and 4 presenters |
| `experiments/workloads.py` | The four traffic models (university, web search, data mining, ISP), each from a paper | Traffic presenter |
| `experiments/repeats.py` | Mean and 95% confidence interval over repeated runs (Student's t) | Whoever is asked about statistics |
| `experiments/controller_agent.py` | Runs POX on a second PC for the harness | Two-PC presenter |
| `demo/run_demo.py` | The live demo (below) | Everyone, at least once |

---

## 4. The live demo (5 minutes)

```bash
sudo python3 demo/run_demo.py            # add --datapath user if the kernel module fails
```

What to point at while it runs:
1. **Reactive:** switch s1 starts with no rules. h1 pings h4; packet 1 takes several ms (the controller round trip), and the rules appear only after the traffic.
2. **Proactive:** s1 already holds all 8 rules before any ping. Packet 1 is under 1 ms, and the controller counter shows **PACKET_IN = 0**.
3. **The summary table** at the end: packet 1, packet 2, steady state, rules, PACKET_INs, side by side.

**Rehearse it once on the laptop you will present from**, the day before.

---

## 5. Suggested split for the presentation

Every member presents one part and must answer its questions. Swap parts if you like; just make sure everyone has read Section 1 and the cheat sheet (Section 6).

| Part | Content | Documents | Suggested owner |
| --- | --- | --- | --- |
| A. Problem, testbed, Review I recap, demo | Reactive vs proactive; Mininet/OVS/POX; first-packet delay and rule counts; the live demo | Review II Sections 0–3; `Progress_Review_1.md`; demo | Nisarg |
| B. Path quality and networks | Fat-tree, Abilene, spanning tree vs shortest path vs ECMP; stretch, throughput, link balance | Review II Section 4; `Path_Quality_Experiment.md` | Prachit |
| C. Realistic traffic and the budgeted hybrid | The four workloads; FCT and controller load; the counter, the oracle, long timeouts, path vs setup split | Review II Sections 5–6; `Realistic_Traffic_Experiment.md`; `Budgeted_Hybrid_Experiment.md` | Mrudul |
| D. Related work, method rigour, limits | Literature, the evaluation plan, realism sources, repeats and confidence intervals, what we do not claim, next steps | Review II Sections 7–9; `Evaluation_Plan.md`; `Realism_Sources.md`; literature docs | Mukul |

**Order and time (about 15 minutes + questions):** A (4 min, including the demo) → B (3 min) → C (5 min) → D (3 min).

---

## 6. Cheat sheet: numbers to know

**Review I** (trees with 4 / 8 / 16 hosts, one run per laptop, two laptops):
- **First packet:** reactive 3.8–6.6 ms (laptop 1), proactive 0.7–0.9 ms; later packets equal (0.06–0.09 ms).
- **Rules when every pair talks:** equal (28 / 216 / 624). Under 200 new flows/s, reactive has 4–83× more.

**Step 1, path quality** (one run; the paths are deterministic):
- **Abilene, reactive:** 70% of pairs on a slower path; delay stretch 1.58 on average, up to 4.47. Ping 40.5 vs 26.9 ms.
- **Fat-tree, total throughput:** ECMP 95 Mbit/s against 64 (reactive) and 62 (one shortest path). Unused links: 16% vs 59%.

**Step 2, realistic traffic** (mean of 5 runs ± 95% CI, Best performance mode):

| Scenario | Reactive small-flow median | Proactive (ECMP) | Ratio |
| --- | --- | --- | --- |
| University | 32.0 ± 4.5 ms | 1.15 ms | 28× |
| Web search | 115.5 ± 16.9 ms | 17.0 ms | 6.8× |
| Data mining | 80.5 ± 12.6 ms | 9.6 ms | 8.4× |
| ISP | 101.5 ± 4.5 ms | 46.3 ms | 2.2× |

The first single runs (Balanced mode) gave 55.7 / 155 / 113 / 120 ms for reactive. Reactive was faster in the faster mode, proactive barely changed.

**Step 4, between reactive and proactive** (mean of 5 runs ± 95% CI, Best performance mode):

| | University | Fat-tree | Abilene |
| --- | --- | --- | --- |
| Hit rate, counter at 25% | 60.7 ± 5.5% | 65.8 ± 1.4% | 53.8 ± 2.3% |
| Counter ÷ oracle at 25 / 50% | 0.89 / 0.93 | 0.89 / 0.88 | 0.91 / 0.93 |
| Path / setup part of reactive's extra delay | 0.6 / 26 ms | 52 / 31 ms | 41 / 10 ms |
| Rules: long timeouts vs reactive | 3.0× | 2.4× | 2.2× |

**Random vs counter** (hit rate at 25%): random 23.9 / 19.3 / 24.5% (university / fat-tree / Abilene), counter 60.7 / 65.8 / 53.8%, oracle 68.2 / 73.7 / 59.2%.

**Larger network** (fat-tree k = 6, 3 runs): proactive needs **13,230 rules**, reactive on shortest paths **2,160**; a 2% budget gives a 40% hit rate with **1,589 rules**; the counter reaches 0.65–0.80 of the oracle there.

---

## 7. Questions to expect, with short answers

**About the setup**
- **Why Mininet and not real switches?**
  - The course has no OpenFlow hardware, and Mininet is the standard research emulator (Handigol et al., CoNEXT 2012).
  - We use real TCP, real Open vSwitch and a real controller; only the wires are virtual.
  - Limit we state: there is no hardware TCAM, so no hardware table-size or update-rate limit.
- **Why POX?** It is simple, written in Python, and easy to instrument; that is how we count PACKET_INs and CPU. It is single-threaded, so absolute controller numbers are POX's, not a production controller's. The comparisons between strategies are what matter.
- **Why exact-match rules for reactive?** That is what POX's own `l2_learning` does, and what our reactive controller copies. It is also why long timeouts do not help: every new TCP connection has a new source port, so its rule is new.
- **Is reactive over a spanning tree unfair?** No. A plain learning switch needs the tree, or broadcasts loop forever. And we measured the fix too: "reactive on shortest paths" (`hybrid_eval` with budget 0). That is how we split reactive's cost into path and setup.
- **How do you know every controller got the same traffic?** The flow schedule (start time, source, destination, size) is generated in advance from a seed, before the controller starts. The same seed gives the same flows (`experiments/workloads.py`).
- **Why 100 Mbit/s links and 30 s runs?** So a laptop can emulate the network faithfully. At 100 Mbit/s the university traffic loads the links by about 5%, close to Benson's finding of low utilisation. 30 s gives about 6,000 university flows per run.

**About the results**
- **What is the hit rate?** The share of new TCP connections whose first packet found a rule at the sender's switch, so it never went to the controller. We count the SYN packets that reached the controller.
- **What is the oracle, and isn't it cheating?** It cheats on purpose. It reads the future flow schedule and installs the busiest pairs before the run. No real controller can do that. It gives the best hit rate any predictor could reach with the same budget. Same idea as Belady's optimal algorithm in caching.
- **Why didn't you use ML?**
  - The oracle shows that at 25–50% budgets a perfect predictor adds only 5–11 points over a simple counter on our traffic.
  - ML could matter for traffic where one flow predicts flows on *other* pairs (microservice call chains), but only at a scale where most pairs are idle, which needs hundreds of hosts.
  - See `docs/literature/ML_Rule_Prediction_Survey.md`, section D.
- **Proactive wins on your networks, so why a hybrid?** Proactive needs a rule for every pair: O(N²). On 16 hosts that is only 624 rules. On the 54-host fat-tree it is already 13,230 in total, against 2,058 for reactive; the busiest switch holds 312. DevoFlow's real switch holds 1,500 wildcard rules [p.4]. An edge switch of a fat-tree needs about k × N pair rules, which passes 1,500 at about 250 hosts. The budget is the middle ground for networks of that size and larger.
- **Why do the numbers differ between the single runs and the repeats?** The single runs were in Windows "Balanced" power mode, the repeats in "Best performance". Absolute times about halved; every ranking held. We compare numbers only within one batch.
- **How are the confidence intervals computed?** 5 runs with different seeds; mean ± t(0.975, 4) × standard deviation / √5, with t = 2.776 (`experiments/repeats.py`).
- **What is the amplification effect?** Under load, one new flow causes more PACKET_INs: about 12 instead of up to 6. More packets of the same flow reach the switch before its rule is installed, and each of them asks the controller again. It is a feedback loop towards overload.

**About novelty and previous work**
- **What is new here?** Not an algorithm: the side-by-side measured comparison, on one testbed with published traffic. Each comparison and the closest paper are in `docs/Evaluation_Plan.md`. The path vs setup split is something we did not find in any paper.
- **How is your hybrid different from CacheFlow?** CacheFlow caches policy rules with dependencies, on hardware with Zipf traffic. Ours pre-installs host-pair rules chosen by a decaying counter. We do not claim it is better; we use it to measure what a budget buys.
- **Where do the traffic parameters come from?** Every one has a row in `docs/Realism_Sources.md`, with the paper and how we checked it (in the PDF, online, or in the data file). Example: the SURGE ISP flow sizes match Table 1 and Section 4 of Barford & Crovella 1998.

**About what is missing**
- **Multiple PCs?** The tool is ready and tested (`controller_agent.py`, `--controller-host`, WSL2 networking documented). The run across two laptops is scheduled; answer with its date and, once done, its result.
- **Biggest limitations?** Emulation, not hardware; POX single-threaded; small networks; generated traffic (except the ISP volumes, which are real); Zipf pair popularity is an assumption from CacheFlow.

---

## 8. Things not to say

- "Our hybrid beats proactive." It does not, on our networks.
- "We used machine learning." We did not; we measured the upper bound for it.
- "This is a novel algorithm." The contribution is the comparison.
- "Results are on real hardware." They are emulated.
- Any number that is not in a table in the repo.
