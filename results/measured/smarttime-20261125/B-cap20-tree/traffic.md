# Realistic traffic results (B-cap20-tree)

Testbed: Linux Harikrushna 6.18.58.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Tue Oct 27 00:24:11 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet
CPU: AMD Ryzen 7 8840HS w/ Radeon 780M Graphics, 16 threads | code: commit e4e178e3b8


**Every value is the mean of 3 runs (seeds 7 to 9, a new flow schedule each time) ± the half-width of its 95% confidence interval (Student's t).**

## Traffic generated (identical for every controller within one seed)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Benson et al., IMC 2010 (university data centres) | 6090 ± 83 | 203.0 ± 2.8 | 89.8 ± 28.9 (6%) | 0 ± 0 | 87 ± 6% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 6062 ± 140 / 28 ± 60 | 5185.24 ± 3663.73 / 1365.30 ± 3050.68 / 23089.87 ± 10027.81 | 14460.6 ± 5466.6 | - |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 6090 ± 83 / 0 ± 0 | 5.81 ± 1.27 / 0.97 ± 0.35 / 44.11 ± 4.48 | 155.0 ± 29.9 | - |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 6075 ± 104 / 15 ± 27 | 5818.94 ± 1645.54 / 2018.07 ± 2200.20 / 25791.42 ± 4551.31 | 18580.6 ± 6991.9 | - |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 6090 ± 83 / 0 ± 0 | 5.89 ± 1.56 / 0.98 ± 0.38 / 45.63 ± 3.22 | 154.6 ± 34.1 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 7542 ± 693 | 7541 ± 693 | 100.1 ± 0.1 | 100 ± 0 | 20 ± 0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 3 ± 8 | 2 ± 8 | 0.2 ± 0.0 | 80 ± 0 | 16 ± 0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 5933 ± 888 | 7567 ± 968 | 96.7 ± 8.3 | 100 ± 0 | 20 ± 0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 4 ± 1 | 3 ± 1 | 0.2 ± 0.0 | 80 ± 0 | 16 ± 0 |

## Capped tables (--table-cap 20 rules per switch, Open vSwitch refuses beyond it)

| Network | Workload | Controller | Hit rate % | Refused installs | Evictions | PACKET_INs at a full table | Samples with a full switch % | SmartTime cost (installs + evictions) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 0.0 ± 0.0 | 218552 ± 18479 | 0 ± 0 | 64883 ± 6623 | 100.0 ± 0.0 | 11646 ± 3898 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 99.5 ± 0.1 | 0 ± 0 | 0 ± 0 | 0 ± 0 | 0.0 ± 0.0 | 200 ± 87 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 0.0 ± 0.0 | 0 ± 0 | 49588 ± 3749 | 49588 ± 3749 | 100.0 ± 0.0 | 229845 ± 29227 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 99.3 ± 0.2 | 0 ± 0 | 0 ± 0 | 0 ± 0 | 0.0 ± 0.0 | 264 ± 13 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 0 of 240 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 0 of 240 | 99.5 ± 0.1 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 0 of 240 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 0 of 240 | 99.3 ± 0.2 | 0 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 7 | 41 | 869.94 / 21859.78 | 7736 | 100.1 | 100 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 7 | 0 | 0.97 / 46.00 | 1 | 0.2 | 80 | 99.6 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 7 | 24 | 1744.49 / 26824.25 | 6023 | 97.4 | 100 | 0.0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 7 | 0 | 0.99 / 47.01 | 4 | 0.3 | 80 | 99.3 |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 8 | 43 | 2763.58 / 27598.22 | 7667 | 100.1 | 100 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 8 | 0 | 1.12 / 42.41 | 6 | 0.2 | 80 | 99.5 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 8 | 18 | 3008.21 / 26873.81 | 6237 | 99.7 | 100 | 0.0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 8 | 0 | 1.13 / 44.44 | 4 | 0.2 | 80 | 99.3 |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 9 | 0 | 462.40 / 19811.62 | 7222 | 100.2 | 100 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 9 | 0 | 0.84 / 43.90 | 1 | 0.2 | 80 | 99.5 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 9 | 3 | 1301.51 / 23676.20 | 5539 | 93.1 | 100 | 0.0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 9 | 0 | 0.82 / 45.44 | 3 | 0.2 | 80 | 99.4 |
