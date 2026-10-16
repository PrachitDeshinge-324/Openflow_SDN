# Realistic traffic results (traffic-20261016-021112)

Testbed: Linux Harikrushna 6.18.33.2-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Thu Jun 18 21:54:43 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet

## Traffic generated (identical for every controller)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Benson et al., IMC 2010 (university data centres) | 6088 | 202.9 | 97.3 (6%) | 0 | 84% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 6088 / 0 | 26.32 / 25.01 / 63.38 | 193.3 | - |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 6088 / 0 | 15.03 / 13.72 / 52.30 | 181.7 | - |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 6088 / 0 | 10.56 / 7.21 / 52.36 | 172.1 | - |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 6088 / 0 | 11.81 / 9.89 / 47.52 | 173.6 | - |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 6088 / 0 | 8.98 / 4.93 / 54.71 | 170.1 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 2480 | 2479 | 64.1 | 11157 | 3514 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 1473 | 1483 | 46.6 | 7286 | 2251 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 790 | 805 | 29.2 | 4604 | 1437 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 1063 | 1062 | 36.5 | 5320 | 1657 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 601 | 600 | 22.2 | 3302 | 1016 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 0 of 240 | 0.0 | 0 | 0 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 24 of 240 | 36.7 | 86 | 54 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 60 of 240 | 63.8 | 153 | 68 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 24 of 240 | 51.6 | 24 | 0 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 60 of 240 | 70.6 | 60 | 0 |
