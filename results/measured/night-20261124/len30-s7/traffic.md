# Realistic traffic results (len30-s7)

Testbed: Linux Harikrushna 6.18.58.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Tue Oct 27 00:24:11 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet
CPU: AMD Ryzen 7 8840HS w/ Radeon 780M Graphics, 16 threads | code: commit 2d76742349


## Traffic generated (identical for every controller)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Benson et al., IMC 2010 (university data centres) | 6088 | 202.9 | 97.3 (6%) | 0 | 84% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 6088 / 0 | 6.76 / 1.52 / 41.58 | 172.5 | - |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 6088 / 0 | 6.88 / 1.58 / 43.36 | 172.9 | - |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 6088 / 0 | 16.70 / 11.76 / 74.70 | 184.6 | - |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (hindsight) | 6088 / 0 | 12.62 / 6.78 / 60.88 | 177.1 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 18 | 17 | 1.2 | 624 | 192 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 8 | 7 | 0.3 | 80 | 16 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 787 | 803 | 46.3 | 4557 | 1418 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (hindsight) | 575 | 575 | 36.8 | 3294 | 1014 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 0 of 240 | 97.9 | 0 | 0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 0 of 240 | 99.6 | 0 | 0 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 60 of 240 | 64.0 | 154 | 67 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (hindsight) | 60 of 240 | 70.6 | 60 | 0 |
