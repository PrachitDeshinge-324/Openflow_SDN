# Realistic traffic results (traffic-20261022-101219)

Testbed: Linux prachit 7.3.0-9-generic #9-Ubuntu SMP PREEMPT_DYNAMIC Mon Oct  5 10:26:36 UTC 2026 aarch64 | Python 3.14.8 | ovs-vsctl (Open vSwitch) 4.0.0 | datapath=kernel | every link 100 Mbit/s | 60 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet

**Every value is the mean of 5 runs (seeds 7 to 11, a new flow schedule each time) ± the half-width of its 95% confidence interval (Student's t).**

## Traffic generated (identical for every controller within one seed)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Benson et al., IMC 2010 (university data centres) | 12177 ± 87 | 202.9 ± 1.5 | 89.6 ± 4.8 (6%) | 0 ± 0 | 83 ± 8% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 12177 ± 87 / 0 ± 0 | 6.92 ± 0.13 / 3.73 ± 0.18 / 42.45 ± 3.01 | 162.9 ± 19.3 | - |
| tree-d2-f4 | university | Hybrid, LSTM forecasts top 25% of pairs | 12177 ± 87 / 0 ± 0 | 7.67 ± 1.20 / 3.96 ± 0.25 / 76.45 ± 90.15 | 162.9 ± 19.1 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 1071 ± 199 | 1079 ± 199 | 16.3 ± 2.3 | 4942 ± 460 | 1513 ± 131 |
| tree-d2-f4 | university | Hybrid, LSTM forecasts top 25% of pairs | 1088 ± 139 | 1121 ± 147 | 17.0 ± 2.3 | 5194 ± 203 | 1603 ± 66 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 60 of 240 | 64.0 ± 5.3 | 149 ± 12 | 65 ± 11 |
| tree-d2-f4 | university | Hybrid, LSTM forecasts top 25% of pairs | 60 of 240 | 62.8 ± 5.2 | 441 ± 100 | 230 ± 83 |

## LSTM vs weighted counter (paired by seed; delta = LSTM - counter)

Negative flow-time and PACKET_IN deltas favor the LSTM; positive hit-rate deltas favor it. Intervals use paired seeds.

| Network | Workload | Budget | Paired runs | Hit-rate delta (pp) | Small p50 delta (ms) | PACKET_IN/s delta |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | 25% | 5 | -1.2 ± 0.4 | +0.2 ± 0.2 | +17 ± 64 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 7 | 0 | 3.54 / 44.47 | 984 | 15.1 | 4680 | 66.3 |
| tree-d2-f4 | university | Hybrid, LSTM forecasts top 25% of pairs | 7 | 0 | 3.90 / 46.89 | 1039 | 16.3 | 5183 | 65.5 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 8 | 0 | 3.78 / 40.69 | 909 | 14.7 | 4648 | 67.9 |
| tree-d2-f4 | university | Hybrid, LSTM forecasts top 25% of pairs | 8 | 0 | 3.83 / 39.47 | 954 | 15.0 | 4935 | 66.3 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 9 | 0 | 3.80 / 44.89 | 1106 | 17.0 | 5282 | 64.2 |
| tree-d2-f4 | university | Hybrid, LSTM forecasts top 25% of pairs | 9 | 0 | 3.93 / 206.20 | 1123 | 17.1 | 5348 | 62.8 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 10 | 0 | 3.63 / 42.91 | 1028 | 15.4 | 4693 | 65.0 |
| tree-d2-f4 | university | Hybrid, LSTM forecasts top 25% of pairs | 10 | 0 | 3.85 / 42.01 | 1067 | 16.4 | 5186 | 63.8 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 11 | 0 | 3.91 / 39.27 | 1327 | 19.2 | 5408 | 56.9 |
| tree-d2-f4 | university | Hybrid, LSTM forecasts top 25% of pairs | 11 | 0 | 4.31 / 47.70 | 1255 | 20.0 | 5320 | 55.8 |
