# Realistic traffic results (B-cap6-tree)

Testbed: Linux Nisarg 6.18.58.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Tue Oct 27 00:24:11 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet
CPU: AMD Ryzen AI 7 350 w/ Radeon 860M, 16 threads | code: commit e9d41c2984


**Every value is the mean of 3 runs (seeds 7 to 9, a new flow schedule each time) ± the half-width of its 95% confidence interval (Student's t).**

## Traffic generated (identical for every controller within one seed)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Benson et al., IMC 2010 (university data centres) | 6090 ± 83 | 203.0 ± 2.8 | 89.8 ± 28.9 (6%) | 0 ± 0 | 87 ± 6% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 5807 ± 307 / 283 ± 242 | 12061.01 ± 6368.12 / 8624.31 ± 8965.17 / 35341.96 ± 2327.23 | 12986.3 ± 7783.5 | - |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 6090 ± 83 / 0 ± 0 | 1504.42 ± 1901.44 / 609.13 ± 652.73 / 7545.86 ± 9582.89 | 6312.9 ± 6388.4 | - |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 5417 ± 481 / 673 ± 469 | 13708.76 ± 1342.18 / 9497.33 ± 1114.02 / 37739.29 ± 2765.23 | 11507.3 ± 15554.4 | - |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 6090 ± 83 / 0 ± 0 | 1129.59 ± 1126.84 / 620.16 ± 550.50 / 5817.94 ± 6747.04 | 8811.9 ± 7636.1 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 10078 ± 1744 | 10078 ± 1744 | 100.1 ± 0.2 | 30 ± 0 | 6 ± 0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 9582 ± 369 | 9582 ± 369 | 99.7 ± 2.1 | 30 ± 0 | 6 ± 0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 8745 ± 307 | 11886 ± 401 | 100.1 ± 0.0 | 30 ± 0 | 6 ± 0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 9028 ± 853 | 10283 ± 844 | 98.8 ± 5.2 | 30 ± 0 | 6 ± 0 |

## Capped tables (--table-cap 6 rules per switch, Open vSwitch refuses beyond it)

| Network | Workload | Controller | Hit rate % | Refused installs | Evictions | PACKET_INs at a full table | Samples with a full switch % | SmartTime cost (installs + evictions) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 0.0 ± 0.0 | 289765 ± 42681 | 0 ± 0 | 82029 ± 5349 | 100.0 ± 0.0 | 17015 ± 7589 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 23.4 ± 67.6 | 283189 ± 16059 | 0 ± 0 | 60920 ± 12357 | 100.0 ± 0.0 | 6832 ± 8562 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 0.0 ± 0.0 | 0 ± 0 | 95389 ± 11394 | 95389 ± 11394 | 100.0 ± 0.0 | 362185 ± 19942 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 32.8 ± 15.1 | 0 ± 0 | 38296 ± 1311 | 38296 ± 1311 | 100.0 ± 0.0 | 312953 ± 26082 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 0 of 240 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 0 of 240 | 23.4 ± 67.6 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 0 of 240 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 0 of 240 | 32.8 ± 15.1 | 0 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 7 | 364 | 8044.09 / 35266.74 | 10479 | 100.0 | 30 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 7 | 0 | 852.49 / 10879.55 | 9549 | 100.1 | 30 | 0.0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 7 | 456 | 9067.83 / 38775.15 | 8662 | 100.0 | 30 | 0.0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 7 | 0 | 702.93 / 6685.89 | 9305 | 100.0 | 30 | 33.6 |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 8 | 309 | 12487.94 / 36314.06 | 10488 | 100.1 | 30 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 8 | 0 | 644.35 / 8437.11 | 9453 | 100.2 | 30 | 17.0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 8 | 800 | 9962.53 / 37880.28 | 8887 | 100.1 | 30 | 0.0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 8 | 0 | 788.44 / 7993.70 | 9134 | 100.0 | 30 | 26.3 |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 9 | 175 | 5340.91 / 34445.08 | 9268 | 100.2 | 30 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 9 | 0 | 330.56 / 3320.93 | 9744 | 98.7 | 30 | 53.3 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 9 | 762 | 9461.64 / 36562.45 | 8686 | 100.1 | 30 | 0.0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 9 | 0 | 369.10 / 2774.23 | 8644 | 96.4 | 30 | 38.5 |
