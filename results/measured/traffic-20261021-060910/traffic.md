# Realistic traffic results (traffic-20261021-060910)

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
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 6093 ± 101 / 0 ± 0 | 26.12 ± 1.16 / 24.79 ± 1.20 / 65.47 ± 4.79 | 185.0 ± 17.3 | - |
| tree-d2-f4 | university | Reactive, long timeouts | 6093 ± 101 / 0 ± 0 | 29.04 ± 0.73 / 27.12 ± 0.73 / 74.76 ± 2.34 | 187.3 ± 16.6 | - |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 6093 ± 101 / 0 ± 0 | 26.30 ± 0.34 / 24.84 ± 0.63 / 66.79 ± 3.39 | 186.2 ± 18.8 | - |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 6093 ± 101 / 0 ± 0 | 5.86 ± 0.76 / 1.01 ± 0.27 / 40.86 ± 4.38 | 163.3 ± 19.1 | - |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 6093 ± 101 / 0 ± 0 | 5.70 ± 0.73 / 0.96 ± 0.19 / 40.33 ± 4.03 | 162.2 ± 18.9 | - |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 6093 ± 101 / 0 ± 0 | 23.32 ± 1.01 / 22.08 ± 1.03 / 62.42 ± 2.40 | 182.4 ± 16.3 | - |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 6093 ± 101 / 0 ± 0 | 19.78 ± 0.63 / 18.40 ± 0.51 / 60.78 ± 3.65 | 179.3 ± 16.8 | - |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 6093 ± 101 / 0 ± 0 | 13.42 ± 0.93 / 11.42 ± 0.94 / 51.05 ± 6.84 | 173.9 ± 26.6 | - |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 6093 ± 101 / 0 ± 0 | 21.73 ± 0.41 / 21.24 ± 0.44 / 60.26 ± 4.16 | 181.0 ± 17.2 | - |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 6093 ± 101 / 0 ± 0 | 16.78 ± 0.78 / 16.66 ± 0.38 / 53.27 ± 4.91 | 174.4 ± 19.0 | - |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 6093 ± 101 / 0 ± 0 | 11.36 ± 0.80 / 8.58 ± 0.94 / 48.26 ± 4.94 | 169.8 ± 19.3 | - |
| tree-d2-f4 | university | Random 10% of pairs (no knowledge) | 6093 ± 101 / 0 ± 0 | 22.78 ± 0.62 / 21.97 ± 0.55 / 63.30 ± 3.96 | 186.6 ± 21.2 | - |
| tree-d2-f4 | university | Random 25% of pairs (no knowledge) | 6093 ± 101 / 0 ± 0 | 18.05 ± 0.78 / 17.73 ± 0.72 / 56.94 ± 3.77 | 178.9 ± 18.2 | - |
| tree-d2-f4 | university | Random 50% of pairs (no knowledge) | 6093 ± 101 / 0 ± 0 | 12.21 ± 0.85 / 9.92 ± 0.88 / 50.07 ± 5.42 | 168.8 ± 16.3 | - |
| tree-d2-f4 | university | Proactive (one shortest path) | 6093 ± 101 / 0 ± 0 | 5.70 ± 0.70 / 0.96 ± 0.20 / 40.61 ± 3.15 | 162.8 ± 19.3 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 2473 ± 82 | 2473 ± 82 | 65.8 ± 1.2 | 10834 ± 187 | 3339 ± 56 |
| tree-d2-f4 | university | Reactive, long timeouts | 2396 ± 62 | 2396 ± 62 | 63.7 ± 0.9 | 31645 ± 480 | 9728 ± 147 |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 2475 ± 73 | 2474 ± 73 | 65.9 ± 0.9 | 10813 ± 221 | 3333 ± 68 |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 20 ± 3 | 20 ± 3 | 0.8 ± 0.1 | 624 ± 0 | 192 ± 0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 3 ± 5 | 2 ± 5 | 0.2 ± 0.1 | 80 ± 0 | 16 ± 0 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 2271 ± 64 | 2281 ± 65 | 63.4 ± 0.9 | 9825 ± 134 | 3021 ± 39 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 1952 ± 51 | 1967 ± 51 | 58.0 ± 0.9 | 8369 ± 86 | 2596 ± 55 |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 1248 ± 17 | 1264 ± 19 | 43.0 ± 0.2 | 5880 ± 133 | 1833 ± 81 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 2132 ± 51 | 2131 ± 51 | 61.0 ± 0.6 | 9586 ± 129 | 2959 ± 46 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 1660 ± 42 | 1659 ± 42 | 52.0 ± 0.9 | 7854 ± 117 | 2426 ± 39 |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 971 ± 38 | 971 ± 38 | 35.3 ± 0.9 | 5255 ± 213 | 1637 ± 86 |
| tree-d2-f4 | university | Random 10% of pairs (no knowledge) | 2176 ± 67 | 2176 ± 67 | 62.0 ± 1.4 | 9745 ± 245 | 2992 ± 78 |
| tree-d2-f4 | university | Random 25% of pairs (no knowledge) | 1763 ± 37 | 1763 ± 37 | 54.3 ± 1.1 | 8204 ± 173 | 2526 ± 95 |
| tree-d2-f4 | university | Random 50% of pairs (no knowledge) | 1073 ± 62 | 1072 ± 62 | 38.5 ± 2.7 | 5680 ± 306 | 1752 ± 131 |
| tree-d2-f4 | university | Proactive (one shortest path) | 0 ± 0 | 0 ± 0 | 0.1 ± 0.0 | 624 ± 0 | 192 ± 0 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 0 of 240 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 0 of 240 | 98.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 0 of 240 | 99.6 ± 0.0 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 24 of 240 | 9.7 ± 0.8 | 81 ± 3 | 52 ± 4 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 60 of 240 | 24.8 ± 0.7 | 151 ± 8 | 76 ± 7 |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 120 of 240 | 48.7 ± 0.7 | 216 ± 13 | 62 ± 10 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 24 of 240 | 12.5 ± 0.2 | 24 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 60 of 240 | 29.4 ± 0.5 | 60 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 120 of 240 | 55.5 ± 0.6 | 120 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Random 10% of pairs (no knowledge) | 24 of 240 | 10.0 ± 0.3 | 24 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Random 25% of pairs (no knowledge) | 60 of 240 | 25.3 ± 0.8 | 60 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Random 50% of pairs (no knowledge) | 120 of 240 | 51.0 ± 0.6 | 120 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 7 | 0 | 23.52 / 60.42 | 2543 | 65.5 | 10895 | - |
| tree-d2-f4 | university | Reactive, long timeouts | 7 | 0 | 26.36 / 75.90 | 2445 | 64.1 | 31852 | - |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 7 | 0 | 24.49 / 64.74 | 2513 | 66.3 | 10908 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 7 | 0 | 0.84 / 37.62 | 21 | 0.8 | 624 | 98.0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 7 | 0 | 0.84 / 40.20 | 1 | 0.1 | 80 | 99.6 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 7 | 0 | 21.14 / 59.12 | 2318 | 63.0 | 9802 | 10.4 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 7 | 0 | 18.06 / 57.05 | 1992 | 58.1 | 8428 | 25.4 |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 7 | 0 | 10.87 / 43.38 | 1245 | 43.0 | 5922 | 49.2 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 7 | 0 | 20.77 / 60.67 | 2164 | 61.4 | 9648 | 12.7 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 7 | 0 | 16.27 / 48.86 | 1700 | 52.9 | 7835 | 29.9 |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 7 | 0 | 7.58 / 45.29 | 975 | 35.4 | 5017 | 56.0 |
| tree-d2-f4 | university | Random 10% of pairs (no knowledge) | 7 | 0 | 21.40 / 60.45 | 2198 | 62.1 | 9783 | 9.8 |
| tree-d2-f4 | university | Random 25% of pairs (no knowledge) | 7 | 0 | 17.64 / 54.96 | 1807 | 55.0 | 8305 | 24.8 |
| tree-d2-f4 | university | Random 50% of pairs (no knowledge) | 7 | 0 | 10.36 / 48.39 | 1122 | 40.3 | 6007 | 50.5 |
| tree-d2-f4 | university | Proactive (one shortest path) | 7 | 0 | 0.82 / 40.71 | 0 | 0.1 | 624 | - |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 8 | 0 | 25.04 / 67.25 | 2509 | 66.8 | 11059 | - |
| tree-d2-f4 | university | Reactive, long timeouts | 8 | 0 | 27.76 / 76.80 | 2438 | 64.1 | 32161 | - |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 8 | 0 | 25.24 / 67.48 | 2539 | 66.7 | 11081 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 8 | 0 | 1.05 / 44.93 | 22 | 0.8 | 624 | 98.1 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 8 | 0 | 0.98 / 44.79 | 10 | 0.2 | 80 | 99.6 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 8 | 0 | 22.19 / 62.48 | 2309 | 64.0 | 9984 | 9.0 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 8 | 0 | 18.25 / 63.59 | 2002 | 58.8 | 8361 | 25.1 |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 8 | 0 | 10.98 / 51.62 | 1264 | 43.3 | 5697 | 49.4 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 8 | 0 | 21.42 / 58.20 | 2151 | 61.4 | 9733 | 12.5 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 8 | 0 | 16.99 / 56.39 | 1674 | 52.2 | 7954 | 29.4 |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 8 | 0 | 9.28 / 52.81 | 1020 | 36.4 | 5426 | 55.4 |
| tree-d2-f4 | university | Random 10% of pairs (no knowledge) | 8 | 0 | 22.58 / 66.60 | 2250 | 63.9 | 10074 | 9.8 |
| tree-d2-f4 | university | Random 25% of pairs (no knowledge) | 8 | 0 | 17.66 / 58.92 | 1777 | 55.5 | 8197 | 26.3 |
| tree-d2-f4 | university | Random 50% of pairs (no knowledge) | 8 | 0 | 10.66 / 53.37 | 1123 | 41.3 | 5782 | 51.4 |
| tree-d2-f4 | university | Proactive (one shortest path) | 8 | 0 | 1.03 / 44.54 | 0 | 0.1 | 624 | - |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 9 | 0 | 25.57 / 63.43 | 2506 | 66.8 | 10810 | - |
| tree-d2-f4 | university | Reactive, long timeouts | 9 | 0 | 27.57 / 71.89 | 2409 | 64.4 | 31557 | - |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 9 | 0 | 25.12 / 64.34 | 2491 | 65.9 | 10737 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 9 | 0 | 0.85 / 37.70 | 23 | 0.8 | 624 | 98.0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 9 | 0 | 0.86 / 35.63 | 1 | 0.1 | 80 | 99.6 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 9 | 0 | 22.73 / 63.67 | 2299 | 64.4 | 9876 | 9.2 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 9 | 0 | 18.41 / 58.42 | 1927 | 58.1 | 8267 | 23.9 |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 9 | 0 | 11.11 / 47.96 | 1254 | 42.9 | 5909 | 48.0 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 9 | 0 | 21.50 / 56.84 | 2154 | 61.3 | 9555 | 12.6 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 9 | 0 | 16.42 / 49.94 | 1668 | 52.0 | 7765 | 29.7 |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 9 | 0 | 8.16 / 43.04 | 955 | 35.5 | 5247 | 55.9 |
| tree-d2-f4 | university | Random 10% of pairs (no knowledge) | 9 | 0 | 22.11 / 59.37 | 2182 | 62.0 | 9649 | 10.2 |
| tree-d2-f4 | university | Random 25% of pairs (no knowledge) | 9 | 0 | 17.03 / 52.94 | 1743 | 53.8 | 7973 | 25.3 |
| tree-d2-f4 | university | Random 50% of pairs (no knowledge) | 9 | 0 | 8.95 / 43.14 | 1045 | 36.9 | 5396 | 51.5 |
| tree-d2-f4 | university | Proactive (one shortest path) | 9 | 0 | 0.83 / 37.72 | 0 | 0.1 | 624 | - |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 10 | 0 | 24.05 / 65.62 | 2426 | 65.0 | 10735 | - |
| tree-d2-f4 | university | Reactive, long timeouts | 10 | 0 | 26.72 / 75.07 | 2350 | 62.6 | 31128 | - |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 10 | 0 | 24.13 / 71.14 | 2436 | 65.9 | 10670 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 10 | 0 | 0.92 / 39.80 | 17 | 0.7 | 624 | 98.0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 10 | 0 | 0.89 / 40.66 | 1 | 0.2 | 80 | 99.6 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 10 | 0 | 21.33 / 62.94 | 2205 | 63.0 | 9706 | 10.1 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 10 | 0 | 18.17 / 61.49 | 1916 | 56.8 | 8352 | 24.7 |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 10 | 0 | 11.41 / 55.69 | 1249 | 42.9 | 5891 | 48.3 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 10 | 0 | 20.95 / 59.97 | 2129 | 60.4 | 9524 | 12.2 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 10 | 0 | 16.80 / 57.99 | 1644 | 51.8 | 7949 | 28.9 |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 10 | 0 | 8.52 / 49.99 | 968 | 34.9 | 5413 | 54.9 |
| tree-d2-f4 | university | Random 10% of pairs (no knowledge) | 10 | 0 | 21.71 / 64.79 | 2146 | 61.3 | 9605 | 10.4 |
| tree-d2-f4 | university | Random 25% of pairs (no knowledge) | 10 | 0 | 17.67 / 57.34 | 1759 | 53.3 | 8221 | 25.4 |
| tree-d2-f4 | university | Random 50% of pairs (no knowledge) | 10 | 0 | 9.42 / 52.37 | 1064 | 37.6 | 5737 | 50.5 |
| tree-d2-f4 | university | Proactive (one shortest path) | 10 | 0 | 0.91 / 39.22 | 0 | 0.1 | 624 | - |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 11 | 0 | 25.76 / 70.64 | 2383 | 64.9 | 10672 | - |
| tree-d2-f4 | university | Reactive, long timeouts | 11 | 0 | 27.18 / 74.13 | 2338 | 63.2 | 31528 | - |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 11 | 0 | 25.24 / 66.27 | 2396 | 64.7 | 10671 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 11 | 0 | 1.37 / 44.27 | 19 | 0.8 | 624 | 98.0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 11 | 0 | 1.21 / 40.35 | 1 | 0.2 | 80 | 99.6 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 11 | 0 | 23.01 / 63.91 | 2227 | 62.8 | 9759 | 9.6 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 11 | 0 | 19.09 / 63.37 | 1923 | 58.3 | 8439 | 24.9 |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 11 | 0 | 12.72 / 56.64 | 1226 | 42.7 | 5980 | 48.6 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 11 | 0 | 21.56 / 65.63 | 2062 | 60.4 | 9472 | 12.4 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 11 | 0 | 16.84 / 53.18 | 1611 | 51.0 | 7765 | 29.2 |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 11 | 0 | 9.38 / 50.17 | 937 | 34.3 | 5171 | 55.2 |
| tree-d2-f4 | university | Random 10% of pairs (no knowledge) | 11 | 0 | 22.06 / 65.28 | 2106 | 61.0 | 9613 | 9.8 |
| tree-d2-f4 | university | Random 25% of pairs (no knowledge) | 11 | 0 | 18.65 / 60.51 | 1730 | 54.1 | 8322 | 24.7 |
| tree-d2-f4 | university | Random 50% of pairs (no knowledge) | 11 | 0 | 10.18 / 53.10 | 1009 | 36.5 | 5476 | 51.0 |
| tree-d2-f4 | university | Proactive (one shortest path) | 11 | 0 | 1.21 / 40.86 | 0 | 0.1 | 624 | - |
