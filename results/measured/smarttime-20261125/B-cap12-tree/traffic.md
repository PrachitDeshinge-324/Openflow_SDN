# Realistic traffic results (B-cap12-tree)

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
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 5853 ± 103 / 236 ± 114 | 10117.32 ± 6953.02 / 5513.04 ± 7503.32 / 34411.07 ± 8011.81 | 11982.0 ± 6006.1 | - |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 6090 ± 83 / 0 ± 0 | 56.92 ± 143.04 / 5.81 ± 2.93 / 511.92 ± 1085.59 | 470.3 ± 850.9 | - |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 4636 ± 858 / 1453 ± 896 | 13227.09 ± 2016.69 / 6933.67 ± 5751.25 / 42590.37 ± 5584.99 | 6715.0 ± 710.6 | - |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 6090 ± 83 / 0 ± 0 | 15.48 ± 1.15 / 8.82 ± 0.79 / 83.07 ± 2.76 | 198.7 ± 13.6 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 7975 ± 417 | 7975 ± 417 | 100.0 ± 0.1 | 60 ± 0 | 12 ± 0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 4106 ± 2240 | 4105 ± 2240 | 75.8 ± 28.8 | 60 ± 0 | 12 ± 0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 6510 ± 446 | 8705 ± 304 | 100.1 ± 0.1 | 60 ± 0 | 12 ± 0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 1496 ± 151 | 1705 ± 188 | 35.4 ± 3.3 | 60 ± 0 | 12 ± 0 |

## Capped tables (--table-cap 12 rules per switch, Open vSwitch refuses beyond it)

| Network | Workload | Controller | Hit rate % | Refused installs | Evictions | PACKET_INs at a full table | Samples with a full switch % | SmartTime cost (installs + evictions) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 0.0 ± 0.0 | 225959 ± 9825 | 0 ± 0 | 69079 ± 2621 | 100.0 ± 0.0 | 16645 ± 9105 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 86.7 ± 3.0 | 122686 ± 65931 | 0 ± 0 | 32806 ± 13201 | 100.0 ± 0.0 | 679 ± 1530 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 0.0 ± 0.0 | 0 ± 0 | 66640 ± 5777 | 66640 ± 5777 | 100.0 ± 0.0 | 265296 ± 10110 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 80.4 ± 3.0 | 0 ± 0 | 6399 ± 1161 | 6399 ± 1161 | 100.0 ± 0.0 | 52259 ± 5471 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 0 of 240 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 0 of 240 | 86.7 ± 3.0 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 0 of 240 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 0 of 240 | 80.4 ± 3.0 | 0 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 7 | 189 | 5632.75 / 36480.66 | 8070 | 100.0 | 60 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 7 | 0 | 6.71 / 1015.38 | 5126 | 87.9 | 60 | 88.1 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 7 | 1084 | 7117.58 / 40167.10 | 6619 | 100.1 | 60 | 0.0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 7 | 0 | 8.64 / 81.88 | 1499 | 35.6 | 60 | 81.4 |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 8 | 239 | 8471.66 / 36057.28 | 8075 | 100.1 | 60 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 8 | 0 | 6.26 / 289.23 | 3775 | 74.8 | 60 | 86.3 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 8 | 1471 | 9151.23 / 42995.97 | 6608 | 100.1 | 60 | 0.0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 8 | 0 | 8.63 / 83.24 | 1433 | 34.0 | 60 | 80.9 |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 9 | 281 | 2434.72 / 30695.28 | 7781 | 100.0 | 60 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 9 | 0 | 4.48 / 231.16 | 3416 | 64.7 | 60 | 85.8 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 9 | 1805 | 4532.19 / 44608.04 | 6303 | 100.1 | 60 | 0.0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 9 | 0 | 9.18 / 84.08 | 1555 | 36.6 | 60 | 79.1 |
