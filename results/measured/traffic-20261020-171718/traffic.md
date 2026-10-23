# Realistic traffic results (traffic-20261020-171718)

Testbed: Linux Harikrushna 6.18.33.2-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Thu Jun 18 21:54:43 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet

**Every value is the mean of 5 runs (seeds 7 to 11, a new flow schedule each time) ± the half-width of its 95% confidence interval (Student's t).**

## Traffic generated (identical for every controller within one seed)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Benson et al., IMC 2010 (university data centres) | 6073 ± 41 | 202.4 ± 1.4 | 85.5 ± 14.1 (5%) | 0 ± 0 | 83 ± 8% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 6073 ± 41 / 0 ± 0 | 50.41 ± 16.00 / 47.74 ± 14.84 / 118.45 ± 37.34 | 196.4 ± 18.7 | - |
| tree-d2-f4 | university | Reactive, long timeouts | 6073 ± 41 / 0 ± 0 | 57.33 ± 11.37 / 52.07 ± 14.24 / 149.11 ± 19.77 | 201.3 ± 21.1 | - |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 6073 ± 41 / 0 ± 0 | 55.49 ± 5.65 / 52.52 ± 5.02 / 129.89 ± 12.66 | 202.4 ± 24.1 | - |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 6073 ± 41 / 0 ± 0 | 5.93 ± 1.13 / 1.49 ± 0.27 / 39.10 ± 5.10 | 149.2 ± 20.5 | - |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 6073 ± 41 / 0 ± 0 | 5.92 ± 1.23 / 1.47 ± 0.22 / 40.31 ± 5.40 | 149.6 ± 22.1 | - |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 6073 ± 41 / 0 ± 0 | 31.60 ± 5.65 / 29.88 ± 5.70 / 96.71 ± 17.92 | 177.7 ± 17.5 | - |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 6073 ± 41 / 0 ± 0 | 16.31 ± 2.52 / 11.98 ± 3.49 / 68.02 ± 8.19 | 159.9 ± 17.3 | - |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 6073 ± 41 / 0 ± 0 | 10.48 ± 1.01 / 3.51 ± 1.03 / 57.18 ± 4.62 | 152.9 ± 20.3 | - |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 6073 ± 41 / 0 ± 1 | 19.41 ± 2.24 / 16.62 ± 3.52 / 66.90 ± 4.60 | 162.4 ± 19.5 | - |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 6073 ± 41 / 0 ± 0 | 12.28 ± 1.28 / 6.28 ± 1.24 / 54.47 ± 5.70 | 154.7 ± 21.4 | - |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 6073 ± 41 / 0 ± 0 | 8.25 ± 0.98 / 2.19 ± 0.74 / 45.06 ± 5.45 | 152.0 ± 22.5 | - |
| tree-d2-f4 | university | Random 10% of pairs (no knowledge) | 6073 ± 41 / 0 ± 0 | 45.96 ± 7.39 / 45.20 ± 6.75 / 113.78 ± 14.84 | 190.6 ± 22.9 | - |
| tree-d2-f4 | university | Random 25% of pairs (no knowledge) | 6073 ± 41 / 0 ± 0 | 33.90 ± 6.47 / 35.07 ± 5.98 / 90.79 ± 13.22 | 178.9 ± 25.7 | - |
| tree-d2-f4 | university | Random 50% of pairs (no knowledge) | 6073 ± 41 / 0 ± 0 | 20.32 ± 6.68 / 18.78 ± 10.91 / 69.45 ± 14.18 | 164.8 ± 22.5 | - |
| tree-d2-f4 | university | Proactive (one shortest path) | 6073 ± 41 / 0 ± 0 | 5.76 ± 1.15 / 1.49 ± 0.27 / 39.28 ± 4.37 | 148.6 ± 19.5 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 2402 ± 99 | 2402 ± 99 | 81.8 ± 11.0 | 10979 ± 658 | 3443 ± 315 |
| tree-d2-f4 | university | Reactive, long timeouts | 2349 ± 88 | 2349 ± 88 | 81.9 ± 8.2 | 32350 ± 2034 | 10104 ± 987 |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 2352 ± 110 | 2351 ± 110 | 84.9 ± 2.1 | 10987 ± 665 | 3448 ± 321 |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 34 ± 14 | 34 ± 14 | 2.1 ± 0.6 | 624 ± 1 | 192 ± 0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 8 ± 3 | 7 ± 3 | 0.4 ± 0.2 | 80 ± 0 | 16 ± 0 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 1690 ± 269 | 1697 ± 274 | 73.7 ± 5.8 | 7666 ± 1102 | 2372 ± 386 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 903 ± 178 | 922 ± 181 | 52.3 ± 6.6 | 5084 ± 776 | 1565 ± 232 |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 453 ± 72 | 479 ± 74 | 31.7 ± 3.2 | 3115 ± 331 | 967 ± 106 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 1099 ± 159 | 1099 ± 159 | 58.0 ± 4.2 | 5617 ± 648 | 1751 ± 204 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 646 ± 118 | 645 ± 118 | 40.5 ± 5.2 | 3589 ± 530 | 1101 ± 174 |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 295 ± 47 | 294 ± 47 | 21.6 ± 2.8 | 2013 ± 270 | 618 ± 86 |
| tree-d2-f4 | university | Random 10% of pairs (no knowledge) | 2101 ± 191 | 2100 ± 191 | 81.4 ± 2.6 | 9969 ± 936 | 3120 ± 370 |
| tree-d2-f4 | university | Random 25% of pairs (no knowledge) | 1781 ± 158 | 1780 ± 158 | 75.6 ± 3.7 | 8574 ± 870 | 2687 ± 309 |
| tree-d2-f4 | university | Random 50% of pairs (no knowledge) | 1135 ± 355 | 1134 ± 355 | 58.5 ± 10.7 | 6055 ± 1636 | 1927 ± 575 |
| tree-d2-f4 | university | Proactive (one shortest path) | 0 ± 0 | 0 ± 0 | 0.1 ± 0.0 | 624 ± 0 | 192 ± 0 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 0 of 240 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 0 of 240 | 97.9 ± 0.0 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 0 of 240 | 99.6 ± 0.1 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 24 of 240 | 33.4 ± 12.6 | 63 ± 20 | 32 ± 24 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 60 of 240 | 60.6 ± 6.6 | 151 ± 13 | 73 ± 17 |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 120 of 240 | 78.9 ± 2.8 | 223 ± 3 | 71 ± 7 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 24 of 240 | 49.3 ± 6.0 | 24 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 60 of 240 | 68.2 ± 4.3 | 60 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 120 of 240 | 84.7 ± 2.1 | 120 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Random 10% of pairs (no knowledge) | 24 of 240 | 9.9 ± 7.2 | 24 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Random 25% of pairs (no knowledge) | 60 of 240 | 23.9 ± 7.9 | 60 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Random 50% of pairs (no knowledge) | 120 of 240 | 49.8 ± 12.3 | 120 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 7 | 0 | 27.64 / 69.05 | 2468 | 66.1 | 11163 | - |
| tree-d2-f4 | university | Reactive, long timeouts | 7 | 0 | 33.14 / 158.51 | 2344 | 70.2 | 32631 | - |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 7 | 0 | 54.50 / 122.68 | 2296 | 83.9 | 11148 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 7 | 0 | 1.59 / 44.87 | 36 | 2.3 | 624 | 97.9 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 7 | 0 | 1.56 / 45.78 | 4 | 0.3 | 80 | 99.6 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 7 | 0 | 24.04 / 83.34 | 1421 | 67.8 | 6429 | 46.3 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 7 | 0 | 11.96 / 73.53 | 832 | 50.1 | 4914 | 63.6 |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 7 | 0 | 4.31 / 62.54 | 438 | 30.9 | 3250 | 79.6 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 7 | 1 | 16.61 / 68.33 | 997 | 54.9 | 5336 | 51.6 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 7 | 0 | 6.71 / 59.92 | 578 | 37.9 | 3293 | 70.6 |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 7 | 0 | 2.65 / 52.17 | 272 | 20.3 | 1926 | 85.7 |
| tree-d2-f4 | university | Random 10% of pairs (no knowledge) | 7 | 0 | 38.57 / 111.01 | 1845 | 78.4 | 8883 | 19.8 |
| tree-d2-f4 | university | Random 25% of pairs (no knowledge) | 7 | 0 | 41.05 / 105.24 | 1915 | 78.9 | 9512 | 18.1 |
| tree-d2-f4 | university | Random 50% of pairs (no knowledge) | 7 | 0 | 19.73 / 68.75 | 1094 | 58.9 | 6006 | 50.9 |
| tree-d2-f4 | university | Proactive (one shortest path) | 7 | 0 | 1.59 / 43.51 | 0 | 0.1 | 624 | - |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 8 | 0 | 57.07 / 134.91 | 2381 | 85.5 | 11277 | - |
| tree-d2-f4 | university | Reactive, long timeouts | 8 | 0 | 61.87 / 159.28 | 2361 | 85.3 | 33337 | - |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 8 | 0 | 55.65 / 134.42 | 2372 | 85.4 | 11309 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 8 | 0 | 1.83 / 39.74 | 37 | 2.3 | 624 | 97.9 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 8 | 0 | 1.74 / 41.37 | 6 | 0.3 | 80 | 99.5 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 8 | 0 | 25.89 / 85.86 | 1489 | 69.4 | 7048 | 37.6 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 8 | 0 | 10.10 / 62.18 | 748 | 47.0 | 4554 | 66.2 |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 8 | 0 | 4.36 / 55.99 | 369 | 28.3 | 2656 | 82.1 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 8 | 0 | 14.49 / 62.02 | 979 | 54.9 | 5040 | 54.0 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 8 | 0 | 7.08 / 53.60 | 554 | 36.7 | 3173 | 71.4 |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 8 | 0 | 2.98 / 43.96 | 255 | 19.5 | 1754 | 86.3 |
| tree-d2-f4 | university | Random 10% of pairs (no knowledge) | 8 | 0 | 53.10 / 128.37 | 2235 | 84.1 | 10784 | 6.0 |
| tree-d2-f4 | university | Random 25% of pairs (no knowledge) | 8 | 0 | 38.84 / 91.34 | 1850 | 76.7 | 9068 | 21.4 |
| tree-d2-f4 | university | Random 50% of pairs (no knowledge) | 8 | 0 | 26.35 / 87.62 | 1318 | 64.4 | 6954 | 43.6 |
| tree-d2-f4 | university | Proactive (one shortest path) | 8 | 0 | 1.82 / 41.80 | 0 | 0.1 | 624 | - |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 9 | 0 | 55.35 / 146.24 | 2479 | 86.8 | 11362 | - |
| tree-d2-f4 | university | Reactive, long timeouts | 9 | 0 | 59.43 / 163.63 | 2440 | 85.9 | 33811 | - |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 9 | 0 | 54.65 / 145.85 | 2484 | 87.6 | 11405 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 9 | 0 | 1.39 / 39.88 | 43 | 2.4 | 624 | 97.9 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 9 | 0 | 1.40 / 42.09 | 9 | 0.4 | 80 | 99.5 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 9 | 0 | 32.06 / 94.51 | 1828 | 77.2 | 8514 | 34.3 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 9 | 0 | 13.74 / 65.60 | 968 | 53.4 | 5612 | 59.7 |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 9 | 0 | 3.43 / 55.38 | 473 | 31.8 | 3286 | 78.3 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 9 | 0 | 16.99 / 66.98 | 1127 | 58.6 | 5922 | 48.7 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 9 | 0 | 6.39 / 51.67 | 666 | 40.8 | 3688 | 67.5 |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 9 | 0 | 2.01 / 44.62 | 304 | 22.0 | 2058 | 84.3 |
| tree-d2-f4 | university | Random 10% of pairs (no knowledge) | 9 | 0 | 46.93 / 123.67 | 2198 | 82.1 | 10492 | 9.5 |
| tree-d2-f4 | university | Random 25% of pairs (no knowledge) | 9 | 0 | 29.94 / 90.81 | 1635 | 73.2 | 7886 | 31.5 |
| tree-d2-f4 | university | Random 50% of pairs (no knowledge) | 9 | 0 | 9.16 / 59.37 | 823 | 47.8 | 4730 | 61.8 |
| tree-d2-f4 | university | Proactive (one shortest path) | 9 | 0 | 1.38 / 39.62 | 0 | 0.1 | 624 | - |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 10 | 0 | 52.25 / 128.84 | 2400 | 86.2 | 11034 | - |
| tree-d2-f4 | university | Reactive, long timeouts | 10 | 0 | 55.83 / 136.01 | 2359 | 84.7 | 32371 | - |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 10 | 0 | 52.12 / 123.88 | 2357 | 84.1 | 11003 | 0.1 |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 10 | 0 | 1.34 / 33.58 | 41 | 2.3 | 622 | 97.9 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 10 | 0 | 1.36 / 34.30 | 8 | 0.4 | 80 | 99.6 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 10 | 0 | 33.91 / 119.48 | 1848 | 76.6 | 8261 | 29.8 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 10 | 0 | 8.51 / 62.31 | 847 | 49.9 | 4477 | 61.5 |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 10 | 0 | 2.46 / 52.91 | 457 | 31.9 | 3107 | 78.9 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 10 | 0 | 13.90 / 65.17 | 1094 | 58.2 | 5430 | 50.8 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 10 | 0 | 4.56 / 48.86 | 634 | 39.6 | 3525 | 68.7 |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 10 | 0 | 1.67 / 40.08 | 290 | 21.0 | 1980 | 85.2 |
| tree-d2-f4 | university | Random 10% of pairs (no knowledge) | 10 | 0 | 45.16 / 99.97 | 2143 | 81.1 | 10095 | 8.5 |
| tree-d2-f4 | university | Random 25% of pairs (no knowledge) | 10 | 0 | 31.02 / 75.17 | 1655 | 71.9 | 7988 | 29.9 |
| tree-d2-f4 | university | Random 50% of pairs (no knowledge) | 10 | 0 | 28.20 / 71.33 | 1521 | 69.1 | 7754 | 36.5 |
| tree-d2-f4 | university | Proactive (one shortest path) | 10 | 0 | 1.37 / 35.55 | 0 | 0.1 | 624 | - |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 11 | 0 | 46.38 / 113.19 | 2281 | 84.5 | 10057 | - |
| tree-d2-f4 | university | Reactive, long timeouts | 11 | 0 | 50.10 / 128.12 | 2241 | 83.3 | 29602 | - |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 11 | 0 | 45.66 / 122.63 | 2249 | 83.4 | 10068 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 11 | 0 | 1.31 / 37.42 | 15 | 1.3 | 624 | 97.9 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 11 | 0 | 1.30 / 38.03 | 10 | 0.6 | 80 | 99.6 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 11 | 0 | 33.53 / 100.36 | 1865 | 77.4 | 8077 | 18.7 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 11 | 0 | 15.57 / 76.45 | 1117 | 60.9 | 5862 | 52.1 |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 11 | 0 | 2.99 / 59.11 | 529 | 35.6 | 3278 | 75.8 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 11 | 0 | 21.09 / 72.00 | 1299 | 63.2 | 6358 | 41.4 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 11 | 0 | 6.68 / 58.28 | 796 | 47.5 | 4264 | 62.6 |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 11 | 0 | 1.65 / 44.46 | 354 | 25.3 | 2346 | 82.0 |
| tree-d2-f4 | university | Random 10% of pairs (no knowledge) | 11 | 0 | 42.22 / 105.90 | 2084 | 81.4 | 9592 | 5.5 |
| tree-d2-f4 | university | Random 25% of pairs (no knowledge) | 11 | 0 | 34.51 / 91.42 | 1849 | 77.3 | 8418 | 18.6 |
| tree-d2-f4 | university | Random 50% of pairs (no knowledge) | 11 | 0 | 10.44 / 60.17 | 919 | 52.3 | 4832 | 55.9 |
| tree-d2-f4 | university | Proactive (one shortest path) | 11 | 0 | 1.30 / 35.93 | 0 | 0.1 | 624 | - |
