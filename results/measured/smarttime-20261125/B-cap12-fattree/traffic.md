# Realistic traffic results (B-cap12-fattree)

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
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 875 ± 91 / 249 ± 32 | 6824.76 ± 2424.21 / 1841.00 ± 2036.32 / 35205.22 ± 5670.83 | 11253.8 ± 3237.1 | 12961.8 ± 15722.6 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 1124 ± 70 / 0 ± 0 | 241.79 ± 358.89 / 61.44 ± 29.80 / 4124.55 ± 7706.40 | 3433.6 ± 2063.5 | 12421.6 ± 13089.3 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 1023 ± 144 / 100 ± 85 | 4576.86 ± 5043.83 / 999.17 ± 1142.75 / 29743.00 ± 9892.53 | 11461.2 ± 8434.4 | 18761.0 ± 6682.1 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 1124 ± 70 / 0 ± 0 | 70.33 ± 20.69 / 50.20 ± 15.40 / 333.42 ± 64.63 | 2708.5 ± 635.1 | 11137.2 ± 9863.6 |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 7405 ± 618 | 7401 ± 618 | 98.3 ± 1.0 | 240 ± 0 | 12 ± 0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 5257 ± 1990 | 5253 ± 1990 | 92.5 ± 6.4 | 237 ± 4 | 12 ± 0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 5988 ± 1023 | 6387 ± 1152 | 95.7 ± 5.4 | 240 ± 0 | 12 ± 0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 354 ± 187 | 366 ± 186 | 12.5 ± 5.0 | 227 ± 9 | 12 ± 0 |

## Capped tables (--table-cap 12 rules per switch, Open vSwitch refuses beyond it)

| Network | Workload | Controller | Hit rate % | Refused installs | Evictions | PACKET_INs at a full table | Samples with a full switch % | SmartTime cost (installs + evictions) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 0.0 ± 0.0 | 211713 ± 25682 | 0 ± 0 | 45072 ± 12912 | 100.0 ± 0.0 | 18345 ± 3809 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 86.1 ± 2.6 | 154252 ± 56859 | 0 ± 0 | 18135 ± 2785 | 93.7 ± 2.8 | 8617 ± 5101 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 17.4 ± 41.4 | 242 ± 1043 | 12518 ± 4269 | 12518 ± 4269 | 100.0 ± 0.0 | 198402 ± 34726 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 80.5 ± 1.7 | 15 ± 63 | 478 ± 33 | 478 ± 33 | 87.2 ± 5.5 | 11331 ± 5757 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 0 of 240 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 0 of 240 | 86.1 ± 2.6 | 0 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 0 of 240 | 17.4 ± 41.4 | 0 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 0 of 240 | 80.5 ± 1.7 | 0 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 7 | 240 | 1573.61 / 33212.08 | 7688 | 98.7 | 240 | 0.0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 7 | 0 | 47.81 / 568.79 | 4336 | 89.6 | 236 | 87.1 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 7 | 75 | 529.22 / 26082.23 | 5549 | 93.4 | 240 | 33.2 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 7 | 0 | 44.68 / 303.53 | 435 | 14.6 | 227 | 80.6 |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 8 | 264 | 2760.96 / 37695.43 | 7221 | 98.2 | 240 | 0.0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 8 | 0 | 66.13 / 6276.31 | 5787 | 94.4 | 236 | 85.1 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 8 | 87 | 1019.79 / 29164.03 | 6049 | 97.8 | 240 | 19.1 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 8 | 0 | 49.02 / 350.95 | 287 | 10.5 | 231 | 79.8 |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 9 | 243 | 1188.41 / 34708.14 | 7307 | 97.9 | 240 | 0.0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 9 | 0 | 70.38 / 5528.55 | 5649 | 93.6 | 239 | 86.1 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 9 | 139 | 1448.49 / 33982.75 | 6366 | 95.8 | 240 | 0.0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 9 | 0 | 56.91 / 345.78 | 341 | 12.4 | 224 | 81.2 |
