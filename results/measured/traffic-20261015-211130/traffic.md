# Realistic traffic results (traffic-20261015-211130)

Testbed: Linux Harikrushna 6.18.33.2-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Thu Jun 18 21:54:43 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 120 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet

## Traffic generated (identical for every controller)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Benson et al., IMC 2010 (university data centres) | 24457 | 203.8 | 88.1 (6%) | 0 | 84% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 24457 / 0 | 77.59 / 69.78 / 210.21 | 229.9 | - |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 24457 / 0 | 33.93 / 33.91 / 114.21 | 181.2 | - |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 24457 / 0 | 21.26 / 17.08 / 80.21 | 169.8 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 2439 | 2438 | 89.9 | 11525 | 3639 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 1620 | 1622 | 76.1 | 8377 | 2641 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 1112 | 1112 | 61.6 | 5576 | 1734 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 0 of 240 | 0.0 | 0 | 0 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 24 of 240 | 38.1 | 78 | 45 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 24 of 240 | 51.5 | 24 | 0 |
