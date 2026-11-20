# Realistic traffic results (traffic-20261022-083359)

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
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 12177 ± 87 / 0 ± 0 | 6.82 ± 0.45 / 3.67 ± 0.27 / 41.41 ± 5.58 | 160.8 ± 18.4 | - |
| tree-d2-f4 | university | Hybrid, LSTM forecasts top 25% of pairs | 12177 ± 87 / 0 ± 0 | 9.03 ± 5.98 / 3.77 ± 0.18 / 76.48 ± 95.51 | 161.4 ± 19.4 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 1085 ± 222 | 1093 ± 224 | 16.1 ± 2.5 | 5025 ± 783 | 1551 ± 201 |
| tree-d2-f4 | university | Hybrid, LSTM forecasts top 25% of pairs | 1109 ± 166 | 1145 ± 172 | 16.6 ± 2.0 | 4997 ± 289 | 1540 ± 90 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 60 of 240 | 63.4 ± 6.5 | 149 ± 20 | 66 ± 20 |
| tree-d2-f4 | university | Hybrid, LSTM forecasts top 25% of pairs | 60 of 240 | 63.5 ± 5.1 | 469 ± 88 | 267 ± 75 |

## LSTM vs weighted counter (paired by seed; delta = LSTM - counter)

Negative flow-time and PACKET_IN deltas favor the LSTM; positive hit-rate deltas favor it. Intervals use paired seeds.

| Network | Workload | Budget | Paired runs | Hit-rate delta (pp) | Small p50 delta (ms) | PACKET_IN/s delta |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | 25% | 5 | +0.0 ± 1.8 | +0.1 ± 0.2 | +24 ± 67 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 7 | 0 | 3.52 / 45.59 | 939 | 15.1 | 4407 | 68.0 |
| tree-d2-f4 | university | Hybrid, LSTM forecasts top 25% of pairs | 7 | 0 | 3.88 / 213.95 | 1016 | 15.6 | 4784 | 65.8 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 8 | 0 | 3.53 / 45.29 | 952 | 14.5 | 4542 | 67.4 |
| tree-d2-f4 | university | Hybrid, LSTM forecasts top 25% of pairs | 8 | 0 | 3.65 / 44.97 | 1012 | 15.3 | 5238 | 67.2 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 9 | 0 | 3.50 / 37.84 | 1090 | 15.8 | 5067 | 63.4 |
| tree-d2-f4 | university | Hybrid, LSTM forecasts top 25% of pairs | 9 | 0 | 3.58 / 40.20 | 1135 | 16.4 | 4987 | 63.7 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 10 | 0 | 3.81 / 42.74 | 1060 | 15.6 | 5100 | 63.4 |
| tree-d2-f4 | university | Hybrid, LSTM forecasts top 25% of pairs | 10 | 0 | 3.89 / 46.04 | 1048 | 16.3 | 4751 | 64.2 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 11 | 0 | 3.98 / 35.59 | 1382 | 19.5 | 6010 | 54.9 |
| tree-d2-f4 | university | Hybrid, LSTM forecasts top 25% of pairs | 11 | 0 | 3.86 / 37.24 | 1330 | 19.3 | 5226 | 56.5 |
