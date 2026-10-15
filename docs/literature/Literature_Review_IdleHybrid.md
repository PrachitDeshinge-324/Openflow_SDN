# Literature Review: Preparing Flow Rules During Quiet Time

**CS G525 Advanced Computer Networks · Research Project SA7 · Group 2**
Review for our extension, the **idle-time hybrid controller**.

---

## 0. Our idea in one paragraph

Reactive controllers make the first packet of every new flow wait for the controller. Proactive controllers avoid that wait but fill the switch with rules for every possible flow. Our extension is a **hybrid**. The controller keeps working reactively, but it also **watches which host pairs talk most often**. When the controller is **quiet** (few PACKET_IN messages), it **pre-installs rules for the most popular pairs**, up to a **fixed rule budget per switch**. Everything it did not predict is still handled reactively. The aims are near-proactive first-packet latency, a small flow table, and no extra controller work while it is busy.

**Research question:** Can a reactive controller that pre-installs rules only during idle periods get close to proactive first-packet latency, while using a fraction of the flow table and adding no controller load during bursts?

---

## 1. How this review was done

- We searched for work on five topics:
  1. the cost of reactive flow setup;
  2. keeping packets in the data plane (proactive designs);
  3. rule caching under limited flow-table (TCAM) space;
  4. flow-rule timeouts and eviction;
  5. hybrid proactive/reactive installation, including prediction-driven installation.
  
  We also looked at measurement studies of real traffic, to justify our workload.
- **14 papers** are covered, grouped by theme.
- **11 of the 14 were checked against their full text.** Every number from those papers carries a page reference, for example **[p.9]**. The PDFs are in `docs/literature/papers/`; see the Appendix.
- **3 papers are paywalled** (PARD, the IEEE 2022 hybrid paper, Humayun 2025). For these we used only the published abstract, marked **[Abstract]**. Get the full text through the BITS library before the final report.
- Corrections made after reading the full texts are listed in the **Verification log** at the end.

---

## 2. Summary table

| # | Paper (year, venue) | What it does, in one line | Key result | Source | How it relates to our idea |
|---|---|---|---|---|---|
| 1 | **Ethane** (Casado et al., 2007, SIGCOMM) | Central controller sets up **every** flow reactively | One controller could "comfortably handle **10,000 new flow requests per second**"; set up flows in **< 1.5 ms** at up to 11,000 flows/s | [p.9] | The classic reactive design we start from |
| 2 | **DIFANE** (Yu et al., 2010, SIGCOMM) | Keeps all packets in the data plane by pre-placing rules in "authority" switches | First-packet RTT **10 ms (NOX)** vs **0.4 ms (DIFANE)**; flow setup **75K vs 20K flows/s** on one switch | [p.9] | Shows the latency gain from proactive placement, which is what we try to get cheaply |
| 3 | **DevoFlow** (Curtis et al., 2011, SIGCOMM) | Keeps the controller only for "significant" (elephant) flows | **10–53×** fewer flow-table entries, **10–42×** fewer control messages; a real switch did only **≈275 flow setups/s** | [p.1], [p.4] | Reactive setup does not scale, and only popular/heavy flows need special handling |
| 4 | **On Controller Performance** (Tootoonchian et al., 2012, Hot-ICE) | Benchmarks controllers with cbench | NOX-MT: **1.6 M requests/s**, **2 ms** average response on 8 cores; **33×** faster than NOX (≈30k flows/s) | [p.1], [p.6] | Controller capacity limits; puts our POX numbers in context |
| 5 | **Kandoo** (Hassas Yeganeh & Ganjali, 2012, HotSDN) | Two-layer controllers: local controllers absorb frequent events | Root-controller load **5× lower in packets** and **about 10× lower in bytes** | [p.4] | Another way to cut controller load; ours cuts it by timing instead |
| 6 | **Network Traffic Characteristics of DCs in the Wild** (Benson et al., 2010, IMC) | Measures traffic in 10 real data centres | Traffic is **ON/OFF, heavy-tailed (lognormal fits)**; **80% of flows < 10 KB**; **80% last < 11 s** | [p.2], [p.6], [p.7] | Justifies our bursty ON/OFF workload with quiet gaps |
| 7 | **SmartTime** (Vishnoi et al., 2014, DEBS) | Adaptive idle timeouts + proactive eviction of rules | Up to **58% lower total cost** than the best static timeout or random eviction (real DC traces) | [p.1] | Timeouts matter; motivates our "keep rules longer" baseline and our eviction of unpopular rules |
| 8 | **CacheFlow** (Katta et al., 2016, SOSR) | Caches the most popular rules in the TCAM, sends misses to software | **90% cache hits** by caching **< 5% of rules**; REANNZ trace: **84% with 2%**, **97% with 10%** of rules | [p.2], [p.9] | Strongest evidence that a small budget of popular rules can cover most traffic |
| 9 | **AH-IHTA** (Isyaku et al., 2020, Electronics) | Adaptive hybrid idle + hard timeouts by flow type, plus eviction | **28%** fewer flow-setup requests, **39%** fewer evictions | [p.1] | Timeout tuning alone already cuts controller requests: a baseline we must beat |
| 10 | **PARD** (Rzepka et al., 2020, J. Netw. Syst. Manag.) | Hybrid: coarse proactive entries + detailed reactive entries | "Significantly reduces" first-packet latency; works with existing hardware and protocols | [Abstract] | Closest hybrid design; it does not decide **when** to install based on controller load |
| 11 | **Hybrid Flow-Rule Placement** (Khoobbakht, Noei & Parvizimosaed, 2021, ICCKE) | Hybrid placement under flow-table limits to cut controller load | **20–50%** lower controller load on a real network | [Abstract] | Hybrids work in practice; also uses a table budget |
| 12 | **Mobility-Aware Hybrid Flow Rule Cache** (Kim, Park & Kyung, 2022, Electronics) | Uses an **LSTM to predict the controller's response delay**, then installs each flow's rule proactively or reactively | Better flow-table use, install delay and hit ratio than earlier schemes (simulation, Abilene topology) | [p.1], [p.8–9] | Install decision depends on the controller's state, close to our "busy vs quiet" idea |
| 13 | **LSTM scheduler for reactive OpenFlow** (Batista et al., 2024, Discover IoT) | Predicts the next IoT transmission with an LSTM and installs rules in advance | ≈**51% lower response time**; built on **Mininet + POX/Ryu, OpenFlow 1.0** | [p.3], [p.10] | **Same tools as ours**: the best published system to compare our predictor against |
| 14 | **Dynamic-timeout prediction & proactive eviction** (Humayun et al., 2025, Cluster Computing) | Predicts per-flow timeouts from packet inter-arrival times; evicts unused entries early | Better latency, PACKET_IN count, table occupancy and drops than reactive dynamic-timeout schemes | [Abstract] | Most recent related work; same metrics as ours |

---

## 3. The papers, by theme

### Theme A: Reactive flow setup is expensive

**1. Ethane: Taking Control of the Enterprise** (Casado, Freedman, Pettit, Luo, McKeown, Shenker; SIGCOMM 2007)
- **Idea:** a central controller decides every flow. Switches send the first packet of each new flow to it, and it installs the rule. This is the original **reactive** model.
- **Results:**
  - The deployment "supported over **300 hosts** for the past **four months**" [p.1].
  - About 120 hosts were active in any 5-minute window. They generated **30–40 new flow requests per second**, with a **peak of 750/s** [p.9].
  - Under load, "for up to **11,000 flows per second** … flows were set up in **less than 1.5 milliseconds** in the worst case" [p.9].
  - "A single Controller could comfortably handle **10,000 new flow requests per second**" [p.9], enough for a network of "**over 20,000 hosts**" [p.10].
  - Setup latency was **under 0.6 ms** at loads up to 6,000/s, and **0.4 ms** below 2,000/s [p.10].
- **For us:** our reactive baseline (`reactive_eval.py`, like POX's `l2_learning`) follows the same model. Ethane shows that even a fast controller adds delay to **every** new flow's first packet, which is what we measured.

**3. DevoFlow: Scaling Flow Management for High-Performance Networks** (Curtis, Mogul, Tourrilhes, Yalagandula, Sharma, Banerjee; SIGCOMM 2011)
- **Idea:** asking the controller for every flow overloads the switch and the controller. Handle most flows inside the switch (wildcard rules, **rule cloning**), and involve the controller only for **significant (elephant) flows**.
- **Results:**
  - A real HP ProCurve 5406zl switch "completes roughly **275 flow setups per second**" [p.4].
  - The switch's link from its forwarding chip to its CPU was "just **80 Mbit/sec**", against "**300 Gbit/sec**" of forwarding capacity [p.4].
  - The switch hardware "can support about **1500 OpenFlow rules**", against up to 64,000 ordinary Ethernet forwarding entries [p.5].
  - In simulation, DevoFlow "uses **10–53 times fewer** flow table entries at an average switch, and uses **10–42 times fewer** control messages" [p.1].
- **For us:**
  - It confirms the cost we measured: reactive setup sends a PACKET_IN per switch on the path.
  - It supports our core assumption: **only some flows deserve special treatment**. DevoFlow picks elephants; we pick **popular pairs**.

**4. On Controller Performance in Software-Defined Networks** (Tootoonchian, Gorbunov, Ganjali, Casado, Sherwood; Hot-ICE 2012)
- **Idea:** measure how many flow requests a controller can handle, using the `cbench` tool.
- **Results:**
  - Earlier studies reported that NOX "handles around **30k** flow initiation events per second" with sub-10 ms install time [p.1].
  - The authors' multi-threaded NOX-MT outperforms NOX "by a factor of **33**" on two quad-core 2 GHz CPUs [p.1].
  - On an 8-core 2 GHz machine, NOX-MT "handles **1.6 million requests per second** with an average response time of **2ms**" [p.6].
- **For us:**
  - Our POX controller is single-threaded Python. We measured **786 PACKET_IN/s at 36% of one core**, far below NOX-MT.
  - That is why our H2 (does *when* we install matter?) needs a **deliberately slowed controller** to reach saturation.

**5. Kandoo: A Framework for Efficient and Scalable Offloading of Control Applications** (Hassas Yeganeh & Ganjali; HotSDN 2012)
- **Idea:** two layers of controllers. Local controllers near the switches handle frequent, local events, and a root controller handles network-wide decisions.
- **Results:**
  - On a tree with fanout 6 (36 hosts, each starting 100 UDP flows), the root controller's load and control-channel use were "**five times smaller** in terms of packets … and an **order of magnitude** in terms of bytes", even when every flow was an elephant [p.4].
  - The local controllers scale linearly with network size [p.4].
- **For us:** an alternative way to cut controller load (more controllers). Ours cuts load by **choosing when to work**, with a single controller.

### Theme B: Keeping packets in the data plane (proactive)

**2. Scalable Flow-Based Networking with DIFANE** (Yu, Rexford, Freedman, Wang; SIGCOMM 2010)
- **Idea:** the controller **pre-partitions all rules** across "authority switches". A packet that misses at its first switch is redirected inside the data plane to the authority switch that has the rule, instead of going to the controller.
- **Results:** Click-based OpenFlow prototype vs NOX, at 100 single-packet flows/s.
  - With NOX, first packets "still experience a RTT of **10 ms** on average". With DIFANE, "only **0.4 ms** RTT". All following packets take **0.3 ms** in both [p.9].
  - On one switch, DIFANE reached the client's maximum setup rate of **75K flows/s**, while NOX managed **20K flows/s** [p.9].
  - With four ingress switches, NOX peaked at **50K** flows/s; DIFANE with one authority switch reached **800K** [p.9]. With four authority switches it exceeded **3M flows/s** [p.10].
  - Commercial OpenFlow switches of the time "can only send **60–330 flows/s** to the controller" [p.9].
- **For us:**
  - The same trend as our measurement: reactive **3.8–6.6 ms** vs proactive **0.7–0.9 ms** first packet. Like DIFANE, our "after the first packet" times are equal in both modes.
  - DIFANE pays for the speed by storing **all** rules somewhere. We try to store only the popular ones.

### Theme C: Caching popular rules in a small table

**8. CacheFlow: Dependency-Aware Rule-Caching for Software-Defined Networks** (Katta, Alipourfard, Rexford, Walker; SOSR 2016)
- **Idea:** treat the hardware flow table (TCAM) as a **cache**. Keep the **most popular rules** there and send misses to software switches. Overlapping wildcard rules depend on each other, so CacheFlow "splices" long dependency chains (cover-set and mixed-set algorithms) to cache safely.
- **Results:**
  - "Traffic tends to follow a **Zipf distribution**" [p.1]. CacheFlow reaches "a cache-hit rate of **90%** of the traffic by caching **less than 5%** of the rules" [p.2].
  - On a **two-day real trace** from the REANNZ research network: **84%** hit rate with a cache of **2%** of the rules, and up to **97%** with **10%** [p.9].
  - On the Stanford backbone policy with Zipf traffic: at least **88%** hit rate with 2,000 rules (**1.1%** of the table). Mixed-set leads dependent-set by at least **9%** [p.9].
- **For us:**
  - **This is the strongest support for our idea.** If traffic is skewed (Zipf), a small budget of popular rules covers most packets.
  - Differences:
    - CacheFlow caches *policy rules* in a hardware/software split.
    - We pre-install *pair rules* in one switch table.
    - We also decide **when** to install, based on controller load.
  - Our pair rules do not overlap, so we avoid CacheFlow's dependency problem. We also use a **Zipf** popularity distribution, the same assumption CacheFlow makes.

### Theme D: Timeouts and eviction

**7. SmartTime: Effective Switch Memory Management in OpenFlow Networks** (Vishnoi, Poddar, Mann, Bhattacharya; DEBS 2014)
- **Idea:**
  - One fixed idle timeout is a bad compromise. Too long wastes table space on dead flows; too short makes flows return to the controller.
  - SmartTime adapts the idle timeout per flow and **proactively evicts** rules when the table is getting full.
- **Results:** "using multiple real data center packet traces and cache sizes, SmartTime … consistently outperformed the best performing static idle timeout policy or random eviction policy by **up to 58%** in terms of total cost" [p.1]. Citing an earlier study, the paper notes that almost **50% of data-centre flows last under 1 second** and 80% under 10 seconds [p.1].
- **For us:**
  - It is why we added the **"reactive that simply keeps rules longer" baseline**: smarter timeouts alone give real gains.
  - It also supports our consolidator's step of **removing the least popular pre-installed rules** when over budget.

**9. AH-IHTA: Adaptive and Hybrid Idle–Hard Timeout Allocation and Flow Eviction** (Isyaku, Abu Bakar, Mohd Zahid, Yusuf; Electronics 2020)
- **Idea:** choose idle and hard timeouts per flow according to traffic pattern, protocol (TCP, UDP, ICMP) and how full the flow table is; evict entries when it fills.
- **Results:** "a **28%** and **39%** reduction in the flow setup request and flow eviction, respectively" [p.1]. Its eviction is compared with random, FIFO and LRU, and its timeouts with static ones.
- **For us:** another strong timeout-only baseline. If simple timeout tuning gives 28% fewer controller requests, our idea must do clearly better to be worth it.

**14. Dynamic-Timeout Prediction and Proactive Eviction for SDN Flow-Table Overflow Mitigation** (Humayun, Hamdan, Mohammed, Elshafie, Marsono; Cluster Computing 2025)
- **Idea:** predict a per-entry timeout from packet inter-arrival times (decision-tree based), and evict unused entries early when the table is short of space.
- **Results:** in simulation on several datasets, it beat reactive dynamic-timeout schemes on **latency, PACKET_IN count, table occupancy and packet drops** [Abstract].
- **For us:** the most recent related work, and it uses the **same metrics we plan to use**. It predicts *how long to keep* a rule; we predict *which rules to add in advance* and *when*.

### Theme E: Hybrid proactive + reactive installation

**10. PARD: Hybrid Proactive and Reactive Method Eliminating Flow Setup Latency in SDN** (Rzepka, Boryło, Lasoń, Szymański; J. Netw. Syst. Manag. 28, 2020)
- **Idea:** install **coarse proactive entries** so every new flow has somewhere to go immediately, while **detailed reactive entries** are installed for each flow in the background. It supports multiple flow tables and needs no protocol or hardware changes.
- **Results:** "significantly reduces" first-packet latency, which also reduces packet loss and improves perceived throughput [Abstract].
- **For us:** the closest hybrid design. PARD makes *every* flow fast through coarse rules, but it does not use popularity or controller load to decide **what** and **when** to install, which is our contribution.

**11. Hybrid Flow-Rule Placement Method of Proactive and Reactive in SDNs** (Khoobbakht, Noei, Parvizimosaed; 11th Int. Conf. on Computer and Knowledge Engineering (ICCKE), 2021; IEEE Xplore 9721507)
- **Idea:** combine reactive and proactive placement under limited flow-table capacity, installing rules that stop packets from being sent to the controller.
- **Results:** **20–50% lower controller load** in tests on a real network [Abstract].
- **For us:** evidence that hybrids reduce controller load in practice, also under a table budget. *(Authors and venue from the ICCKE conference listing; the IEEE Xplore page lists the publication year as 2022.)*

**12. Mobility-Aware Hybrid Flow Rule Cache Scheme in Software-Defined Access Networks** (Kim, Park, Kyung; Electronics 11(1):160, 2022)
- **Idea:**
  - An **LSTM network predicts the controller's next response delay**.
  - For each flow, its delay requirement is compared with that predicted delay. If the controller will be too slow, the rule is installed **proactively**; otherwise **reactively**.
  - An ILP (solved heuristically) decides how many proactive rules fit in the cache [p.1].
- **Setup:** simulation on the **Abilene WAN topology**, 10 mobile users, controller capacity **5,000 messages/s**, delay constraint 30 ms [p.8–9].
- **Results:** outperforms earlier schemes on flow-table utilization, rule-installation delay and hit ratio [p.1, p.11]. The paper reports the results as graphs only, with no headline numbers.
- **For us:**
  - The closest idea to our **"busy vs quiet"** switch: the install decision depends on the controller's state.
  - Difference: they decide per flow, based on delay needs and user mobility. We decide based on **controller idleness and pair popularity**.
  - Like sir's suggestion, they use a **real ISP topology (Abilene)**.

### Theme F: Predicting traffic to install rules in advance

**13. A New Intelligent Scheduler to Improve Reactive OpenFlow Communication in SDN-Based IoT Data Streams** (Batista, Alencar, Silva, Canário, Rios, Dustdar, Figueiredo, Prazeres; Discover Internet of Things 4:15, 2024)
- **Idea:** an **LSTM** predicts when an IoT device will send next, and the rule is installed **before** the request arrives. The **Page-Hinkley** test detects when the traffic pattern changes (concept drift).
- **Setup:** **Mininet**, **OpenFlow 1.0**, with **POX and Ryu** controllers [p.10, p.13, p.18], the same environment as ours.
- **Results:** "installing OpenFlow rules in advance reduced about **51%** of communications response time" [p.3].
- **For us:**
  - This is the **best published system to compare against**, as our reviewer asked ("compare with previous works which already have a predictor"). It runs on the same tools, so we can reuse its approach (LSTM predictor) as a baseline next to our simple popularity predictor (an EWMA score per host pair).
  - Its concept-drift handling also matches our **drift experiment**, where the popular pairs change over time.

### Theme G: What real traffic looks like (to design our workload)

**6. Network Traffic Characteristics of Data Centers in the Wild** (Benson, Akella, Maltz; IMC 2010)
- **Idea:** measure traffic in **10 data centres** (3 university, 2 private enterprise, 5 commercial cloud) using SNMP counters, topology data and packet traces.
- **Results:**
  - "Most flows in the data centers are small in size (**≤10KB**)" [p.2]; across data centres, "**80% of the flows are smaller than 10KB**" and "**80% of the flows are less than 11 seconds long**" [p.6].
  - Traffic from a rack "is **ON/OFF** in nature with properties that fit **heavy-tailed** distributions" [p.2]. The ON and OFF periods fit **lognormal** distributions best [p.7].
  - In cloud data centres "**80%**" of server traffic stays within the rack, while in university and enterprise data centres most traffic crosses the network [p.2].
- **For us:**
  - Our workload uses **ON/OFF bursts with quiet gaps**, which is realistic. The quiet gaps are where our consolidator works.
  - This paper also gives us real **university and data-centre traffic parameters**, as our reviewer asked for.

---

## 4. Our measurements next to the literature

| What | Literature | Our testbed (WSL2, Open vSwitch kernel datapath, POX) |
|---|---|---|
| First-packet delay, reactive | 10 ms (NOX, DIFANE p.9); < 1.5 ms worst case (Ethane p.9) | **3.8–6.6 ms** |
| First-packet delay, proactive / data plane | 0.4 ms (DIFANE p.9) | **0.67–0.86 ms** (includes Open vSwitch's cache fill) |
| Delay of later packets | 0.3 ms, equal in both modes (DIFANE p.9) | **0.06–0.09 ms**, equal in both modes |
| Controller capacity | NOX ≈30k flows/s; NOX-MT 1.6M/s (Tootoonchian p.1, p.6); Ethane ≈10k/s (p.9) | POX: 786 PACKET_IN/s used **36%** of one core |
| Switch → controller capacity | 275 setups/s (DevoFlow p.4); 60–330 flows/s (DIFANE p.9) | Not a limit for software Open vSwitch in our tests |
| Small rule budget covers most traffic | 90% hits with < 5% of rules; 84% with 2% (CacheFlow p.2, p.9) | To be tested: our budget sweep (10–100% of proactive) |
| Effect of timeouts | Up to 58% lower cost (SmartTime p.1); 28% fewer setups (AH-IHTA p.1) | Our 10 s idle timeout left **2,321 rules** after 5 s at 200 new flows/s; the long-timeout baseline will measure this |

Numbers from different papers are **not directly comparable**: different hardware, controllers and years. The table shows that our results are **in the same range and show the same trends** as published work.

---

## 5. The gap our idea fills

What the literature already covers:
- **Reactive vs proactive trade-off:** well known (Ethane, DIFANE, DevoFlow).
- **Caching popular rules** in a small table works very well (CacheFlow: 90% hits with < 5% of rules).
- **Smarter timeouts and eviction** reduce controller requests and table use (SmartTime, AH-IHTA, Humayun 2025).
- **Hybrid installation** reduces latency and controller load (PARD, IEEE 2022).
- **Prediction-driven pre-installation** works (Batista 2024: −51% response time, on POX).
- One paper makes the install choice depend on the **predicted controller response delay** (Kim 2022).

What we **did not find** in the papers we reviewed:
- A controller that **schedules its proactive installs into the controller's idle periods** (busy/quiet detection with hysteresis), and
- does so **under a fixed per-switch rule budget**, and
- is evaluated against **(a)** the same predictor installing immediately and **(b)** plain reactive with longer timeouts, to separate **"what to install"** from **"when to install"**.

> **In simple words:** others decided **which** rules to keep or add. Kim 2022 made the choice depend on the controller's delay, but per flow and at the moment the flow arrives. Our new part is choosing **when** to do the work: only when the controller is free. We also test honestly whether that timing matters at all (our H2).

*This is a claim about the papers we reviewed, not proof that nobody has done it. Do one more search before the final report (Google Scholar: "idle period" / "background" rule installation SDN controller load).*

---

## 6. What we take from the literature into our design

| Design choice in our extension | Taken from |
|---|---|
| Pre-installed rules match **host pairs** (source/destination), not exact connections | DevoFlow (wildcard rules), CacheFlow (rules must match future traffic) |
| A **fixed rule budget per switch**; remove the least popular when over budget | CacheFlow (small cache of popular rules), SmartTime (proactive eviction) |
| A **"keep rules longer" baseline** | SmartTime, AH-IHTA (timeouts alone give large gains) |
| An **"install immediately" baseline** with the same predictor | Separates our timing idea from prediction (PARD and Batista install as soon as they decide) |
| An **LSTM-predictor baseline** next to our EWMA predictor | Batista 2024 (same tools: Mininet + POX), Kim 2022 |
| **Zipf** popularity of host pairs, plus a **drift** experiment | CacheFlow (traffic follows Zipf), Batista 2024 (concept drift) |
| **ON/OFF bursty workload** with lognormal ON/OFF periods; mostly short flows | Benson 2010 (ON/OFF, lognormal, 80% < 10 KB, 80% < 11 s) |
| **Real ISP topology** (e.g. Abilene) in addition to trees | Kim 2022 (Abilene), our reviewer's feedback |
| A **slowed controller** to test saturation (H2) | Tootoonchian 2012 (controller capacity), DevoFlow and DIFANE (setup-rate limits) |
| Metrics: first-packet latency, **hit rate**, **PACKET_IN count**, **table occupancy**, wasted installs | DIFANE (first-packet RTT), CacheFlow (hit rate), Humayun 2025 (PACKET_IN, occupancy) |

---

## 7. References

1. M. Casado, M. J. Freedman, J. Pettit, J. Luo, N. McKeown, S. Shenker. *Ethane: Taking Control of the Enterprise.* ACM SIGCOMM 2007. doi:10.1145/1282427.1282382
2. M. Yu, J. Rexford, M. J. Freedman, J. Wang. *Scalable Flow-Based Networking with DIFANE.* ACM SIGCOMM 2010; CCR 40(4):351–362.
3. A. R. Curtis, J. C. Mogul, J. Tourrilhes, P. Yalagandula, P. Sharma, S. Banerjee. *DevoFlow: Scaling Flow Management for High-Performance Networks.* ACM SIGCOMM 2011, pp. 254–265.
4. A. Tootoonchian, S. Gorbunov, Y. Ganjali, M. Casado, R. Sherwood. *On Controller Performance in Software-Defined Networks.* USENIX Hot-ICE 2012.
5. S. Hassas Yeganeh, Y. Ganjali. *Kandoo: A Framework for Efficient and Scalable Offloading of Control Applications.* ACM HotSDN 2012, pp. 19–24.
6. T. Benson, A. Akella, D. A. Maltz. *Network Traffic Characteristics of Data Centers in the Wild.* ACM IMC 2010, pp. 267–280. doi:10.1145/1879141.1879175
7. A. Vishnoi, R. Poddar, V. Mann, S. Bhattacharya. *Effective Switch Memory Management in OpenFlow Networks* (SmartTime). ACM DEBS 2014, pp. 177–188. doi:10.1145/2611286.2611301
8. N. Katta, O. Alipourfard, J. Rexford, D. Walker. *CacheFlow: Dependency-Aware Rule-Caching for Software-Defined Networks.* ACM SOSR 2016. doi:10.1145/2890955.2890969
9. B. Isyaku, K. Abu Bakar, M. S. Mohd Zahid, M. N. Yusuf. *Adaptive and Hybrid Idle–Hard Timeout Allocation and Flow Eviction Mechanism Considering Traffic Characteristics.* Electronics 9(11):1983, 2020. doi:10.3390/electronics9111983
10. M. Rzepka, P. Boryło, A. Lasoń, A. Szymański. *PARD: Hybrid Proactive and Reactive Method Eliminating Flow Setup Latency in SDN.* J. Netw. Syst. Manag. 28:1547–1574, 2020. doi:10.1007/s10922-020-09550-z
11. M. Khoobbakht, M. Noei, M. Parvizimosaed. *Hybrid Flow-Rule Placement Method of Proactive and Reactive in SDNs.* 11th Int. Conf. on Computer and Knowledge Engineering (ICCKE), 2021. https://ieeexplore.ieee.org/document/9721507
12. Y. Kim, J. Park, Y. Kyung. *Mobility-Aware Hybrid Flow Rule Cache Scheme in Software-Defined Access Networks.* Electronics 11(1):160, 2022. doi:10.3390/electronics11010160
13. E. Batista, B. Alencar, E. Silva, J. Canário, R. A. Rios, S. Dustdar, G. Figueiredo, C. Prazeres. *A New Intelligent Scheduler to Improve Reactive OpenFlow Communication in SDN-Based IoT Data Streams.* Discover Internet of Things 4:15, 2024. doi:10.1007/s43926-024-00068-3
14. U. Humayun, M. Hamdan, M. S. Mohammed, H. Elshafie, M. N. Marsono. *Dynamic-Timeout Prediction and Proactive Eviction for SDN Flow Table Overflow Mitigation.* Cluster Computing 28:456, 2025. doi:10.1007/s10586-025-05227-x

---

## Verification log

What changed after reading the full texts of papers 1–9, 12 and 13:

| Paper | Before (from abstracts, slides, surveys) | After (full text) |
|---|---|---|
| Ethane | 10,000 flows/s marked as "secondary" | **Confirmed in the paper** [p.9]; added setup-latency and load numbers |
| DIFANE | 10 ms vs 0.4 ms from the slides | **Confirmed in the paper** [p.9]; added 0.3 ms later packets, 75K vs 20K flows/s, 800K and 3M flows/s, 60–330 flows/s for commercial switches |
| DevoFlow | Chip-to-CPU link "35 Mbit/s" | **Corrected to 80 Mbit/s** [p.4] (35 was likely the earlier HotNets version) |
| Tootoonchian | NOX-MT latency "2–3 ms" | **Corrected to 2 ms** [p.6] |
| Kandoo | No numbers | **Added:** 5× fewer packets, about 10× fewer bytes at the root controller [p.4] |
| Benson | 80% < 10 KB and 80% < 11 s marked as "secondary" | **Confirmed in the paper** [p.6]; lognormal fit is in this paper [p.7] |
| CacheFlow | 87% at 1% cache from an older report | **Replaced** with this paper's own numbers: 84% with 2%, 97% with 10% (REANNZ), ≥ 88% at 1.1% (Stanford) [p.9] |
| Kim 2022 | "Numbers not retrieved" | **Added:** uses an LSTM to predict controller delay; Abilene topology; 5,000 msg/s controller; results reported only as graphs |
| Batista 2024 | Lead author inferred | **Confirmed full author list**; confirmed Mininet + POX/Ryu + OpenFlow 1.0 |
| SmartTime, AH-IHTA | From abstracts | **Confirmed** [p.1] |

Still from abstracts only (paywalled): PARD (10), IEEE hybrid placement (11), Humayun 2025 (14).

---

## Appendix: Getting the PDFs

```bash
bash docs/literature/download_papers.sh
```

This downloads the freely available papers into `docs/literature/papers/`. MDPI papers (9 and 12) block command-line downloads, so open their links in a browser and save the files into that folder. The folder is **git-ignored**: the PDFs are copyrighted by their publishers and our repository is public, so we keep them locally and cite the references above. Papers 10, 11 and 14 are paywalled; get them through the BITS library.
