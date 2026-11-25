# Realistic traffic results (B-cap6-fattree)

Testbed: Linux Harikrushna 6.18.58.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Tue Oct 27 00:24:11 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet
CPU: AMD Ryzen 7 8840HS w/ Radeon 780M Graphics, 16 threads | code: commit e4e178e3b8


**Every value is the mean of 3 runs (seeds 7 to 9, a new flow schedule each time) ± the half-width of its 95% confidence interval (Student's t).**

## Traffic generated (identical for every controller within one seed)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | DCTCP, SIGCOMM 2010 / pFabric web search workload | 1124 ± 70 | 37.5 ± 2.3 | 476.5 ± 46.1 (30%) | 15 ± 12 | 95 ± 4% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 565 ± 80 / 559 ± 13 | 10652.01 ± 2220.46 / 5010.28 ± 5029.24 / 39900.84 ± 4170.32 | 7515.8 ± 3373.5 | 6305.5 ± 15003.7 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 713 ± 126 / 411 ± 76 | 7562.71 ± 4520.50 / 1494.18 ± 2563.20 / 38062.77 ± 8375.18 | 6218.8 ± 1914.6 | 7544.1 ± 11984.2 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 429 ± 170 / 695 ± 146 | 13094.54 ± 4236.14 / 10101.14 ± 6948.88 / 41370.67 ± 6042.03 | 13449.2 ± 2296.6 | 20141.2 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 833 ± 316 / 291 ± 262 | 7663.66 ± 4028.19 / 3178.96 ± 4891.95 / 34304.99 ± 2856.92 | 15101.2 ± 4135.9 | 35939.0 ± 49063.4 |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 6867 ± 454 | 6863 ± 454 | 99.1 ± 0.9 | 120 ± 0 | 6 ± 0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 6832 ± 722 | 6828 ± 722 | 98.6 ± 1.0 | 120 ± 0 | 6 ± 0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 6064 ± 418 | 6962 ± 607 | 98.9 ± 0.8 | 120 ± 0 | 6 ± 0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 6247 ± 754 | 6603 ± 902 | 98.0 ± 1.7 | 120 ± 0 | 6 ± 0 |

## Capped tables (--table-cap 6 rules per switch, Open vSwitch refuses beyond it)

| Network | Workload | Controller | Hit rate % | Refused installs | Evictions | PACKET_INs at a full table | Samples with a full switch % | SmartTime cost (installs + evictions) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 0.0 ± 0.0 | 197609 ± 18343 | 0 ± 0 | 55310 ± 13515 | 100.0 ± 0.0 | 14192 ± 2233 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 0.0 ± 0.0 | 196871 ± 20331 | 0 ± 0 | 37770 ± 3607 | 100.0 ± 0.0 | 16684 ± 3340 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 0.0 ± 0.0 | 0 ± 0 | 27646 ± 6727 | 27646 ± 6727 | 100.0 ± 0.0 | 213276 ± 25750 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 5.8 ± 21.7 | 0 ± 0 | 10953 ± 4308 | 10953 ± 4308 | 100.0 ± 0.0 | 201322 ± 22364 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 0 of 240 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 0 of 240 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 0 of 240 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 0 of 240 | 5.8 ± 21.7 | 0 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 7 | 554 | 4093.79 / 41837.51 | 7070 | 99.6 | 120 | 0.0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 7 | 390 | 790.22 / 38073.00 | 7095 | 98.9 | 120 | 0.0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 7 | 678 | 10267.85 / 38697.14 | 6204 | 99.2 | 120 | 0.0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 7 | 194 | 1564.25 / 33121.55 | 5996 | 97.6 | 120 | 15.8 |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 8 | 564 | 3606.22 / 39002.09 | 6814 | 98.8 | 120 | 0.0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 8 | 446 | 1013.79 / 34686.48 | 6882 | 98.2 | 120 | 0.0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 8 | 760 | 12811.13 / 41963.10 | 6110 | 98.9 | 120 | 0.0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 8 | 403 | 5372.66 / 35418.28 | 6585 | 98.8 | 120 | 0.0 |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 9 | 558 | 7330.82 / 38862.93 | 6716 | 99.0 | 120 | 0.0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 9 | 397 | 2678.52 / 41428.84 | 6520 | 98.9 | 120 | 0.0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 9 | 646 | 7224.44 / 43451.77 | 5877 | 98.6 | 120 | 0.0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 9 | 276 | 2599.98 / 34375.14 | 6161 | 97.6 | 120 | 1.4 |
