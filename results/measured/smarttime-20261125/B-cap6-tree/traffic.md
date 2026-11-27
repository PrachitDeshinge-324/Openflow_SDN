# Realistic traffic results (B-cap6-tree)

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
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 3320 ± 867 / 2770 ± 785 | 11975.50 ± 634.31 / 6363.53 ± 1000.03 / 45795.75 ± 5085.16 | 12475.2 ± 3788.5 | - |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 6035 ± 124 / 55 ± 95 | 6327.41 ± 1050.88 / 2440.89 ± 1711.63 / 28875.66 ± 3851.83 | 15453.2 ± 1343.6 | - |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 2169 ± 548 / 3921 ± 549 | 8850.91 ± 1655.21 / 3969.03 ± 837.07 / 40898.88 ± 9217.22 | 12369.4 ± 10708.6 | - |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 5964 ± 169 / 126 ± 99 | 7445.93 ± 2139.13 / 4473.79 ± 3679.49 / 30352.67 ± 4454.71 | 21901.8 ± 6792.2 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 6719 ± 694 | 6719 ± 694 | 99.1 ± 0.9 | 30 ± 0 | 6 ± 0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 6261 ± 642 | 6260 ± 642 | 98.6 ± 0.1 | 30 ± 0 | 6 ± 0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 5523 ± 615 | 7937 ± 425 | 99.7 ± 0.1 | 30 ± 0 | 6 ± 0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 6118 ± 407 | 7221 ± 583 | 99.5 ± 0.1 | 30 ± 0 | 6 ± 0 |

## Capped tables (--table-cap 6 rules per switch, Open vSwitch refuses beyond it)

| Network | Workload | Controller | Hit rate % | Refused installs | Evictions | PACKET_INs at a full table | Samples with a full switch % | SmartTime cost (installs + evictions) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 0.0 ± 0.0 | 179766 ± 24523 | 0 ± 0 | 53532 ± 27519 | 100.0 ± 0.0 | 25034 ± 7523 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 0.0 ± 0.0 | 178046 ± 18845 | 0 ± 0 | 41857 ± 5130 | 100.0 ± 0.0 | 12168 ± 1481 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 0.0 ± 0.0 | 0 ± 0 | 73517 ± 7343 | 73517 ± 7343 | 100.0 ± 0.0 | 242333 ± 14741 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 0.0 ± 0.0 | 0 ± 0 | 33164 ± 5830 | 33164 ± 5830 | 100.0 ± 0.0 | 217140 ± 17966 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 0 of 240 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 0 of 240 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 0 of 240 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 0 of 240 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 7 | 2866 | 5900.80 / 48117.87 | 6400 | 99.5 | 30 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 7 | 99 | 3060.33 / 30612.96 | 6468 | 98.6 | 30 | 0.0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 7 | 3666 | 3973.19 / 41625.08 | 5763 | 99.7 | 30 | 0.0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 7 | 95 | 3239.89 / 28493.42 | 6166 | 99.5 | 30 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 8 | 3027 | 6556.90 / 45016.21 | 6917 | 99.2 | 30 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 8 | 30 | 1698.85 / 28381.50 | 5971 | 98.6 | 30 | 0.0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 8 | 4037 | 4303.87 / 44192.22 | 5536 | 99.7 | 30 | 0.0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 8 | 171 | 6116.27 / 32071.38 | 5936 | 99.5 | 30 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 9 | 2417 | 6632.90 / 44253.16 | 6840 | 98.7 | 30 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 9 | 36 | 2563.50 / 27632.53 | 6344 | 98.7 | 30 | 0.0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 9 | 4060 | 3630.03 / 36879.35 | 5269 | 99.8 | 30 | 0.0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 9 | 112 | 4065.22 / 30493.20 | 6253 | 99.5 | 30 | 0.0 |
