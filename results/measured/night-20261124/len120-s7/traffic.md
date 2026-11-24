# Realistic traffic results (len120-s7)

Testbed: Linux Harikrushna 6.18.58.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Tue Oct 27 00:24:11 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 120 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet
CPU: AMD Ryzen 7 8840HS w/ Radeon 780M Graphics, 16 threads | code: commit 2d76742349


## Traffic generated (identical for every controller)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Benson et al., IMC 2010 (university data centres) | 24457 | 203.8 | 88.1 (6%) | 0 | 84% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 24457 / 0 | 6.18 / 1.50 / 41.94 | 151.9 | - |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 24457 / 0 | 6.01 / 1.49 / 41.61 | 152.7 | - |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 24457 / 0 | 16.14 / 7.61 / 108.02 | 170.8 | - |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (hindsight) | 24457 / 0 | 12.37 / 5.37 / 56.22 | 160.8 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 43 | 43 | 3.1 | 624 | 192 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 10 | 9 | 0.7 | 80 | 16 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 713 | 716 | 47.1 | 4603 | 1435 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (hindsight) | 632 | 632 | 40.2 | 3544 | 1072 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 0 of 240 | 98.0 | 0 | 0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 0 of 240 | 99.6 | 0 | 0 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 60 of 240 | 68.0 | 128 | 45 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (hindsight) | 60 of 240 | 69.9 | 60 | 0 |
