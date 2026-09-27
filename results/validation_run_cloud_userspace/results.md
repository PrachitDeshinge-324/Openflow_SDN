# Measured results (full)

Testbed: Linux vm 6.18.44-fc-v37 #1 SMP PREEMPT_DYNAMIC @0 x86_64 | Python 3.11.15 | ovs-vsctl (Open vSwitch) 3.3.9 | datapath=user

## Experiment 1: flow-setup latency (RTT, ms, mean +/- std over host pairs)

| Hosts | Mode | Packet 1 | Packet 2 | Steady state (pkts 3..N) | Lost |
| --- | --- | --- | --- | --- | --- |
| 4 | reactive | 4.377 +/- 1.410 | 0.718 +/- 0.256 | 0.528 +/- 0.125 | 0 |
| 4 | proactive | 0.848 +/- 0.188 | 0.493 +/- 0.064 | 0.510 +/- 0.062 | 0 |
| 8 | reactive | 8.695 +/- 3.426 | 1.196 +/- 0.402 | 1.057 +/- 0.352 | 0 |
| 8 | proactive | 1.423 +/- 0.620 | 1.147 +/- 0.412 | 1.126 +/- 0.341 | 0 |
| 16 | reactive | 6.334 +/- 1.380 | 1.070 +/- 0.303 | 0.997 +/- 0.280 | 0 |
| 16 | proactive | 0.937 +/- 0.243 | 0.932 +/- 0.436 | 0.860 +/- 0.213 | 0 |

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
| 4 | reactive | 10 | 24.5 | 24.5 | 1.6 | 120 |
| 4 | reactive | 50 | 120.5 | 120.5 | 7.2 | 600 |
| 4 | reactive | 100 | 241.3 | 241.3 | 13.2 | 1204 |
| 4 | reactive | 200 | 463.2 | 463.2 | 25.2 | 2314 |
| 4 | proactive | 10 | 0.0 | 0.0 | 0.0 | 28 |
| 4 | proactive | 50 | 0.0 | 0.0 | 0.1 | 28 |
| 4 | proactive | 100 | 0.0 | 0.0 | 0.1 | 28 |
| 4 | proactive | 200 | 0.0 | 0.0 | 0.0 | 28 |
| 8 | reactive | 10 | 39.2 | 39.2 | 2.7 | 192 |
| 8 | reactive | 50 | 191.6 | 191.6 | 10.9 | 954 |
| 8 | reactive | 100 | 375.9 | 375.9 | 21.0 | 1876 |
| 8 | reactive | 200 | 761.1 | 761.1 | 38.6 | 3802 |
| 8 | proactive | 10 | 0.0 | 0.0 | 0.2 | 216 |
| 8 | proactive | 50 | 0.0 | 0.0 | 0.1 | 216 |
| 8 | proactive | 100 | 0.0 | 0.0 | 0.1 | 216 |
| 8 | proactive | 200 | 0.0 | 0.0 | 0.1 | 216 |
| 16 | reactive | 10 | 27.3 | 27.3 | 1.8 | 134 |
| 16 | reactive | 50 | 129.7 | 129.7 | 7.9 | 646 |
| 16 | reactive | 100 | 255.9 | 255.9 | 14.6 | 1277 |
| 16 | reactive | 200 | 518.7 | 518.7 | 29.3 | 2591 |
| 16 | proactive | 10 | 0.0 | 0.0 | 0.1 | 624 |
| 16 | proactive | 50 | 0.0 | 0.0 | 0.0 | 624 |
| 16 | proactive | 100 | 0.0 | 0.0 | 0.1 | 624 |
| 16 | proactive | 200 | 0.0 | 0.0 | 0.1 | 624 |

## Controller-side numbers

| Hosts | Mode | PACKET_IN handling time (us, mean / p95) | Proactive install time (ms, max over switches) |
| --- | --- | --- | --- |
| 4 | reactive | 254 / 367 | - |
| 4 | proactive | - | 47.9 |
| 8 | reactive | 239 / 351 | - |
| 8 | proactive | - | 48.3 |
| 16 | reactive | 241 / 354 | - |
| 16 | proactive | - | 62.9 |
