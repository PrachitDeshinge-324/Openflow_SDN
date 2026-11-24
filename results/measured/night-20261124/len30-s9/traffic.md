# Realistic traffic results (len30-s9)

Testbed: Linux Harikrushna 6.18.58.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Tue Oct 27 00:24:11 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet
CPU: AMD Ryzen 7 8840HS w/ Radeon 780M Graphics, 16 threads | code: commit 2d76742349


## Traffic generated (identical for every controller)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Benson et al., IMC 2010 (university data centres) | 6124 | 204.1 | 76.4 (5%) | 0 | 88% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 6124 / 0 | 6.20 / 1.53 / 41.58 | 147.9 | - |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 6124 / 0 | 5.81 / 1.49 / 39.95 | 146.3 | - |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 6124 / 0 | 16.69 / 13.13 / 65.79 | 154.6 | - |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (hindsight) | 6124 / 0 | 12.23 / 6.70 / 54.55 | 148.0 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 34 | 33 | 2.2 | 624 | 192 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 1 | 1 | 0.3 | 80 | 16 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 921 | 936 | 51.3 | 5023 | 1601 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (hindsight) | 662 | 661 | 40.9 | 3682 | 1112 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 0 of 240 | 97.9 | 0 | 0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 0 of 240 | 99.5 | 0 | 0 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 60 of 240 | 60.6 | 151 | 72 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (hindsight) | 60 of 240 | 67.5 | 60 | 0 |
