# Realistic traffic results (traffic-20261020-183215)

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
| fattree-k4 | websearch | Reactive (learning + spanning tree) | 1116 ± 34 / 5 ± 14 | 149.51 ± 43.00 / 124.10 ± 33.77 / 556.73 ± 215.18 | 5405.4 ± 2108.4 | 16812.0 ± 6712.5 |
| fattree-k4 | websearch | Reactive, long timeouts | 898 ± 576 / 223 ± 600 | 126.27 ± 84.88 / 103.02 ± 71.80 / 480.87 ± 343.46 | 4544.0 ± 3562.4 | 13498.0 ± 10719.7 |
| fattree-k4 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 1121 ± 27 / 0 ± 0 | 110.21 ± 62.41 / 94.25 ± 68.84 / 347.66 ± 111.47 | 2491.7 ± 496.7 | 9684.2 ± 4655.7 |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 1121 ± 27 / 0 ± 0 | 64.70 ± 26.74 / 39.20 ± 18.75 / 351.94 ± 125.82 | 2752.1 ± 1214.2 | 10440.8 ± 4774.5 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 1121 ± 27 / 0 ± 0 | 56.67 ± 9.31 / 31.62 ± 4.28 / 299.52 ± 45.91 | 2424.7 ± 545.7 | 9219.4 ± 4922.2 |
| fattree-k4 | websearch | Hybrid, counter keeps top 10% of pairs | 1121 ± 27 / 0 ± 0 | 66.22 ± 9.07 / 47.65 ± 4.80 / 291.41 ± 46.57 | 2391.0 ± 497.9 | 9503.2 ± 4612.8 |
| fattree-k4 | websearch | Hybrid, counter keeps top 25% of pairs | 1121 ± 27 / 0 ± 0 | 61.89 ± 9.09 / 42.61 ± 6.31 / 293.91 ± 40.68 | 2369.8 ± 484.1 | 9470.8 ± 4264.5 |
| fattree-k4 | websearch | Hybrid, counter keeps top 50% of pairs | 1121 ± 27 / 0 ± 0 | 59.85 ± 10.17 / 38.61 ± 6.42 / 303.12 ± 52.33 | 2423.9 ± 514.2 | 9447.5 ± 4611.9 |
| fattree-k4 | websearch | Oracle, busiest 10% of pairs (upper bound) | 1121 ± 27 / 0 ± 0 | 62.40 ± 8.35 / 44.27 ± 5.21 / 289.76 ± 45.34 | 2312.0 ± 449.9 | 9550.7 ± 4664.0 |
| fattree-k4 | websearch | Oracle, busiest 25% of pairs (upper bound) | 1121 ± 27 / 0 ± 0 | 58.56 ± 9.89 / 36.77 ± 4.56 / 303.88 ± 53.53 | 2393.0 ± 526.6 | 9397.5 ± 4498.8 |
| fattree-k4 | websearch | Oracle, busiest 50% of pairs (upper bound) | 1121 ± 27 / 0 ± 0 | 55.52 ± 9.96 / 33.35 ± 5.17 / 306.14 ± 47.62 | 2397.5 ± 512.7 | 9212.6 ± 4453.6 |
| fattree-k4 | websearch | Random 10% of pairs (no knowledge) | 1121 ± 27 / 0 ± 0 | 81.94 ± 10.47 / 65.00 ± 8.84 / 311.35 ± 50.86 | 2341.1 ± 428.2 | 9451.5 ± 4664.2 |
| fattree-k4 | websearch | Random 25% of pairs (no knowledge) | 1121 ± 27 / 0 ± 0 | 77.65 ± 11.26 / 60.43 ± 11.20 / 309.17 ± 30.22 | 2346.5 ± 460.6 | 9369.7 ± 4550.7 |
| fattree-k4 | websearch | Random 50% of pairs (no knowledge) | 1121 ± 27 / 0 ± 0 | 69.42 ± 7.91 / 51.07 ± 3.72 / 302.52 ± 37.31 | 2402.1 ± 400.3 | 9100.2 ± 4855.0 |
| fattree-k4 | websearch | Proactive (ECMP) | 1121 ± 27 / 0 ± 0 | 54.46 ± 9.55 / 28.66 ± 5.24 / 321.18 ± 42.64 | 2412.8 ± 454.0 | 9379.1 ± 4725.6 |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive (learning + spanning tree) | 454 ± 37 | 434 ± 35 | 30.7 ± 8.0 | 4377 ± 560 | 754 ± 141 |
| fattree-k4 | websearch | Reactive, long timeouts | 412 ± 89 | 344 ± 224 | 24.5 ± 10.7 | 8489 ± 5874 | 1459 ± 1018 |
| fattree-k4 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 507 ± 44 | 503 ± 44 | 34.6 ± 14.9 | 3765 ± 429 | 374 ± 54 |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 115 ± 41 | 111 ± 41 | 5.8 ± 3.1 | 832 ± 28 | 51 ± 1 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 69 ± 45 | 65 ± 45 | 2.2 ± 0.7 | 280 ± 6 | 16 ± 0 |
| fattree-k4 | websearch | Hybrid, counter keeps top 10% of pairs | 266 ± 25 | 271 ± 27 | 16.3 ± 1.4 | 1875 ± 112 | 137 ± 14 |
| fattree-k4 | websearch | Hybrid, counter keeps top 25% of pairs | 186 ± 16 | 205 ± 19 | 12.4 ± 1.2 | 1566 ± 71 | 110 ± 15 |
| fattree-k4 | websearch | Hybrid, counter keeps top 50% of pairs | 121 ± 23 | 153 ± 28 | 9.2 ± 1.1 | 1492 ± 102 | 97 ± 6 |
| fattree-k4 | websearch | Oracle, busiest 10% of pairs (upper bound) | 235 ± 17 | 230 ± 17 | 14.5 ± 1.3 | 1729 ± 195 | 125 ± 11 |
| fattree-k4 | websearch | Oracle, busiest 25% of pairs (upper bound) | 141 ± 11 | 137 ± 11 | 8.4 ± 0.9 | 1223 ± 85 | 82 ± 7 |
| fattree-k4 | websearch | Oracle, busiest 50% of pairs (upper bound) | 64 ± 5 | 59 ± 5 | 4.4 ± 0.4 | 990 ± 57 | 62 ± 2 |
| fattree-k4 | websearch | Random 10% of pairs (no knowledge) | 451 ± 31 | 447 ± 31 | 27.0 ± 1.9 | 3557 ± 398 | 348 ± 41 |
| fattree-k4 | websearch | Random 25% of pairs (no knowledge) | 397 ± 48 | 393 ± 48 | 24.2 ± 4.3 | 3267 ± 559 | 318 ± 78 |
| fattree-k4 | websearch | Random 50% of pairs (no knowledge) | 266 ± 50 | 262 ± 50 | 18.1 ± 3.0 | 2648 ± 399 | 284 ± 45 |
| fattree-k4 | websearch | Proactive (ECMP) | 0 ± 0 | 0 ± 0 | 0.3 ± 0.1 | 1072 ± 0 | 58 ± 0 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 0 of 240 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 0 of 240 | 86.1 ± 0.2 | 0 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 0 of 240 | 93.6 ± 0.7 | 0 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | Hybrid, counter keeps top 10% of pairs | 24 of 240 | 50.7 ± 1.9 | 51 ± 5 | 23 ± 7 |
| fattree-k4 | websearch | Hybrid, counter keeps top 25% of pairs | 60 of 240 | 65.7 ± 1.8 | 118 ± 8 | 43 ± 10 |
| fattree-k4 | websearch | Hybrid, counter keeps top 50% of pairs | 120 of 240 | 77.6 ± 1.4 | 195 ± 15 | 53 ± 12 |
| fattree-k4 | websearch | Oracle, busiest 10% of pairs (upper bound) | 24 of 240 | 56.2 ± 1.3 | 24 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | Oracle, busiest 25% of pairs (upper bound) | 60 of 240 | 73.7 ± 1.2 | 60 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | Oracle, busiest 50% of pairs (upper bound) | 120 of 240 | 88.3 ± 0.7 | 120 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | Random 10% of pairs (no knowledge) | 24 of 240 | 8.4 ± 3.2 | 24 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | Random 25% of pairs (no knowledge) | 60 of 240 | 19.3 ± 9.0 | 60 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | Random 50% of pairs (no knowledge) | 120 of 240 | 43.5 ± 6.7 | 120 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive (learning + spanning tree) | 7 | 0 | 126.72 / 540.55 | 487 | 41.9 | 4482 | - |
| fattree-k4 | websearch | Reactive, long timeouts | 7 | 1087 | 11.48 / 75.97 | 292 | 9.5 | 138 | - |
| fattree-k4 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 7 | 0 | 192.89 / 496.84 | 526 | 55.9 | 3850 | 0.0 |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 7 | 0 | 65.05 / 514.23 | 106 | 10.0 | 844 | 86.3 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 7 | 0 | 27.31 / 277.32 | 56 | 2.5 | 275 | 93.3 |
| fattree-k4 | websearch | Hybrid, counter keeps top 10% of pairs | 7 | 0 | 46.22 / 277.37 | 263 | 17.6 | 1792 | 51.6 |
| fattree-k4 | websearch | Hybrid, counter keeps top 25% of pairs | 7 | 0 | 38.73 / 288.73 | 184 | 12.3 | 1548 | 66.7 |
| fattree-k4 | websearch | Hybrid, counter keeps top 50% of pairs | 7 | 0 | 34.28 / 292.63 | 101 | 8.1 | 1436 | 78.5 |
| fattree-k4 | websearch | Oracle, busiest 10% of pairs (upper bound) | 7 | 0 | 40.23 / 291.12 | 224 | 13.6 | 1620 | 57.2 |
| fattree-k4 | websearch | Oracle, busiest 25% of pairs (upper bound) | 7 | 0 | 34.29 / 300.40 | 136 | 8.2 | 1207 | 74.7 |
| fattree-k4 | websearch | Oracle, busiest 50% of pairs (upper bound) | 7 | 0 | 30.15 / 304.67 | 63 | 4.2 | 972 | 88.8 |
| fattree-k4 | websearch | Random 10% of pairs (no knowledge) | 7 | 0 | 60.93 / 303.50 | 440 | 26.2 | 3578 | 9.0 |
| fattree-k4 | websearch | Random 25% of pairs (no knowledge) | 7 | 0 | 57.19 / 311.08 | 429 | 25.8 | 3656 | 12.9 |
| fattree-k4 | websearch | Random 50% of pairs (no knowledge) | 7 | 0 | 52.01 / 310.95 | 285 | 21.5 | 2929 | 40.2 |
| fattree-k4 | websearch | Proactive (ECMP) | 7 | 0 | 26.45 / 345.13 | 0 | 0.2 | 1072 | - |
| fattree-k4 | websearch | Reactive (learning + spanning tree) | 8 | 26 | 159.84 / 789.63 | 483 | 28.3 | 4829 | - |
| fattree-k4 | websearch | Reactive, long timeouts | 8 | 29 | 160.40 / 792.18 | 481 | 27.9 | 11249 | - |
| fattree-k4 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 8 | 0 | 63.38 / 294.44 | 549 | 29.3 | 4016 | 0.0 |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 8 | 0 | 26.99 / 316.22 | 107 | 4.3 | 836 | 86.0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 8 | 0 | 30.65 / 324.66 | 43 | 1.8 | 275 | 93.6 |
| fattree-k4 | websearch | Hybrid, counter keeps top 10% of pairs | 8 | 0 | 46.99 / 313.19 | 301 | 15.7 | 1998 | 49.3 |
| fattree-k4 | websearch | Hybrid, counter keeps top 25% of pairs | 8 | 0 | 38.66 / 313.60 | 206 | 11.4 | 1629 | 63.6 |
| fattree-k4 | websearch | Hybrid, counter keeps top 50% of pairs | 8 | 0 | 36.05 / 328.88 | 148 | 10.3 | 1603 | 76.2 |
| fattree-k4 | websearch | Oracle, busiest 10% of pairs (upper bound) | 8 | 0 | 41.09 / 296.49 | 256 | 13.9 | 1914 | 55.0 |
| fattree-k4 | websearch | Oracle, busiest 25% of pairs (upper bound) | 8 | 0 | 32.28 / 327.68 | 155 | 7.8 | 1299 | 72.5 |
| fattree-k4 | websearch | Oracle, busiest 50% of pairs (upper bound) | 8 | 0 | 31.19 / 316.72 | 66 | 4.4 | 1028 | 87.9 |
| fattree-k4 | websearch | Random 10% of pairs (no knowledge) | 8 | 0 | 58.24 / 324.20 | 479 | 25.7 | 3634 | 12.3 |
| fattree-k4 | websearch | Random 25% of pairs (no knowledge) | 8 | 0 | 51.33 / 321.56 | 389 | 20.4 | 2961 | 31.3 |
| fattree-k4 | websearch | Random 50% of pairs (no knowledge) | 8 | 0 | 49.01 / 294.21 | 321 | 18.7 | 2981 | 39.1 |
| fattree-k4 | websearch | Proactive (ECMP) | 8 | 0 | 23.65 / 321.00 | 0 | 0.2 | 1072 | - |
| fattree-k4 | websearch | Reactive (learning + spanning tree) | 9 | 0 | 114.72 / 603.82 | 444 | 26.0 | 4475 | - |
| fattree-k4 | websearch | Reactive, long timeouts | 9 | 0 | 120.05 / 631.45 | 435 | 26.1 | 10851 | - |
| fattree-k4 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 9 | 0 | 71.26 / 354.42 | 492 | 28.2 | 3970 | 0.0 |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 9 | 0 | 38.96 / 372.80 | 170 | 6.0 | 824 | 86.1 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 9 | 0 | 36.81 / 352.14 | 128 | 3.1 | 283 | 93.1 |
| fattree-k4 | websearch | Hybrid, counter keeps top 10% of pairs | 9 | 0 | 53.04 / 342.64 | 252 | 15.0 | 1785 | 51.4 |
| fattree-k4 | websearch | Hybrid, counter keeps top 25% of pairs | 9 | 0 | 49.91 / 328.19 | 169 | 11.8 | 1478 | 67.4 |
| fattree-k4 | websearch | Hybrid, counter keeps top 50% of pairs | 9 | 0 | 46.89 / 343.31 | 107 | 8.4 | 1442 | 78.8 |
| fattree-k4 | websearch | Oracle, busiest 10% of pairs (upper bound) | 9 | 0 | 50.42 / 332.13 | 222 | 14.2 | 1531 | 56.8 |
| fattree-k4 | websearch | Oracle, busiest 25% of pairs (upper bound) | 9 | 0 | 41.12 / 349.13 | 132 | 7.9 | 1144 | 74.8 |
| fattree-k4 | websearch | Oracle, busiest 50% of pairs (upper bound) | 9 | 0 | 40.60 / 348.19 | 56 | 4.1 | 925 | 89.1 |
| fattree-k4 | websearch | Random 10% of pairs (no knowledge) | 9 | 0 | 73.17 / 363.92 | 453 | 28.1 | 3834 | 8.2 |
| fattree-k4 | websearch | Random 25% of pairs (no knowledge) | 9 | 0 | 67.18 / 337.44 | 401 | 26.5 | 3551 | 18.9 |
| fattree-k4 | websearch | Random 50% of pairs (no knowledge) | 9 | 0 | 54.70 / 329.19 | 240 | 16.5 | 2396 | 51.9 |
| fattree-k4 | websearch | Proactive (ECMP) | 9 | 0 | 34.79 / 347.24 | 0 | 0.3 | 1072 | - |
| fattree-k4 | websearch | Reactive (learning + spanning tree) | 10 | 0 | 85.45 / 305.14 | 416 | 27.2 | 3616 | - |
| fattree-k4 | websearch | Reactive, long timeouts | 10 | 0 | 86.37 / 349.90 | 412 | 27.9 | 9274 | - |
| fattree-k4 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 10 | 0 | 65.27 / 265.97 | 455 | 28.4 | 3164 | 0.0 |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 10 | 0 | 30.93 / 245.31 | 80 | 3.8 | 858 | 86.0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 10 | 0 | 30.91 / 267.80 | 42 | 1.5 | 286 | 93.4 |
| fattree-k4 | websearch | Hybrid, counter keeps top 10% of pairs | 10 | 0 | 42.63 / 244.69 | 264 | 15.7 | 1927 | 52.3 |
| fattree-k4 | websearch | Hybrid, counter keeps top 25% of pairs | 10 | 0 | 39.77 / 241.99 | 187 | 13.0 | 1599 | 65.6 |
| fattree-k4 | websearch | Hybrid, counter keeps top 50% of pairs | 10 | 0 | 35.43 / 235.51 | 130 | 9.3 | 1556 | 77.3 |
| fattree-k4 | websearch | Oracle, busiest 10% of pairs (upper bound) | 10 | 0 | 43.14 / 231.21 | 237 | 14.7 | 1846 | 56.9 |
| fattree-k4 | websearch | Oracle, busiest 25% of pairs (upper bound) | 10 | 0 | 36.45 / 234.62 | 144 | 8.9 | 1288 | 73.3 |
| fattree-k4 | websearch | Oracle, busiest 50% of pairs (upper bound) | 10 | 0 | 32.49 / 243.86 | 67 | 4.5 | 1038 | 87.7 |
| fattree-k4 | websearch | Random 10% of pairs (no knowledge) | 10 | 0 | 60.40 / 250.43 | 415 | 25.9 | 3010 | 6.4 |
| fattree-k4 | websearch | Random 25% of pairs (no knowledge) | 10 | 0 | 54.00 / 271.95 | 337 | 20.5 | 2626 | 19.3 |
| fattree-k4 | websearch | Random 50% of pairs (no knowledge) | 10 | 0 | 47.12 / 254.47 | 217 | 15.3 | 2250 | 40.5 |
| fattree-k4 | websearch | Proactive (ECMP) | 10 | 0 | 28.01 / 262.92 | 0 | 0.3 | 1072 | - |
| fattree-k4 | websearch | Reactive (learning + spanning tree) | 11 | 0 | 133.74 / 544.53 | 442 | 29.9 | 4482 | - |
| fattree-k4 | websearch | Reactive, long timeouts | 11 | 0 | 136.80 / 554.85 | 441 | 31.2 | 10935 | - |
| fattree-k4 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 11 | 0 | 78.45 / 326.62 | 515 | 31.4 | 3827 | 0.0 |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 11 | 0 | 34.07 / 311.13 | 112 | 5.1 | 798 | 86.1 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 11 | 0 | 32.41 / 275.67 | 75 | 2.3 | 281 | 94.5 |
| fattree-k4 | websearch | Hybrid, counter keeps top 10% of pairs | 11 | 0 | 49.39 / 279.17 | 253 | 17.2 | 1871 | 48.8 |
| fattree-k4 | websearch | Hybrid, counter keeps top 25% of pairs | 11 | 0 | 45.99 / 297.02 | 186 | 13.8 | 1577 | 65.3 |
| fattree-k4 | websearch | Hybrid, counter keeps top 50% of pairs | 11 | 0 | 40.39 / 315.25 | 119 | 9.6 | 1422 | 76.9 |
| fattree-k4 | websearch | Oracle, busiest 10% of pairs (upper bound) | 11 | 0 | 46.47 / 297.87 | 234 | 16.2 | 1736 | 55.2 |
| fattree-k4 | websearch | Oracle, busiest 25% of pairs (upper bound) | 11 | 0 | 39.71 / 307.56 | 137 | 9.4 | 1176 | 73.2 |
| fattree-k4 | websearch | Oracle, busiest 50% of pairs (upper bound) | 11 | 0 | 32.31 / 317.24 | 65 | 4.9 | 987 | 88.1 |
| fattree-k4 | websearch | Random 10% of pairs (no knowledge) | 11 | 0 | 72.26 / 314.69 | 469 | 29.1 | 3728 | 6.0 |
| fattree-k4 | websearch | Random 25% of pairs (no knowledge) | 11 | 0 | 72.47 / 303.82 | 432 | 27.5 | 3542 | 14.2 |
| fattree-k4 | websearch | Random 50% of pairs (no knowledge) | 11 | 0 | 52.48 / 323.80 | 266 | 18.8 | 2686 | 45.8 |
| fattree-k4 | websearch | Proactive (ECMP) | 11 | 0 | 30.42 / 329.63 | 0 | 0.3 | 1072 | - |
