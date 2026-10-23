# Realistic traffic results (traffic-20261021-050401)

Testbed: Linux Harikrushna 6.18.33.2-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Thu Jun 18 21:54:43 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet

**Every value is the mean of 5 runs (seeds 7 to 11, a new flow schedule each time) ± the half-width of its 95% confidence interval (Student's t).**

## Traffic generated (identical for every controller within one seed)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Abilene traffic matrices (Zhang et al., IMC 2005) + SURGE flow sizes | 1749 ± 43 | 58.3 ± 1.4 | 28.5 ± 2.9 (3%) | 0 ± 0 | 100 ± 0% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Reactive (learning + spanning tree) | 1749 ± 43 / 0 ± 0 | 110.92 ± 2.51 / 99.16 ± 5.19 / 342.67 ± 21.64 | 251.8 ± 25.2 | 1608.4 ± 139.5 |
| abilene | isp | Reactive, long timeouts | 1749 ± 43 / 0 ± 0 | 110.96 ± 2.73 / 98.72 ± 5.59 / 344.67 ± 23.51 | 252.0 ± 24.6 | 1605.1 ± 171.8 |
| abilene | isp | Reactive on shortest paths (hybrid, budget 0%) | 1749 ± 43 / 0 ± 0 | 70.83 ± 3.69 / 56.46 ± 2.70 / 223.50 ± 29.91 | 189.1 ± 9.5 | 1466.1 ± 365.4 |
| abilene | isp | Reactive on shortest paths, pair rules | 1749 ± 43 / 0 ± 0 | 58.88 ± 3.46 / 46.13 ± 1.53 / 205.58 ± 35.82 | 177.2 ± 10.9 | 1453.4 ± 336.8 |
| abilene | isp | Reactive on shortest paths, destination rules | 1749 ± 43 / 0 ± 0 | 58.73 ± 3.42 / 46.05 ± 1.61 / 205.39 ± 36.53 | 176.9 ± 10.2 | 1456.5 ± 368.7 |
| abilene | isp | Hybrid, counter keeps top 10% of pairs | 1749 ± 43 / 0 ± 0 | 66.73 ± 4.07 / 54.17 ± 2.92 / 219.11 ± 33.58 | 184.5 ± 10.2 | 1462.1 ± 330.5 |
| abilene | isp | Hybrid, counter keeps top 25% of pairs | 1749 ± 43 / 0 ± 0 | 63.02 ± 3.56 / 50.90 ± 2.52 / 217.07 ± 30.66 | 181.3 ± 11.1 | 1455.5 ± 319.1 |
| abilene | isp | Hybrid, counter keeps top 50% of pairs | 1749 ± 43 / 0 ± 0 | 60.47 ± 3.42 / 47.84 ± 2.33 / 209.49 ± 37.58 | 178.9 ± 10.6 | 1456.2 ± 307.8 |
| abilene | isp | Oracle, busiest 10% of pairs (upper bound) | 1749 ± 43 / 0 ± 0 | 65.42 ± 3.34 / 53.66 ± 2.59 / 218.78 ± 29.13 | 183.2 ± 11.0 | 1456.2 ± 307.4 |
| abilene | isp | Oracle, busiest 25% of pairs (upper bound) | 1749 ± 43 / 0 ± 0 | 61.88 ± 3.36 / 49.93 ± 3.04 / 213.24 ± 32.39 | 180.4 ± 11.1 | 1455.0 ± 312.8 |
| abilene | isp | Oracle, busiest 50% of pairs (upper bound) | 1749 ± 43 / 0 ± 0 | 59.81 ± 3.30 / 47.28 ± 1.41 / 208.00 ± 33.90 | 177.7 ± 10.6 | 1455.7 ± 310.9 |
| abilene | isp | Random 10% of pairs (no knowledge) | 1749 ± 43 / 0 ± 0 | 68.89 ± 3.16 / 54.59 ± 2.50 / 224.26 ± 34.76 | 187.0 ± 11.1 | 1457.4 ± 305.8 |
| abilene | isp | Random 25% of pairs (no knowledge) | 1749 ± 43 / 0 ± 0 | 65.89 ± 2.83 / 52.53 ± 2.27 / 217.89 ± 33.99 | 184.4 ± 10.7 | 1452.7 ± 298.0 |
| abilene | isp | Random 50% of pairs (no knowledge) | 1749 ± 43 / 0 ± 0 | 62.35 ± 3.83 / 48.61 ± 1.90 / 214.26 ± 33.21 | 180.6 ± 10.0 | 1454.6 ± 322.8 |
| abilene | isp | Proactive (one shortest path) | 1749 ± 43 / 0 ± 0 | 58.66 ± 3.48 / 46.00 ± 1.47 / 205.48 ± 37.62 | 176.9 ± 10.6 | 1458.4 ± 384.2 |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Reactive (learning + spanning tree) | 607 ± 18 | 601 ± 18 | 28.5 ± 1.3 | 7329 ± 160 | 1080 ± 30 |
| abilene | isp | Reactive, long timeouts | 600 ± 25 | 593 ± 25 | 28.4 ± 1.0 | 16333 ± 429 | 2429 ± 88 |
| abilene | isp | Reactive on shortest paths (hybrid, budget 0%) | 444 ± 25 | 442 ± 25 | 21.4 ± 1.7 | 5319 ± 112 | 828 ± 30 |
| abilene | isp | Reactive on shortest paths, pair rules | 15 ± 1 | 13 ± 1 | 0.9 ± 0.0 | 380 ± 5 | 61 ± 2 |
| abilene | isp | Reactive on shortest paths, destination rules | 6 ± 1 | 4 ± 1 | 0.4 ± 0.1 | 120 ± 2 | 11 ± 0 |
| abilene | isp | Hybrid, counter keeps top 10% of pairs | 337 ± 19 | 339 ± 19 | 17.3 ± 1.9 | 4041 ± 246 | 677 ± 90 |
| abilene | isp | Hybrid, counter keeps top 25% of pairs | 207 ± 20 | 214 ± 20 | 11.7 ± 1.2 | 2621 ± 211 | 454 ± 64 |
| abilene | isp | Hybrid, counter keeps top 50% of pairs | 93 ± 10 | 103 ± 11 | 6.0 ± 0.4 | 1321 ± 192 | 252 ± 48 |
| abilene | isp | Oracle, busiest 10% of pairs (upper bound) | 284 ± 9 | 282 ± 9 | 15.3 ± 1.2 | 3778 ± 68 | 613 ± 55 |
| abilene | isp | Oracle, busiest 25% of pairs (upper bound) | 168 ± 8 | 166 ± 8 | 9.5 ± 0.8 | 2419 ± 168 | 415 ± 52 |
| abilene | isp | Oracle, busiest 50% of pairs (upper bound) | 67 ± 5 | 65 ± 5 | 4.1 ± 0.4 | 1141 ± 129 | 210 ± 24 |
| abilene | isp | Random 10% of pairs (no knowledge) | 402 ± 29 | 400 ± 29 | 19.6 ± 1.4 | 4876 ± 317 | 749 ± 71 |
| abilene | isp | Random 25% of pairs (no knowledge) | 330 ± 19 | 328 ± 19 | 16.4 ± 1.2 | 4013 ± 222 | 644 ± 23 |
| abilene | isp | Random 50% of pairs (no knowledge) | 207 ± 50 | 205 ± 50 | 10.7 ± 1.9 | 2701 ± 346 | 447 ± 121 |
| abilene | isp | Proactive (one shortest path) | 0 ± 0 | 0 ± 0 | 0.1 ± 0.0 | 386 ± 0 | 62 ± 0 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Reactive on shortest paths (hybrid, budget 0%) | 0 of 110 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| abilene | isp | Reactive on shortest paths, pair rules | 0 of 110 | 96.5 ± 0.1 | 0 ± 0 | 0 ± 0 |
| abilene | isp | Reactive on shortest paths, destination rules | 0 of 110 | 97.8 ± 0.3 | 0 ± 0 | 0 ± 0 |
| abilene | isp | Hybrid, counter keeps top 10% of pairs | 11 of 110 | 26.0 ± 2.0 | 27 ± 5 | 14 ± 6 |
| abilene | isp | Hybrid, counter keeps top 25% of pairs | 28 of 110 | 52.2 ± 1.8 | 59 ± 5 | 22 ± 9 |
| abilene | isp | Hybrid, counter keeps top 50% of pairs | 55 of 110 | 76.8 ± 2.0 | 87 ± 11 | 20 ± 7 |
| abilene | isp | Oracle, busiest 10% of pairs (upper bound) | 11 of 110 | 33.1 ± 1.0 | 11 ± 0 | 0 ± 0 |
| abilene | isp | Oracle, busiest 25% of pairs (upper bound) | 28 of 110 | 59.2 ± 0.8 | 28 ± 0 | 0 ± 0 |
| abilene | isp | Oracle, busiest 50% of pairs (upper bound) | 55 of 110 | 83.0 ± 1.0 | 55 ± 0 | 0 ± 0 |
| abilene | isp | Random 10% of pairs (no knowledge) | 11 of 110 | 9.6 ± 4.8 | 11 ± 0 | 0 ± 0 |
| abilene | isp | Random 25% of pairs (no knowledge) | 28 of 110 | 24.5 ± 4.8 | 28 ± 0 | 0 ± 0 |
| abilene | isp | Random 50% of pairs (no knowledge) | 55 of 110 | 54.1 ± 5.4 | 55 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Reactive (learning + spanning tree) | 7 | 0 | 97.94 / 340.95 | 608 | 30.1 | 7182 | - |
| abilene | isp | Reactive, long timeouts | 7 | 0 | 98.67 / 343.69 | 582 | 28.7 | 16441 | - |
| abilene | isp | Reactive on shortest paths (hybrid, budget 0%) | 7 | 0 | 59.56 / 214.86 | 462 | 23.5 | 5322 | 0.0 |
| abilene | isp | Reactive on shortest paths, pair rules | 7 | 0 | 47.24 / 189.47 | 14 | 1.0 | 380 | 96.5 |
| abilene | isp | Reactive on shortest paths, destination rules | 7 | 0 | 47.19 / 189.76 | 4 | 0.5 | 121 | 97.4 |
| abilene | isp | Hybrid, counter keeps top 10% of pairs | 7 | 0 | 56.82 / 213.53 | 360 | 20.0 | 4273 | 23.7 |
| abilene | isp | Hybrid, counter keeps top 25% of pairs | 7 | 0 | 52.55 / 210.50 | 221 | 13.1 | 2656 | 50.5 |
| abilene | isp | Hybrid, counter keeps top 50% of pairs | 7 | 0 | 48.94 / 191.21 | 83 | 6.1 | 1148 | 78.1 |
| abilene | isp | Oracle, busiest 10% of pairs (upper bound) | 7 | 0 | 56.12 / 213.79 | 296 | 17.0 | 3761 | 33.2 |
| abilene | isp | Oracle, busiest 25% of pairs (upper bound) | 7 | 0 | 52.85 / 207.24 | 169 | 10.6 | 2389 | 59.1 |
| abilene | isp | Oracle, busiest 50% of pairs (upper bound) | 7 | 0 | 48.17 / 191.04 | 63 | 4.4 | 1117 | 83.2 |
| abilene | isp | Random 10% of pairs (no knowledge) | 7 | 0 | 57.01 / 212.72 | 413 | 20.7 | 4927 | 9.0 |
| abilene | isp | Random 25% of pairs (no knowledge) | 7 | 0 | 54.00 / 206.02 | 327 | 16.8 | 4008 | 28.4 |
| abilene | isp | Random 50% of pairs (no knowledge) | 7 | 0 | 48.29 / 206.65 | 217 | 11.3 | 2984 | 53.2 |
| abilene | isp | Proactive (one shortest path) | 7 | 0 | 46.90 / 189.28 | 0 | 0.1 | 386 | - |
| abilene | isp | Reactive (learning + spanning tree) | 8 | 0 | 99.12 / 343.59 | 600 | 28.5 | 7246 | - |
| abilene | isp | Reactive, long timeouts | 8 | 0 | 95.82 / 339.24 | 593 | 29.2 | 16016 | - |
| abilene | isp | Reactive on shortest paths (hybrid, budget 0%) | 8 | 0 | 54.32 / 194.01 | 431 | 20.7 | 5202 | 0.0 |
| abilene | isp | Reactive on shortest paths, pair rules | 8 | 0 | 44.82 / 173.91 | 16 | 0.9 | 380 | 96.4 |
| abilene | isp | Reactive on shortest paths, destination rules | 8 | 0 | 44.63 / 171.73 | 6 | 0.4 | 118 | 97.9 |
| abilene | isp | Hybrid, counter keeps top 10% of pairs | 8 | 0 | 51.32 / 181.95 | 330 | 16.7 | 3908 | 26.1 |
| abilene | isp | Hybrid, counter keeps top 25% of pairs | 8 | 0 | 48.75 / 182.93 | 181 | 10.5 | 2334 | 54.2 |
| abilene | isp | Hybrid, counter keeps top 50% of pairs | 8 | 0 | 45.56 / 175.05 | 88 | 5.6 | 1232 | 77.8 |
| abilene | isp | Oracle, busiest 10% of pairs (upper bound) | 8 | 0 | 51.53 / 187.57 | 285 | 15.2 | 3795 | 34.0 |
| abilene | isp | Oracle, busiest 25% of pairs (upper bound) | 8 | 0 | 47.17 / 176.58 | 162 | 9.0 | 2322 | 60.2 |
| abilene | isp | Oracle, busiest 50% of pairs (upper bound) | 8 | 0 | 45.83 / 174.77 | 67 | 3.9 | 1100 | 83.3 |
| abilene | isp | Random 10% of pairs (no knowledge) | 8 | 0 | 51.65 / 190.98 | 399 | 19.5 | 4779 | 10.5 |
| abilene | isp | Random 25% of pairs (no knowledge) | 8 | 0 | 51.42 / 184.90 | 358 | 17.9 | 4225 | 18.2 |
| abilene | isp | Random 50% of pairs (no knowledge) | 8 | 0 | 46.81 / 181.53 | 180 | 10.0 | 2506 | 58.6 |
| abilene | isp | Proactive (one shortest path) | 8 | 0 | 44.81 / 171.08 | 0 | 0.1 | 386 | - |
| abilene | isp | Reactive (learning + spanning tree) | 9 | 0 | 96.59 / 323.05 | 632 | 28.8 | 7515 | - |
| abilene | isp | Reactive, long timeouts | 9 | 0 | 96.31 / 324.85 | 634 | 28.9 | 16858 | - |
| abilene | isp | Reactive on shortest paths (hybrid, budget 0%) | 9 | 0 | 54.79 / 240.31 | 467 | 22.0 | 5447 | 0.0 |
| abilene | isp | Reactive on shortest paths, pair rules | 9 | 0 | 45.21 / 232.27 | 15 | 0.9 | 386 | 96.6 |
| abilene | isp | Reactive on shortest paths, destination rules | 9 | 0 | 45.15 / 231.86 | 6 | 0.4 | 121 | 97.8 |
| abilene | isp | Hybrid, counter keeps top 10% of pairs | 9 | 0 | 52.96 / 242.72 | 327 | 16.7 | 3983 | 26.9 |
| abilene | isp | Hybrid, counter keeps top 25% of pairs | 9 | 0 | 50.41 / 237.95 | 212 | 11.7 | 2752 | 51.2 |
| abilene | isp | Hybrid, counter keeps top 50% of pairs | 9 | 0 | 46.82 / 239.49 | 101 | 6.3 | 1423 | 75.4 |
| abilene | isp | Oracle, busiest 10% of pairs (upper bound) | 9 | 0 | 52.74 / 233.81 | 278 | 15.1 | 3848 | 33.4 |
| abilene | isp | Oracle, busiest 25% of pairs (upper bound) | 9 | 0 | 48.91 / 234.28 | 171 | 9.4 | 2395 | 59.0 |
| abilene | isp | Oracle, busiest 50% of pairs (upper bound) | 9 | 0 | 46.65 / 231.97 | 74 | 4.4 | 1304 | 81.8 |
| abilene | isp | Random 10% of pairs (no knowledge) | 9 | 0 | 55.09 / 255.62 | 436 | 20.8 | 5280 | 3.5 |
| abilene | isp | Random 25% of pairs (no knowledge) | 9 | 0 | 50.53 / 236.44 | 327 | 15.9 | 3954 | 24.2 |
| abilene | isp | Random 50% of pairs (no knowledge) | 9 | 0 | 47.99 / 238.54 | 249 | 12.2 | 2825 | 50.2 |
| abilene | isp | Proactive (one shortest path) | 9 | 0 | 45.04 / 231.42 | 0 | 0.1 | 386 | - |
| abilene | isp | Reactive (learning + spanning tree) | 10 | 0 | 106.29 / 335.30 | 601 | 27.9 | 7383 | - |
| abilene | isp | Reactive, long timeouts | 10 | 0 | 106.53 / 339.54 | 596 | 27.6 | 16315 | - |
| abilene | isp | Reactive on shortest paths (hybrid, budget 0%) | 10 | 0 | 57.73 / 255.00 | 435 | 20.6 | 5345 | 0.0 |
| abilene | isp | Reactive on shortest paths, pair rules | 10 | 0 | 47.59 / 239.93 | 15 | 0.9 | 374 | 96.5 |
| abilene | isp | Reactive on shortest paths, destination rules | 10 | 0 | 47.62 / 240.52 | 5 | 0.4 | 120 | 98.1 |
| abilene | isp | Hybrid, counter keeps top 10% of pairs | 10 | 0 | 56.38 / 248.34 | 343 | 17.4 | 4222 | 28.0 |
| abilene | isp | Hybrid, counter keeps top 25% of pairs | 10 | 0 | 53.44 / 244.29 | 218 | 11.9 | 2619 | 52.2 |
| abilene | isp | Hybrid, counter keeps top 50% of pairs | 10 | 0 | 50.40 / 243.06 | 92 | 5.6 | 1267 | 78.1 |
| abilene | isp | Oracle, busiest 10% of pairs (upper bound) | 10 | 0 | 55.65 / 248.77 | 281 | 14.5 | 3697 | 31.8 |
| abilene | isp | Oracle, busiest 25% of pairs (upper bound) | 10 | 0 | 52.16 / 242.31 | 163 | 8.9 | 2336 | 59.4 |
| abilene | isp | Oracle, busiest 50% of pairs (upper bound) | 10 | 0 | 48.63 / 239.45 | 63 | 3.8 | 1022 | 84.0 |
| abilene | isp | Random 10% of pairs (no knowledge) | 10 | 0 | 55.44 / 251.24 | 381 | 18.5 | 4594 | 14.3 |
| abilene | isp | Random 25% of pairs (no knowledge) | 10 | 0 | 54.88 / 254.27 | 319 | 15.6 | 3754 | 25.1 |
| abilene | isp | Random 50% of pairs (no knowledge) | 10 | 0 | 50.96 / 244.81 | 238 | 11.6 | 2874 | 49.9 |
| abilene | isp | Proactive (one shortest path) | 10 | 0 | 47.54 / 242.81 | 0 | 0.1 | 386 | - |
| abilene | isp | Reactive (learning + spanning tree) | 11 | 0 | 95.84 / 370.46 | 596 | 27.3 | 7317 | - |
| abilene | isp | Reactive, long timeouts | 11 | 0 | 96.30 / 376.04 | 592 | 27.4 | 16035 | - |
| abilene | isp | Reactive on shortest paths (hybrid, budget 0%) | 11 | 0 | 55.91 / 213.33 | 422 | 20.2 | 5277 | 0.0 |
| abilene | isp | Reactive on shortest paths, pair rules | 11 | 0 | 45.79 / 192.33 | 16 | 0.9 | 380 | 96.5 |
| abilene | isp | Reactive on shortest paths, destination rules | 11 | 0 | 45.68 / 193.09 | 6 | 0.4 | 119 | 97.8 |
| abilene | isp | Hybrid, counter keeps top 10% of pairs | 11 | 0 | 53.39 / 209.00 | 323 | 16.0 | 3819 | 25.2 |
| abilene | isp | Hybrid, counter keeps top 25% of pairs | 11 | 0 | 49.36 / 209.68 | 201 | 11.1 | 2742 | 52.8 |
| abilene | isp | Hybrid, counter keeps top 50% of pairs | 11 | 0 | 47.47 / 198.63 | 100 | 6.2 | 1533 | 74.8 |
| abilene | isp | Oracle, busiest 10% of pairs (upper bound) | 11 | 0 | 52.25 / 209.96 | 278 | 14.8 | 3788 | 33.1 |
| abilene | isp | Oracle, busiest 25% of pairs (upper bound) | 11 | 0 | 48.56 / 205.81 | 177 | 9.6 | 2654 | 58.3 |
| abilene | isp | Oracle, busiest 50% of pairs (upper bound) | 11 | 0 | 47.11 / 202.77 | 67 | 3.9 | 1160 | 82.7 |
| abilene | isp | Random 10% of pairs (no knowledge) | 11 | 0 | 53.76 / 210.71 | 382 | 18.5 | 4801 | 10.7 |
| abilene | isp | Random 25% of pairs (no knowledge) | 11 | 0 | 51.83 / 207.82 | 321 | 15.8 | 4122 | 26.6 |
| abilene | isp | Random 50% of pairs (no knowledge) | 11 | 0 | 49.00 / 199.75 | 152 | 8.3 | 2317 | 58.9 |
| abilene | isp | Proactive (one shortest path) | 11 | 0 | 45.70 / 192.82 | 0 | 0.1 | 386 | - |
