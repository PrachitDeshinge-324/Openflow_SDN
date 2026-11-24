# Realistic traffic results (len120-s9)

Testbed: Linux Harikrushna 6.18.58.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Tue Oct 27 00:24:11 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 120 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet
CPU: AMD Ryzen 7 8840HS w/ Radeon 780M Graphics, 16 threads | code: commit 2d76742349


## Traffic generated (identical for every controller)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Benson et al., IMC 2010 (university data centres) | 24238 | 202.0 | 96.2 (6%) | 0 | 88% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 24237 / 1 | 7.25 / 1.84 / 43.72 | 182.6 | - |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 24238 / 0 | 7.09 / 1.76 / 44.15 | 180.4 | - |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 24238 / 0 | 13.96 / 10.27 / 60.92 | 189.0 | - |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (hindsight) | 24238 / 0 | 12.27 / 7.79 / 55.83 | 184.6 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 42 | 42 | 3.0 | 624 | 192 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 12 | 12 | 0.8 | 80 | 16 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 769 | 774 | 40.0 | 6009 | 1916 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (hindsight) | 642 | 641 | 35.3 | 3664 | 1121 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 0 of 240 | 98.0 | 0 | 0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 0 of 240 | 99.6 | 0 | 0 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 60 of 240 | 64.7 | 158 | 71 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (hindsight) | 60 of 240 | 68.3 | 60 | 0 |
