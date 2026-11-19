# Novelty plan (version 3): forward first, tell the controller in parallel

CS G525 Advanced Computer Networks, Project SA7, Group 2. Written 19 Nov 2026 for the final presentation on 20 Nov.

> **Status, 19 Nov afternoon.** Steps 1 and 2 are done: the tap controller ran on four networks (18 runs), as fast as proactive, 100% of connections heard of. Results: `docs/Tap_Experiment.md`. Next: Step 3a (`--pause-controller`) and the demo (`demo/freeze_demo.py`).

**How to use this file:** Section 4 is the work list for today, in order. Section 8 is the timeline.

Versions 1 and 2 (a flow-table model; a limit on what prediction can add) are kept as supporting material in Section 7. They are true but small. This version is a controller that is already written and checked offline.

---

## 1. The one point

> **Every strategy we tested makes the network choose: either the first packet waits for the controller (reactive), or the controller never learns which flows exist (proactive, wildcard rules). That choice is not necessary. A switch rule can have two actions: forward the packet, and send a copy to the controller. We built a controller that does this for the first and last packet of every TCP connection. Nobody waits, the controller hears of every flow, and it needs fewer rules than proactive.**

The slide is one table (Section 2) in which the last row has no bad column, then a live demo: **freeze the controller during traffic.** With a reactive controller new connections hang. With ours nothing happens.

## 2. What it is and what is already checked

`controllers/tap_eval.py` (written 19 Nov):

- **Forwarding:** one destination rule per host on every switch, installed when the switch connects. On the fat-tree each switch picks among equal-cost next hops by a hash of the destination.
- **Tap:** at the switch a host is attached to, three more rules per host with a higher priority. They match TCP packets to that host with SYN (not ACK), FIN or RST set. Actions: output to the host **and** send a 128-byte copy to the controller.
- **Result:** the first packet is forwarded at once. The controller gets one PACKET_IN when a connection starts and one or two when it ends. No rule is installed per flow.
- **A reactive decision is still possible:** `--block_rate=N` drops a source that opens more than N connections in a second, with a rule at its own switch.

TCP-flag matching is not in OpenFlow 1.0. It is the Open vSwitch field `NXM_NX_TCP_FLAGS` (Open vSwitch 2.1 and later; we run 3.7.1), sent as a Nicira flow-mod. POX 0.7.0 has it (`pox/openflow/nicira.py`). The connection stays OpenFlow 1.0.

**Checked offline** (`python3 experiments/test_tap_offline.py [topology.json]`, no switch needed):

- every rule packs into a valid message;
- from every switch, forwarding reaches every host with no loop, on all four networks, and uses every link direction;
- SYN starts a flow, a repeated SYN does not count twice, FIN from either side or RST ends it;
- a source above the rate limit gets exactly one drop rule.

**Not checked yet: anything on a real switch.** Step 1 below is the first real run. Until it passes, nothing here is a result.

**Rules needed** (from the offline test; proactive from our measured tables):

| Network | Proactive, pair rules | Tap: forwarding + tap rules | Busiest switch: proactive / tap |
| --- | --- | --- | --- |
| University tree (16 hosts) | 624 | 80 + 48 = 128 | - / 28 |
| Fat-tree k=4 (16 hosts) | 1,072 | 320 + 48 = 368 | - / 22 |
| Abilene (11 hosts) | 386 | 121 + 33 = 154 | - / 14 |
| Fat-tree k=6 (54 hosts) | 13,230 | 2,430 + 162 = 2,592 | 312 / 63 |

**The table for the slide** (university tree, Zipf; rows 1 to 4 are our measured values from `Granularity_Baseline_Experiment.md`; row 5 is to be measured tonight):

| Controller | Small-flow median | Flows whose first packet waits | Rules | Flows the controller hears of |
| --- | --- | --- | --- | --- |
| Reactive, exact rules | 52.5 ms | all, at every switch | 10,987 | 100% |
| Reactive, pair rules | 1.49 ms | 2.1% | 624 | 2.1% |
| Reactive, destination rules | 1.47 ms | 0.4% | 80 | 0.4% |
| Proactive | 1.49 ms | none | 624 | 0% |
| **Tap** | expect about 1.5 ms | **none** | **128** | **expect 100%** |

"Hears of" for the wildcard rows is 100 minus the hit rate: the controller only sees a flow that misses.

Expected cost, to report honestly: about 3 PACKET_INs per flow (about 600 per second on the university workload). None of them delays a packet.

## 3. Is it new? What to say

Checked on 19 Nov by web search. Read the first item in full today (BITS library); we only have its abstract.

| Prior work | What it does | What differs here |
| --- | --- | --- |
| **PARD** (Rzepka et al., JNSM 2020; row 10 of our literature review) | Coarse proactive rules so packets are forwarded before the controller decides; the controller is notified and installs a detailed rule per flow in the background | **Same principle. Say so first.** Ours installs no rule per flow, and also reports when a flow ends, by matching TCP flags. We did not find PARD compared on one testbed with reactive, proactive, wildcard and budgeted hybrids under published traffic |
| DevoFlow (SIGCOMM 2011) | Wildcard rules by default; the controller is told only about significant flows | It gives up per-flow visibility on purpose. Ours keeps it |
| Wang, Butnariu, Rexford (Hot-ICE 2011) | Notes OpenFlow cannot match TCP flags; the controller inspects the SYN reactively | That is the reactive wait we remove. Open vSwitch added the match later |
| NetFlow / sFlow / IPFIX | Flow records exported by the switch | Records arrive after the flow or by sampling, outside the control loop. Ours arrives at flow start, as a PACKET_IN the controller can act on |

**Wording to use:** "The principle is PARD's. Our contribution is a version with no per-flow state, built on a real software switch, and the first side-by-side measurement of this idea against the others on our testbed. We did not find either in the literature we searched." Do not say "novel architecture".

If the full text of PARD shows it already uses flag matching with no per-flow rules, change the claim to "we implement and measure PARD against the alternatives". The table and the demo still stand.

## 4. Work list for today (in this order)

### Step 1. First real run (15 minutes, on the laptop, before anything else)

```bash
python3 experiments/test_tap_offline.py
```

```bash
sudo python3 experiments/run_traffic_experiments.py --quick --modes proactive reactive-dst tap
```

Pass when the `tap` run shows: 0 failed flows; `tap: controller heard of N of N flows` at or near 100%; `0 switch errors`; small-flow FCT close to proactive's.

If the switch refuses the tap rules (errors in `*-tap-pox.log`, 0 flows heard):

1. Check by hand that this Open vSwitch accepts the match: `sudo ovs-ofctl add-flow s1 "priority=200,tcp,tcp_flags=+syn-ack,dl_dst=00:00:00:00:00:01,actions=output:1,controller:128"`.
2. If that works, the problem is the Nicira flow-mod from POX. Fallback A: have the harness install the tap rules with `ovs-ofctl` after the switches connect (the PACKET_INs still reach POX).
3. Fallback B, pure OpenFlow 1.0, no flags: the tap rule is `dl_dst=host` at the host's switch with the same two actions; on each copy the controller installs an exact-match rule (output only, idle 10 s) at that one switch so later packets of the flow are not copied. This is PARD's design; the claim becomes "implemented and measured".

Say in the write-up which variant ran.

### Step 2. The main comparison (start it as soon as Step 1 passes; it runs for hours)

Add `tap` to the same batches that produced the granularity tables, so every controller runs for every seed:

```bash
sudo python3 experiments/run_traffic_experiments.py --scenarios tree-d2-f4:university --pair-zipf 1 --repeats 5 --modes reactive-sp reactive-pair reactive-dst proactive tap
```

```bash
sudo python3 experiments/run_traffic_experiments.py --scenarios fattree-k4:websearch --pair-zipf 1 --repeats 5 --modes reactive-sp reactive-pair reactive-dst proactive-ecmp tap
```

```bash
sudo python3 experiments/run_traffic_experiments.py --scenarios abilene:isp --pair-zipf 1 --repeats 5 --modes reactive-sp reactive-pair reactive-dst proactive tap
```

```bash
sudo python3 experiments/run_traffic_experiments.py --scenarios fattree-k6:websearch --load 0.05 --pair-zipf 1 --repeats 3 --modes reactive-sp reactive-pair reactive-dst proactive-ecmp tap
```

Report per scenario: small-flow median with 95% interval, failed flows, PACKET_IN/s, controller CPU, peak rules (total and busiest switch), and the share of flows the controller heard of. If tap is slower than proactive anywhere, report it and look for the reason (the fat-tree uses destination-hash paths, proactive-ecmp uses pair-hash paths).

### Step 3. The two experiments that show why it matters

Both need a small addition to `run_traffic_experiments.py`. Test each with a 10 s run first.

**3a. Controller frozen (`--pause-controller START:SECONDS`).** Send SIGSTOP to the POX process START seconds into the traffic and SIGCONT after SECONDS. Per controller, report failed flows and the small-flow median for flows that started inside the window. Run: university tree, `--pause-controller 10:10`, modes `reactive-sp reactive-pair reactive-dst proactive tap`, 3 seeds. Expected: exact-match reactive loses or stalls every new flow in the window; wildcard reactive stalls the new pairs; proactive and tap are untouched; tap's count of flows heard drops for that window (copies are lost) and recovers. Report what actually happens, including if the switch disconnects.

**3b. Control-channel delay (`--ctrl-delay MS`).** Add delay to OpenFlow traffic only (netem on the loopback device with a filter on TCP port 6633, both directions; or on the controller-facing interface with `--controller-host`). Sweep 0, 5, 20, 50 ms on the university tree, same five modes, 3 seeds. One figure: small-flow median against control-channel delay, one line per controller. Expected: reactive lines rise, proactive and tap stay flat. This is also the "controller on another machine" question (T9), answered as a sweep.

### Step 4. The live demo (`demo/run_demo.py`)

Add a third act after reactive and proactive, on the same 4-host tree:

1. Tap controller starts; show `ovs-ofctl dump-flows s2`: the forwarding rules and the three tap rules per host.
2. `h1` opens a TCP connection to `h4`. Show: first-packet time as proactive's, and the controller's line "flow h1 -> h4 started / ended".
3. Freeze the controller (`kill -STOP`), open another connection: it works. Repeat the same freeze in the reactive act: the connection hangs until `kill -CONT`.
4. Optional: start the controller with `--block_rate=5`, let `h1` open 20 connections quickly, show the log line "Blocked h1" and the drop rule.

Keep it under 3 minutes. Rehearse on the presenting laptop.

### Step 5. Write-up and pointers

- `docs/Tap_Experiment.md`, same layout as the other experiment files: why, design, prior work (Section 3), results, limits.
- New T13 in `docs/Test_Catalogue.md`; rows in `README.md`, `results/measured/INDEX.md`, `docs/Viva_Guide.md`, `docs/Final_Report.md` (contribution 5, Section 4.5 with the delay sweep).
- Delete the two `:Zone.Identifier` files that came with the last commit on `main`.

## 5. Limits (say them before being asked)

- **TCP only.** UDP has no SYN. A UDP flow would need the fallback B rule.
- **No byte counts per flow.** The controller knows start, end and duration. To count bytes for a chosen flow it must install one rule for it.
- **Decide-before-forward is not possible.** A packet is forwarded before the controller sees it. An access list known in advance is a pre-installed drop rule (as in any proactive design). A decision taken from behaviour, like the rate block, takes effect a few milliseconds late.
- **A switch extension, not standard OpenFlow 1.0.** OpenFlow 1.5 has the match as a standard field; hardware switches of the OpenFlow 1.0 era do not.
- **Three control messages per flow.** They do not delay packets, but a controller still has to read them. Give the measured CPU.
- **Destination rules.** Per-switch rules grow with the number of hosts (63 on the busiest switch at 54 hosts). Prefix aggregation is the known fix and is not built.
- **Emulation,** as everywhere in the project.

## 6. The questions

- *Is this new?* The principle is PARD's (2020). New here: no per-flow rule, flow end reported too, built on Open vSwitch, and measured against reactive, proactive, wildcard and hybrid controllers on one testbed.
- *Isn't this just proactive plus port mirroring?* Yes, and that is the point: a PACKET_IN did two jobs, asking and telling. Only the asking is slow. Keeping the telling costs three rules per host.
- *Why not NetFlow?* NetFlow reports after the flow. The copy arrives at flow start, inside the OpenFlow session, so the controller can act on it. The block demo shows that.
- *What if the controller must approve a flow first?* Then that flow needs a reactive rule, and pays for it. Our measurements say what it pays (T5, T11).
- *What does the controller do with the knowledge?* In this project: a complete flow log (start, end, duration) and the rate block. Anything a reactive controller does after the first packet (accounting, rerouting a large flow) is possible in the same way.
- *Why did the budgeted hybrid and prediction not get there?* They try to guess which rule will be needed. Section 7: with wildcard rules that guess is worth very little. Not having to wait removes the need to guess.

**Do not say:** "novel architecture", "better than PARD" (we did not run PARD's variant unless fallback B is used), or any number before it is in a committed table.

## 7. Supporting material from versions 1 and 2 (one backup slide at most)

- `experiments/model_validate.py`: a replay of the stored schedules through a timeout cache reproduces all 46 measured wildcard runs to 0.1 points of hit rate. The formula behind it is known (Metter et al., IEEE TNSM 2017; Zarek, MSc thesis, Toronto 2012).
- With a wildcard fallback, one pre-installed rule saves at most 1/(e·T) controller requests per second (Poisson arrivals, idle timeout T). On the university tree a 25% budget can add at most about 1.4 points of hit rate. This is why the counter and the oracle added nothing over pair rules. Numbers from throwaway scripts on 19 Nov; reproduce before quoting.
- Tried and dropped: pre-installing the pairs that miss most instead of the busiest. In steady state it is worse than the ordinary counter.

## 8. Timeline for today

| When | What | Who |
| --- | --- | --- |
| Now | Step 1 on the laptop (15 min). Get PARD's full text from the library | Laptop owner; one reader |
| Then | Start the Step 2 batch (hours) | Laptop owner |
| While it runs | Step 3 options and Step 4 demo; read PARD and fix the claim wording | Two of us |
| Evening | Step 3 runs (about an hour), results into Step 5, the slide | All |
| Before sleeping | Rehearse the demo twice on the presenting laptop | Presenter |
