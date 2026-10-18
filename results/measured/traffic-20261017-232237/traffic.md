# Realistic traffic results (traffic-20261017-232237)

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
| fattree-k6 | websearch | Reactive (learning + spanning tree) | 642 ± 114 / 0 ± 0 | 111.11 ± 51.70 / 99.57 ± 48.49 / 311.03 ± 227.47 | 911.1 ± 697.4 | 4061.2 ± 2504.2 |
| fattree-k6 | websearch | Reactive, long timeouts | 642 ± 114 / 0 ± 0 | 105.75 ± 27.77 / 93.73 ± 33.02 / 300.12 ± 23.15 | 904.8 ± 618.4 | 3966.1 ± 2219.2 |
| fattree-k6 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 642 ± 114 / 0 ± 0 | 57.16 ± 3.90 / 51.45 ± 7.08 / 183.90 ± 27.98 | 356.7 ± 115.8 | 1765.9 ± 70.8 |
| fattree-k6 | websearch | Hybrid, counter keeps top 2% of pairs | 642 ± 114 / 0 ± 0 | 33.69 ± 9.54 / 31.29 ± 7.91 / 138.24 ± 39.03 | 335.3 ± 120.9 | 1738.9 ± 70.0 |
| fattree-k6 | websearch | Hybrid, counter keeps top 5% of pairs | 642 ± 114 / 0 ± 0 | 30.02 ± 8.07 / 26.85 ± 8.19 / 130.72 ± 5.21 | 328.8 ± 114.7 | 1733.3 ± 82.9 |
| fattree-k6 | websearch | Hybrid, counter keeps top 10% of pairs | 642 ± 114 / 0 ± 0 | 29.17 ± 16.70 / 24.98 ± 15.49 / 146.48 ± 68.68 | 328.5 ± 122.7 | 1737.5 ± 62.8 |
| fattree-k6 | websearch | Oracle, busiest 2% of pairs (upper bound) | 642 ± 114 / 0 ± 0 | 25.93 ± 7.01 / 22.96 ± 9.35 / 127.58 ± 18.35 | 325.2 ± 113.9 | 1734.8 ± 90.5 |
| fattree-k6 | websearch | Oracle, busiest 5% of pairs (upper bound) | 642 ± 114 / 0 ± 0 | 20.96 ± 8.57 / 13.54 ± 17.61 / 132.40 ± 28.76 | 319.7 ± 109.9 | 1734.7 ± 65.3 |
| fattree-k6 | websearch | Oracle, busiest 10% of pairs (upper bound) | 642 ± 114 / 0 ± 0 | 18.30 ± 7.70 / 8.02 ± 4.86 / 132.72 ± 40.33 | 316.4 ± 116.5 | 1717.6 ± 54.0 |
| fattree-k6 | websearch | Proactive (ECMP) | 642 ± 114 / 0 ± 0 | 12.95 ± 3.77 / 4.88 ± 0.63 / 134.68 ± 56.20 | 314.1 ± 110.2 | 1714.0 ± 43.4 |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k6 | websearch | Reactive (learning + spanning tree) | 344 ± 29 | 321 ± 18 | 24.4 ± 7.8 | 3012 ± 660 | 406 ± 82 |
| fattree-k6 | websearch | Reactive, long timeouts | 354 ± 47 | 332 ± 23 | 23.0 ± 1.1 | 8023 ± 1003 | 1061 ± 137 |
| fattree-k6 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 367 ± 50 | 360 ± 50 | 19.3 ± 2.5 | 2160 ± 406 | 138 ± 86 |
| fattree-k6 | websearch | Hybrid, counter keeps top 2% of pairs | 229 ± 59 | 248 ± 61 | 13.2 ± 4.3 | 1589 ± 283 | 69 ± 25 |
| fattree-k6 | websearch | Hybrid, counter keeps top 5% of pairs | 204 ± 60 | 254 ± 74 | 12.2 ± 3.7 | 1819 ± 385 | 77 ± 5 |
| fattree-k6 | websearch | Hybrid, counter keeps top 10% of pairs | 189 ± 59 | 287 ± 66 | 12.9 ± 6.5 | 2374 ± 329 | 89 ± 13 |
| fattree-k6 | websearch | Oracle, busiest 2% of pairs (upper bound) | 195 ± 45 | 188 ± 45 | 9.8 ± 2.7 | 1370 ± 312 | 54 ± 12 |
| fattree-k6 | websearch | Oracle, busiest 5% of pairs (upper bound) | 143 ± 45 | 136 ± 45 | 7.0 ± 2.9 | 1430 ± 241 | 56 ± 14 |
| fattree-k6 | websearch | Oracle, busiest 10% of pairs (upper bound) | 96 ± 46 | 89 ± 46 | 4.7 ± 2.9 | 2019 ± 113 | 68 ± 9 |
| fattree-k6 | websearch | Proactive (ECMP) | 0 ± 0 | 0 ± 0 | 0.4 ± 0.1 | 13230 ± 0 | 312 ± 0 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| fattree-k6 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 0 of 2862 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| fattree-k6 | websearch | Hybrid, counter keeps top 2% of pairs | 57 of 2862 | 40.0 ± 6.8 | 118 ± 27 | 51 ± 35 |
| fattree-k6 | websearch | Hybrid, counter keeps top 5% of pairs | 143 of 2862 | 47.1 ± 9.6 | 273 ± 67 | 125 ± 55 |
| fattree-k6 | websearch | Hybrid, counter keeps top 10% of pairs | 286 of 2862 | 50.9 ± 7.8 | 500 ± 31 | 214 ± 31 |
| fattree-k6 | websearch | Oracle, busiest 2% of pairs (upper bound) | 57 of 2862 | 50.3 ± 7.1 | 57 ± 0 | 0 ± 0 |
| fattree-k6 | websearch | Oracle, busiest 5% of pairs (upper bound) | 143 of 2862 | 65.5 ± 9.6 | 143 ± 0 | 0 ± 0 |
| fattree-k6 | websearch | Oracle, busiest 10% of pairs (upper bound) | 286 of 2862 | 77.8 ± 8.1 | 286 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k6 | websearch | Reactive (learning + spanning tree) | 7 | 0 | 109.07 / 293.79 | 332 | 24.1 | 3059 | - |
| fattree-k6 | websearch | Reactive, long timeouts | 7 | 0 | 108.72 / 291.87 | 341 | 23.5 | 8054 | - |
| fattree-k6 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 7 | 0 | 54.63 / 171.32 | 356 | 19.4 | 2121 | 0.0 |
| fattree-k6 | websearch | Hybrid, counter keeps top 2% of pairs | 7 | 0 | 31.17 / 155.53 | 214 | 12.4 | 1520 | 41.8 |
| fattree-k6 | websearch | Hybrid, counter keeps top 5% of pairs | 7 | 0 | 26.56 / 133.08 | 190 | 11.9 | 1682 | 49.4 |
| fattree-k6 | websearch | Hybrid, counter keeps top 10% of pairs | 7 | 0 | 24.73 / 133.01 | 174 | 12.5 | 2266 | 52.2 |
| fattree-k6 | websearch | Oracle, busiest 2% of pairs (upper bound) | 7 | 0 | 22.66 / 135.79 | 181 | 9.8 | 1279 | 51.9 |
| fattree-k6 | websearch | Oracle, busiest 5% of pairs (upper bound) | 7 | 0 | 10.91 / 127.95 | 136 | 6.5 | 1397 | 67.0 |
| fattree-k6 | websearch | Oracle, busiest 10% of pairs (upper bound) | 7 | 0 | 7.30 / 119.57 | 89 | 4.3 | 2009 | 78.6 |
| fattree-k6 | websearch | Proactive (ECMP) | 7 | 0 | 4.91 / 121.89 | 0 | 0.4 | 13230 | - |
| fattree-k6 | websearch | Reactive (learning + spanning tree) | 8 | 0 | 77.12 / 229.32 | 355 | 21.4 | 2726 | - |
| fattree-k6 | websearch | Reactive, long timeouts | 8 | 0 | 89.09 / 310.23 | 376 | 22.6 | 7604 | - |
| fattree-k6 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 8 | 0 | 50.61 / 187.32 | 355 | 18.2 | 2020 | 0.0 |
| fattree-k6 | websearch | Hybrid, counter keeps top 2% of pairs | 8 | 0 | 28.17 / 134.31 | 217 | 12.1 | 1526 | 41.4 |
| fattree-k6 | websearch | Hybrid, counter keeps top 5% of pairs | 8 | 0 | 23.71 / 129.07 | 190 | 10.9 | 1788 | 49.2 |
| fattree-k6 | websearch | Hybrid, counter keeps top 10% of pairs | 8 | 0 | 18.87 / 128.15 | 176 | 10.5 | 2334 | 53.2 |
| fattree-k6 | websearch | Oracle, busiest 2% of pairs (upper bound) | 8 | 0 | 19.35 / 125.48 | 189 | 8.7 | 1317 | 52.1 |
| fattree-k6 | websearch | Oracle, busiest 5% of pairs (upper bound) | 8 | 0 | 8.14 / 123.72 | 129 | 6.2 | 1353 | 68.4 |
| fattree-k6 | websearch | Oracle, busiest 10% of pairs (upper bound) | 8 | 0 | 6.52 / 127.74 | 82 | 3.8 | 1980 | 80.6 |
| fattree-k6 | websearch | Proactive (ECMP) | 8 | 0 | 4.61 / 121.34 | 0 | 0.4 | 13230 | - |
| fattree-k6 | websearch | Reactive (learning + spanning tree) | 9 | 0 | 112.52 / 409.99 | 346 | 27.6 | 3251 | - |
| fattree-k6 | websearch | Reactive, long timeouts | 9 | 0 | 83.39 / 298.27 | 345 | 22.9 | 8410 | - |
| fattree-k6 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 9 | 0 | 49.12 / 193.05 | 390 | 20.2 | 2340 | 0.0 |
| fattree-k6 | websearch | Hybrid, counter keeps top 2% of pairs | 9 | 0 | 34.54 / 124.86 | 256 | 15.2 | 1720 | 36.8 |
| fattree-k6 | websearch | Hybrid, counter keeps top 5% of pairs | 9 | 0 | 30.28 / 130.00 | 231 | 13.8 | 1987 | 42.6 |
| fattree-k6 | websearch | Hybrid, counter keeps top 10% of pairs | 9 | 0 | 31.34 / 178.28 | 216 | 15.6 | 2522 | 47.3 |
| fattree-k6 | websearch | Oracle, busiest 2% of pairs (upper bound) | 9 | 0 | 26.86 / 121.47 | 215 | 10.9 | 1513 | 47.1 |
| fattree-k6 | websearch | Oracle, busiest 5% of pairs (upper bound) | 9 | 0 | 21.57 / 145.55 | 164 | 8.3 | 1539 | 61.2 |
| fattree-k6 | websearch | Oracle, busiest 10% of pairs (upper bound) | 9 | 0 | 10.23 / 150.86 | 117 | 6.0 | 2069 | 74.2 |
| fattree-k6 | websearch | Proactive (ECMP) | 9 | 0 | 5.11 / 160.80 | 0 | 0.5 | 13230 | - |
