# Realism Sources: Which Paper Is Behind Each Choice

CS G525 Advanced Computer Networks, Project SA7, Group 2

Every network, traffic pattern and parameter in our experiments should come from a published measurement or a standard design, so that nobody can say "you made this up". This document tracks those sources.

**How to use it**
- When you add or change a network, traffic pattern or parameter, add a row with the paper behind it.
- **Status:**
  - **Used**: already in our experiments.
  - **Planned**: chosen for the next step.
  - **Option**: a possible extra.
- **Verified:**
  - **PDF**: checked in the paper's full text.
  - **Online**: checked from the paper's public pages or abstract, or from papers quoting it.
  - **POX source**: checked in POX's code.
  - **To check**: not confirmed yet; do not quote the number until it is checked.
- The full reference list is in Section 5. Numbers like [1] point there.

---

## 1. Realistic networks (topologies)

| Our network | What it represents | Paper / source behind it | What we take from it | Used in | Status | Verified |
| --- | --- | --- | --- | --- | --- | --- |
| **Trees**: `tree-d2-f2` (4 hosts), `tree-d3-f2` (8), `tree-d2-f4` (16) | The classic tree-shaped (3-tier) data-centre and campus network | Benson et al. 2010 [1] show the "canonical 3-tier data center" (Fig. 1) and find the enterprise data centres follow it; Al-Fares et al. 2008 [2] describe it as the traditional design. Built with Mininet's `TreeTopo`. | The tree shape: one path between any two hosts | Review I (latency, rule count, churn) | Used | PDF [1] |
| **Fat-tree, k = 4** (`fattree-k4`): 4 core, 8 aggregation, 8 edge switches, 16 hosts | A modern data-centre network with many equal paths | Al-Fares et al. 2008 [2], "A Scalable, Commodity Data Center Network Architecture" | The exact construction. With k pods, each pod has k/2 edge and k/2 aggregation switches; there are (k/2)² core switches and k³/4 hosts. That gives up to 4 equal paths between pods. | Step 1 (path quality) | Used | Standard design (paper not in our folder yet) |
| **Abilene** (`abilene`): 11 cities, 14 links, 1 host per city | A real ISP / research backbone (Internet2, USA) | The Internet Topology Zoo, Knight et al. 2011 [3], file `Abilene.gml` | The cities and which cities are linked | Step 1 | Used | Online (paper). The 11 / 14 counts should be checked against `Abilene.gml` |
| **GÉANT** (`--gml Geant2012.gml`) | The European research backbone, bigger (about 40 cities) | Internet Topology Zoo [3] | Cities and links, loaded by our GML reader | Step 1 (optional) | Option | To check (node count) |

### Parameters of the networks

| Parameter | Our value | Where it comes from | Status | Verified |
| --- | --- | --- | --- | --- |
| Abilene link delay | Straight-line distance between the cities ÷ 200 km per ms | Physics: light in optical fibre travels at about 2/3 of its speed in vacuum, about 200,000 km/s. City coordinates as in the Topology Zoo [3]. Real cables are longer, so our delays are a **lower bound**. | Used | Standard physics |
| Link bandwidth | 10 Mbit/s on every link | A scaled-down speed so that a laptop can emulate it faithfully. Handigol et al. 2012 [4] show that Mininet reproduces published results when link rates are scaled to what the machine can handle. Same speed everywhere, so only path choice matters. | Used | To check (exact wording in [4]) |
| Rule timeouts (reactive) | idle 10 s, hard 30 s, exact match | The defaults of POX's own `forwarding.l2_learning` module, which our reactive controller copies | Used | POX source code |
| Link bandwidth in Step 2 | 100 Mbit/s on every link | Benson [1] found link utilisation low everywhere except the core. At 100 Mbit/s our university traffic loads the hosts' links by about 5%, close to that; at 10 Mbit/s it would overload them. | Used | PDF [1] |
| Largest flow (Step 2) | Flows above 20 MB are cut to 20 MB | Not from a paper: it keeps one run to minutes on a laptop. It affects 0% of university flows, about 1% of web search flows and about 4% of data mining flows; all the small flows the controller has to set up are unchanged. | Used | Our choice |
| Flow arrivals (web search, data mining) | Poisson, random source and destination, rate set by the target load (30%) | pFabric [8] Sec. 5: "flows arrive according to a Poisson process and the source and destination for each flow is chosen uniformly at random" | Used | Online |

---

## 2. Realistic traffic

| Traffic pattern | What it represents | Paper / source behind it | Key numbers we take from it | Used in | Status | Verified |
| --- | --- | --- | --- | --- | --- | --- |
| **Ping pairs** (ICMP, 6–10 pings per pair) | Measures delay only; not a traffic model | Standard measurement method | — | Review I, Step 1 | Used | — |
| **Single-packet UDP flows at a fixed rate** (10–200 new flows/s) | A stress test for the controller ("flow churn") | Same idea as the controller benchmarks in Tootoonchian et al. 2012 [5] (cbench-style: many new flows per second) | — | Review I (churn) | Used | PDF [5] |
| **Permutation traffic** (every host sends one long TCP flow to another host, all at once) | The standard data-centre stress test | Al-Fares et al. 2008 [2] and Hedera, Al-Fares et al. 2010 [6] (which calls it "random bijective") | Each host sends to exactly one host and receives from exactly one | Step 1 (throughput, link balance) | Used | To check (pattern name in [6]) |
| **University / enterprise data-centre traffic** | Many small, short flows, arriving in ON/OFF bursts | **Benson et al. 2010 [1]**, "Network Traffic Characteristics of Data Centers in the Wild". They measured 10 data centres: 3 university, 2 private enterprise and 5 cloud. | See the Benson list below. Flow sizes read off Fig. 4(a) (curves EDU1/EDU3); arrivals per edge switch from a Weibull fitted to Benson's "80% of gaps 4–40 ms" (Weibull, as in Table 4) | Step 2 | Used | **PDF** |
| **Data-centre "web search" traffic** | Production search cluster: mostly small queries plus large background flows | **DCTCP, Alizadeh et al. 2010 [7]** (about 6,000 servers, more than 150 TB of traces over a month). The flow-size distribution was published as the "web search" workload in **pFabric, Alizadeh et al. 2013 [8]**. | See the DCTCP / pFabric list below. Exact table `CDF_dctcp.tcl` from the PIAS simulator [15] | Step 2 | Used | Online + table file |
| **Data-centre "data mining" traffic** | Big-data cluster: very skewed, a few giant flows | **VL2, Greenberg et al. 2009 [9]**. The distribution was published as the "data mining" workload in **pFabric [8]**. | See the VL2 / pFabric list below. Exact table `CDF_vl2.tcl` from the PIAS simulator [15] | Step 2 | Used | Online + table file |
| **ISP traffic between cities** (traffic matrix) | How much traffic each city sends to every other city, every 5 minutes | **Abilene traffic matrices**, Zhang et al. 2005 [10] (real NetFlow data, 2004). They are also in SNDlib [11]. | Real city-to-city traffic volumes on the same Abilene map we use | Step 2 | Planned | Online. The weeks covered and the node list are still to check. That dataset has 12 nodes (Atlanta appears to have two routers), so we may need to merge them. |
| **GÉANT traffic matrices** | The same for the European backbone | Uhlig et al. 2006 [12]: one matrix every 15 minutes over several months | City-to-city volumes for GÉANT | Step 2 (if we use GÉANT) | Option | Online |
| **ISP backbone packet traces** | Real packets on a backbone link (Japan, WIDE) | **MAWI archive**, Cho et al. 2000 [13]. Daily traces from "samplepoint-F", a 1 Gbit/s transit link in Tokyo; IP addresses are anonymised. | Flow sizes and the mix of protocols on a real backbone, if we need them | Step 2 | Option | Online |

### Key numbers, written out

**Benson et al. 2010 [1]**, verified in the PDF:
- **Flow size:** 80% of flows are smaller than 10 KB, and most of the bytes are in the top 10% of flows (Sec. 5, Fig. 4a).
- **Flow length:** in most of the data centres, 80% of flows last less than 11 seconds (Fig. 4b).
- **University data centres:** 80% of the gaps between new flows are **4 to 40 ms**. In the busy enterprise data centre (PRV2), 80% of gaps are **under 1 ms** (Fig. 3b).
- **Bursts:** traffic leaving a rack is **ON/OFF**. The OFF periods fit a **lognormal** distribution; ON periods and arrival gaps fit lognormal or Weibull (Tables 4–5).
- **Where traffic goes:** in university and enterprise data centres, 40–90% of the traffic leaves the rack. In cloud data centres, about 80% stays inside the rack (Sec. 1, key findings).
- **Why it matters for our project:** Benson et al. point out that the gap between new flows decides whether a central controller can handle every new flow.

**DCTCP [7]**, verified online:
- **Three kinds of flows:** query traffic of 2–20 KB, short messages of 100 KB–1 MB, and long background flows of 1–100 MB.
- **Protocol:** 99.91% of the traffic is TCP.

**pFabric [8]**, verified online through papers quoting it; to check in pFabric's own text:
- **Web search workload:** more than 95% of the bytes are in the 30% of flows larger than 1 MB.
- **Data mining workload:** about 80% of flows are under 10 KB, while 95% of the bytes are in the roughly 3.6% of flows larger than 35 MB.

**VL2 [9]**, verified online:
- **Size limit:** 99% of flows are smaller than 100 MB.
- **Where the bytes are:** more than 90% of bytes are in flows between 100 MB and 1 GB. The bump near 100 MB comes from the file system cutting files into 100 MB chunks.
- **Small flows:** most of them are hellos and meta-data requests.

---

## 3. Tools

| Tool | What for | Source | Status |
| --- | --- | --- | --- |
| Mininet 2.3.0 + Open vSwitch | Emulating the network on one laptop | Handigol et al. 2012 [4]; mininet.org | Used |
| POX 0.7.0 (`gar`) | Controller platform | github.com/noxrepo/pox | Used |
| `netem` (Linux) | Adding link delay | Part of the Linux kernel | Used (laptop) |
| Our own Python TCP sender/receiver | Throughput flows (Step 1) | Built into `run_path_experiments.py` | Used |
| D-ITG | A traffic generator that can follow statistical distributions | Botta et al. 2012 [14] | Option for Step 2 |
| iperf3 | Simple TCP/UDP flows | iperf.fr | Option |

---

## 4. Still to check (open items)

- [ ] Abilene in Topology Zoo: confirm 11 nodes and 14 links in `Abilene.gml`.
- [ ] Abilene traffic matrices [10]: the exact weeks covered, the 12-node list, and the download location.
- [x] pFabric [8] CDF points: the exact tables are `CDF_dctcp.tcl` (web search) and `CDF_vl2.tcl` (data mining) from the PIAS simulator [15], in 1460-byte packets. Their means are 1.67 MB and 7.47 MB.
- [ ] pFabric [8]: confirm the two workload descriptions in its own evaluation section.
- [ ] Hedera [6]: confirm the name "random bijective" for permutation traffic.
- [ ] Handigol et al. 2012 [4]: confirm the wording about scaling link rates.
- [ ] GÉANT in Topology Zoo: number of nodes and links in `Geant2012.gml`.
- [ ] Download the PDFs of [2], [4], [6], [7], [8], [9] and [10] (all free from the authors' pages) and verify against them.

---

## 5. References

1. T. Benson, A. Akella, D. A. Maltz. *Network Traffic Characteristics of Data Centers in the Wild.* ACM IMC 2010. (In our literature folder.)
2. M. Al-Fares, A. Loukissas, A. Vahdat. *A Scalable, Commodity Data Center Network Architecture.* ACM SIGCOMM 2008.
3. S. Knight, H. X. Nguyen, N. Falkner, R. Bowden, M. Roughan. *The Internet Topology Zoo.* IEEE Journal on Selected Areas in Communications 29(9), Oct 2011. Data: <http://www.topology-zoo.org/>
4. N. Handigol, B. Heller, V. Jeyakumar, B. Lantz, N. McKeown. *Reproducible Network Experiments Using Container-Based Emulation.* ACM CoNEXT 2012.
5. A. Tootoonchian, S. Gorbunov, Y. Ganjali, M. Casado, R. Sherwood. *On Controller Performance in Software-Defined Networks.* USENIX Hot-ICE 2012. (In our literature folder.)
6. M. Al-Fares, S. Radhakrishnan, B. Raghavan, N. Huang, A. Vahdat. *Hedera: Dynamic Flow Scheduling for Data Center Networks.* USENIX NSDI 2010.
7. M. Alizadeh, A. Greenberg, D. A. Maltz, J. Padhye, P. Patel, B. Prabhakar, S. Sengupta, M. Sridharan. *Data Center TCP (DCTCP).* ACM SIGCOMM 2010. <https://people.csail.mit.edu/alizadeh/papers/dctcp-sigcomm10.pdf>
8. M. Alizadeh, S. Yang, M. Sharif, S. Katti, N. McKeown, B. Prabhakar, S. Shenker. *pFabric: Minimal Near-Optimal Datacenter Transport.* ACM SIGCOMM 2013. <https://people.csail.mit.edu/alizadeh/papers/pfabric-sigcomm13.pdf>
9. A. Greenberg, J. R. Hamilton, N. Jain, S. Kandula, C. Kim, P. Lahiri, D. A. Maltz, P. Patel, S. Sengupta. *VL2: A Scalable and Flexible Data Center Network.* ACM SIGCOMM 2009. <https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/vl2-sigcomm09-final.pdf>
10. Y. Zhang, Z. Ge, A. Greenberg, M. Roughan. *Network Anomography.* ACM/USENIX IMC 2005. (Source of the public Abilene traffic matrices.)
11. S. Orlowski, R. Wessäly, M. Pióro, A. Tomaszewski. *SNDlib 1.0: Survivable Network Design Library.* Networks 55(3), 2010. <http://sndlib.zib.de/>
12. S. Uhlig, B. Quoitin, S. Balon, J. Lepropre. *Providing Public Intradomain Traffic Matrices to the Research Community.* ACM SIGCOMM CCR 36(1), Jan 2006. Data: <https://totem.info.ucl.ac.be/dataset.html>
13. K. Cho, K. Mitsuya, A. Kato. *Traffic Data Repository at the WIDE Project.* USENIX ATC 2000, FREENIX Track. Data: <https://mawi.wide.ad.jp/mawi/>
14. A. Botta, A. Dainotti, A. Pescapè. *A Tool for the Generation of Realistic Network Workload for Emerging Networking Scenarios.* Computer Networks 56(15), 2012.
15. W. Bai, L. Chen, K. Chen, D. Han, C. Tian, H. Wang. *Information-Agnostic Flow Scheduling for Commodity Data Centers (PIAS).* USENIX NSDI 2015. Simulator and workload files: <https://github.com/HKUST-SING/PIAS-NS2> (`scripts/CDF_dctcp.tcl`, `scripts/CDF_vl2.tcl`)

---

## Change log

| Date | Change |
| --- | --- |
| 15 Oct 2026 | Created. Networks and traffic for Review I and Step 1 (used); data-centre, university and ISP traffic sources for Step 2 (planned). |
| 15 Oct 2026 | Step 2: university, web search and data mining traffic now used. Added the PIAS table files [15], the 100 Mbit/s and 20 MB-cap choices, and the Poisson arrivals. |
