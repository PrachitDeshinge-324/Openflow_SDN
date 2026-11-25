# Realistic traffic results (B-cap12-tree)

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
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 6052 ± 156 / 38 ± 89 | 5547.61 ± 3396.14 / 2134.14 ± 2016.32 / 22628.51 ± 11049.10 | 16359.4 ± 3653.8 | - |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 6090 ± 83 / 0 ± 0 | 29.71 ± 46.72 / 5.63 ± 2.92 / 284.50 ± 383.47 | 307.2 ± 332.3 | - |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 6001 ± 112 / 88 ± 37 | 8337.19 ± 1323.93 / 4644.19 ± 1524.63 / 29956.83 ± 2466.10 | 22309.4 ± 3462.4 | - |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 6090 ± 83 / 0 ± 0 | 15.26 ± 0.85 / 8.85 ± 0.40 / 78.92 ± 17.26 | 192.5 ± 37.6 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 10193 ± 251 | 10192 ± 251 | 100.1 ± 0.1 | 60 ± 0 | 12 ± 0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 4301 ± 2760 | 4300 ± 2760 | 69.3 ± 28.1 | 60 ± 0 | 12 ± 0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 8439 ± 171 | 10852 ± 381 | 99.8 ± 0.7 | 60 ± 0 | 12 ± 0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 1492 ± 92 | 1700 ± 111 | 32.7 ± 1.3 | 60 ± 0 | 12 ± 0 |

## Capped tables (--table-cap 12 rules per switch, Open vSwitch refuses beyond it)

| Network | Workload | Controller | Hit rate % | Refused installs | Evictions | PACKET_INs at a full table | Samples with a full switch % | SmartTime cost (installs + evictions) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 0.0 ± 0.0 | 297738 ± 7462 | 0 ± 0 | 80690 ± 10226 | 100.0 ± 0.0 | 12520 ± 4674 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 86.7 ± 2.9 | 129521 ± 83572 | 0 ± 0 | 36922 ± 20230 | 100.0 ± 0.0 | 298 ± 720 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 0.0 ± 0.0 | 0 ± 0 | 73140 ± 6264 | 73140 ± 6264 | 100.0 ± 0.0 | 329806 ± 14700 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 81.3 ± 3.4 | 0 ± 0 | 6363 ± 1125 | 6363 ± 1125 | 100.0 ± 0.0 | 51891 ± 3088 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 0 of 240 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 0 of 240 | 86.7 ± 2.9 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 0 of 240 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 0 of 240 | 81.3 ± 3.4 | 0 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 7 | 71 | 2691.77 / 25590.27 | 10266 | 100.1 | 60 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 7 | 0 | 6.43 / 447.98 | 5545 | 80.3 | 60 | 88.1 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 7 | 76 | 3955.60 / 28817.42 | 8379 | 99.8 | 60 | 0.0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 7 | 0 | 8.70 / 74.38 | 1449 | 32.1 | 60 | 82.6 |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 8 | 43 | 2507.64 / 24780.98 | 10235 | 100.2 | 60 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 8 | 0 | 6.17 / 264.25 | 3950 | 70.0 | 60 | 86.3 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 8 | 105 | 5133.42 / 30634.64 | 8423 | 100.1 | 60 | 0.0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 8 | 0 | 8.81 / 86.91 | 1515 | 32.9 | 60 | 81.3 |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 9 | 0 | 1203.03 / 17514.27 | 10078 | 100.1 | 60 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 9 | 0 | 4.28 / 141.26 | 3407 | 57.7 | 60 | 85.8 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 9 | 84 | 4843.55 / 30418.43 | 8514 | 99.5 | 60 | 0.0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 9 | 0 | 9.02 / 75.45 | 1511 | 33.1 | 60 | 79.9 |
