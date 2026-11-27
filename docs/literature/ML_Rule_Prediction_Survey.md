# Survey: Prediction and ML for OpenFlow Flow Rules: What Do They Compare Against?

CS G525, Project SA7, Group 2. Compiled 15 Oct 2026.

**The question.** When papers use prediction or machine learning to manage flow rules, do they show that it beats **simple baselines** (a frequency counter, LRU/LFU, a fixed or longer timeout)? Or only that it beats plain reactive? This decides whether our extension has a real gap to fill.

**How it was done.**
- Web searches (Google-style) on proactive/predictive rule installation, ML eviction, ML timeouts, rule caching with prefetching, and RL rule placement.
- For each paper: what it predicts with, **what it is compared against**, how it was tested, and on what traffic.
- **Checked level:**
  - **Full text**: we read the paper (in `docs/literature/papers/`).
  - **Abstract**: only the abstract, publisher page or other papers quoting it. Treat these rows as **unverified**: baselines named in an abstract may be incomplete. Check the full text before quoting a row in the report.

Abbreviations:
- **LRU:** least recently used.
- **LFU:** least frequently used. LFU is a counter.
- **MBF:** Multiple Bloom Filters, a heuristic.
- **RL / DRL / DQN:** (deep) reinforcement learning / deep Q-network.

---

## A. Pre-installing rules before flows arrive (our problem)

| # | Paper | Predictor | Compared against | Simple frequency baseline? | Tested on | Traffic | Checked |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | Batista et al., *Discover IoT* 2024: intelligent scheduler for reactive OpenFlow | LSTM: time until a device's next transmission | Reactive mode | **No** | Mininet + POX, Ryu | IoT sensor streams (periodic intervals) | Full text |
| A2 | Bull, Austin, Sharma, FiCloud 2015: PFIM, pre-emptive flow installation for IoT | Learns each flow's transmission interval (not ML) | Reactive (proof of concept) | It *is* a simple method | Proof of concept | Periodic IoT | Abstract |
| A3 | PSPFIM / EPFIM / DAPFIM (*Computer Networks* 2021, dynamic adjustment) | Period detection, down to ms | Earlier PFIM variants | Variants of a simple method | ? | Periodic IoT | Abstract |
| A4 | CTTC 2018: SDN-based pro-active flow installation for delay reduction in IoT | ? | Reactive; −90% installation delay | **No** (as far as the abstract shows) | Experimental | IoT | Abstract |
| A5 | Kim et al., *Electronics* 2022: mobility-aware hybrid flow-rule cache | Delay-aware proactive/reactive choice per flow | Basic reactive cache; MobiFlow | **No** | Simulation (Abilene) | Mobility | Full text |
| A6 | Bera, Misra, Obaidat (IEEE): Mobi-Flow | Order-k Markov predictor of user location | OSPF, minimum occupied rule capacity, distributed (non-SDN), MoRule | **No** | Simulation | Mobility | Abstract / PDF snippet |
| A7 | *J. Cloud Computing* 2024: mobility-aware adaptive flow-entry placement for SDN-IoT | Q-learning + AdaBoost | ? | ? | ? | Mobility | Abstract |
| A8 | Sowmya et al., *ETASR* 2026: LSTM-based QoS-aware proactive flow-rule placement in SD-IoV | LSTM: vehicle's next access point | "Existing methods" (not named in abstract) | ? | ? | Vehicular mobility | Abstract |
| A9 | Nokia Bell Labs 2019: DRL application for network latency management | DRL for placement + LSTM traffic forecast | Not named in the listing | ? | ONOS + Open vSwitch | ? | Abstract |
| A10 | Rzepka et al., *JNSM* 2020: PARD hybrid proactive/reactive (not ML) | Hybrid method | Not in the abstract | ? | ? | ? | Abstract (paywalled) |
| A11 | Red Hat Research 2026: on the benefits of predictable traffic in virtual switches | Studies pre-emptive installation of predicted flows in a virtual switch | Benefit **varies with the flow rate** of the traces | n/a (benefit study) | Virtual switch | Traces | Abstract |
| A12 | Hariri, Yuksel, Mohaisen, IEEE ICMLCN 2024: RL-based speculative installation of unseen flows in SDNs | Reinforcement learning | **Not read** | ? | ? | ? | **Cited only** (found 22 Nov in the references of B1; not on arXiv, not accessible to us). Not counted in the paper's 11 |

**Pattern in A:**
- **Baselines:** reactive, other placement schemes, or unnamed "existing methods".
- **Missing:** in the papers found, **none compares against a frequency counter, or an LRU/LFU-style policy, choosing which rules to pre-install under the same rule budget.**
- **Traffic:** almost all use **periodic IoT** or **mobility**, where the future is structured; almost none use data-centre, campus or ISP traffic.

---

## A'. The 11 pre-installation papers, as counted in the paper (Paper_TODO 0.1)

One section per paper (what it does, setup, baselines, results, granularity, upper bound): `Preinstallation_Papers_Summary.md`.

Built 22 Nov from section A above and `Literature_Review_IdleHybrid.md`. "n/s" = not stated in the material we
had: for **Abstract** rows that means the abstract does not say it, not that the paper lacks it. A12 (Hariri et
al.) was found later, could not be read, and is not counted.

| # | Baseline group (paper, Section II) | Baselines named | Coarse-rule reactive baseline? | Frequency counter at the same rule budget? | Upper bound / oracle? | Traffic | Network size | Evaluation | Code | Checked |
|---|---|---|---|---|---|---|---|---|---|---|
| A1 | Plain reactive only | Reactive mode (POX, Ryu) | No | No | No | Periodic IoT streams | small Mininet (n/s) | Emulation (Mininet) | n/s | Full text |
| A2 | Plain reactive only | POX L3 learning switch; the pre-installed rule is the same rule, re-installed before each 5 s ping (idle timeout 1 s) | n/a (same rule) | No (it is itself a simple method) | No | One periodic ping flow | 1 switch, 2 hosts | Emulation (Mininet, POX); RTT about 10 ms to under 1 ms | n/s | **Full text** (25 Nov) |
| A4 | Plain reactive only | Conventional reactive (Ryu); same rule, idle timeout 1 s below the 3-5 s duty cycle; no longer-timeout baseline | n/a (same rule) | No | No | Periodic and periodic/bursty sensor traffic (2 Z1 motes) | 2 gateways | Testbed: Raspberry Pi 3 + OVS 2.7, Ryu 4.4; head-of-flow delay 4 ms to 0.4 ms, OF messages 3 to 1 | n/s | **Full text** (25 Nov) |
| A5 | Reactive and other published schemes | Basic reactive cache; MobiFlow (a predictor) | No | No | No | Mobile users | Abilene, 10 users | Simulation | n/s | Full text |
| A6 | Reactive and other published schemes | OSPF, minimum-occupied-rule-capacity, distributed (non-SDN), MoRule | n/s | n/s | n/s | Mobility | n/s | Simulation | n/s | Abstract / PDF snippet |
| A3 | Own earlier variants | Earlier PFIM variants | n/s | n/s | n/s | Periodic IoT | n/s | n/s | n/s | Abstract |
| A7 | Reactive and other published schemes | Standard hard-timeout scheme ("table miss"); Mobi-Flow | No (rule contents random, granularity not stated) | No | No | Exponential flow arrivals, mobile end devices | Tree, 25 switches, 200 hosts (parameter table says 3 switches) | Simulation (NS3, Matlab); delay 3.29 / 4.21 / 7.35 ms | n/s | **Full text** (25 Nov) |
| A8 | Reactive and other published schemes | Reactive controller; FIFO and LRU schemes | **No; confound present**: pre-installed rules match a DSCP class, reactive rules match a src/dst MAC pair | No (LRU is named as a scheme, not as a budgeted pre-installation baseline) | No | Vehicular mobility (PeMS data) | 10 APs, 10 vehicles | Emulation (Mininet, Ryu); RTT 0.15 / 0.27 ms vs 2.04 ms reactive; -32% vs FIFO, -36% vs LRU | dataset public | **Full text** (25 Nov) |
| A9 | No baseline named | n/s | n/s | n/s | n/s | n/s | n/s | ONOS + Open vSwitch | n/s | Abstract |
| A10 | No baseline named | n/s (paywalled) | n/s | n/s | n/s | n/s | n/s | n/s | n/s | Abstract |
| A11 | Benefit study: no prediction vs perfect prediction | Empty OVS caches vs "Optimal" (all associated flows preloaded), with partial prediction in between | n/a (same OVS cache mechanism) | No | **Yes**: the perfect-prediction case is a stated performance ceiling | Google search RPC and Facebook Hadoop coflow traces | up to 200,000 flows | Testbed: OVS 3.3 / OVN on Xeon servers; predicting 25% of flows: about -24% latency, -12% CPU; benefit shrinks at high flow rates | n/s | **Full text** (25 Nov) |

**Counts (11 papers, updated 25 Nov after reading A2, A4, A7, A8 and A11 in full):** 3 compare only against plain reactive installation (A1, A2, A4); 4 against reactive and other published schemes (A5, A6, A7, A8); 1 against its own earlier variants (A3); 2 name no baseline in the abstract available (A9, A10); 1 compares no prediction with perfect prediction (A11). Read in full: 7 (A1, A2, A4, A5, A7, A8, A11); abstract only: 4 (A3, A6, A9, A10). Of the 7 read in full: in A2 and A4 the pre-installed rule is the rule the reactive baseline installs, so granularity is not confounded; their gain comes from installing it before a 1 s idle timeout (shorter than the traffic period) lets it expire, and neither reports a baseline with a longer timeout. A8 pre-installs coarser rules (per DSCP class) than its reactive baseline (per MAC pair), with no same-granularity reactive baseline. None of the 7 compares coarser pre-installed rules with a reactive baseline of the same granularity. Only A11 reports an upper bound (its perfect-prediction ceiling). Traffic is periodic IoT or mobility in 8 of the 9 rows that state it (A11: data-centre traces). The earlier statement "none reports an upper bound" was wrong for A11.

---

## B. ML for eviction, caching and timeouts (which rules to keep or remove)

| # | Paper | Method | Compared against | Simple baseline? | Result vs simple baseline | Tested on | Checked |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B1 | Rouf & Yuksel, arXiv 2025: spatial encoding of flow spaces | DQN eviction + Bloom-filter encoding | **LRU, LFU** | **Yes (LFU is a counter)** | **Only ~7% (vs LRU) and ~8% (vs LFU) lower *normalized* miss rate** (the gap to the optimal policy: 0.512 to 0.467 vs LFU), which is **+0.95 (LFU) and +1.60 (LRU) points of hit rate**, over 10 h of traffic; reports an optimal (Belady) bound; tables of 16-32 entries | Discrete-time simulator, IoT traces; code public | **Full text** (arXiv 2509.16485, read 22 Nov) |
| B2 | Zang et al., IEEE 2023: DRL-driven aggregate flow-entry eviction | DRL | Random, LRU | Yes (recency) | −37% overflows, −87% reinstallations, −45% signalling vs Random/LRU | ? | Abstract |
| B3 | arXiv 1809.09003 (ACM TAAS): SDN flow entry management using RL | RL / DRL: keep in switch or controller | Multiple Bloom Filters (heuristic) | Heuristic, not LRU/LFU | −60% control overhead, +14% table-hit ratio vs MBF (4 KB table) | **Mininet emulation** | Abstract |
| B4 | Challa, Lee, Choo, NetSoft 2016: intelligent eviction (not ML) | Multiple Bloom Filters scoring | **LRU** | Yes | +37% table-hit ratio vs LRU (2K table) | ? | Abstract |
| B5 | Huang & Youn, *Front. Comput. Sci.* 2020: proactive eviction with HMM | Hidden Markov model of matching probability | Hard timeout; FlowMaster | Fixed timeout | Fewer table misses | Simulation | Abstract |
| B6 | Kannan & Banerjee, ICDCN 2014: FlowMaster | Per-flow prediction for early eviction | ? | ? | ? | ? | Cited only |
| B7 | H. Li, S. Guo, C. Wu, J. Li, ICC 2015 (arXiv 1803.04270): FDRC flow-driven rule caching | Prefetching for predictable flows + replacement | **FIFO, LRU** | Yes (recency) | "Significantly outperforms" | Simulation | Abstract |
| B8 | Li, Chi, Wang, ACM ICPS 2019: LSTM cache prefetching for flow tables | LSTM predicts future rules | **FIFO, LRU** | Yes (recency) | Higher TCAM hit ratio (no numbers in abstract) | ? | Abstract |
| B9 | *Cluster Computing* 2025: dynamic-timeout prediction + proactive eviction | Decision tree predicts timeout | Reactive dynamic-timeout methods | Partly | Better latency, PACKET_IN, occupancy, drops | Simulation | Abstract |
| B10 | Harris et al., *JNSM* 2024: DDT | RL assigns timeouts | **Static timeouts** | Yes (fixed timeout) | Better match rate and rule activity | ? | Abstract |
| B11 | DRL-FTO, AINTEC 2021 | DQN tunes timeouts | Estimation-based methods | No fixed-timeout baseline found | Fewer messages, same throughput | **Mininet + Ryu**, synthesized Internet traffic | Abstract |
| B12 | Liao et al., *Sensors* 2024: explainable timeout optimisation for elephant prediction | **Logistic regression** + Bayesian optimisation | Not retrieved | ? | ? | ? | Abstract |
| B13 | Isyaku et al., *Electronics* 2020: AH-IHTA (not ML) | Adaptive idle/hard timeouts | Fixed timeouts | Yes | −28% flow setups, −39% evictions | Ryu + Open vSwitch | Full text |
| B14 | Vishnoi et al., DEBS 2014: SmartTime (not ML) | Adaptive timeouts | Fixed timeouts | Yes | Up to −58% cost | Open vSwitch + IBM G8264 hardware switch | Full text |

**Pattern in B:**
- **Simple baselines are common:** eviction and timeout papers usually compare with LRU, FIFO, Random or fixed timeouts, and one compares with LFU.
- **Gains vary a lot.** The only paper we found that compares with **LFU** (B1, a frequency counter) beats it by just **~8%**. Large gains (B2) are reported against **Random and LRU**, not against a frequency counter.

---

## C. Evidence that simple methods match or beat complex ones (adjacent problems)

| # | Paper | Finding | Checked |
| --- | --- | --- | --- |
| C1 | Jurkiewicz, arXiv 2005.00173 (AGH), 2020: boundaries of flow-table reduction via elephant detection | **Plain packet sampling** cut flow entries **up to 400×** while still covering 80% of traffic. It can serve as a lower bound for, and replace, more complex detectors where rerouting is allowed. Based on a 30-day campus trace of ~4 billion flows. | Abstract |
| C2 | Same group, 2024: elephant flow classification on the first packet with neural networks | Neural networks at the first packet: **up to 15×** fewer entries at 80% coverage. First-packet methods are bounded more tightly than sampling (different conditions, so not a direct head-to-head). | Abstract |
| C3 | *Scientific Reports* 2024: ACL policy change with reactive and proactive installation | Proactive installs rules "where there will be no communication". Reactive came out better on several metrics in their simulation. | Abstract |

---

## D. What this means for our project

1. **The gap is specific to pre-installation (Section A).**
   - **What exists:** prediction-based pre-installation is shown to beat **reactive**, mostly on **periodic IoT or mobility** traffic.
   - **What we did not find:** a comparison against a **simple frequency counter** (top-K by weighted count) choosing what to pre-install **under the same rule budget**, and none on data-centre, campus or ISP traffic.
2. **Do not claim "nobody compares ML with simple baselines" in general.** It is false for eviction and timeouts (Section B), where LRU, LFU and fixed timeouts are standard.
3. **That literature is a warning sign for ML.** Against LFU (a counter), DQN eviction gained only ~8% (B1). Against simple sampling, complex elephant detection did not do better (C1, C2).
4. **Our weighted-counter baseline has a name in caching.** A frequency count with exponential decay is close to the classic **LRFU** policy (Lee et al., *IEEE Trans. Computers* 2001), which blends LRU and LFU. To check before citing: the exact reference and formula.
5. **How to word our gap safely:**
   > "Prediction-based pre-installation has been shown to beat reactive mode, mainly on periodic IoT and mobility traffic. In the papers we reviewed, it was not compared with a simple frequency-count predictor under the same rule budget, nor evaluated on data-centre, campus or ISP traffic. In the related eviction problem, where LFU baselines are used, ML gains can be small (≈ 8%)."

6. **What our measurements add (Step 4, 15 Oct 2026).** We ran the weighted counter against an **oracle**, which pre-installs the pairs that really carry the most flows, at the same budget (`docs/Budgeted_Hybrid_Experiment.md`):
   - at 25–50% of host pairs the counter reached **0.88–0.94 of the oracle's hit rate** on university, data-centre and real ISP traffic;
   - so no predictor, ML or otherwise, could add more than 5–10 points of hit rate there;
   - the gap is larger only at a 10% budget with many flows per pair (0.47 of the oracle in 30 s, 0.74 in 120 s), and part of that is our counter's design.

   This supports point 3, and it narrows where an ML comparison (Evaluation Plan #8) could show anything.

**Caveat.** Most rows were checked from abstracts only. Before the final report:
- read the full text of **A6, A8, A9, B1, B2, B7 and B8**, the most relevant ones;
- run one Google Scholar search: "flow rule pre-installation" + "LFU" / "frequency".
