# Forward first, tell the controller: the tap controller (T13)

CS G525 Advanced Computer Networks - Project SA7, Group 2.
Batch of 19 Nov 2026 (laptop, WSL2, Open vSwitch 3.7.1 kernel datapath).

## 1. Why this test

Every controller we measured so far makes the same trade:

- **reactive:** the controller hears of every new flow, because the flow's first packet has to wait for it;
- **proactive and wildcard rules:** nothing waits, but the controller hears of few flows or none.

A PACKET_IN does two jobs at once: it **asks** the controller what to do, and it **tells** the controller that a flow exists. Only the asking is slow. This test checks whether a switch can keep the telling without the asking.

## 2. Design (`controllers/tap_eval.py`)

| Part | Rules | What it does |
| --- | --- | --- |
| Forwarding | one rule per host on every switch, installed when the switch connects | the switch forwards every packet itself; on the fat-tree each switch picks one of its equal-cost next hops by a hash of the destination |
| Tap | three rules per host, at the switch the host is attached to | TCP packets to that host with SYN (not ACK), FIN or RST set are **forwarded and copied** to the controller (first 128 bytes) |

- No rule is installed per flow. Every new connection is forwarded at once; the controller receives one copy when it starts and one or two when it ends.
- TCP-flag matching is not in OpenFlow 1.0. It is the Open vSwitch field `NXM_NX_TCP_FLAGS` (Open vSwitch 2.1 and later), sent as a Nicira flow-mod from POX. The connection stays OpenFlow 1.0.
- The controller can still act on what it hears: `--block_rate=N` drops a source that opens more than N connections in one second (a decision taken after the first packets have passed).

Checks: `experiments/test_tap_offline.py` (every rule packs; forwarding reaches every host from every switch with no loop on all four networks; start and end of flows counted correctly). `experiments/tap_check.py` matches the schedule with the controller's flow log, flow by flow.

## 3. Setup

Same harness, traffic and seeds as the granularity test (`docs/Granularity_Baseline_Experiment.md`), so the rows are comparable. 30 s of arrivals, 100 Mbit/s links, Zipf 1 pair popularity, web search at 30% load on the k=4 fat-tree and 5% on k=6.

```bash
sudo python3 experiments/run_traffic_experiments.py --scenarios <network:workload> --pair-zipf 1 --repeats 5 \
    --modes reactive-sp reactive-pair reactive-dst proactive tap      # proactive-ecmp on the fat-trees
```

| Scenario | Runs | Folder |
| --- | --- | --- |
| University tree (16 hosts) | 5 (seeds 7-11) | `results/measured/traffic-20261119-114525/` |
| Fat-tree k=4, web search (16 hosts) | 5 | `results/measured/traffic-20261119-120616/` |
| Abilene ISP (11 hosts) | 5 | `results/measured/traffic-20261119-123520/` |
| Fat-tree k=6, web search (54 hosts) | 3 (seeds 7-9) | `results/measured/traffic-20261119-125611/` |

The three quick runs before the batch (`traffic-20261119-112325/`, `-113446/`, `-114426/`) found and fixed a counting bug (the controller's baseline was read half a second into the run); they are not used below.

## 4. Results

Small-flow FCT below is the **mean of the per-run means** (flows under 100 KB) with a 95% interval, read from the run log. For medians, run `python3 experiments/tap_summary.py <the four folders>`.

"Heard of" is the share of new TCP connections the controller learned about. For tap it is measured (SYN copies against the schedule). For the wildcard rows it is 100 minus the hit rate of the earlier batch with the same seeds (`Granularity_Baseline_Experiment.md`); `tap_summary.py` prints the values of this batch.

### University tree

| Controller | Small-flow FCT (ms) | PACKET_IN/s | CPU % | Peak rules (busiest switch) | Heard of |
| --- | --- | --- | --- | --- | --- |
| Reactive on shortest paths, exact rules | 37.8 ± 6.5 | 2,486 | 74.8 | 11,392 (3,654) | 100% |
| Reactive, pair rules | 5.4 ± 1.3 | 31 | 1.3 | 624 (192) | 2.1% |
| Reactive, destination rules | 5.2 ± 1.3 | 3 | 0.2 | 80 (16) | 0.4% |
| Proactive | 5.2 ± 1.4 | 0 | 0.1 | 624 (192) | 0% |
| **Tap** | **5.1 ± 1.3** | 602 | 14.4 | **128 (28)** | **100%** |

### Fat-tree k=4, web search

| Controller | Small-flow FCT (ms) | PACKET_IN/s | CPU % | Peak rules (busiest switch) | Heard of |
| --- | --- | --- | --- | --- | --- |
| Reactive on shortest paths, exact rules | 90.6 ± 12.5 | 494 | 33.1 | 4,028 (424) | 100% |
| Reactive, pair rules | 55.7 ± 10.9 | 111 | 5.0 | 858 (54) | 13.9% |
| Reactive, destination rules | 56.0 ± 8.6 | 59 | 2.1 | 285 (16) | 6.4% |
| Proactive (ECMP) | 53.5 ± 8.9 | 0 | 0.2 | 1,072 (58) | 0% |
| **Tap** | 62.2 ± 32.3 | 109 | 4.3 | **368 (22)** | **100%** |

Seed 8 is an outlier for tap: 3 failed flows and a 108 ms mean. Without seed 8, tap is 50.7 ± 8.3 ms against proactive's 53.1 ± 13.1 ms. Large flows (over 10 MB) were slower under tap than under proactive in 4 of 5 runs. Likely cause: tap's paths are chosen per destination, so all flows to one host share a path, while proactive ECMP chooses per host pair and spreads them. Not yet confirmed; a pair-hash version of tap would test it.

### Abilene ISP (real traffic matrices)

| Controller | Small-flow FCT (ms) | PACKET_IN/s | CPU % | Peak rules (busiest switch) | Heard of |
| --- | --- | --- | --- | --- | --- |
| Reactive on shortest paths, exact rules | 72.5 ± 3.8 | 452 | 23.8 | 5,430 (855) | 100% |
| Reactive, pair rules | 58.9 ± 3.5 | 15 | 1.0 | 386 (62) | 3.5% |
| Reactive, destination rules | 58.8 ± 3.5 | 5 | 0.4 | 121 (11) | 2.2% |
| Proactive | 58.7 ± 3.5 | 0 | 0.1 | 386 (62) | 0% |
| **Tap** | **58.8 ± 3.5** | 174 | 5.0 | **154 (14)** | **100%** |

### Fat-tree k=6, web search (54 hosts, 3 runs)

| Controller | Small-flow FCT (ms) | PACKET_IN/s | CPU % | Peak rules (busiest switch) | Heard of |
| --- | --- | --- | --- | --- | --- |
| Reactive on shortest paths, exact rules | 58.8 ± 13.3 | 362 | 21.0 | 2,341 (160) | 100% |
| Reactive, pair rules | 26.9 ± 9.5 | 212 | 10.4 | 1,352 (54) | 49.2% |
| Reactive, destination rules | 19.8 ± 4.9 | 154 | 6.5 | 804 (26) | 40.7% |
| Proactive (ECMP) | 13.0 ± 3.5 | 0 | 0.5 | 13,230 (312) | 0% |
| **Tap** | **14.2 ± 4.8** | **63** | 2.8 | **2,592 (63)** | **100%** |

Every run of every controller: 0 failed flows, except tap seed 8 on the k=4 fat-tree (3 of 1,111). Tap heard of every connection in every run: 46,641 of 46,641 over the 18 runs.

## 5. What it shows

1. **The trade-off is not necessary.** On all four networks tap is as fast as proactive within the interval, and the controller heard of 100% of connections in all 18 runs. No other controller we measured has both.
2. **It needs fewer rules than proactive.** 128 against 624 on the university tree, 154 against 386 on Abilene, 2,592 against 13,230 at 54 hosts (busiest switch 63 against 312).
3. **At 54 hosts it beats every reactive variant.** Wildcard rules are rarely reused there (hit rate 51 to 59%), so pair and destination rules are 1.4 to 1.9 times slower than tap and send 2.4 to 3.4 times more PACKET_INs, while hearing of fewer than half the connections. Tap sends the fewest control messages of any controller that hears anything.
4. **The cost is controller reading, not waiting.** Tap sends about 3 copies per connection: 602 PACKET_IN/s and 14% CPU on the university workload (about 200 connections per second). None of them delays a packet. Wildcard reactive is cheaper there because it hears of almost nothing.

## 6. What it does not show

- **TCP only.** UDP has no SYN; a UDP flow would need a per-flow rule.
- **No per-flow byte counts.** The controller knows start, end and duration of each connection.
- **No decision before the first packet.** An access list must be a pre-installed rule; a decision from behaviour (the rate block) takes effect after the first packets.
- **Destination-based paths.** Possibly the cause of the slower large flows on the k=4 fat-tree.
- **An Open vSwitch extension**, not OpenFlow 1.0. OpenFlow 1.5 has TCP flags as a standard match field.
- **One machine, emulated network**, as for every test in this project.

## 7. Prior work

| Paper | What it does | Difference |
| --- | --- | --- |
| PARD (Rzepka et al., JNSM 2020) | Coarse proactive rules forward packets before the controller decides; the controller installs a detailed rule per flow in the background | Same principle. Tap installs no rule per flow, reports flow ends too, and is measured here against reactive, proactive and wildcard controllers. We have read only PARD's abstract; check the full text before claiming any difference beyond that |
| DevoFlow (SIGCOMM 2011) | Wildcard rules by default; the controller hears only of significant flows | Gives up per-flow visibility on purpose |
| Wang, Butnariu, Rexford (Hot-ICE 2011) | Notes that OpenFlow 1.0 cannot match TCP flags; the controller checks the SYN reactively | That is the reactive wait tap removes |
| NetFlow / IPFIX | Flow records exported by the switch | After the flow or sampled, outside the control loop |

## 8. Next

1. Controller frozen during traffic: `--pause-controller 10:5` (same five controllers, university tree, 3 seeds). Expected: reactive stalls every new connection for the 5 s; tap and proactive do not notice.
2. Live demo: `sudo python3 demo/freeze_demo.py`.
3. Tap with pair-hash ECMP paths, to test the large-flow explanation on the k=4 fat-tree.
