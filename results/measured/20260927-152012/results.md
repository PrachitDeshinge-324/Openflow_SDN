# Measured results (20260927-152012)

Testbed: Linux Harikrushna 6.18.33.2-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Thu Jun 18 21:54:43 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel

## Experiment 1: flow-setup latency (RTT, ms, mean +/- std over host pairs)

| Hosts | Mode | Packet 1 | Packet 2 | Steady state (pkts 3..N) | Lost |
| --- | --- | --- | --- | --- | --- |
| 4 | reactive | 3.807 +/- 1.319 | 0.889 +/- 0.436 | 0.062 +/- 0.007 | 0 |
| 4 | proactive | 0.667 +/- 0.263 | 0.081 +/- 0.023 | 0.064 +/- 0.006 | 0 |
| 8 | reactive | 6.596 +/- 2.551 | 0.959 +/- 0.338 | 0.071 +/- 0.012 | 0 |
| 8 | proactive | 0.863 +/- 0.261 | 0.088 +/- 0.029 | 0.093 +/- 0.016 | 0 |
| 16 | reactive | 5.442 +/- 1.541 | 0.949 +/- 0.326 | 0.085 +/- 0.011 | 0 |
| 16 | proactive | 0.772 +/- 0.254 | 0.107 +/- 0.036 | 0.092 +/- 0.010 | 0 |

## Experiment 2: flow-table occupancy (rules in all switches / max in one switch)

| Hosts | Mode | 25% pairs active | 50% pairs active | 100% pairs active |
| --- | --- | --- | --- | --- |
| 4 | reactive | 8 / 4 | 14 / 6 | 28 / 10 |
| 4 | proactive | 28 / 10 | 28 / 10 | 28 / 10 |
| 8 | reactive | 54 / 12 | 108 / 20 | 216 / 40 |
| 8 | proactive | 216 / 40 | 216 / 40 | 216 / 40 |
| 16 | reactive | 160 / 50 | 312 / 96 | 624 / 192 |
| 16 | proactive | 624 / 192 | 624 / 192 | 624 / 192 |

## Experiment 3: control-plane load under churn

| Hosts | Mode | New flows/s | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Rules after |
| --- | --- | --- | --- | --- | --- | --- |
| 4 | reactive | 10 | 29.0 | 28.2 | 1.5 | 138 |
| 4 | reactive | 50 | 120.5 | 116.9 | 6.9 | 582 |
| 4 | reactive | 100 | 235.1 | 231.5 | 12.8 | 1155 |
| 4 | reactive | 200 | 465.2 | 464.6 | 20.8 | 2321 |
| 4 | proactive | 10 | 0.0 | 0.0 | 0.1 | 28 |
| 4 | proactive | 50 | 0.0 | 0.0 | 0.0 | 28 |
| 4 | proactive | 100 | 0.0 | 0.0 | 0.1 | 28 |
| 4 | proactive | 200 | 0.0 | 0.0 | 0.0 | 28 |
| 8 | reactive | 10 | 40.6 | 39.6 | 2.1 | 194 |
| 8 | reactive | 50 | 196.0 | 189.1 | 11.1 | 942 |
| 8 | reactive | 100 | 396.6 | 394.0 | 19.0 | 1966 |
| 8 | reactive | 200 | 786.1 | 772.1 | 36.4 | 3857 |
| 8 | proactive | 10 | 0.0 | 0.0 | 0.1 | 216 |
| 8 | proactive | 50 | 0.0 | 0.0 | 0.1 | 216 |
| 8 | proactive | 100 | 0.0 | 0.0 | 0.1 | 216 |
| 8 | proactive | 200 | 0.0 | 0.0 | 0.2 | 216 |
| 16 | reactive | 10 | 29.8 | 27.3 | 2.0 | 134 |
| 16 | reactive | 50 | 133.7 | 132.1 | 7.3 | 658 |
| 16 | reactive | 100 | 285.8 | 255.7 | 19.0 | 1276 |
| 16 | reactive | 200 | 543.9 | 526.7 | 31.6 | 2631 |
| 16 | proactive | 10 | 0.0 | 0.0 | 0.1 | 624 |
| 16 | proactive | 50 | 0.0 | 0.0 | 0.1 | 624 |
| 16 | proactive | 100 | 0.0 | 0.0 | 0.1 | 624 |
| 16 | proactive | 200 | 0.0 | 0.0 | 0.1 | 624 |

## Controller-side numbers

| Hosts | Mode | PACKET_IN handling time (us, mean / p95) | Proactive install time (ms, max over switches) |
| --- | --- | --- | --- |
| 4 | reactive | 195 / 274 | - |
| 4 | proactive | - | 47.7 |
| 8 | reactive | 184 / 292 | - |
| 8 | proactive | - | 50.5 |
| 16 | reactive | 199 / 327 | - |
| 16 | proactive | - | 48.4 |
