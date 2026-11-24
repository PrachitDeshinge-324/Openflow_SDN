# Realistic traffic results (len30-s8)

Testbed: Linux Harikrushna 6.18.58.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Tue Oct 27 00:24:11 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet
CPU: AMD Ryzen 7 8840HS w/ Radeon 780M Graphics, 16 threads | code: commit 2d76742349


## Traffic generated (identical for every controller)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Benson et al., IMC 2010 (university data centres) | 6057 | 201.9 | 95.7 (6%) | 0 | 88% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 6057 / 0 | 6.87 / 1.81 / 42.76 | 163.9 | - |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 6057 / 0 | 6.62 / 1.78 / 39.50 | 163.7 | - |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 6057 / 0 | 16.09 / 12.07 / 65.71 | 177.2 | - |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (hindsight) | 6057 / 0 | 12.25 / 7.12 / 55.47 | 166.6 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 20 | 19 | 1.6 | 624 | 192 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 5 | 5 | 0.4 | 80 | 16 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 775 | 790 | 46.6 | 4725 | 1463 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (hindsight) | 542 | 542 | 35.9 | 3131 | 961 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 0 of 240 | 97.9 | 0 | 0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 0 of 240 | 99.5 | 0 | 0 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 60 of 240 | 64.3 | 153 | 75 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (hindsight) | 60 of 240 | 71.4 | 60 | 0 |
