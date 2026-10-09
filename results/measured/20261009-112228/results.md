# Measured results (20261009-112228)

Testbed: Linux Nisarg 6.18.40.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Fri Jul 31 22:12:15 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel

## Experiment 1: flow-setup latency (RTT, ms, mean +/- std over host pairs)

| Hosts | Mode | Packet 1 | Packet 2 | Steady state (pkts 3..N) | Lost |
| --- | --- | --- | --- | --- | --- |
| 4 | reactive | 7.212 +/- 3.031 | 1.014 +/- 0.379 | 0.099 +/- 0.012 | 0 |
| 4 | proactive | 1.005 +/- 0.352 | 0.109 +/- 0.046 | 0.098 +/- 0.010 | 0 |
| 8 | reactive | 11.404 +/- 4.923 | 1.413 +/- 0.620 | 0.102 +/- 0.014 | 0 |
| 8 | proactive | 1.496 +/- 0.388 | 0.105 +/- 0.033 | 0.106 +/- 0.010 | 0 |
| 16 | reactive | 8.681 +/- 3.015 | 1.132 +/- 0.283 | 0.107 +/- 0.014 | 0 |
| 16 | proactive | 0.953 +/- 0.327 | 0.110 +/- 0.041 | 0.101 +/- 0.014 | 0 |

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
| 4 | reactive | 10 | 26.9 | 26.1 | 2.4 | 128 |
| 4 | reactive | 50 | 121.7 | 115.7 | 11.8 | 576 |
| 4 | reactive | 100 | 229.4 | 225.8 | 18.3 | 1127 |
| 4 | reactive | 200 | 476.7 | 476.3 | 30.6 | 2379 |
| 4 | proactive | 10 | 0.0 | 0.0 | 0.0 | 28 |
| 4 | proactive | 50 | 0.0 | 0.0 | 0.1 | 28 |
| 4 | proactive | 100 | 0.0 | 0.0 | 0.2 | 28 |
| 4 | proactive | 200 | 0.0 | 0.0 | 0.1 | 28 |
| 8 | reactive | 10 | 39.8 | 38.8 | 3.5 | 190 |
| 8 | reactive | 50 | 207.6 | 200.4 | 17.9 | 998 |
| 8 | reactive | 100 | 373.7 | 372.3 | 25.9 | 1858 |
| 8 | reactive | 200 | 782.3 | 768.3 | 45.0 | 3838 |
| 8 | proactive | 10 | 0.0 | 0.0 | 0.1 | 216 |
| 8 | proactive | 50 | 0.0 | 0.0 | 0.2 | 216 |
| 8 | proactive | 100 | 0.0 | 0.0 | 0.0 | 216 |
| 8 | proactive | 200 | 0.0 | 0.0 | 0.1 | 216 |
| 16 | reactive | 10 | 30.2 | 26.5 | 5.2 | 130 |
| 16 | reactive | 50 | 130.1 | 129.9 | 21.6 | 647 |
| 16 | reactive | 100 | 287.8 | 257.7 | 43.1 | 1286 |
| 16 | reactive | 200 | 535.3 | 518.5 | 73.4 | 2590 |
| 16 | proactive | 10 | 0.0 | 0.0 | 0.2 | 624 |
| 16 | proactive | 50 | 0.0 | 0.0 | 0.1 | 624 |
| 16 | proactive | 100 | 0.0 | 0.0 | 0.1 | 624 |
| 16 | proactive | 200 | 0.0 | 0.0 | 0.2 | 624 |

## Controller-side numbers

| Hosts | Mode | PACKET_IN handling time (us, mean / p95) | Proactive install time (ms, max over switches) |
| --- | --- | --- | --- |
| 4 | reactive | 244 / 423 | - |
| 4 | proactive | - | 44.4 |
| 8 | reactive | 226 / 373 | - |
| 8 | proactive | - | 54.7 |
| 16 | reactive | 385 / 671 | - |
| 16 | proactive | - | 64.5 |
