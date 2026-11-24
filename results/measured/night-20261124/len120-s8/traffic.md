# Realistic traffic results (len120-s8)

Testbed: Linux Harikrushna 6.18.58.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Tue Oct 27 00:24:11 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 120 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet
CPU: AMD Ryzen 7 8840HS w/ Radeon 780M Graphics, 16 threads | code: commit 2d76742349


## Traffic generated (identical for every controller)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Benson et al., IMC 2010 (university data centres) | 24419 | 203.5 | 87.3 (5%) | 0 | 87% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 24419 / 0 | 6.87 / 1.65 / 44.13 | 155.5 | - |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 24419 / 0 | 6.90 / 1.63 / 46.90 | 158.1 | - |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 24419 / 0 | 13.90 / 8.06 / 65.63 | 167.2 | - |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (hindsight) | 24419 / 0 | 12.55 / 7.03 / 55.83 | 163.2 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 40 | 39 | 3.0 | 624 | 192 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 12 | 11 | 0.7 | 80 | 16 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 639 | 642 | 42.4 | 3991 | 1206 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (hindsight) | 585 | 585 | 38.1 | 3245 | 1002 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 0 of 240 | 98.0 | 0 | 0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 0 of 240 | 99.6 | 0 | 0 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 60 of 240 | 70.0 | 144 | 59 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (hindsight) | 60 of 240 | 71.3 | 60 | 0 |
