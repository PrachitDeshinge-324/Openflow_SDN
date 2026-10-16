# Realistic traffic results (traffic-20261015-225412)

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
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 6073 ± 41 / 0 ± 0 | 29.60 ± 2.97 / 27.86 ± 2.38 / 75.15 ± 12.30 | 175.5 ± 18.9 | - |
| tree-d2-f4 | university | Reactive, long timeouts | 6073 ± 41 / 0 ± 0 | 31.47 ± 4.75 / 29.64 ± 4.10 / 82.54 ± 17.83 | 174.3 ± 24.0 | - |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 6073 ± 41 / 0 ± 0 | 28.71 ± 4.42 / 27.29 ± 3.91 / 70.32 ± 10.64 | 172.6 ± 21.6 | - |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 6073 ± 41 / 0 ± 0 | 18.65 ± 2.90 / 17.73 ± 2.85 / 61.72 ± 12.48 | 163.5 ± 21.5 | - |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 6073 ± 42 / 0 ± 1 | 11.51 ± 2.10 / 8.36 ± 1.38 / 59.92 ± 30.88 | 154.4 ± 20.0 | - |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 6073 ± 41 / 0 ± 0 | 7.62 ± 1.05 / 2.80 ± 0.95 / 43.19 ± 4.32 | 149.5 ± 22.3 | - |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 6073 ± 41 / 0 ± 0 | 12.81 ± 1.13 / 11.12 ± 1.33 / 47.72 ± 5.19 | 156.1 ± 22.8 | - |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 6073 ± 41 / 0 ± 0 | 8.71 ± 0.50 / 4.95 ± 0.63 / 44.90 ± 8.59 | 149.4 ± 20.1 | - |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 6073 ± 41 / 0 ± 0 | 6.27 ± 0.87 / 1.68 ± 0.70 / 38.32 ± 4.75 | 145.9 ± 20.6 | - |
| tree-d2-f4 | university | Proactive (one shortest path) | 6073 ± 41 / 0 ± 0 | 5.13 ± 1.07 / 0.96 ± 0.21 / 37.63 ± 4.10 | 145.5 ± 21.4 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 2553 ± 114 | 2552 ± 114 | 67.2 ± 1.9 | 10965 ± 637 | 3438 ± 314 |
| tree-d2-f4 | university | Reactive, long timeouts | 2454 ± 106 | 2453 ± 106 | 64.8 ± 2.6 | 32363 ± 2018 | 10109 ± 981 |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 2549 ± 130 | 2548 ± 130 | 68.1 ± 3.1 | 10983 ± 663 | 3440 ± 325 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 1819 ± 196 | 1827 ± 196 | 55.9 ± 3.4 | 8005 ± 872 | 2520 ± 319 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 936 ± 209 | 952 ± 211 | 35.4 ± 5.8 | 5278 ± 1205 | 1645 ± 389 |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 448 ± 66 | 470 ± 69 | 18.7 ± 2.4 | 2938 ± 347 | 914 ± 114 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 1145 ± 188 | 1145 ± 188 | 41.6 ± 3.8 | 5621 ± 704 | 1753 ± 224 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 658 ± 118 | 657 ± 118 | 25.6 ± 3.1 | 3586 ± 555 | 1101 ± 181 |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 324 ± 53 | 323 ± 53 | 12.9 ± 1.5 | 2012 ± 262 | 618 ± 83 |
| tree-d2-f4 | university | Proactive (one shortest path) | 0 ± 0 | 0 ± 0 | 0.1 ± 0.0 | 624 ± 0 | 192 ± 0 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 0 of 240 | 0.0 ± 0.1 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 24 of 240 | 30.8 ± 10.2 | 70 ± 18 | 40 ± 18 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 60 of 240 | 60.7 ± 5.5 | 144 ± 8 | 64 ± 11 |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 120 of 240 | 78.9 ± 1.8 | 217 ± 8 | 63 ± 9 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 24 of 240 | 49.3 ± 6.0 | 24 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 60 of 240 | 68.2 ± 4.3 | 60 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 120 of 240 | 84.7 ± 2.1 | 120 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 7 | 0 | 27.73 / 85.18 | 2483 | 67.2 | 11168 | - |
| tree-d2-f4 | university | Reactive, long timeouts | 7 | 0 | 30.50 / 95.21 | 2389 | 65.3 | 32629 | - |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 7 | 0 | 29.19 / 72.43 | 2461 | 68.2 | 11174 | 0.1 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 7 | 0 | 17.66 / 64.07 | 1599 | 53.5 | 7892 | 35.7 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 7 | 0 | 7.37 / 56.16 | 783 | 30.7 | 4410 | 65.0 |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 7 | 0 | 3.55 / 49.17 | 390 | 17.6 | 2645 | 79.3 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 7 | 0 | 11.76 / 52.77 | 1058 | 40.7 | 5296 | 51.6 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 7 | 0 | 5.00 / 55.97 | 597 | 23.2 | 3303 | 70.6 |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 7 | 0 | 2.02 / 43.08 | 307 | 12.3 | 1940 | 85.7 |
| tree-d2-f4 | university | Proactive (one shortest path) | 7 | 0 | 1.00 / 41.72 | 0 | 0.1 | 624 | - |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 8 | 0 | 29.36 / 77.85 | 2566 | 68.5 | 11263 | - |
| tree-d2-f4 | university | Reactive, long timeouts | 8 | 0 | 29.96 / 77.34 | 2479 | 65.2 | 33344 | - |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 8 | 0 | 27.21 / 67.59 | 2580 | 68.1 | 11322 | 0.0 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 8 | 0 | 21.37 / 65.90 | 1974 | 60.0 | 8638 | 23.6 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 8 | 1 | 7.39 / 46.49 | 735 | 30.2 | 4264 | 64.9 |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 8 | 0 | 3.54 / 42.68 | 396 | 16.3 | 2922 | 81.0 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 8 | 0 | 10.12 / 47.54 | 969 | 36.7 | 5008 | 54.0 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 8 | 0 | 5.56 / 45.58 | 567 | 23.0 | 3137 | 71.4 |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 8 | 0 | 2.46 / 40.59 | 286 | 11.3 | 1746 | 86.3 |
| tree-d2-f4 | university | Proactive (one shortest path) | 8 | 0 | 1.21 / 39.11 | 0 | 0.1 | 624 | - |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 9 | 0 | 29.83 / 83.00 | 2672 | 68.7 | 11314 | - |
| tree-d2-f4 | university | Reactive, long timeouts | 9 | 0 | 33.04 / 100.36 | 2558 | 66.8 | 33842 | - |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 9 | 0 | 30.17 / 83.84 | 2639 | 70.2 | 11320 | 0.1 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 9 | 0 | 17.66 / 74.57 | 1879 | 57.2 | 8513 | 37.1 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 9 | 0 | 10.07 / 103.71 | 987 | 39.8 | 5559 | 61.7 |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 9 | 0 | 2.86 / 42.04 | 511 | 21.4 | 3362 | 78.4 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 9 | 0 | 12.21 / 50.96 | 1193 | 44.2 | 5921 | 48.7 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 9 | 0 | 5.07 / 43.43 | 669 | 27.2 | 3681 | 67.5 |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 9 | 0 | 1.56 / 37.68 | 321 | 13.0 | 2063 | 84.3 |
| tree-d2-f4 | university | Proactive (one shortest path) | 9 | 0 | 0.89 / 37.40 | 0 | 0.0 | 624 | - |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 10 | 0 | 27.40 / 62.54 | 2601 | 66.6 | 11010 | - |
| tree-d2-f4 | university | Reactive, long timeouts | 10 | 0 | 30.56 / 70.53 | 2496 | 65.6 | 32348 | - |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 10 | 0 | 27.83 / 66.70 | 2646 | 70.0 | 11047 | 0.0 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 10 | 0 | 15.06 / 48.29 | 1712 | 53.8 | 6869 | 37.4 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 10 | 0 | 8.65 / 48.73 | 1080 | 39.4 | 6639 | 56.2 |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 10 | 0 | 2.15 / 40.12 | 462 | 19.1 | 3022 | 79.2 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 10 | 0 | 9.81 / 42.89 | 1135 | 42.9 | 5434 | 50.8 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 10 | 0 | 4.15 / 37.17 | 643 | 25.7 | 3513 | 68.7 |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 10 | 0 | 1.26 / 32.90 | 309 | 13.1 | 1982 | 85.2 |
| tree-d2-f4 | university | Proactive (one shortest path) | 10 | 0 | 0.93 / 32.69 | 0 | 0.1 | 624 | - |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 11 | 0 | 24.96 / 67.17 | 2441 | 65.0 | 10071 | - |
| tree-d2-f4 | university | Reactive, long timeouts | 11 | 0 | 24.12 / 69.28 | 2345 | 61.3 | 29653 | - |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 11 | 0 | 22.05 / 61.04 | 2416 | 64.0 | 10050 | 0.0 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 11 | 0 | 16.89 / 55.77 | 1931 | 54.8 | 8113 | 20.2 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 11 | 0 | 8.30 / 44.51 | 1098 | 36.8 | 5518 | 56.0 |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 11 | 0 | 1.90 / 41.92 | 479 | 19.0 | 2738 | 76.9 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 11 | 0 | 11.68 / 44.47 | 1370 | 43.5 | 6446 | 41.4 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 11 | 0 | 4.96 / 42.36 | 812 | 28.8 | 4296 | 62.5 |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 11 | 0 | 1.08 / 37.35 | 397 | 14.6 | 2327 | 82.0 |
| tree-d2-f4 | university | Proactive (one shortest path) | 11 | 0 | 0.75 / 37.22 | 0 | 0.0 | 624 | - |
