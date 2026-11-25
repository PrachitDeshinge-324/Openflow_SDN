# Realistic traffic results (B-cap12-fattree)

Testbed: Linux Nisarg 6.18.58.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Tue Oct 27 00:24:11 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet
CPU: AMD Ryzen AI 7 350 w/ Radeon 860M, 16 threads | code: commit e9d41c2984


**Every value is the mean of 3 runs (seeds 7 to 9, a new flow schedule each time) ± the half-width of its 95% confidence interval (Student's t).**

## Traffic generated (identical for every controller within one seed)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | DCTCP, SIGCOMM 2010 / pFabric web search workload | 1124 ± 70 | 37.5 ± 2.3 | 476.5 ± 46.1 (30%) | 15 ± 12 | 95 ± 4% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 925 ± 158 / 199 ± 89 | 5931.14 ± 2944.04 / 1390.92 ± 1893.56 / 35386.40 ± 3542.58 | 11420.5 ± 2386.6 | 17368.9 ± 18258.8 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 1124 ± 70 / 0 ± 0 | 135.55 ± 149.62 / 58.50 ± 42.41 / 1524.66 ± 2782.30 | 3031.2 ± 1457.9 | 12266.0 ± 13073.3 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 1090 ± 80 / 33 ± 50 | 2091.95 ± 1261.86 / 388.56 ± 433.88 / 17428.59 ± 4728.55 | 10083.0 ± 3261.3 | 20407.0 ± 13138.9 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 1124 ± 70 / 0 ± 0 | 69.02 ± 21.20 / 49.71 ± 13.72 / 317.72 ± 97.85 | 2631.5 ± 659.9 | 11295.7 ± 9836.4 |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 10441 ± 77 | 10437 ± 77 | 98.7 ± 1.5 | 240 ± 0 | 12 ± 0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 6749 ± 3308 | 6744 ± 3308 | 90.8 ± 13.9 | 237 ± 4 | 12 ± 0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 7521 ± 1762 | 7941 ± 1863 | 95.4 ± 8.3 | 240 ± 0 | 12 ± 0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 300 ± 15 | 311 ± 9 | 9.6 ± 0.3 | 229 ± 13 | 12 ± 0 |

## Capped tables (--table-cap 12 rules per switch, Open vSwitch refuses beyond it)

| Network | Workload | Controller | Hit rate % | Refused installs | Evictions | PACKET_INs at a full table | Samples with a full switch % | SmartTime cost (installs + evictions) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 0.0 ± 0.0 | 300739 ± 9543 | 0 ± 0 | 51342 ± 11372 | 100.0 ± 0.0 | 20806 ± 5358 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 86.3 ± 3.2 | 200942 ± 98589 | 0 ± 0 | 20830 ± 5056 | 100.0 ± 0.0 | 8510 ± 5505 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 34.8 ± 10.1 | 177 ± 763 | 12922 ± 3618 | 12922 ± 3618 | 100.0 ± 0.0 | 241980 ± 66034 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 80.8 ± 3.6 | 0 ± 1 | 461 ± 195 | 461 ± 195 | 92.6 ± 9.2 | 9378 ± 309 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 0 of 240 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 0 of 240 | 86.3 ± 3.2 | 0 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 0 of 240 | 34.8 ± 10.1 | 0 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 0 of 240 | 80.8 ± 3.6 | 0 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 7 | 158 | 796.22 / 33877.06 | 10423 | 99.4 | 240 | 0.0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 7 | 0 | 39.44 / 363.13 | 5217 | 84.4 | 236 | 87.3 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 7 | 34 | 219.46 / 15235.29 | 6767 | 92.1 | 240 | 34.8 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 7 | 0 | 44.09 / 272.43 | 300 | 9.5 | 228 | 81.1 |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 8 | 223 | 2250.14 / 35571.14 | 10423 | 98.4 | 240 | 0.0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 8 | 0 | 63.66 / 2597.77 | 7629 | 94.7 | 237 | 84.9 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 8 | 53 | 568.27 / 18403.58 | 8176 | 98.8 | 240 | 30.8 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 8 | 0 | 49.90 / 336.78 | 294 | 9.6 | 234 | 79.3 |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 9 | 216 | 1126.41 / 36710.99 | 10477 | 98.3 | 240 | 0.0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 9 | 0 | 72.39 / 1613.08 | 7400 | 93.3 | 239 | 86.9 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 9 | 13 | 377.95 / 18646.90 | 7620 | 95.2 | 240 | 38.9 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 9 | 0 | 55.13 / 343.95 | 306 | 9.7 | 224 | 82.2 |
