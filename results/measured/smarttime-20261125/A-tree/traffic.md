# Realistic traffic results (A-tree)

Testbed: Linux Harikrushna 6.18.58.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Tue Oct 27 00:24:11 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet
CPU: AMD Ryzen 7 8840HS w/ Radeon 780M Graphics, 16 threads | code: commit e4e178e3b8


**Every value is the mean of 5 runs (seeds 7 to 11, a new flow schedule each time) ± the half-width of its 95% confidence interval (Student's t).**

## Traffic generated (identical for every controller within one seed)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Benson et al., IMC 2010 (university data centres) | 6073 ± 41 | 202.4 ± 1.4 | 85.5 ± 14.1 (5%) | 0 ± 0 | 83 ± 8% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 6073 ± 41 / 0 ± 0 | 5.68 ± 1.04 / 1.33 ± 0.21 / 38.86 ± 4.44 | 148.6 ± 19.3 | - |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 6073 ± 41 / 0 ± 0 | 5.76 ± 1.22 / 1.33 ± 0.23 / 40.68 ± 6.24 | 150.1 ± 22.5 | - |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, exact-match rules | 6073 ± 41 / 0 ± 0 | 46.33 ± 8.36 / 41.96 ± 6.12 / 132.04 ± 43.12 | 190.5 ± 24.1 | - |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 6073 ± 41 / 0 ± 0 | 6.10 ± 1.27 / 1.50 ± 0.40 / 39.28 ± 6.57 | 150.3 ± 24.1 | - |
| tree-d2-f4 | university | Proactive (one shortest path) | 6073 ± 41 / 0 ± 0 | 5.59 ± 1.44 / 1.26 ± 0.38 / 38.97 ± 6.02 | 148.2 ± 23.5 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 30 ± 14 | 30 ± 14 | 1.5 ± 0.4 | 624 ± 1 | 192 ± 0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 5 ± 5 | 4 ± 5 | 0.3 ± 0.1 | 80 ± 0 | 16 ± 0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, exact-match rules | 2403 ± 141 | 2403 ± 141 | 87.0 ± 3.2 | 1241 ± 71 | 391 ± 21 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 120 ± 9 | 119 ± 9 | 6.8 ± 0.4 | 603 ± 11 | 186 ± 4 |
| tree-d2-f4 | university | Proactive (one shortest path) | 0 ± 0 | 0 ± 0 | 0.1 ± 0.0 | 624 ± 0 | 192 ± 0 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 0 of 240 | 97.9 ± 0.0 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 0 of 240 | 99.6 ± 0.1 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, exact-match rules | 0 of 240 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 0 of 240 | 93.8 ± 0.2 | 0 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 7 | 0 | 1.36 / 43.58 | 24 | 1.3 | 624 | 97.9 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 7 | 0 | 1.43 / 47.97 | 1 | 0.3 | 80 | 99.6 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, exact-match rules | 7 | 0 | 43.54 / 157.93 | 2313 | 86.9 | 1289 | 0.0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 7 | 0 | 1.71 / 47.50 | 120 | 6.9 | 600 | 93.7 |
| tree-d2-f4 | university | Proactive (one shortest path) | 7 | 0 | 1.50 / 46.69 | 0 | 0.1 | 624 | - |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 8 | 0 | 1.62 / 40.78 | 17 | 1.1 | 624 | 97.9 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 8 | 0 | 1.60 / 41.59 | 2 | 0.3 | 80 | 99.5 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, exact-match rules | 8 | 0 | 45.89 / 128.89 | 2407 | 88.1 | 1232 | 0.0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 8 | 0 | 1.96 / 40.42 | 124 | 7.1 | 594 | 93.6 |
| tree-d2-f4 | university | Proactive (one shortest path) | 8 | 0 | 1.54 / 39.63 | 0 | 0.1 | 624 | - |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 9 | 0 | 1.25 / 38.93 | 26 | 1.4 | 624 | 97.9 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 9 | 0 | 1.26 / 41.74 | 1 | 0.3 | 80 | 99.5 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, exact-match rules | 9 | 0 | 40.14 / 113.56 | 2531 | 86.3 | 1291 | 0.0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 9 | 0 | 1.34 / 39.09 | 123 | 7.0 | 616 | 93.9 |
| tree-d2-f4 | university | Proactive (one shortest path) | 9 | 0 | 1.25 / 38.54 | 0 | 0.1 | 624 | - |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 10 | 0 | 1.25 / 34.32 | 42 | 1.9 | 622 | 97.9 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 10 | 0 | 1.22 / 34.80 | 10 | 0.4 | 80 | 99.6 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, exact-match rules | 10 | 0 | 34.22 / 86.35 | 2497 | 83.2 | 1150 | 0.0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 10 | 0 | 1.30 / 34.04 | 107 | 6.2 | 606 | 93.8 |
| tree-d2-f4 | university | Proactive (one shortest path) | 10 | 0 | 1.24 / 33.88 | 0 | 0.1 | 624 | - |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 11 | 0 | 1.18 / 36.70 | 43 | 1.8 | 624 | 97.9 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 11 | 0 | 1.14 / 37.31 | 8 | 0.4 | 80 | 99.6 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, exact-match rules | 11 | 0 | 45.99 / 173.47 | 2268 | 90.3 | 1242 | 0.0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 11 | 0 | 1.21 / 35.34 | 124 | 6.8 | 598 | 94.0 |
| tree-d2-f4 | university | Proactive (one shortest path) | 11 | 0 | 0.77 / 36.15 | 0 | 0.1 | 624 | - |
