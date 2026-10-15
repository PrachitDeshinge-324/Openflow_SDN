# Realistic traffic results (traffic-20261015-213728)

Testbed: Linux Harikrushna 6.18.33.2-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Thu Jun 18 21:54:43 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet

## Traffic generated (identical for every controller)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | DCTCP, SIGCOMM 2010 / pFabric web search workload | 1156 | 38.5 | 497.8 (31%) | 21 | 94% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive (learning + spanning tree) | 1156 / 0 | 160.27 / 142.68 / 552.23 | 4953.4 | 14727.7 |
| fattree-k4 | websearch | Reactive, long timeouts | 1156 / 0 | 160.76 / 141.52 / 617.58 | 4737.2 | 15522.1 |
| fattree-k4 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 1156 / 0 | 115.12 / 103.94 / 347.08 | 2433.8 | 8085.3 |
| fattree-k4 | websearch | Hybrid, counter keeps top 10% of pairs | 1156 / 0 | 77.20 / 64.92 / 315.69 | 2468.9 | 8345.5 |
| fattree-k4 | websearch | Hybrid, counter keeps top 25% of pairs | 1156 / 0 | 66.75 / 55.41 / 297.90 | 2527.4 | 7848.2 |
| fattree-k4 | websearch | Hybrid, counter keeps top 50% of pairs | 1156 / 0 | 61.93 / 46.63 / 306.55 | 2443.8 | 8223.0 |
| fattree-k4 | websearch | Oracle, busiest 10% of pairs (upper bound) | 1156 / 0 | 74.64 / 61.83 / 332.87 | 2508.6 | 7756.0 |
| fattree-k4 | websearch | Oracle, busiest 25% of pairs (upper bound) | 1156 / 0 | 63.87 / 50.34 / 306.41 | 2534.0 | 7684.7 |
| fattree-k4 | websearch | Oracle, busiest 50% of pairs (upper bound) | 1156 / 0 | 54.72 / 37.41 / 318.17 | 2490.4 | 8121.1 |
| fattree-k4 | websearch | Proactive (ECMP) | 1156 / 0 | 51.64 / 26.28 / 295.76 | 2596.0 | 7383.8 |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive (learning + spanning tree) | 509 | 484 | 44.2 | 4398 | 682 |
| fattree-k4 | websearch | Reactive, long timeouts | 468 | 442 | 41.2 | 10912 | 1682 |
| fattree-k4 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 514 | 510 | 42.4 | 3843 | 378 |
| fattree-k4 | websearch | Hybrid, counter keeps top 10% of pairs | 288 | 293 | 29.8 | 1865 | 134 |
| fattree-k4 | websearch | Hybrid, counter keeps top 25% of pairs | 180 | 201 | 21.4 | 1525 | 110 |
| fattree-k4 | websearch | Hybrid, counter keeps top 50% of pairs | 127 | 164 | 17.2 | 1624 | 102 |
| fattree-k4 | websearch | Oracle, busiest 10% of pairs (upper bound) | 226 | 222 | 25.7 | 1610 | 118 |
| fattree-k4 | websearch | Oracle, busiest 25% of pairs (upper bound) | 132 | 128 | 15.5 | 1214 | 76 |
| fattree-k4 | websearch | Oracle, busiest 50% of pairs (upper bound) | 60 | 56 | 7.7 | 972 | 64 |
| fattree-k4 | websearch | Proactive (ECMP) | 0 | 0 | 0.4 | 1072 | 58 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 0 of 240 | 0.0 | 0 | 0 |
| fattree-k4 | websearch | Hybrid, counter keeps top 10% of pairs | 24 of 240 | 51.5 | 52 | 22 |
| fattree-k4 | websearch | Hybrid, counter keeps top 25% of pairs | 60 of 240 | 67.6 | 118 | 43 |
| fattree-k4 | websearch | Hybrid, counter keeps top 50% of pairs | 120 of 240 | 78.5 | 207 | 68 |
| fattree-k4 | websearch | Oracle, busiest 10% of pairs (upper bound) | 24 of 240 | 57.2 | 24 | 0 |
| fattree-k4 | websearch | Oracle, busiest 25% of pairs (upper bound) | 60 of 240 | 74.7 | 60 | 0 |
| fattree-k4 | websearch | Oracle, busiest 50% of pairs (upper bound) | 120 of 240 | 88.8 | 120 | 0 |
