# Realistic traffic results (traffic-20261015-233914)

Testbed: Linux Harikrushna 6.18.33.2-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Thu Jun 18 21:54:43 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet

**Every value is the mean of 5 runs (seeds 7 to 11, a new flow schedule each time) ± the half-width of its 95% confidence interval (Student's t).**

## Traffic generated (identical for every controller within one seed)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | DCTCP, SIGCOMM 2010 / pFabric web search workload | 1121 ± 27 | 37.4 ± 0.9 | 477.6 ± 19.1 (30%) | 14 ± 6 | 92 ± 10% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive (learning + spanning tree) | 1116 ± 34 / 5 ± 15 | 137.05 ± 48.59 / 110.83 ± 38.01 / 539.67 ± 231.95 | 5383.2 ± 2058.9 | 16058.2 ± 7483.5 |
| fattree-k4 | websearch | Reactive, long timeouts | 1116 ± 34 / 5 ± 15 | 137.64 ± 45.57 / 111.71 ± 36.11 / 555.93 ± 208.50 | 5429.8 ± 2085.9 | 16059.2 ± 7044.7 |
| fattree-k4 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 1121 ± 27 / 0 ± 0 | 78.11 ± 9.76 / 59.30 ± 6.63 / 308.62 ± 47.16 | 2360.1 ± 481.7 | 9317.5 ± 4826.5 |
| fattree-k4 | websearch | Hybrid, counter keeps top 10% of pairs | 1121 ± 27 / 0 ± 0 | 62.43 ± 8.79 / 42.79 ± 5.97 / 291.30 ± 36.46 | 2332.5 ± 458.5 | 9251.6 ± 4419.3 |
| fattree-k4 | websearch | Hybrid, counter keeps top 25% of pairs | 1121 ± 27 / 0 ± 0 | 59.60 ± 9.56 / 38.17 ± 5.08 / 297.43 ± 50.41 | 2377.2 ± 488.4 | 9409.7 ± 4663.3 |
| fattree-k4 | websearch | Hybrid, counter keeps top 50% of pairs | 1121 ± 27 / 0 ± 0 | 57.64 ± 7.57 / 34.95 ± 5.14 / 301.95 ± 39.59 | 2394.2 ± 429.2 | 9218.8 ± 4781.3 |
| fattree-k4 | websearch | Oracle, busiest 10% of pairs (upper bound) | 1121 ± 27 / 0 ± 0 | 59.35 ± 9.91 / 38.81 ± 5.20 / 285.68 ± 44.77 | 2325.7 ± 532.3 | 9521.4 ± 4513.5 |
| fattree-k4 | websearch | Oracle, busiest 25% of pairs (upper bound) | 1121 ± 27 / 0 ± 0 | 56.86 ± 9.29 / 34.01 ± 5.20 / 300.62 ± 47.13 | 2346.3 ± 475.4 | 9391.5 ± 4726.5 |
| fattree-k4 | websearch | Oracle, busiest 50% of pairs (upper bound) | 1121 ± 27 / 0 ± 0 | 54.96 ± 8.10 / 31.63 ± 5.34 / 297.52 ± 26.23 | 2372.8 ± 410.6 | 9024.4 ± 4970.0 |
| fattree-k4 | websearch | Proactive (ECMP) | 1121 ± 27 / 0 ± 0 | 53.23 ± 9.40 / 28.62 ± 5.20 / 304.18 ± 55.59 | 2362.8 ± 459.0 | 9332.9 ± 4852.4 |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive (learning + spanning tree) | 455 ± 42 | 436 ± 42 | 25.6 ± 2.0 | 4406 ± 569 | 757 ± 144 |
| fattree-k4 | websearch | Reactive, long timeouts | 450 ± 35 | 432 ± 37 | 25.8 ± 1.0 | 10643 ± 969 | 1786 ± 285 |
| fattree-k4 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 492 ± 55 | 488 ± 55 | 25.8 ± 2.3 | 3752 ± 428 | 372 ± 55 |
| fattree-k4 | websearch | Hybrid, counter keeps top 10% of pairs | 259 ± 26 | 263 ± 26 | 13.8 ± 0.6 | 1901 ± 104 | 142 ± 17 |
| fattree-k4 | websearch | Hybrid, counter keeps top 25% of pairs | 180 ± 14 | 199 ± 16 | 10.1 ± 0.5 | 1569 ± 89 | 107 ± 10 |
| fattree-k4 | websearch | Hybrid, counter keeps top 50% of pairs | 123 ± 15 | 157 ± 19 | 7.4 ± 0.6 | 1517 ± 84 | 99 ± 9 |
| fattree-k4 | websearch | Oracle, busiest 10% of pairs (upper bound) | 231 ± 19 | 226 ± 19 | 11.8 ± 0.5 | 1714 ± 182 | 124 ± 12 |
| fattree-k4 | websearch | Oracle, busiest 25% of pairs (upper bound) | 139 ± 11 | 134 ± 11 | 7.1 ± 0.3 | 1221 ± 86 | 82 ± 7 |
| fattree-k4 | websearch | Oracle, busiest 50% of pairs (upper bound) | 63 ± 5 | 59 ± 5 | 3.3 ± 0.2 | 984 ± 57 | 62 ± 2 |
| fattree-k4 | websearch | Proactive (ECMP) | 0 ± 0 | 0 ± 0 | 0.2 ± 0.0 | 1072 ± 0 | 58 ± 0 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 0 of 240 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | Hybrid, counter keeps top 10% of pairs | 24 of 240 | 51.1 ± 1.6 | 52 ± 6 | 21 ± 6 |
| fattree-k4 | websearch | Hybrid, counter keeps top 25% of pairs | 60 of 240 | 65.8 ± 1.4 | 118 ± 8 | 42 ± 12 |
| fattree-k4 | websearch | Hybrid, counter keeps top 50% of pairs | 120 of 240 | 77.4 ± 1.8 | 198 ± 12 | 56 ± 9 |
| fattree-k4 | websearch | Oracle, busiest 10% of pairs (upper bound) | 24 of 240 | 56.2 ± 1.3 | 24 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | Oracle, busiest 25% of pairs (upper bound) | 60 of 240 | 73.7 ± 1.2 | 60 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | Oracle, busiest 50% of pairs (upper bound) | 120 of 240 | 88.3 ± 0.7 | 120 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive (learning + spanning tree) | 7 | 0 | 89.23 / 457.61 | 486 | 27.1 | 4452 | - |
| fattree-k4 | websearch | Reactive, long timeouts | 7 | 0 | 88.27 / 498.22 | 478 | 27.0 | 10911 | - |
| fattree-k4 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 7 | 0 | 57.53 / 296.41 | 495 | 25.8 | 3833 | 0.0 |
| fattree-k4 | websearch | Hybrid, counter keeps top 10% of pairs | 7 | 0 | 40.14 / 285.69 | 259 | 13.7 | 1816 | 52.2 |
| fattree-k4 | websearch | Hybrid, counter keeps top 25% of pairs | 7 | 0 | 35.48 / 271.91 | 169 | 10.0 | 1564 | 66.7 |
| fattree-k4 | websearch | Hybrid, counter keeps top 50% of pairs | 7 | 0 | 33.10 / 276.78 | 112 | 6.8 | 1497 | 79.0 |
| fattree-k4 | websearch | Oracle, busiest 10% of pairs (upper bound) | 7 | 0 | 35.45 / 277.95 | 223 | 11.8 | 1598 | 57.2 |
| fattree-k4 | websearch | Oracle, busiest 25% of pairs (upper bound) | 7 | 0 | 31.96 / 276.62 | 133 | 6.9 | 1206 | 74.7 |
| fattree-k4 | websearch | Oracle, busiest 50% of pairs (upper bound) | 7 | 0 | 28.37 / 290.56 | 62 | 3.3 | 972 | 88.8 |
| fattree-k4 | websearch | Proactive (ECMP) | 7 | 0 | 26.15 / 299.54 | 0 | 0.2 | 1072 | - |
| fattree-k4 | websearch | Reactive (learning + spanning tree) | 8 | 27 | 155.24 / 807.40 | 488 | 26.2 | 4934 | - |
| fattree-k4 | websearch | Reactive, long timeouts | 8 | 27 | 151.76 / 788.04 | 476 | 25.6 | 11249 | - |
| fattree-k4 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 8 | 0 | 56.31 / 317.79 | 552 | 27.4 | 4016 | 0.0 |
| fattree-k4 | websearch | Hybrid, counter keeps top 10% of pairs | 8 | 0 | 40.02 / 318.66 | 290 | 14.6 | 2033 | 49.1 |
| fattree-k4 | websearch | Hybrid, counter keeps top 25% of pairs | 8 | 0 | 36.13 / 327.87 | 195 | 10.2 | 1660 | 64.5 |
| fattree-k4 | websearch | Hybrid, counter keeps top 50% of pairs | 8 | 0 | 30.00 / 324.97 | 141 | 8.0 | 1610 | 75.3 |
| fattree-k4 | websearch | Oracle, busiest 10% of pairs (upper bound) | 8 | 0 | 38.14 / 298.95 | 254 | 12.5 | 1873 | 55.0 |
| fattree-k4 | websearch | Oracle, busiest 25% of pairs (upper bound) | 8 | 0 | 30.39 / 330.80 | 152 | 7.3 | 1298 | 72.5 |
| fattree-k4 | websearch | Oracle, busiest 50% of pairs (upper bound) | 8 | 0 | 28.33 / 307.16 | 70 | 3.3 | 1018 | 87.9 |
| fattree-k4 | websearch | Proactive (ECMP) | 8 | 0 | 23.86 / 328.57 | 0 | 0.2 | 1072 | - |
| fattree-k4 | websearch | Reactive (learning + spanning tree) | 9 | 0 | 112.64 / 607.84 | 444 | 25.1 | 4475 | - |
| fattree-k4 | websearch | Reactive, long timeouts | 9 | 0 | 113.46 / 631.70 | 446 | 24.8 | 10844 | - |
| fattree-k4 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 9 | 0 | 65.44 / 366.17 | 501 | 26.5 | 3919 | 0.0 |
| fattree-k4 | websearch | Hybrid, counter keeps top 10% of pairs | 9 | 0 | 50.48 / 324.74 | 254 | 13.4 | 1889 | 50.9 |
| fattree-k4 | websearch | Hybrid, counter keeps top 25% of pairs | 9 | 0 | 45.37 / 350.47 | 173 | 9.5 | 1521 | 67.3 |
| fattree-k4 | websearch | Hybrid, counter keeps top 50% of pairs | 9 | 0 | 40.81 / 334.14 | 111 | 7.1 | 1471 | 78.7 |
| fattree-k4 | websearch | Oracle, busiest 10% of pairs (upper bound) | 9 | 0 | 45.11 / 334.65 | 220 | 11.3 | 1538 | 56.8 |
| fattree-k4 | websearch | Oracle, busiest 25% of pairs (upper bound) | 9 | 0 | 40.71 / 333.36 | 130 | 6.8 | 1142 | 74.8 |
| fattree-k4 | websearch | Oracle, busiest 50% of pairs (upper bound) | 9 | 0 | 38.68 / 321.12 | 58 | 3.2 | 920 | 89.1 |
| fattree-k4 | websearch | Proactive (ECMP) | 9 | 0 | 34.69 / 341.01 | 0 | 0.2 | 1072 | - |
| fattree-k4 | websearch | Reactive (learning + spanning tree) | 10 | 0 | 76.12 / 302.41 | 407 | 23.1 | 3668 | - |
| fattree-k4 | websearch | Reactive, long timeouts | 10 | 0 | 79.52 / 334.44 | 409 | 25.5 | 9274 | - |
| fattree-k4 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 10 | 0 | 52.96 / 262.12 | 427 | 22.6 | 3149 | 0.0 |
| fattree-k4 | websearch | Hybrid, counter keeps top 10% of pairs | 10 | 0 | 38.82 / 259.98 | 259 | 13.6 | 1920 | 51.6 |
| fattree-k4 | websearch | Hybrid, counter keeps top 25% of pairs | 10 | 0 | 36.38 / 252.27 | 190 | 10.0 | 1618 | 65.1 |
| fattree-k4 | websearch | Hybrid, counter keeps top 50% of pairs | 10 | 0 | 33.72 / 260.30 | 126 | 7.5 | 1561 | 76.9 |
| fattree-k4 | websearch | Oracle, busiest 10% of pairs (upper bound) | 10 | 0 | 34.82 / 235.16 | 238 | 11.8 | 1841 | 56.9 |
| fattree-k4 | websearch | Oracle, busiest 25% of pairs (upper bound) | 10 | 0 | 31.56 / 246.18 | 140 | 7.0 | 1288 | 73.3 |
| fattree-k4 | websearch | Oracle, busiest 50% of pairs (upper bound) | 10 | 0 | 30.22 / 265.12 | 63 | 3.3 | 1037 | 87.7 |
| fattree-k4 | websearch | Proactive (ECMP) | 10 | 0 | 27.79 / 228.75 | 0 | 0.2 | 1072 | - |
| fattree-k4 | websearch | Reactive (learning + spanning tree) | 11 | 0 | 120.93 / 523.06 | 450 | 26.4 | 4502 | - |
| fattree-k4 | websearch | Reactive, long timeouts | 11 | 0 | 125.51 / 527.25 | 441 | 26.1 | 10935 | - |
| fattree-k4 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 11 | 0 | 64.23 / 300.62 | 487 | 26.5 | 3842 | 0.0 |
| fattree-k4 | websearch | Hybrid, counter keeps top 10% of pairs | 11 | 0 | 44.51 / 267.42 | 232 | 13.7 | 1847 | 51.9 |
| fattree-k4 | websearch | Hybrid, counter keeps top 25% of pairs | 11 | 0 | 37.48 / 284.63 | 176 | 10.6 | 1483 | 65.5 |
| fattree-k4 | websearch | Hybrid, counter keeps top 50% of pairs | 11 | 0 | 37.12 / 313.55 | 124 | 7.7 | 1445 | 77.2 |
| fattree-k4 | websearch | Oracle, busiest 10% of pairs (upper bound) | 11 | 0 | 40.50 / 281.71 | 217 | 11.7 | 1719 | 55.2 |
| fattree-k4 | websearch | Oracle, busiest 25% of pairs (upper bound) | 11 | 0 | 35.44 / 316.16 | 137 | 7.4 | 1172 | 73.2 |
| fattree-k4 | websearch | Oracle, busiest 50% of pairs (upper bound) | 11 | 0 | 32.57 / 303.63 | 64 | 3.5 | 974 | 88.1 |
| fattree-k4 | websearch | Proactive (ECMP) | 11 | 0 | 30.63 / 323.04 | 0 | 0.2 | 1072 | - |
