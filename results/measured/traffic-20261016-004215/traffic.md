# Realistic traffic results (traffic-20261016-004215)

Testbed: Linux Harikrushna 6.18.33.2-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Thu Jun 18 21:54:43 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: uniform

Controller: same machine as Mininet

**Every value is the mean of 5 runs (seeds 7 to 11, a new flow schedule each time) ± the half-width of its 95% confidence interval (Student's t).**

## Traffic generated (identical for every controller within one seed)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Abilene traffic matrices (Zhang et al., IMC 2005) + SURGE flow sizes | 1749 ± 43 | 58.3 ± 1.4 | 28.5 ± 2.9 (3%) | 0 ± 0 | 100 ± 0% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Reactive (learning + spanning tree) | 1749 ± 43 / 0 ± 0 | 108.93 ± 2.82 / 96.83 ± 6.83 / 338.28 ± 20.56 | 250.3 ± 23.0 | 1610.3 ± 176.7 |
| abilene | isp | Reactive, long timeouts | 1749 ± 43 / 0 ± 0 | 108.96 ± 2.58 / 97.33 ± 6.22 / 342.66 ± 29.85 | 249.5 ± 24.2 | 1626.2 ± 511.0 |
| abilene | isp | Reactive on shortest paths (hybrid, budget 0%) | 1749 ± 43 / 0 ± 0 | 69.74 ± 3.83 / 55.62 ± 2.04 / 220.37 ± 30.42 | 188.8 ± 10.5 | 1463.1 ± 348.3 |
| abilene | isp | Hybrid, counter keeps top 10% of pairs | 1749 ± 43 / 0 ± 0 | 66.20 ± 3.24 / 53.33 ± 2.20 / 219.89 ± 31.40 | 184.4 ± 11.1 | 1459.0 ± 344.7 |
| abilene | isp | Hybrid, counter keeps top 25% of pairs | 1749 ± 43 / 0 ± 0 | 62.35 ± 3.69 / 50.02 ± 2.49 / 211.47 ± 35.69 | 180.3 ± 10.6 | 1455.4 ± 268.1 |
| abilene | isp | Hybrid, counter keeps top 50% of pairs | 1749 ± 43 / 0 ± 0 | 60.26 ± 3.45 / 47.44 ± 1.92 / 207.21 ± 36.08 | 178.9 ± 10.8 | 1455.3 ± 315.0 |
| abilene | isp | Oracle, busiest 10% of pairs (upper bound) | 1749 ± 43 / 0 ± 0 | 64.86 ± 3.67 / 52.69 ± 2.44 / 222.47 ± 40.26 | 183.4 ± 10.2 | 1456.0 ± 317.8 |
| abilene | isp | Oracle, busiest 25% of pairs (upper bound) | 1749 ± 43 / 0 ± 0 | 61.52 ± 3.36 / 49.42 ± 2.49 / 210.55 ± 34.20 | 179.7 ± 11.4 | 1455.7 ± 309.5 |
| abilene | isp | Oracle, busiest 50% of pairs (upper bound) | 1749 ± 43 / 0 ± 0 | 59.71 ± 3.46 / 47.16 ± 1.36 / 206.81 ± 36.34 | 177.9 ± 10.4 | 1455.4 ± 309.5 |
| abilene | isp | Proactive (one shortest path) | 1749 ± 43 / 0 ± 0 | 58.71 ± 3.48 / 45.97 ± 1.50 / 206.14 ± 37.23 | 176.8 ± 10.7 | 1453.9 ± 331.8 |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Reactive (learning + spanning tree) | 604 ± 22 | 598 ± 22 | 27.1 ± 0.7 | 7339 ± 148 | 1081 ± 30 |
| abilene | isp | Reactive, long timeouts | 604 ± 16 | 598 ± 16 | 27.3 ± 0.6 | 16332 ± 427 | 2429 ± 88 |
| abilene | isp | Reactive on shortest paths (hybrid, budget 0%) | 447 ± 17 | 445 ± 17 | 20.8 ± 0.8 | 5321 ± 111 | 828 ± 30 |
| abilene | isp | Hybrid, counter keeps top 10% of pairs | 334 ± 26 | 336 ± 27 | 16.6 ± 1.2 | 4103 ± 357 | 671 ± 96 |
| abilene | isp | Hybrid, counter keeps top 25% of pairs | 198 ± 19 | 203 ± 19 | 10.7 ± 1.0 | 2615 ± 245 | 460 ± 68 |
| abilene | isp | Hybrid, counter keeps top 50% of pairs | 92 ± 11 | 101 ± 13 | 5.5 ± 0.5 | 1328 ± 143 | 245 ± 37 |
| abilene | isp | Oracle, busiest 10% of pairs (upper bound) | 287 ± 9 | 285 ± 9 | 14.6 ± 0.3 | 3778 ± 73 | 613 ± 57 |
| abilene | isp | Oracle, busiest 25% of pairs (upper bound) | 169 ± 9 | 167 ± 9 | 9.0 ± 0.5 | 2418 ± 168 | 415 ± 53 |
| abilene | isp | Oracle, busiest 50% of pairs (upper bound) | 67 ± 5 | 65 ± 5 | 3.8 ± 0.3 | 1141 ± 129 | 210 ± 24 |
| abilene | isp | Proactive (one shortest path) | 0 ± 0 | 0 ± 0 | 0.1 ± 0.0 | 386 ± 0 | 62 ± 0 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Reactive on shortest paths (hybrid, budget 0%) | 0 of 110 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| abilene | isp | Hybrid, counter keeps top 10% of pairs | 11 of 110 | 26.6 ± 2.3 | 27 ± 4 | 13 ± 6 |
| abilene | isp | Hybrid, counter keeps top 25% of pairs | 28 of 110 | 53.8 ± 2.3 | 55 ± 7 | 17 ± 7 |
| abilene | isp | Hybrid, counter keeps top 50% of pairs | 55 of 110 | 77.2 ± 1.8 | 87 ± 13 | 19 ± 11 |
| abilene | isp | Oracle, busiest 10% of pairs (upper bound) | 11 of 110 | 33.1 ± 1.0 | 11 ± 0 | 0 ± 0 |
| abilene | isp | Oracle, busiest 25% of pairs (upper bound) | 28 of 110 | 59.2 ± 0.8 | 28 ± 0 | 0 ± 0 |
| abilene | isp | Oracle, busiest 50% of pairs (upper bound) | 55 of 110 | 83.0 ± 1.0 | 55 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Reactive (learning + spanning tree) | 7 | 0 | 95.72 / 330.26 | 601 | 27.1 | 7211 | - |
| abilene | isp | Reactive, long timeouts | 7 | 0 | 95.79 / 335.07 | 609 | 27.5 | 16434 | - |
| abilene | isp | Reactive on shortest paths (hybrid, budget 0%) | 7 | 0 | 56.85 / 208.05 | 450 | 20.9 | 5333 | 0.0 |
| abilene | isp | Hybrid, counter keeps top 10% of pairs | 7 | 0 | 55.02 / 211.85 | 320 | 16.1 | 4021 | 25.7 |
| abilene | isp | Hybrid, counter keeps top 25% of pairs | 7 | 0 | 50.77 / 195.57 | 208 | 11.0 | 2623 | 53.9 |
| abilene | isp | Hybrid, counter keeps top 50% of pairs | 7 | 0 | 48.25 / 190.59 | 81 | 5.1 | 1185 | 78.1 |
| abilene | isp | Oracle, busiest 10% of pairs (upper bound) | 7 | 0 | 53.69 / 211.97 | 299 | 14.8 | 3767 | 33.2 |
| abilene | isp | Oracle, busiest 25% of pairs (upper bound) | 7 | 0 | 50.91 / 195.46 | 173 | 9.2 | 2379 | 59.1 |
| abilene | isp | Oracle, busiest 50% of pairs (upper bound) | 7 | 0 | 48.03 / 191.03 | 63 | 3.7 | 1117 | 83.2 |
| abilene | isp | Proactive (one shortest path) | 7 | 0 | 46.98 / 189.93 | 0 | 0.1 | 386 | - |
| abilene | isp | Reactive (learning + spanning tree) | 8 | 0 | 92.07 / 335.94 | 597 | 26.7 | 7270 | - |
| abilene | isp | Reactive, long timeouts | 8 | 0 | 93.27 / 329.67 | 593 | 26.8 | 16016 | - |
| abilene | isp | Reactive on shortest paths (hybrid, budget 0%) | 8 | 0 | 53.86 / 191.97 | 437 | 20.3 | 5202 | 0.0 |
| abilene | isp | Hybrid, counter keeps top 10% of pairs | 8 | 0 | 50.89 / 189.80 | 342 | 16.6 | 4086 | 25.3 |
| abilene | isp | Hybrid, counter keeps top 25% of pairs | 8 | 0 | 47.89 / 175.61 | 174 | 9.4 | 2298 | 56.5 |
| abilene | isp | Hybrid, counter keeps top 50% of pairs | 8 | 0 | 45.32 / 173.25 | 88 | 5.3 | 1246 | 77.2 |
| abilene | isp | Oracle, busiest 10% of pairs (upper bound) | 8 | 0 | 50.34 / 183.58 | 283 | 14.5 | 3795 | 34.0 |
| abilene | isp | Oracle, busiest 25% of pairs (upper bound) | 8 | 0 | 46.85 / 176.44 | 161 | 8.6 | 2322 | 60.2 |
| abilene | isp | Oracle, busiest 50% of pairs (upper bound) | 8 | 0 | 45.76 / 174.82 | 67 | 3.9 | 1100 | 83.3 |
| abilene | isp | Proactive (one shortest path) | 8 | 0 | 44.62 / 172.82 | 0 | 0.1 | 386 | - |
| abilene | isp | Reactive (learning + spanning tree) | 9 | 0 | 94.90 / 320.06 | 634 | 27.9 | 7523 | - |
| abilene | isp | Reactive, long timeouts | 9 | 0 | 96.93 / 324.71 | 623 | 28.1 | 16858 | - |
| abilene | isp | Reactive on shortest paths (hybrid, budget 0%) | 9 | 0 | 54.64 / 238.45 | 467 | 21.9 | 5446 | 0.0 |
| abilene | isp | Hybrid, counter keeps top 10% of pairs | 9 | 0 | 53.50 / 235.06 | 357 | 18.2 | 4547 | 25.1 |
| abilene | isp | Hybrid, counter keeps top 25% of pairs | 9 | 0 | 49.56 / 237.11 | 213 | 11.4 | 2802 | 51.6 |
| abilene | isp | Hybrid, counter keeps top 50% of pairs | 9 | 0 | 46.82 / 233.63 | 102 | 6.1 | 1420 | 75.4 |
| abilene | isp | Oracle, busiest 10% of pairs (upper bound) | 9 | 0 | 51.96 / 248.07 | 287 | 14.9 | 3860 | 33.4 |
| abilene | isp | Oracle, busiest 25% of pairs (upper bound) | 9 | 0 | 48.77 / 234.53 | 172 | 9.2 | 2397 | 59.0 |
| abilene | isp | Oracle, busiest 50% of pairs (upper bound) | 9 | 0 | 46.55 / 232.31 | 73 | 4.2 | 1304 | 81.8 |
| abilene | isp | Proactive (one shortest path) | 9 | 0 | 45.06 / 232.72 | 0 | 0.1 | 386 | - |
| abilene | isp | Reactive (learning + spanning tree) | 10 | 0 | 106.35 / 340.60 | 603 | 27.2 | 7373 | - |
| abilene | isp | Reactive, long timeouts | 10 | 0 | 105.96 / 339.32 | 594 | 27.0 | 16314 | - |
| abilene | isp | Reactive on shortest paths (hybrid, budget 0%) | 10 | 0 | 57.80 / 252.44 | 448 | 20.8 | 5345 | 0.0 |
| abilene | isp | Hybrid, counter keeps top 10% of pairs | 10 | 0 | 54.96 / 254.77 | 305 | 15.6 | 3747 | 29.2 |
| abilene | isp | Hybrid, counter keeps top 25% of pairs | 10 | 0 | 53.07 / 244.12 | 198 | 10.7 | 2596 | 54.1 |
| abilene | isp | Hybrid, counter keeps top 50% of pairs | 10 | 0 | 49.46 / 241.19 | 88 | 5.3 | 1328 | 79.0 |
| abilene | isp | Oracle, busiest 10% of pairs (upper bound) | 10 | 0 | 55.50 / 263.05 | 289 | 14.5 | 3697 | 31.8 |
| abilene | isp | Oracle, busiest 25% of pairs (upper bound) | 10 | 0 | 51.90 / 242.55 | 162 | 8.7 | 2336 | 59.4 |
| abilene | isp | Oracle, busiest 50% of pairs (upper bound) | 10 | 0 | 48.45 / 243.02 | 63 | 3.7 | 1022 | 84.0 |
| abilene | isp | Proactive (one shortest path) | 10 | 0 | 47.43 / 242.66 | 0 | 0.1 | 386 | - |
| abilene | isp | Reactive (learning + spanning tree) | 11 | 0 | 95.08 / 364.54 | 587 | 26.5 | 7317 | - |
| abilene | isp | Reactive, long timeouts | 11 | 0 | 94.68 / 384.52 | 600 | 27.1 | 16037 | - |
| abilene | isp | Reactive on shortest paths (hybrid, budget 0%) | 11 | 0 | 54.94 / 210.94 | 432 | 20.3 | 5281 | 0.0 |
| abilene | isp | Hybrid, counter keeps top 10% of pairs | 11 | 0 | 52.30 / 207.98 | 344 | 16.7 | 4115 | 27.8 |
| abilene | isp | Hybrid, counter keeps top 25% of pairs | 11 | 0 | 48.79 / 204.92 | 199 | 10.8 | 2757 | 52.7 |
| abilene | isp | Hybrid, counter keeps top 50% of pairs | 11 | 0 | 47.34 / 197.39 | 100 | 5.9 | 1460 | 76.3 |
| abilene | isp | Oracle, busiest 10% of pairs (upper bound) | 11 | 0 | 51.99 / 205.69 | 279 | 14.3 | 3771 | 33.1 |
| abilene | isp | Oracle, busiest 25% of pairs (upper bound) | 11 | 0 | 48.64 / 203.77 | 177 | 9.4 | 2654 | 58.3 |
| abilene | isp | Oracle, busiest 50% of pairs (upper bound) | 11 | 0 | 46.98 / 192.89 | 67 | 3.8 | 1160 | 82.7 |
| abilene | isp | Proactive (one shortest path) | 11 | 0 | 45.75 / 192.56 | 0 | 0.1 | 386 | - |
