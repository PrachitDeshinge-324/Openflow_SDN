# SmartTime port: a published baseline, and every place it deviates

**Goal.** Compare one published rule-management method with our coarse-rule reactive controllers, on the same testbed and traffic. Then the paper can say "a published method also loses to destination rules", not only "our counter loses to coarse rules".

**Source.** A. Vishnoi, R. Poddar, V. Mann, S. Bhattacharya, "Effective switch memory management in OpenFlow networks", ACM DEBS 2014 (`\cite{smarttime}`). We read the authors' copy (rishabhpoddar.com/publications/SmartTime.pdf, an IBM preprint that may differ slightly from the camera-ready). The policy is "AdaptiveR" (Figure 6 and Section 5.1, F1–F5).

**Name.** Call it **"SmartTime-style"**. Deviations 1 and 7 below change the algorithm's inputs, so it is not a faithful reproduction.

## The paper's algorithm (AdaptiveR)

| Item | The paper | Where |
|---|---|---|
| First idle timeout | MinIdleTimeout = **100 ms** (Open vSwitch patched for ms) | Fig. 6 l.4, F1 |
| Growth | Every PACKET_IN of a flow: FlowRepeatCount += 1, idle = Min × 2^FlowRepeatCount | Fig. 6 l.1–6, F2 |
| "Comes back" | Any later miss of the flow. **No time window**; the count is never reset | Fig. 6 |
| Maximum | MaxIdleTimeout = **10 s**, fixed | F3, Sec. 6.2 |
| Reset | Previous timeout = max and average hold factor (lifetime / active time) > 3 → back to the minimum | Fig. 6 l.7–8 |
| Eviction | TCAM use > **95%** → evict **one random** rule, on the PACKET_IN | Fig. 6 l.11–12, F5 |
| Hard timeout | None | — |
| Flow | Trace analysis: a source–destination pair is a flow; the rule's match is not stated | Sec. 4 |
| Metric | Cost = C_install × misses + C_evict × evictions (Eq. 4); C_evict / C_install = 1 in the trace replays | Sec. 3, 6 |
| Evaluation | 4 university/enterprise traces, TCAM of 750 and 2,000 entries, static timeouts 0.1–10 s with random eviction; SmartTime wins 67 of 72 experiments, cost up to 58% lower | Sec. 6 |

## Deviations (what the port does differently, and why)

Code: `controllers/hybrid_eval.py --timeout_policy=smarttime [--table_cap=N]`; harness modes `smarttime-exact`, `smarttime-pair`, `smarttime-dst`, and `--table-cap N`; replay model `experiments/model_validate.py`.

1. **Whole-second timeouts: 1, 2, 4, 8, 10 s, not 0.1 s … 10 s.** OpenFlow 1.0 timeouts are whole seconds, and the paper changed the switch to get milliseconds. The replay model also runs 0.1–10 s. On our traffic 0.1 s gives lower hit rates (tables below), so the 1 s start is not what makes the method look worse.
2. **The cap is an equality test in the pseudocode** (`if Prev == Max`). A power of two times 100 ms never equals 10 s exactly. We clamp at 10 s, as the text says ("we bound the maximum idle timeout at 10 seconds").
3. **The repeat count is kept per switch and per rule key** (5-tuple, host pair or destination, set by the mode). The paper keeps it per flow, at one switch.
4. **Duplicate PACKET_INs do not count as repeats.** These are packets of a flow that arrive before its rule is in. The controller treats a rule as live until its FLOW_REMOVED (or a refusal) and sends the same timeout again. The pseudocode would count each one.
5. **Table cap through Open vSwitch.** `flow_limit = N + control rules`, with `overflow_policy=refuse`, so the switch never evicts on its own and only SmartTime's own rule removes rules. The controller cannot read TCAM use from the switch. It keeps its own view of each table (FLOW_REMOVED on every reactive rule, refusals taken out), and that view is what the 95% test uses.
6. **When a rule is refused, the packet is still forwarded.** With a cap, every mode sends the FLOW_MOD without the packet and then a separate PACKET_OUT. Otherwise a refused rule would drop the packet, the TCP connection would wait about 1 s for a retransmission, and that delay would come from the setup, not from the policy. The fixed-timeout modes get exactly the same handling.
7. **Traffic and length.** We use our published-workload schedules (Benson university, DCTCP web search, Abilene ISP) and 30 s runs, not the paper's 19–65 minute packet traces. A repeat count needs repeats, so short runs limit what it can learn. The paper's traces are not public.
8. **Forwarding** is on shortest paths (ECMP on the fat-tree), as in our other `reactive-*` modes. The paper used Floodlight's forwarding.
9. **Baselines under a cap.** Our fixed-timeout modes do not evict: the switch refuses. The paper's static baselines evict at random. `--fixed-evict` gives our fixed modes the paper's random eviction, and the replay model shows both.
10. **Cost metric.** Our cost counts every rule install on every switch, plus every eviction (C_evict / C_install = 1). The testbed reports it as `table.smarttime_cost`.

## Check 1: does the port reproduce the paper's result? (replay model)

`python3 experiments/model_validate.py --paper-check` sets up the paper's own conditions. A flow is a host pair, the table is full (a cap of 50% and 25% of the busiest switch's uncapped peak), static timeouts 0.1/0.5/1/5/10 s get random eviction, and the score is the paper's cost (installs + evictions). Each value is the mean of 5 seeds of the 19 Nov schedules.

| Scenario | Cap (rules/switch) | Best static | SmartTime 0.1–10 s vs best static | SmartTime 1–10 s vs best static |
|---|---|---|---|---|
| University tree | 92 (50%) | 1 s | **−5.6% cost** | +2.2% |
| University tree | 46 (25%) | 0.1 s | +16.0% | +40.7% |
| Fat-tree, web search | 36 (50%) | 0.1 s | +3.6% | +33.3% |
| Fat-tree, web search | 18 (25%) | 0.1 s | +15.4% | +31.6% |
| Abilene ISP | 27 (50%) | 1 s | **−7.1% cost** | +0.8% |
| Abilene ISP | 13 (25%) | 0.1 s | +28.3% | +51.6% |

With the paper's values, SmartTime beats the best static timeout in 2 of 6 settings, by 6–7%. The paper reports wins in 67 of 72 settings, of up to 58%. **So the port reproduces the direction only at moderate table pressure, not the size of the gain.** We cannot tell from here whether the cause is the port or the traffic (deviation 7). The paper's traces are not public, so we cannot rerun them. When the table is very small, the best static timeout is always 0.1 s: rules expire before they need evicting, so it saves the eviction cost even though it misses more (hit rate around 40% against SmartTime's 64%). Taking 0.1 s away (the testbed's 1–10 s) loses everywhere except two near-ties.

What this means for the paper: we cannot claim the port is faithful. "SmartTime-style" is the honest name.

## Check 2: prediction for the testbed modes (replay model)

`python3 experiments/model_validate.py --smarttime` (no cap) and `--caps` (caps 20, 12 and 6 rules per switch, with refuse for fixed and random eviction for SmartTime). For the fixed timeout, the model matches the measured hit rate to within 0.1 pp. It matches the measured peak rules on the tree and on Abilene (624 / 80 and 381 / 120) and is within 3% for pair rules on the fat-tree. A running flow keeps its rules alive in the model (touched every 50 ms).

Hit rate (%), mean of 5 seeds:

| Scenario | Cap | reactive-pair | smarttime-pair 1–10 s | smarttime-pair 0.1–10 s | reactive-dst | smarttime-dst |
|---|---|---|---|---|---|---|
| University tree | none | 97.9 | 93.7 | 87.7 | **99.6** | 99.3 |
| | 20 | 46.7 | 42.4 | 42.4 | **99.6** | 99.3 |
| | 12 | 33.2 | 31.0 | 31.5 | **85.2** | 81.1 |
| | 6 | 19.3 | 18.8 | 18.8 | **45.6** | **45.7** |
| Fat-tree, web search | none | 86.0 | 71.6 | 60.3 | **93.6** | 83.3 |
| | 20 | 69.4 | 64.7 | 59.2 | **93.6** | 83.3 |
| | 12 | 56.3 | 53.5 | 51.8 | **86.7** | 80.7 |
| | 6 | 39.4 | 39.2 | 38.4 | 53.8 | **59.0** |
| Abilene ISP | none | 96.4 | 90.3 | 82.1 | **97.8** | 94.4 |
| | 20 | 82.1 | 75.5 | 70.4 | **97.8** | 94.4 |
| | 12 | 59.7 | 53.0 | 49.3 | **97.8** | 94.4 |
| | 6 | 32.5 | 29.1 | 26.5 | **68.2** | 63.5 |

Reading it:
- **smarttime-pair never beats reactive-dst, at any cap, including caps below one rule per destination** (16 hosts on the tree and the fat-tree, 11 on Abilene). It loses 6–22 pp without a cap and 22–57 pp at a cap of 20.
- Against reactive-pair, SmartTime also loses: without a cap, its 10 s maximum is our fixed idle timeout, so it can only pick shorter timeouts. Under a cap it comes close but is never ahead.
- The one place SmartTime helps is **destination rules on the fat-tree at a cap of 6**: 59.0% vs 53.8%. The gain comes from **eviction, not the adaptive timeout**. A fixed 10 s timeout with the same random eviction gets 58.7%, and the tree ties at 45.6–45.7%. So with a table far smaller than the number of destinations, evicting beats refusing. This belongs in the paper as a limit of "coarse rules alone".
- smarttime-exact needs no model: every TCP connection has a new source port, so its hit rate stays near 0%.
- The model's "refused" counts are per 50 ms of a running flow, not per packet, so they only rank the modes. The testbed counts the real refusals.

**Caps chosen for the testbed:** 20 (above 16 destinations), 12 (just below) and 6 (well below). They run on the university tree and the fat-tree; on Abilene, 20 and 12 are both above its 11 destinations.

## What the testbed records

Per run, in `traffic.json` (`table.*`, averaged in `traffic.md` under "Capped tables"):
- `refused_installs`: OFPFMFC_ALL_TABLES_FULL errors from the switches;
- `table_full_events`: PACKET_INs that found the controller's view of the table full;
- `full_samples_pct`: share of 1 s samples (ovs-ofctl) in which at least one switch was at the cap, and `full_switch_samples_pct` per switch;
- `evictions`, and `smarttime_cost` = rules installed + evictions (the paper's Eq. 4 with C_evict / C_install = 1);
- as before: hit rate, small-flow FCT, PACKET_IN/s and peak rules.

## Running it

Setup and quick checks:

```
cd ~/Openflow_SDN
python3 experiments/test_smarttime_offline.py          # "all SmartTime checks passed"
python3 experiments/model_validate.py --smarttime      # the prediction, seconds
```

The batch, inside tmux (Best performance, sleep off):

```
tmux new -s smarttime
sudo bash experiments/smarttime_batch.sh
```

It first checks that Open vSwitch really enforces the cap: a 10 s run at cap 6 must show refusals, SmartTime evictions, and no switch above 6. Then it runs part A (no cap, 3 scenarios × 5 modes × 5 seeds, about 1–1.5 h) and part B (caps 20/12/6, tree and fat-tree, 4 modes × 3 seeds, about 1 h). Finished folders are skipped on a re-run. `sudo PART=A bash …` runs part A only. The summary commands are at the end of the script.

Suggested wording for the paper: *"a SmartTime-style adaptive idle timeout with random eviction, reimplemented from [6]; deviations: whole-second timeouts (1–10 s instead of 0.1–10 s), table cap enforced by the switch (refuse) with the controller evicting, repeat count per switch and rule, our workloads instead of the paper's traces (deviations listed in the artifact)."*
