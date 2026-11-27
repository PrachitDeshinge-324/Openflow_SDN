# The 11 pre-installation papers: what each does, and what it means for our claim

CS G525 Advanced Computer Networks, Project SA7. Written 27 Nov 2026.

These are the 11 papers counted in the paper's related work ("Our survey covers 11 papers that pre-install
rules using a predictor") and in table A' of `ML_Rule_Prediction_Survey.md`. The A-numbers are the same in both.
Each section answers the same questions:

- **What it does**, in two or three lines.
- **Setup:** how and where it was evaluated.
- **Compared against:** its baselines.
- **Result:** its headline numbers, as reported.
- **Rule granularity:** do the pre-installed rules match more traffic than the baseline's rules? (Our main claim is
  that a gain measured against exact-match reactive mixes *when* a rule is installed with *how coarse* it is.)
- **Upper bound:** does it report a best-possible reference?
- **For us:** what it means for our paper.

**Source of each summary.** Seven were read in full (A1, A2, A4, A5, A7, A8, A11). Four are known only from their
abstract or publisher page (A3, A6, A9, A10). For those, "not stated" means the abstract does not say it, not that
the paper lacks it. Numbers are quoted as the papers report them; we did not reproduce them.

## At a glance

| # | Paper | Read | Compared against | Pre-installed rules coarser than the baseline's? | Upper bound? |
| --- | --- | --- | --- | --- | --- |
| A1 | Batista et al. 2024, LSTM scheduler for IoT | full | reactive mode (POX, Ryu) | no coarse-rule baseline reported | no |
| A2 | Bull, Austin, Sharma 2015, PFIM | full | POX L3 learning switch | no: same rule, re-installed in time | no |
| A4 | Sanabria-Russo et al. 2018, CTTC | full | conventional reactive (Ryu) | no: same rule, re-installed in time | no |
| A5 | Kim, Park, Kyung 2022, hybrid flow-rule cache | full | basic reactive cache; MobiFlow | no coarse-rule baseline reported | no |
| A7 | Huang et al. 2024, MAPQ | full | hard-timeout scheme; Mobi-Flow | not stated (rule contents random) | no |
| A8 | Sowmya et al. 2026, LSTM for vehicles | full | reactive; FIFO; LRU | **yes**: per traffic class vs per MAC pair | no |
| A11 | Ståhl et al. 2025, predictable traffic in OVS | full | no prediction | no: same cache mechanism | **yes**: perfect prediction |
| A3 | Cai et al. 2021, DAPFIM | abstract | earlier PFIM variants | not stated | not stated |
| A6 | Bera, Misra, Obaidat 2019, Mobi-Flow | abstract | OSPF, MRC, distributed, MoRule | not stated | not stated |
| A9 | Nokia Bell Labs 2019, DRL for latency | abstract | not stated | not stated | not stated |
| A10 | Rzepka et al. 2020, PARD | abstract | not stated | not stated | not stated |

---

## Read in full (7)

### A1. Batista et al., *A new intelligent scheduler to improve reactive OpenFlow communication in SDN-based IoT data streams*, Discover Internet of Things 4:15, 2024
- **What it does:** an LSTM predicts when an IoT device will send next, and the controller installs the rule before
  the request arrives. A Page-Hinkley test detects when the traffic pattern changes (concept drift).
- **Setup:** Mininet, OpenFlow 1.0, POX and Ryu controllers: the same tools as ours. Periodic IoT sensor streams.
- **Compared against:** reactive mode.
- **Result:** "installing OpenFlow rules in advance reduced about 51% of communications response time" [p.3].
- **Rule granularity:** no coarse-rule reactive baseline is reported.
- **Upper bound:** none.
- **For us:** the closest published system to our setup, and the example in the paper's related work. Its gain is
  measured against plain reactive only.

### A2. P. Bull, R. Austin, M. Sharma, *Pre-emptive flow installation for Internet of Things devices within software defined networks*, IEEE FiCloud 2015
- **What it does:** PFIM, the Pre-emptive Flow Installation Mechanism. The controller watches when a flow's packets
  arrive. Once it has seen a regular interval (5 occurrences in the experiment), it re-installs the flow's rule
  500 ms before the next packet is due. It stops after 15 pre-emptive installs and starts observing again.
- **Setup:** first a Python simulation of idle-timeout values on continuous, bursty and periodic traffic (100 flows,
  120 s; a 1 s idle timeout gave the best memory use). Then a proof of concept: POX L3 learning switch, Mininet,
  2 hosts, 1 switch, one ping flow every 5 s, idle timeout 1 s (Section VI).
- **Compared against:** the standard POX L3 learning controller.
- **Result:** RTT drops "from around 10ms to less than 1ms" once pre-emptive installation starts.
- **Rule granularity:** the pre-installed rule is **the same rule** the learning switch installs. So coarseness plays
  no part. The gain comes from timing: a 1 s idle timeout is shorter than the 5 s ping period, so the reactive
  rule expires between packets.
- **Upper bound:** none.
- **For us:** a different gap from ours. The missing baseline is **reactive with an idle timeout longer than the
  traffic period**, which would also avoid the misses.

### A4. L. Sanabria-Russo, J. Alonso-Zarate, C. Verikoukis, *SDN-based pro-active flow installation mechanism for delay reduction in IoT*, IEEE GLOBECOM 2018
- **What it does:** extends PFIM (A2) so the controller also *forgets* a flow's period when it breaks: if a PACKET_IN
  arrives for a flow already scheduled, or if a pre-installed rule expires unused.
- **Setup:** a real testbed: Raspberry Pi 3 gateways running Open vSwitch 2.7.0, Ryu 4.4 (OpenFlow 1.4) on a PC, two
  Zolertia Z1 sensor motes, clocks synchronised with PTP. Periodic (5 s) and periodic/bursty traffic; the idle
  timeout is set below the duty cycle (1 s).
- **Compared against:** the conventional reactive flow installation.
- **Result:** reactive: the first packet of each burst takes about 4 ms, the rest 0.12 ms, and each burst costs 3
  OpenFlow messages. With PFIM: the first packet takes about 0.4 ms ("around 90%" less), and only one message
  (FLOW_MOD) per burst.
- **Rule granularity:** **the same rule** as reactive, re-installed in time. Again the gain is timing, against a
  timeout deliberately shorter than the traffic period.
- **Upper bound:** none.
- **For us:** the same gap as A2: no baseline with a longer timeout. Also a careful real-hardware testbed, which our
  emulation is not.

### A5. Y. Kim, J. Park, Y. Kyung, *Mobility-aware hybrid flow rule cache scheme in software-defined access networks*, Electronics 11(1):160, 2022
- **What it does:** an LSTM predicts the controller's next response delay. For each flow, if the controller will be
  too slow for the flow's delay requirement, its rule is installed proactively; otherwise reactively. An ILP, solved
  heuristically, decides how many proactive rules fit in the cache.
- **Setup:** simulation on the Abilene topology, 10 mobile users, controller capacity 5,000 messages/s, delay
  constraint 30 ms [p.8–9].
- **Compared against:** a basic reactive cache, and MobiFlow (a predictor).
- **Result:** better flow-table use, install delay and hit ratio than the other schemes, shown as graphs only.
- **Rule granularity:** no coarse-rule reactive baseline is reported.
- **Upper bound:** none.
- **For us:** cited in the paper's related work as comparing against reactive and other published schemes.

### A7. G. Huang, I. Ullah, H. Huang, K. T. Kim, *Predictive mobility and cost-aware flow placement in SDN-based IoT networks: a Q-learning approach*, Journal of Cloud Computing 13:26, 2024
- **What it does:** MAPQ. Q-learning predicts where a mobile device will move next; a cost-sensitive AdaBoost
  classifier keeps only "heavy and active" flows (mice and inactive flows are excluded); the controller places those
  flows' rules in advance at the predicted switches.
- **Setup:** simulation with NS3 and Matlab; the text describes a tree of 25 switches and 200 hosts (its parameter
  table lists 3 switches and 100–200 entries per table); flows arrive with an exponential distribution and "the
  contents of the flow entries are decided randomly".
- **Compared against:** "the standard hard time-out scheme" (the "table miss" column) and Mobi-Flow (A6).
- **Result (Table 7):** average delay 3.29 ms (MAPQ) vs 4.21 ms (Mobi-Flow) vs 7.35 ms (table miss); packet-drop
  rate 0.389 vs 0.602 vs 0.764. Prediction accuracy higher than Mobi-Flow in every tested setting.
- **Rule granularity:** not stated: the rule contents are random.
- **Upper bound:** none.
- **For us:** a simulation-only evaluation against a hard-timeout scheme and one earlier predictor.

### A8. P. Sowmya, P. Dinesha, A. Saravana Kumar, J. Akilandeswari, *LSTM-based QoS-aware proactive flow-rule placement in software-defined Internet of Vehicles*, ETASR 16(3), 2026
- **What it does:** an LSTM forecasts the next access point each vehicle will connect to, from movement trends
  (PeMS traffic data). The controller pre-installs QoS rules at the predicted access point. Traffic is classified by
  DSCP: time-critical (46) and drop-critical (34) go to priority queues.
- **Setup:** Mininet and Ryu, 10 access points, 10 vehicles at 0–30 mph.
- **Compared against:** a reactive controller, and FIFO and LRU schemes.
- **Result:** proactive RTT averages 0.15 ms (time-critical) and 0.267 ms (drop-critical), against 2.04 ms on
  average for reactive (0.052–6.627 ms). RTT 32% lower than FIFO and 36% lower than LRU.
- **Rule granularity:** **yes, this is exactly our confound.** The pre-installed rules match a whole traffic class
  (DSCP value), while the reactive rules match a source and destination MAC pair. No reactive baseline with
  class-level rules is reported.
- **Upper bound:** none.
- **For us:** the clearest example among the seven of a gain that mixes prediction with coarser rules.

### A11. E. Ståhl, M. Chiesa, S. Ferlin, E. Chaudron, *On the benefits of predictable traffic in virtual switches: a case study*, ACM ANRW 2025 (Red Hat, KTH, Karlstad University)
- **What it does:** a benefit study, not a new mechanism. In Open vSwitch, a packet with no cache entry takes the slow
  path (an "upcall" to user space). The paper asks how much latency and CPU would be saved if flows could be
  predicted and preloaded into the cache. It groups related flows into "coflows" and varies how many of them are
  predicted.
- **Setup:** Open vSwitch 3.3 and OVN on Red Hat OpenShift, Xeon servers; traces from Google search RPC and Facebook
  Hadoop (526 coflows, scaled up, UDP); cache of 200,000 entries, timeouts disabled.
- **Compared against:** no prediction (empty caches), and an **"Optimal"** case where every associated flow is
  preloaded, with partial prediction in between.
- **Result:** "a system that could predict 25% of the traffic flows would decrease the average latency by up to
  approximately 24% and reduce CPU utilization by approximately 12%"; the benefit shrinks at high flow rates.
- **Rule granularity:** the same OVS cache mechanism on both sides, so not confounded.
- **Upper bound:** **yes**: the perfect-prediction case is stated as a performance ceiling.
- **For us:** the one paper of the 11 with an upper bound. It corrected our earlier claim that none had one.

---

## Abstract only (4)

### A3. Cai et al., *Dynamic adjustment for proactive flow installation mechanism in SDN-based IoT*, Computer Networks, 2021
- **What it does (abstract):** DAPFIM improves the authors' earlier PSPFIM, which split flows into periodic subflows
  and pre-installed their rules. DAPFIM detects periods down to milliseconds, is less disturbed by noise, and
  corrects for the gap between expected and actual periods.
- **Compared against:** PSPFIM and related work.
- **Result (abstract):** up to 78% less flow-entry duration on average than related work.
- **Not stated in the abstract:** rule granularity, an upper bound, network size. The full text is behind a paywall.

### A6. S. Bera, S. Misra, M. S. Obaidat, *Mobi-Flow: mobility-aware adaptive flow-rule placement in software-defined access network*, IEEE Trans. Mobile Computing 18(8), 2019
- **What it does (abstract):** an order-k Markov predictor estimates users' future locations from their history; an
  integer linear program places flow rules at the predicted access points at minimum cost.
- **Compared against:** OSPF, MRC (minimum occupied rule capacity), a distributed non-SDN approach, and MoRule.
- **Result (abstract):** cost lower by 39%, 38%, 65% and 11% than those four.
- **Not stated in the abstract:** rule granularity, an upper bound. It is itself the baseline in A5 and A7.

### A9. *Deep reinforcement learning application for network latency management in software defined networks*, Nokia Bell Labs, 2019
- **What it does (publication page):** deep reinforcement learning decides where flow rules go; an LSTM estimates
  future traffic demand.
- **Setup:** ONOS controller and Open vSwitch.
- **Result (publication page):** lower network latency and packet loss, higher throughput.
- **Not stated:** the baselines, rule granularity, an upper bound. We could not confirm the author list, so it is not
  given here.

### A10. R. Rzepka, P. Boryło, A. Lasoń, A. Szymański, *PARD: hybrid proactive and reactive method eliminating flow setup latency in SDN*, J. Network and Systems Management 28, 2020
- **What it does (abstract):** coarse "aggregate" entries are installed proactively, and detailed entries are added
  reactively in the background. PARD-ST uses one flow table; PARD-MT spreads entries over several tables and needs
  switches that support them.
- **Result (abstract):** the latency of the first packet of a new flow is significantly reduced, which also improves
  packet loss and throughput; no protocol or hardware changes are needed.
- **Not stated in the abstract:** the baselines, an upper bound.
- **For us:** PARD is the published design closest to "coarse rules first, detail later". It is cited in our related
  work next to the hybrids.

---

## What the 11 say together

- **Baselines:** 3 compare only with plain reactive installation (A1, A2, A4); 4 with reactive and other published
  schemes (A5, A6, A7, A8); 1 with its own earlier variants (A3); 2 name no baseline in the abstract available (A9,
  A10); 1 compares no prediction with perfect prediction (A11).
- **The granularity confound** is clear in A8 (class rules against MAC-pair rules). In A2 and A4 it does not apply:
  the pre-installed rule is the reactive rule itself, and their missing baseline is a longer idle timeout.
- **None of the seven read in full** compares coarser pre-installed rules with a reactive baseline that uses the same
  coarse rules.
- **Upper bound:** only A11 reports one.
- **Traffic:** periodic IoT or mobility in 8 of the 9 that state it; A11 uses data-centre traces.
- **Not counted:** Hariri, Yuksel and Mohaisen, *RL-based speculative installation of unseen flows in SDNs*, IEEE
  ICMLCN 2024, found in another paper's references but not accessible to us.

**Viva line:** "We read 7 of the 11 in full. None compares coarse pre-installed rules with reactive using the same
coarse rules. Two IoT papers have a different gap: their rules expire after one second and they never try a longer
timeout. Only the Red Hat/KTH study reports an upper bound."
