# Realistic traffic results (traffic-20261016-012626)

Testbed: Linux Harikrushna 6.18.33.2-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Thu Jun 18 21:54:43 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: uniform

Controller: same machine as Mininet

**Every value is the mean of 5 runs (seeds 7 to 11, a new flow schedule each time) ± the half-width of its 95% confidence interval (Student's t).**

## Traffic generated (identical for every controller within one seed)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Benson et al., IMC 2010 (university data centres) | 6093 ± 101 | 203.1 ± 3.4 | 97.7 ± 9.0 (6%) | 0 ± 0 | 80 ± 1% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 6093 ± 101 / 0 ± 0 | 24.96 ± 0.74 / 23.64 ± 0.70 / 62.97 ± 5.11 | 186.2 ± 16.9 | - |
| tree-d2-f4 | university | Reactive, long timeouts | 6093 ± 101 / 0 ± 0 | 27.81 ± 0.84 / 25.68 ± 0.76 / 75.01 ± 8.78 | 186.8 ± 18.2 | - |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 6093 ± 101 / 0 ± 0 | 24.88 ± 0.76 / 23.65 ± 0.75 / 61.59 ± 4.16 | 182.9 ± 16.4 | - |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 6093 ± 101 / 0 ± 0 | 22.65 ± 0.62 / 21.51 ± 0.66 / 60.54 ± 4.32 | 181.2 ± 17.6 | - |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 6093 ± 101 / 0 ± 0 | 18.91 ± 0.52 / 17.56 ± 0.58 / 56.71 ± 4.95 | 181.8 ± 17.5 | - |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 6093 ± 101 / 0 ± 0 | 13.21 ± 0.62 / 11.19 ± 1.00 / 50.53 ± 2.76 | 171.2 ± 17.1 | - |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 6093 ± 101 / 0 ± 0 | 20.80 ± 0.62 / 20.35 ± 0.40 / 58.76 ± 3.60 | 179.3 ± 15.8 | - |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 6093 ± 101 / 0 ± 0 | 16.43 ± 0.96 / 16.16 ± 0.59 / 53.05 ± 6.78 | 173.9 ± 19.4 | - |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 6093 ± 101 / 0 ± 0 | 11.10 ± 1.02 / 8.41 ± 1.13 / 47.67 ± 6.42 | 168.8 ± 18.7 | - |
| tree-d2-f4 | university | Proactive (one shortest path) | 6093 ± 101 / 0 ± 0 | 5.71 ± 0.78 / 0.96 ± 0.18 / 41.38 ± 4.60 | 164.2 ± 18.7 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 2462 ± 73 | 2461 ± 73 | 64.2 ± 1.0 | 10836 ± 201 | 3342 ± 58 |
| tree-d2-f4 | university | Reactive, long timeouts | 2392 ± 80 | 2392 ± 80 | 62.6 ± 0.7 | 31644 ± 478 | 9728 ± 145 |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 2476 ± 70 | 2475 ± 70 | 64.4 ± 0.8 | 10841 ± 201 | 3341 ± 63 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 2270 ± 62 | 2280 ± 62 | 61.9 ± 0.7 | 9802 ± 110 | 3024 ± 58 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 1943 ± 50 | 1959 ± 50 | 56.3 ± 0.8 | 8336 ± 223 | 2576 ± 77 |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 1255 ± 37 | 1273 ± 39 | 42.1 ± 0.7 | 5947 ± 146 | 1864 ± 95 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 2121 ± 57 | 2120 ± 57 | 59.4 ± 0.6 | 9585 ± 98 | 2960 ± 39 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 1658 ± 59 | 1657 ± 59 | 50.7 ± 0.8 | 7840 ± 94 | 2422 ± 28 |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 961 ± 39 | 960 ± 39 | 34.0 ± 1.2 | 5245 ± 210 | 1629 ± 95 |
| tree-d2-f4 | university | Proactive (one shortest path) | 0 ± 0 | 0 ± 0 | 0.1 ± 0.0 | 624 ± 0 | 192 ± 0 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 0 of 240 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 24 of 240 | 9.6 ± 0.2 | 82 ± 3 | 53 ± 3 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 60 of 240 | 24.5 ± 1.2 | 155 ± 6 | 82 ± 5 |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 120 of 240 | 48.4 ± 0.2 | 227 ± 16 | 75 ± 9 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 24 of 240 | 12.5 ± 0.2 | 24 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 60 of 240 | 29.4 ± 0.5 | 60 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 120 of 240 | 55.4 ± 0.6 | 120 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 7 | 0 | 23.10 / 61.14 | 2534 | 64.7 | 10914 | - |
| tree-d2-f4 | university | Reactive, long timeouts | 7 | 0 | 25.08 / 77.40 | 2446 | 63.2 | 31841 | - |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 7 | 0 | 23.21 / 57.96 | 2539 | 65.0 | 10904 | 0.0 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 7 | 0 | 20.86 / 60.59 | 2325 | 62.4 | 9851 | 9.5 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 7 | 0 | 17.00 / 51.79 | 1977 | 56.3 | 8342 | 25.8 |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 7 | 0 | 10.44 / 49.31 | 1247 | 41.6 | 5885 | 48.4 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 7 | 0 | 20.13 / 55.52 | 2168 | 60.1 | 9610 | 12.7 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 7 | 0 | 15.54 / 47.79 | 1690 | 51.1 | 7767 | 29.9 |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 7 | 0 | 7.12 / 41.03 | 953 | 33.2 | 5016 | 55.9 |
| tree-d2-f4 | university | Proactive (one shortest path) | 7 | 0 | 0.84 / 37.81 | 0 | 0.1 | 624 | - |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 8 | 0 | 24.40 / 69.44 | 2493 | 65.3 | 11068 | - |
| tree-d2-f4 | university | Reactive, long timeouts | 8 | 0 | 26.46 / 71.47 | 2431 | 63.3 | 32163 | - |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 8 | 0 | 24.52 / 61.69 | 2518 | 65.1 | 11087 | 0.0 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 8 | 0 | 21.08 / 59.51 | 2289 | 62.4 | 9728 | 9.7 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 8 | 0 | 17.25 / 55.83 | 1975 | 57.2 | 8398 | 24.9 |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 8 | 0 | 10.48 / 48.76 | 1262 | 42.2 | 5812 | 48.5 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 8 | 0 | 20.45 / 62.31 | 2137 | 59.7 | 9679 | 12.5 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 8 | 0 | 16.15 / 54.30 | 1697 | 51.2 | 7893 | 29.4 |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 8 | 0 | 9.21 / 53.84 | 999 | 35.3 | 5433 | 55.4 |
| tree-d2-f4 | university | Proactive (one shortest path) | 8 | 0 | 0.99 / 44.79 | 0 | 0.0 | 624 | - |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 9 | 0 | 23.67 / 58.28 | 2473 | 63.6 | 10802 | - |
| tree-d2-f4 | university | Reactive, long timeouts | 9 | 0 | 25.53 / 70.06 | 2434 | 62.2 | 31554 | - |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 9 | 0 | 23.15 / 59.67 | 2480 | 63.9 | 10806 | 0.0 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 9 | 0 | 21.92 / 55.41 | 2301 | 61.9 | 9928 | 9.5 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 9 | 0 | 18.09 / 54.38 | 1952 | 55.6 | 8587 | 24.0 |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 9 | 0 | 11.76 / 48.95 | 1302 | 43.0 | 6079 | 48.2 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 9 | 0 | 20.44 / 56.02 | 2147 | 59.4 | 9612 | 12.6 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 9 | 0 | 15.90 / 46.88 | 1681 | 50.9 | 7834 | 29.7 |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 9 | 0 | 7.89 / 43.88 | 953 | 34.3 | 5256 | 55.9 |
| tree-d2-f4 | university | Proactive (one shortest path) | 9 | 0 | 0.86 / 37.35 | 0 | 0.1 | 624 | - |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 10 | 0 | 23.08 / 63.55 | 2429 | 63.5 | 10752 | - |
| tree-d2-f4 | university | Reactive, long timeouts | 10 | 0 | 25.17 / 69.72 | 2353 | 62.4 | 31129 | - |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 10 | 0 | 23.33 / 66.88 | 2443 | 63.9 | 10736 | 0.0 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 10 | 0 | 21.59 / 62.50 | 2204 | 61.3 | 9715 | 9.5 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 10 | 0 | 17.48 / 60.60 | 1932 | 56.5 | 8104 | 23.3 |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 10 | 0 | 11.02 / 53.87 | 1239 | 41.8 | 5895 | 48.5 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 10 | 0 | 19.97 / 59.86 | 2102 | 59.0 | 9559 | 12.2 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 10 | 0 | 16.45 / 57.64 | 1636 | 50.4 | 7939 | 28.9 |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 10 | 0 | 8.54 / 50.64 | 981 | 34.3 | 5374 | 54.9 |
| tree-d2-f4 | university | Proactive (one shortest path) | 10 | 0 | 0.92 / 41.79 | 0 | 0.0 | 624 | - |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 11 | 0 | 23.95 / 62.45 | 2381 | 64.0 | 10643 | - |
| tree-d2-f4 | university | Reactive, long timeouts | 11 | 0 | 26.17 / 86.38 | 2298 | 62.0 | 31534 | - |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 11 | 0 | 24.06 / 61.72 | 2398 | 63.9 | 10674 | 0.0 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 11 | 0 | 22.11 / 64.68 | 2232 | 61.6 | 9789 | 9.6 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 11 | 0 | 17.97 / 60.96 | 1879 | 55.6 | 8247 | 24.5 |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 11 | 0 | 12.27 / 51.78 | 1223 | 41.7 | 6063 | 48.5 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 11 | 0 | 20.79 / 60.08 | 2051 | 58.9 | 9467 | 12.4 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 11 | 0 | 16.76 / 58.62 | 1584 | 49.7 | 7769 | 29.2 |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 11 | 0 | 9.28 / 48.95 | 916 | 33.0 | 5148 | 55.1 |
| tree-d2-f4 | university | Proactive (one shortest path) | 11 | 0 | 1.20 / 45.14 | 0 | 0.0 | 624 | - |
