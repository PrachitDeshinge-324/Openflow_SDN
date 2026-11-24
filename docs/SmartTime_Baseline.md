# SmartTime-style adaptive timeout: a published baseline

**Goal.** Compare one published rule-management method with our coarse-rule reactive controllers on the same testbed and traffic. Then the paper can say "a published method also loses to destination rules", not only "our counter loses to coarse rules".

**Source.** A. Vishnoi, R. Poddar, V. Mann, S. Bhattacharya, "Effective switch memory management in OpenFlow networks", ACM DEBS 2014 (reference [6] / `\cite{smarttime}` in the paper). We read the authors' copy (rishabhpoddar.com/publications/SmartTime.pdf, an IBM preprint that may differ slightly from the camera-ready). The policy is "AdaptiveR" (Figure 6 and Section 5.1, features F1–F5).

## The paper's algorithm

| Item | The paper | Where |
|---|---|---|
| First idle timeout | MinIdleTimeout = **100 ms** (they patched Open vSwitch to accept ms) | Fig. 6 l.4, F1 |
| Growth | On every PACKET_IN of a flow, FlowRepeatCount += 1; idle = MinIdleTimeout × 2^FlowRepeatCount | Fig. 6 l.1–6, F2 |
| "Comes back" | Any later miss of the same flow. **No time window**, and the count is never reset | Fig. 6 |
| Maximum | MaxIdleTimeout = **10 s**, fixed (not tied to table use) | F3, Sec. 6.2 |
| Reset | If the previous timeout was the maximum and the flow's average hold factor (rule lifetime / active time) is above 3, go back to the minimum | Fig. 6 l.7–8 |
| Eviction | When TCAM use is above **95%**, evict **one rule at random** on a PACKET_IN (random beat FIFO; LRU needs counters the switch cannot report cheaply) | Fig. 6 l.11–12, F5 |
| Hard timeout | Not used | — |
| Flow key | Their trace analysis treats a source–destination pair as a flow; the match of the installed rule is not stated | Sec. 4 |
| Evaluation | 4 university/enterprise traces, TCAM of 750 and 2,000 entries, cost = installs + evictions; up to 58% lower cost than the best static timeout | Sec. 6 |

The pseudocode caps the timeout with an equality test (`if Prev == Max`), which a power of two times 100 ms never meets exactly. We read it as a plain cap at 10 s, as the text says.

## What we kept and what we simplified

Implemented in `controllers/hybrid_eval.py --timeout_policy=smarttime`. It is used by the harness modes `smarttime-exact`, `smarttime-pair` and `smarttime-dst`.

Kept:
- Each rule's idle timeout doubles with every earlier install of the same rule on the same switch, up to 10 s. The count has no time window, as in the paper.
- There is no hard timeout.
- The hold-factor reset is kept. The controller asks for FLOW_REMOVED on every reactive rule and computes the hold factor from the rule's duration and idle timeout.

Simplified:
1. **Timeouts are whole seconds.** OpenFlow 1.0 has no millisecond timeouts, so the sequence is 1, 2, 4, 8, 10 s, not 0.1, 0.2, …, 10 s. The replay model runs both: 100 ms does worse on our traffic (see below), so the 1 s start does not make the method look worse.
2. **No eviction.** Our testbed has no table cap, so the 95% random-eviction rule never fires. The replay model has an optional per-switch cap with this eviction rule (`--cap`).
3. **Duplicate PACKET_INs** (a second packet of a flow that arrives before its rule is in) do not count as a repeat. The rule stays "live" until its FLOW_REMOVED, and the same timeout is sent again.
4. **The repeat counter is per switch and per rule key** (exact 5-tuple, host pair, or destination). The paper keeps it per flow at one switch.
5. Forwarding is on shortest paths (ECMP on the fat-tree), as in our other `reactive-*` modes. The paper used Floodlight's forwarding.

Suggested wording for the paper: *"a SmartTime-style adaptive idle timeout, reimplemented from [6]; simplifications: whole-second timeouts (1–10 s instead of 0.1–10 s), no table cap and hence no eviction, repeat count per switch and rule."* This is not a faithful reproduction.

## Prediction from the replay model (no Mininet)

`python3 experiments/model_validate.py --smarttime` replays the stored schedules of the 19 Nov batches (`traffic-20261119-114525`, `-120616`, `-123520`; Zipf 1 pairs, 5 seeds). For the fixed timeout, the model matches the measured hit rate to within 0.1 pp. It also matches the measured peak rules on the tree and on Abilene (624 / 80 and 381 / 120). On the fat-tree it is within 3% for pair rules and below the measurement for destination rules (205 vs 280).

| Scenario | reactive-pair (10 s idle, 30 s hard) | smarttime-pair, 1–10 s | smarttime-pair, 0.1–10 s (paper) | reactive-dst |
|---|---|---|---|---|
| University tree | 97.9% hit, 653 PACKET_IN, 624 peak rules | 93.7%, 1,975, 611 | 87.7%, 3,900, 600 | 99.6%, 84, 80 |
| Fat-tree k=4, web search | 86.0%, 1,478, 852 | 71.7%, 2,983, 613 | 61.2%, 4,662, 440 | 93.6%, 297, 205 |
| Abilene ISP | 96.4%, 446, 381 | 90.3%, 1,184, 367 | 82.7%, 2,234, 344 | 97.8%, 139, 120 |

PACKET_IN here is the total number of rule installs in a 30 s run, over all switches.

**Predicted gain of smarttime-pair: −4 to −14 pp of hit rate against reactive-pair, and −6 to −22 pp against reactive-dst.** It also has 2–3× more PACKET_INs, and its peak rules are only 2–28% lower than reactive-pair's. The reason: SmartTime's largest timeout (10 s) is our fixed timeout. Without a table cap, SmartTime can only use shorter timeouts than the baseline, never longer ones. So it does not behave like reactive-long (60 s idle): it sits below reactive-pair.

smarttime-exact needs no model. Every TCP connection has a new source port, so every rule key is new, every rule starts at 1 s, and the hit rate stays near 0%, as for reactive-sp.

**With a table cap** (`--cap N`, random eviction at 95% for both the fixed and the adaptive policy): with 100 rules per switch, smarttime-pair still loses 1.4 pp on the tree and 14 pp on the fat-tree. With 50 it ties on the tree (68.1% vs 67.6%) and still loses elsewhere. With 25 it is within 3 pp but never ahead by more than noise. Destination rules need at most one rule per host per switch, so they fit every cap we tried and stay at 93.6–99.6%. SmartTime's gains in its paper come from a full table and exact traces; with coarse rules the table is never full.

## Testbed run

```
tmux new -s smarttime
cd ~/Openflow_SDN && git pull
sudo bash experiments/smarttime_batch.sh 2>&1 | tee smarttime_batch.log
```

It runs 3 scenarios × 5 modes (reactive-pair, reactive-dst, smarttime-exact, smarttime-pair, proactive or proactive-ecmp) × 5 seeds, with Zipf 1 pairs, and takes about 1–1.5 hours. The summary for the paper (hit rate, small-flow FCT, PACKET_IN/s, peak rules, paired against reactive-dst):

```
python3 experiments/paired_stats.py $(ls -d results/measured/traffic-* | tail -3) \
    --pairs smarttime-pair:reactive-dst smarttime-pair:reactive-pair smarttime-exact:reactive-dst \
    --metrics hit_rate small_p50 packet_in peak_rules
```

Offline check of the controller logic (no switch): `python3 experiments/test_smarttime_offline.py`.
