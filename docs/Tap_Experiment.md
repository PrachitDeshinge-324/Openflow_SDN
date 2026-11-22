# Forward first, tell the controller: the tap controller (T13)

CS G525 Advanced Computer Networks - Project SA7, Group 2.
Batches of 19 Nov 2026 (laptop, WSL2, Open vSwitch 3.7.1 kernel datapath, Best performance mode).

## 0. In one paragraph

Every controller we measured before makes a trade: either the first packet of a flow waits for the controller (reactive), or the controller does not learn which flows exist (proactive, wildcard rules). The tap controller installs forwarding rules in advance and adds three rules per host that **forward** a connection's SYN, FIN and RST packets **and copy** them to the controller. On four networks (18 runs) it is as fast as proactive on three and slower on the k=4 fat-tree, where the cause is not yet confirmed. The controller heard of **46,641 of 46,641** connections. Tap needs **128 rules where proactive needs 624** (2,592 against 13,230 at 54 hosts). When the controller is frozen for 5 seconds, new connections under exact-match reactive wait about 5 seconds; under tap nothing changes, and the controller still hears of every connection once it resumes.

## 1. Why this test

- **Reactive:** the controller hears of every new flow, because the flow's first packet waits for it.
- **Proactive and wildcard rules:** nothing waits, but the controller hears of few flows or none.

A PACKET_IN does two jobs at once: it **asks** the controller what to do, and it **tells** the controller that a flow exists. Only the asking is slow. This test checks whether a switch can keep the telling without the asking.

## 2. Design (`controllers/tap_eval.py`)

| Part | Rules | What it does |
| --- | --- | --- |
| Forwarding | one rule per host on every switch, installed when the switch connects | the switch forwards every packet itself; on the fat-tree each switch picks one of its equal-cost next hops by a hash of the destination |
| Tap | three rules per host, at the switch the host is attached to | TCP packets to that host with SYN (not ACK), FIN or RST set are **forwarded and copied** to the controller (first 128 bytes) |

- No rule is installed per flow. A new connection is forwarded at once; the controller receives one copy when it starts and one or two when it ends.
- TCP-flag matching is not in OpenFlow 1.0. It is the Open vSwitch field `NXM_NX_TCP_FLAGS` (Open vSwitch 2.1 and later), sent as a Nicira flow-mod from POX. The connection stays OpenFlow 1.0.
- The controller can still act on what it hears: `--block_rate=N` drops a source that opens more than N connections in one second (a decision taken after the first packets have passed).

Checks: `experiments/test_tap_offline.py` (every rule packs; forwarding reaches every host from every switch with no loop on all four networks; flow start and end counted correctly). `experiments/tap_check.py` matches the schedule with the controller's flow log, flow by flow.

## 3. Setup

Same harness, traffic and seeds as the granularity test (`docs/Granularity_Baseline_Experiment.md`). 30 s of arrivals, 100 Mbit/s links, Zipf 1 pair popularity, web search at 30% load on the k=4 fat-tree and 5% on k=6. All controllers run for every seed in one batch.

```bash
sudo python3 experiments/run_traffic_experiments.py --scenarios <network:workload> --pair-zipf 1 --repeats 5 \
    --modes reactive-sp reactive-pair reactive-dst proactive tap      # proactive-ecmp on the fat-trees
python3 experiments/tap_summary.py <result folders>                    # the tables below
```

| Scenario | Runs | Folder |
| --- | --- | --- |
| University tree (16 hosts) | 5 (seeds 7-11) | `results/measured/traffic-20261119-114525/` |
| Fat-tree k=4, web search (16 hosts) | 5 | `results/measured/traffic-20261119-120616/` |
| Abilene ISP (11 hosts) | 5 | `results/measured/traffic-20261119-123520/` |
| Fat-tree k=6, web search (54 hosts) | 3 (seeds 7-9) | `results/measured/traffic-20261119-125611/` |
| Controller frozen 5 s, university tree | 3 (seeds 7-9) | `results/measured/traffic-20261119-175235/` |

The three quick runs before the batch (`traffic-20261119-112325/`, `-113446/`, `-114426/`) found and fixed a counting bug: the controller's baseline was read half a second into the run, so 94-95% of connections were reported as heard of when the flow log showed 100%. They are not used below.

## 4. Results

Small-flow FCT = flows under 100 KB, median (and mean) in ms, mean of the runs with the 95% interval. "Heard of" = share of new TCP connections the controller learned about: tap from its SYN copies; reactive on shortest paths 100% (every connection asks); pair / destination rules 100 minus the hit rate (they only ask on a miss); proactive 0%. All from `tap_summary.py`.

### University tree

| Controller | Small-flow median (ms) | Mean (ms) | PACKET_IN/s | CPU % | Peak rules (busiest switch) | Heard of |
| --- | --- | --- | --- | --- | --- | --- |
| Reactive on shortest paths, exact rules | 35.7 ± 5.7 | 37.8 ± 6.5 | 2,486 | 74.8 | 11,392 (3,654) | 100% |
| Reactive, pair rules | 1.0 ± 0.5 | 5.3 ± 1.3 | 31 | 1.3 | 624 (192) | 2.1% |
| Reactive, destination rules | 0.9 ± 0.4 | 5.2 ± 1.3 | 3 | 0.2 | 80 (16) | 0.4% |
| Proactive | 0.9 ± 0.4 | 5.2 ± 1.3 | 0 | 0.1 | 624 (192) | 0% |
| **Tap** | **1.0 ± 0.4** | **5.2 ± 1.3** | 602 | 14.3 | **128 (28)** | **100%** |

### Abilene ISP (real traffic matrices)

| Controller | Small-flow median (ms) | Mean (ms) | PACKET_IN/s | CPU % | Peak rules (busiest switch) | Heard of |
| --- | --- | --- | --- | --- | --- | --- |
| Reactive on shortest paths, exact rules | 57.8 ± 2.2 | 72.5 ± 3.8 | 452 | 23.9 | 5,430 (855) | 100% |
| Reactive, pair rules | 46.2 ± 1.5 | 58.9 ± 3.5 | 15 | 1.0 | 386 (62) | 3.5% |
| Reactive, destination rules | 46.1 ± 1.6 | 58.8 ± 3.5 | 5 | 0.4 | 121 (11) | 2.2% |
| Proactive | 46.0 ± 1.5 | 58.7 ± 3.5 | 0 | 0.1 | 386 (62) | 0% |
| **Tap** | **46.1 ± 1.5** | **58.8 ± 3.4** | 174 | 5.0 | **154 (14)** | **100%** |

### Fat-tree k=6, web search (54 hosts, 3 runs)

| Controller | Small-flow median (ms) | Mean (ms) | PACKET_IN/s | CPU % | Peak rules (busiest switch) | Heard of |
| --- | --- | --- | --- | --- | --- | --- |
| Reactive on shortest paths, exact rules | 51.9 ± 8.4 | 58.8 ± 13.3 | 362 | 21.0 | 2,341 (160) | 100% |
| Reactive, pair rules | 23.3 ± 8.7 | 26.9 ± 9.6 | 212 | 10.4 | 1,352 (54) | 49.2% |
| Reactive, destination rules | 12.7 ± 4.0 | 19.8 ± 4.9 | 154 | 6.5 | 804 (26) | 40.7% |
| Proactive (ECMP) | 5.0 ± 0.7 | 13.0 ± 3.4 | 0 | 0.4 | 13,230 (312) | 0% |
| **Tap** | **5.3 ± 1.1** | **14.2 ± 4.7** | **63** | 2.8 | **2,592 (63)** | **100%** |

### Fat-tree k=4, web search (16 hosts)

| Controller | Small-flow median (ms) | Mean (ms) | PACKET_IN/s | CPU % | Peak rules (busiest switch) | Heard of |
| --- | --- | --- | --- | --- | --- | --- |
| Reactive on shortest paths, exact rules | 74.2 ± 8.1 | 90.7 ± 12.5 | 494 | 33.1 | 4,028 (424) | 100% |
| Reactive, pair rules | 32.8 ± 5.1 | 55.7 ± 10.9 | 111 | 5.0 | 858 (54) | 13.9% |
| Reactive, destination rules | 31.7 ± 4.6 | 56.0 ± 8.6 | 60 | 2.1 | 285 (16) | 6.4% |
| Proactive (ECMP) | 29.6 ± 5.5 | 53.5 ± 8.9 | 0 | 0.2 | 1,072 (58) | 0% |
| Tap | 39.3 ± 21.9 | 62.2 ± 32.3 | 109 | 4.3 | 368 (22) | 100% |

**This is the one network where tap is slower.** One run (seed 8) had 3 failed flows and a 108 ms small-flow mean; without it tap's mean is 50.7 ± 8.3 ms against proactive's 53.1 ± 13.1 ms. Large flows (over 10 MB) were slower under tap than under proactive in 4 of 5 runs. Likely cause: tap chooses paths per destination, so all flows to one host share a path through the core, while proactive ECMP chooses per host pair and spreads them. Not confirmed; a pair-hash version of tap would test it.

Failed flows: 0 in every run of every controller, except tap seed 8 on the k=4 fat-tree (3 of 1,111).

### Controller frozen for 5 seconds (`--pause-controller 10:5`, university tree, 3 runs)

POX is stopped with SIGSTOP 10 s into the traffic and resumed 5 s later, as in a crash with restart or a long pause. About 1,000 connections start inside the freeze in each run.

| Controller | Connections started in the freeze | Took over 1 s | Small-flow median in the freeze (ms) | Outside the freeze (ms) | Slowest (ms) | Heard of |
| --- | --- | --- | --- | --- | --- | --- |
| Reactive on shortest paths, exact rules | 3,030 | **3,029** | **5,016 / 5,995 / 5,122** | 47.6 / 115.7 / 60.6 | 9,890 | 100% |
| Reactive, destination rules | 3,030 | 4 | 1.3 / 1.6 / 1.2 | 1.6 / 1.5 / 1.3 | 2,054 | under 1% |
| Proactive | 3,030 | 4 | 1.4 / 1.7 / 1.2 | 1.6 / 1.6 / 1.3 | 1,902 | 0% |
| **Tap** | 3,030 | 4 | **1.4 / 2.0 / 1.3** | 1.5 / 1.6 / 1.3 | 1,827 | **100% (18,269 of 18,269)** |

Per-run values are for seeds 7 / 8 / 9. 0 failed flows in all 12 runs. The 4 slow connections are in seed 7 under all three non-waiting controllers, so they are not caused by the controller.

What it shows: a frozen controller stops every new connection under reactive (5 to 10 s, the TCP SYN retransmission times). Tap, like proactive and destination rules, does not notice. Of these, only tap still learns of every connection: the copies queue up while the controller is frozen and are read when it resumes.

Live version: `sudo python3 demo/freeze_demo.py`. One run on 19 Nov: reactive 20.4 ms with the controller running, 5,022.6 ms frozen; tap 7.6 ms and 8.3 ms, and the controller reported both connections started and ended.

## 5. What it shows

1. **The trade-off is not necessary.** On the university tree, Abilene and the 54-host fat-tree, tap's small-flow median is close to proactive's (1.0 vs 0.9, 46.1 vs 46.0, 5.3 vs 5.0 ms). Paired per seed (`experiments/paired_stats.py --paper`) the differences are +0.07 [-0.02, +0.15], +0.11 [-0.03, +0.24] and +0.33 [-0.18, +0.85] ms: not resolved, but tap was the slower one in 11 of 13 seeds, so read it as a cost of at most a fraction of a millisecond, not as equal speed. The controller heard of every connection in all 21 tap runs. No other controller we measured has both.
2. **Its rule cost is 3 rules per host on top of the cheapest proactive.** Against our proactive controller (one rule per host pair) tap needs fewer rules: 128 against 624 on the university tree, 154 against 386 on Abilene, 2,592 against 13,230 at 54 hosts. But that difference is rule granularity, not tapping: a proactive controller with one rule per destination needs exactly tap's forwarding rules (80, 121, 2,430), so tap costs 48, 33 and 162 rules more than it. The fair speed baseline is `proactive-dst` (tap with `--taps=off`). Second batch (21 Nov, `traffic-20261121-073853/-075657/-082609/-084548`, same laptop and seeds): tap minus proactive-dst is 48, 48, 33 and 162 rules (3 per host), and in small-flow median +0.08 [+0.05, +0.11] ms (tree), +0.79 [-0.69, +2.28] (k=4), -0.01 [-0.09, +0.07] (Abilene), +0.29 [+0.06, +0.51] (k=6). The copies cost a little time where it is resolved; the k=4 slowdown is not theirs: in seed 8 tap and proactive-dst fail the same 7 flows with the same 72.7-72.8 ms median, proactive ECMP 23.9 ms.
3. **At 54 hosts it beats every reactive variant.** Wildcard rules are rarely reused there (hit rate 51 to 59%), so destination and pair rules have 2.4 and 4.4 times tap's small-flow median, send 2.4 and 3.4 times more PACKET_INs, and hear of fewer than half the connections.
4. **It survives a frozen controller** like proactive does, and unlike reactive (5 s against 1.4 ms median), without losing track of a single connection.
5. **The cost is reading, not waiting.** About 3 copies per connection: 602 PACKET_IN/s and 14% CPU at about 200 new connections per second. No packet waits for the controller, but the copy rules add a little time: +0.08 ms (tree) and +0.29 ms (54 hosts) of small-flow median against proactive-dst, nothing measurable on Abilene. Destination rules are cheaper on small networks because they hear of almost nothing.

## 6. What it does not show

- **TCP only.** UDP has no SYN; a UDP flow would need a per-flow rule.
- **No per-flow byte counts.** The controller knows start, end and duration of each connection.
- **No decision before the first packet.** An access list must be a pre-installed rule; a decision from behaviour (the rate block) takes effect after the first packets.
- **The k=4 fat-tree:** slower small flows in one run and slower large flows in four; cause not confirmed.
- **An Open vSwitch extension**, not OpenFlow 1.0. OpenFlow 1.5 has TCP flags as a standard match field.
- **One machine, emulated network, POX**, as for every test in this project. The freeze test freezes only the controller process; a real controller failure can also drop the TCP session to the switch.

## 7. Prior work

| Paper | What it does | Difference |
| --- | --- | --- |
| Everflow (Zhu et al., SIGCOMM 2015) | Match-and-mirror on commodity switches to trace packets in a large data centre; as we recall, it traces TCP flows by their SYN, FIN and RST packets, mirrored to analysis servers | **The flag-matching copy is Everflow's idea.** There it feeds monitoring servers, outside the control loop; here it feeds the SDN controller and replaces reactive setup. Verify the details in the paper before quoting it |
| PARD (Rzepka et al., JNSM 2020) | Coarse proactive rules forward packets before the controller decides; the controller installs a detailed rule per flow in the background | Same principle. Tap installs no rule per flow, reports flow ends too, and is measured here against reactive, proactive and wildcard controllers. We have read only PARD's abstract; check the full text before claiming any difference beyond that |
| DevoFlow (SIGCOMM 2011) | Wildcard rules by default; the controller hears only of significant flows | Gives up per-flow visibility on purpose |
| Wang, Butnariu, Rexford (Hot-ICE 2011) | Notes that OpenFlow 1.0 cannot match TCP flags; the controller checks the SYN reactively | That is the reactive wait tap removes |
| NetFlow / IPFIX | Flow records exported by the switch | After the flow or sampled, outside the control loop |

**How to say it:** "Both parts exist: forwarding first is PARD's idea, copying SYN, FIN and RST is Everflow's. We combine them so the SDN controller keeps per-connection visibility with no per-flow rules and no waiting, and we measure that against every other strategy on one testbed." Not "a novel architecture".

## 8. For the presentation (about 3 minutes)

**Slide title:** Forward first, tell the controller.

**Slide body:** the 54-host table of Section 4 (or the university one), with the tap row highlighted, and one line: "A PACKET_IN asks and tells. Only asking is slow. Tap keeps the telling."

**Live:** `sudo python3 demo/freeze_demo.py` (about 1 minute). Say: "We freeze the controller. Reactive: the new connection waits 5 seconds. Tap: 8 milliseconds, and the controller still saw it."

**Three numbers to remember:** 46,641 of 46,641 connections heard of; 128 rules against 624; 5,000 ms against 1.4 ms with the controller frozen.

## 9. Next

0. ~~Run `proactive-dst`~~ done 21 Nov (see Section 4): the k=4 gap is destination-hashed paths, one seed.
1. Tap with pair-hash ECMP paths, to remove the k=4 gap itself.
2. Read PARD in full and fix the wording of Section 7.
3. Freeze test on the 54-host fat-tree, where wildcard rules miss half the time.
