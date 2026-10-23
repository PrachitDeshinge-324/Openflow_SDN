# Realistic traffic results (traffic-20261023-070549)

Testbed: Linux Harikrushna 6.18.33.2-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Thu Jun 18 21:54:43 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 5% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet

**Every value is the mean of 3 runs (seeds 7 to 9, a new flow schedule each time) ± the half-width of its 95% confidence interval (Student's t).**

## Traffic generated (identical for every controller within one seed)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k6 | websearch | DCTCP, SIGCOMM 2010 / pFabric web search workload | 642 ± 114 | 21.4 ± 3.8 | 270.8 ± 73.3 (5%) | 10 ± 5 | 98 ± 2% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| fattree-k6 | websearch | Reactive (learning + spanning tree) | 642 ± 114 / 0 ± 0 | 95.96 ± 34.70 / 85.95 ± 39.69 / 262.64 ± 85.26 | 866.7 ± 633.1 | 3953.7 ± 2055.6 |
| fattree-k6 | websearch | Reactive, long timeouts | 642 ± 114 / 0 ± 0 | 100.73 ± 24.97 / 88.01 ± 25.67 / 288.68 ± 72.03 | 885.8 ± 642.1 | 3974.3 ± 2211.9 |
| fattree-k6 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 642 ± 114 / 0 ± 0 | 57.91 ± 21.83 / 52.45 ± 22.39 / 174.79 ± 88.09 | 361.4 ± 142.5 | 1770.6 ± 83.4 |
| fattree-k6 | websearch | Reactive on shortest paths, pair rules | 642 ± 114 / 0 ± 0 | 24.70 ± 8.84 / 21.52 ± 11.31 / 139.38 ± 19.33 | 321.8 ± 115.5 | 1739.4 ± 36.0 |
| fattree-k6 | websearch | Reactive on shortest paths, destination rules | 642 ± 114 / 0 ± 0 | 20.48 ± 7.66 / 13.36 ± 7.42 / 150.07 ± 67.81 | 316.0 ± 110.9 | 1717.9 ± 51.3 |
| fattree-k6 | websearch | Hybrid, counter keeps top 2% of pairs | 642 ± 114 / 0 ± 0 | 32.38 ± 17.13 / 29.11 ± 18.68 / 138.64 ± 22.76 | 330.7 ± 124.9 | 1734.6 ± 73.5 |
| fattree-k6 | websearch | Hybrid, counter keeps top 5% of pairs | 642 ± 114 / 0 ± 0 | 28.11 ± 12.08 / 24.69 ± 12.34 / 125.78 ± 2.31 | 326.7 ± 119.8 | 1733.7 ± 68.0 |
| fattree-k6 | websearch | Hybrid, counter keeps top 10% of pairs | 642 ± 114 / 0 ± 0 | 27.34 ± 9.80 / 22.56 ± 9.59 / 140.94 ± 35.76 | 326.5 ± 114.6 | 1731.5 ± 72.6 |
| fattree-k6 | websearch | Oracle, busiest 2% of pairs (upper bound) | 642 ± 114 / 0 ± 0 | 25.29 ± 10.37 / 21.95 ± 9.51 / 132.67 ± 34.79 | 326.1 ± 114.2 | 1735.6 ± 83.6 |
| fattree-k6 | websearch | Oracle, busiest 5% of pairs (upper bound) | 642 ± 114 / 0 ± 0 | 20.94 ± 8.93 / 13.39 ± 18.59 / 125.94 ± 4.09 | 316.6 ± 107.0 | 1731.4 ± 46.4 |
| fattree-k6 | websearch | Oracle, busiest 10% of pairs (upper bound) | 642 ± 114 / 0 ± 0 | 18.23 ± 6.81 / 8.10 ± 4.24 / 133.20 ± 54.07 | 317.8 ± 110.2 | 1733.3 ± 21.1 |
| fattree-k6 | websearch | Proactive (ECMP) | 642 ± 114 / 0 ± 0 | 13.14 ± 3.48 / 4.95 ± 0.80 / 131.63 ± 43.98 | 310.8 ± 116.6 | 1729.1 ± 52.6 |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k6 | websearch | Reactive (learning + spanning tree) | 345 ± 47 | 334 ± 43 | 22.3 ± 5.1 | 2977 ± 732 | 396 ± 99 |
| fattree-k6 | websearch | Reactive, long timeouts | 345 ± 23 | 329 ± 35 | 22.7 ± 1.4 | 8023 ± 1003 | 1061 ± 137 |
| fattree-k6 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 371 ± 65 | 364 ± 65 | 20.4 ± 5.6 | 2165 ± 378 | 136 ± 82 |
| fattree-k6 | websearch | Reactive on shortest paths, pair rules | 213 ± 35 | 205 ± 35 | 9.4 ± 2.9 | 1249 ± 253 | 50 ± 10 |
| fattree-k6 | websearch | Reactive on shortest paths, destination rules | 153 ± 15 | 146 ± 15 | 6.3 ± 2.2 | 766 ± 87 | 25 ± 1 |
| fattree-k6 | websearch | Hybrid, counter keeps top 2% of pairs | 231 ± 64 | 249 ± 62 | 12.9 ± 7.7 | 1583 ± 220 | 71 ± 23 |
| fattree-k6 | websearch | Hybrid, counter keeps top 5% of pairs | 212 ± 90 | 264 ± 108 | 12.0 ± 5.3 | 1840 ± 338 | 80 ± 7 |
| fattree-k6 | websearch | Hybrid, counter keeps top 10% of pairs | 189 ± 57 | 288 ± 63 | 12.0 ± 3.9 | 2368 ± 420 | 87 ± 8 |
| fattree-k6 | websearch | Oracle, busiest 2% of pairs (upper bound) | 194 ± 52 | 187 ± 52 | 9.4 ± 4.1 | 1363 ± 269 | 54 ± 13 |
| fattree-k6 | websearch | Oracle, busiest 5% of pairs (upper bound) | 141 ± 47 | 134 ± 47 | 6.9 ± 3.1 | 1430 ± 260 | 56 ± 14 |
| fattree-k6 | websearch | Oracle, busiest 10% of pairs (upper bound) | 94 ± 48 | 87 ± 47 | 4.8 ± 3.0 | 2028 ± 109 | 67 ± 8 |
| fattree-k6 | websearch | Proactive (ECMP) | 0 ± 0 | 0 ± 0 | 0.4 ± 0.1 | 13230 ± 0 | 312 ± 0 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| fattree-k6 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 0 of 2862 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| fattree-k6 | websearch | Reactive on shortest paths, pair rules | 0 of 2862 | 50.8 ± 5.0 | 0 ± 0 | 0 ± 0 |
| fattree-k6 | websearch | Reactive on shortest paths, destination rules | 0 of 2862 | 59.3 ± 2.4 | 0 ± 0 | 0 ± 0 |
| fattree-k6 | websearch | Hybrid, counter keeps top 2% of pairs | 57 of 2862 | 40.0 ± 7.0 | 119 ± 14 | 53 ± 17 |
| fattree-k6 | websearch | Hybrid, counter keeps top 5% of pairs | 143 of 2862 | 46.9 ± 9.5 | 275 ± 78 | 127 ± 65 |
| fattree-k6 | websearch | Hybrid, counter keeps top 10% of pairs | 286 of 2862 | 51.1 ± 7.2 | 500 ± 23 | 214 ± 23 |
| fattree-k6 | websearch | Oracle, busiest 2% of pairs (upper bound) | 57 of 2862 | 50.3 ± 7.1 | 57 ± 0 | 0 ± 0 |
| fattree-k6 | websearch | Oracle, busiest 5% of pairs (upper bound) | 143 of 2862 | 65.5 ± 9.6 | 143 ± 0 | 0 ± 0 |
| fattree-k6 | websearch | Oracle, busiest 10% of pairs (upper bound) | 286 of 2862 | 77.8 ± 8.1 | 286 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k6 | websearch | Reactive (learning + spanning tree) | 7 | 0 | 101.43 / 269.96 | 329 | 22.9 | 3079 | - |
| fattree-k6 | websearch | Reactive, long timeouts | 7 | 0 | 99.88 / 317.57 | 335 | 23.1 | 8054 | - |
| fattree-k6 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 7 | 0 | 44.95 / 142.86 | 353 | 18.5 | 2124 | 0.0 |
| fattree-k6 | websearch | Reactive on shortest paths, pair rules | 7 | 0 | 20.77 / 144.16 | 207 | 8.9 | 1178 | 51.1 |
| fattree-k6 | websearch | Reactive on shortest paths, destination rules | 7 | 0 | 13.21 / 127.99 | 151 | 6.3 | 748 | 58.7 |
| fattree-k6 | websearch | Hybrid, counter keeps top 2% of pairs | 7 | 0 | 24.93 / 129.28 | 217 | 11.2 | 1527 | 41.4 |
| fattree-k6 | websearch | Hybrid, counter keeps top 5% of pairs | 7 | 0 | 22.58 / 124.73 | 193 | 10.6 | 1721 | 49.1 |
| fattree-k6 | websearch | Hybrid, counter keeps top 10% of pairs | 7 | 0 | 21.97 / 136.59 | 171 | 11.8 | 2243 | 52.4 |
| fattree-k6 | websearch | Oracle, busiest 2% of pairs (upper bound) | 7 | 0 | 19.98 / 126.38 | 181 | 8.6 | 1317 | 51.9 |
| fattree-k6 | websearch | Oracle, busiest 5% of pairs (upper bound) | 7 | 0 | 10.21 / 127.71 | 131 | 6.5 | 1388 | 67.0 |
| fattree-k6 | websearch | Oracle, busiest 10% of pairs (upper bound) | 7 | 0 | 7.74 / 113.39 | 86 | 4.5 | 2050 | 78.6 |
| fattree-k6 | websearch | Proactive (ECMP) | 7 | 0 | 4.94 / 117.95 | 0 | 0.4 | 13230 | - |
| fattree-k6 | websearch | Reactive (learning + spanning tree) | 8 | 0 | 69.52 / 225.24 | 341 | 20.0 | 2645 | - |
| fattree-k6 | websearch | Reactive, long timeouts | 8 | 0 | 83.06 / 259.58 | 353 | 23.0 | 7604 | - |
| fattree-k6 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 8 | 0 | 49.95 / 168.56 | 359 | 19.8 | 2037 | 0.0 |
| fattree-k6 | websearch | Reactive on shortest paths, pair rules | 8 | 0 | 17.38 / 130.40 | 202 | 8.6 | 1204 | 52.6 |
| fattree-k6 | websearch | Reactive on shortest paths, destination rules | 8 | 0 | 10.46 / 141.62 | 149 | 5.4 | 743 | 60.4 |
| fattree-k6 | websearch | Hybrid, counter keeps top 2% of pairs | 8 | 0 | 24.62 / 139.06 | 216 | 11.0 | 1537 | 41.7 |
| fattree-k6 | websearch | Hybrid, counter keeps top 5% of pairs | 8 | 0 | 21.13 / 126.49 | 190 | 11.0 | 1810 | 49.0 |
| fattree-k6 | websearch | Hybrid, counter keeps top 10% of pairs | 8 | 0 | 19.03 / 129.22 | 181 | 10.5 | 2300 | 53.1 |
| fattree-k6 | websearch | Oracle, busiest 2% of pairs (upper bound) | 8 | 0 | 19.50 / 122.92 | 183 | 8.4 | 1286 | 52.1 |
| fattree-k6 | websearch | Oracle, busiest 5% of pairs (upper bound) | 8 | 0 | 8.02 / 124.45 | 130 | 5.9 | 1353 | 68.4 |
| fattree-k6 | websearch | Oracle, busiest 10% of pairs (upper bound) | 8 | 0 | 6.61 / 129.71 | 80 | 3.7 | 1978 | 80.6 |
| fattree-k6 | websearch | Proactive (ECMP) | 8 | 0 | 4.63 / 125.32 | 0 | 0.4 | 13230 | - |
| fattree-k6 | websearch | Reactive (learning + spanning tree) | 9 | 0 | 86.90 / 292.70 | 366 | 23.9 | 3207 | - |
| fattree-k6 | websearch | Reactive, long timeouts | 9 | 0 | 81.07 / 288.90 | 347 | 22.1 | 8410 | - |
| fattree-k6 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 9 | 0 | 62.45 / 212.95 | 401 | 22.9 | 2333 | 0.0 |
| fattree-k6 | websearch | Reactive on shortest paths, pair rules | 9 | 0 | 26.39 / 143.58 | 229 | 10.7 | 1366 | 48.6 |
| fattree-k6 | websearch | Reactive on shortest paths, destination rules | 9 | 0 | 16.42 / 180.59 | 160 | 7.2 | 806 | 58.7 |
| fattree-k6 | websearch | Hybrid, counter keeps top 2% of pairs | 9 | 0 | 37.79 / 147.59 | 261 | 16.5 | 1685 | 36.7 |
| fattree-k6 | websearch | Hybrid, counter keeps top 5% of pairs | 9 | 0 | 30.36 / 126.11 | 254 | 14.5 | 1988 | 42.4 |
| fattree-k6 | websearch | Hybrid, counter keeps top 10% of pairs | 9 | 0 | 26.68 / 157.01 | 215 | 13.6 | 2560 | 47.8 |
| fattree-k6 | websearch | Oracle, busiest 2% of pairs (upper bound) | 9 | 0 | 26.36 / 148.72 | 218 | 11.3 | 1487 | 47.1 |
| fattree-k6 | websearch | Oracle, busiest 5% of pairs (upper bound) | 9 | 0 | 21.94 / 125.67 | 163 | 8.3 | 1549 | 61.2 |
| fattree-k6 | websearch | Oracle, busiest 10% of pairs (upper bound) | 9 | 0 | 9.96 / 156.50 | 116 | 6.1 | 2057 | 74.2 |
| fattree-k6 | websearch | Proactive (ECMP) | 9 | 0 | 5.28 / 151.63 | 0 | 0.4 | 13230 | - |
