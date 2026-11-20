# Realistic traffic results (traffic-20261120-151236)

Testbed: Linux prachit 7.3.0-11-generic #12-Ubuntu SMP PREEMPT_DYNAMIC Fri Nov  6 10:32:55 UTC 2026 aarch64 | Python 3.14.8 | ovs-vsctl (Open vSwitch) 4.0.0 | datapath=kernel | every link 100 Mbit/s | 60 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet

## Traffic generated (identical for every controller)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Benson et al., IMC 2010 (university data centres) | 12270 | 204.5 | 91.4 (6%) | 0 | 84% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 12270 / 0 | 9.31 / 3.47 / 207.57 | 163.7 | - |
| tree-d2-f4 | university | Hybrid, LSTM forecasts top 25% of pairs | 12270 / 0 | 16.96 / 3.87 / 216.19 | 162.3 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 1021 | 1030 | 14.8 | 5288 | 1654 |
| tree-d2-f4 | university | Hybrid, LSTM forecasts top 25% of pairs | 999 | 1032 | 15.3 | 4395 | 1373 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 60 of 240 | 66.9 | 143 | 66 |
| tree-d2-f4 | university | Hybrid, LSTM forecasts top 25% of pairs | 60 of 240 | 66.6 | 431 | 227 |

## LSTM vs weighted counter (paired by seed; delta = LSTM - counter)

Negative flow-time and PACKET_IN deltas favor the LSTM; positive hit-rate deltas favor it. Intervals use paired seeds.

| Network | Workload | Budget | Paired runs | Hit-rate delta (pp) | Small p50 delta (ms) | PACKET_IN/s delta |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | 25% | 1 | -0.3 | +0.4 | -22 |
