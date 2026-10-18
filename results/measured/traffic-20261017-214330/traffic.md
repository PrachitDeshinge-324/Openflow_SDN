# Realistic traffic results (traffic-20261017-214330)

Testbed: Linux Harikrushna 6.18.33.2-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Thu Jun 18 21:54:43 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: uniform

Controller: same machine as Mininet

**Every value is the mean of 5 runs (seeds 7 to 11, a new flow schedule each time) ± the half-width of its 95% confidence interval (Student's t).**

## Traffic generated (identical for every controller within one seed)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Benson et al., IMC 2010 (university data centres) | 6093 ± 101 | 203.1 ± 3.4 | 97.7 ± 9.0 (6%) | 0 ± 0 | 80 ± 1% |
| fattree-k4 | websearch | DCTCP, SIGCOMM 2010 / pFabric web search workload | 1136 ± 49 | 37.9 ± 1.6 | 477.9 ± 38.1 (30%) | 15 ± 4 | 93 ± 1% |
| fattree-k4 | datamining | VL2, SIGCOMM 2009 / pFabric data mining workload | 1689 ± 40 | 56.3 ± 1.3 | 476.0 ± 29.6 (30%) | 74 ± 4 | 93 ± 0% |
| abilene | isp | Abilene traffic matrices (Zhang et al., IMC 2005) + SURGE flow sizes | 1749 ± 43 | 58.3 ± 1.4 | 28.5 ± 2.9 (3%) | 0 ± 0 | 100 ± 0% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 6093 ± 101 / 0 ± 0 | 34.20 ± 4.60 / 31.98 ± 4.50 / 92.07 ± 25.46 | 195.3 ± 10.9 | - |
| tree-d2-f4 | university | Proactive (one shortest path) | 6093 ± 101 / 0 ± 0 | 5.91 ± 0.72 / 1.15 ± 0.24 / 41.44 ± 4.39 | 165.0 ± 17.9 | - |
| fattree-k4 | websearch | Reactive (learning + spanning tree) | 1136 ± 49 / 0 ± 0 | 120.54 ± 15.34 / 115.53 ± 16.88 / 308.49 ± 34.87 | 2264.8 ± 608.1 | 10299.7 ± 3337.9 |
| fattree-k4 | websearch | Proactive (one shortest path) | 1136 ± 49 / 0 ± 0 | 67.45 ± 8.84 / 57.27 ± 8.03 / 243.90 ± 20.34 | 2225.3 ± 623.8 | 10472.3 ± 3352.4 |
| fattree-k4 | websearch | Proactive (ECMP) | 1136 ± 49 / 0 ± 0 | 29.19 ± 3.69 / 16.99 ± 3.37 / 193.98 ± 39.31 | 620.0 ± 80.3 | 3185.8 ± 618.8 |
| fattree-k4 | datamining | Reactive (learning + spanning tree) | 1689 ± 40 / 0 ± 0 | 79.73 ± 12.27 / 80.54 ± 12.63 / 183.31 ± 30.34 | 720.3 ± 131.4 | 9850.4 ± 769.2 |
| fattree-k4 | datamining | Proactive (one shortest path) | 1689 ± 40 / 0 ± 0 | 26.44 ± 1.20 / 26.20 ± 1.97 / 99.49 ± 22.55 | 689.4 ± 83.2 | 9981.6 ± 658.5 |
| fattree-k4 | datamining | Proactive (ECMP) | 1689 ± 40 / 0 ± 0 | 14.65 ± 1.63 / 9.58 ± 2.38 / 67.32 ± 9.25 | 312.2 ± 44.2 | 3555.8 ± 450.9 |
| abilene | isp | Reactive (learning + spanning tree) | 1749 ± 43 / 0 ± 0 | 114.05 ± 2.16 / 101.47 ± 4.51 / 350.02 ± 16.92 | 255.1 ± 24.8 | 1613.5 ± 59.3 |
| abilene | isp | Proactive (one shortest path) | 1749 ± 43 / 0 ± 0 | 59.13 ± 3.06 / 46.25 ± 1.18 / 206.50 ± 37.28 | 177.8 ± 10.3 | 1459.5 ± 398.8 |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 2417 ± 47 | 2416 ± 47 | 72.2 ± 4.8 | 10836 ± 196 | 3336 ± 59 |
| tree-d2-f4 | university | Proactive (one shortest path) | 0 ± 0 | 0 ± 0 | 0.1 ± 0.0 | 624 ± 0 | 192 ± 0 |
| fattree-k4 | websearch | Reactive (learning + spanning tree) | 489 ± 22 | 468 ± 21 | 36.5 ± 4.5 | 4329 ± 419 | 722 ± 79 |
| fattree-k4 | websearch | Proactive (one shortest path) | 0 ± 0 | 0 ± 0 | 0.2 ± 0.1 | 1072 ± 0 | 192 ± 0 |
| fattree-k4 | websearch | Proactive (ECMP) | 0 ± 0 | 0 ± 0 | 0.3 ± 0.1 | 1072 ± 0 | 58 ± 0 |
| fattree-k4 | datamining | Reactive (learning + spanning tree) | 684 ± 29 | 664 ± 29 | 47.0 ± 4.1 | 5862 ± 218 | 979 ± 31 |
| fattree-k4 | datamining | Proactive (one shortest path) | 0 ± 0 | 0 ± 0 | 0.2 ± 0.1 | 1072 ± 0 | 192 ± 0 |
| fattree-k4 | datamining | Proactive (ECMP) | 0 ± 0 | 0 ± 0 | 0.3 ± 0.1 | 1072 ± 0 | 58 ± 0 |
| abilene | isp | Reactive (learning + spanning tree) | 611 ± 20 | 606 ± 19 | 31.9 ± 3.5 | 7332 ± 160 | 1080 ± 32 |
| abilene | isp | Proactive (one shortest path) | 0 ± 0 | 0 ± 0 | 0.1 ± 0.0 | 386 ± 0 | 62 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 7 | 0 | 33.09 / 126.37 | 2428 | 72.9 | 10917 | - |
| tree-d2-f4 | university | Proactive (one shortest path) | 7 | 0 | 0.85 / 38.16 | 0 | 0.1 | 624 | - |
| fattree-k4 | websearch | Reactive (learning + spanning tree) | 7 | 0 | 121.14 / 333.36 | 480 | 35.8 | 4632 | - |
| fattree-k4 | websearch | Proactive (one shortest path) | 7 | 0 | 61.86 / 245.25 | 0 | 0.2 | 1072 | - |
| fattree-k4 | websearch | Proactive (ECMP) | 7 | 0 | 17.16 / 164.02 | 0 | 0.2 | 1072 | - |
| fattree-k4 | datamining | Reactive (learning + spanning tree) | 7 | 0 | 77.22 / 212.27 | 704 | 46.9 | 6104 | - |
| fattree-k4 | datamining | Proactive (one shortest path) | 7 | 0 | 24.83 / 123.09 | 0 | 0.2 | 1072 | - |
| fattree-k4 | datamining | Proactive (ECMP) | 7 | 0 | 9.67 / 59.33 | 0 | 0.2 | 1072 | - |
| abilene | isp | Reactive (learning + spanning tree) | 7 | 0 | 101.46 / 354.09 | 619 | 34.5 | 7166 | - |
| abilene | isp | Proactive (one shortest path) | 7 | 0 | 47.03 / 189.85 | 0 | 0.1 | 386 | - |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 8 | 0 | 33.73 / 91.14 | 2456 | 74.5 | 11065 | - |
| tree-d2-f4 | university | Proactive (one shortest path) | 8 | 0 | 1.07 / 44.66 | 0 | 0.1 | 624 | - |
| fattree-k4 | websearch | Reactive (learning + spanning tree) | 8 | 0 | 120.59 / 319.23 | 467 | 38.1 | 3968 | - |
| fattree-k4 | websearch | Proactive (one shortest path) | 8 | 0 | 50.14 / 257.44 | 0 | 0.2 | 1072 | - |
| fattree-k4 | websearch | Proactive (ECMP) | 8 | 0 | 15.03 / 177.80 | 0 | 0.3 | 1072 | - |
| fattree-k4 | datamining | Reactive (learning + spanning tree) | 8 | 0 | 82.41 / 172.39 | 682 | 47.5 | 5734 | - |
| fattree-k4 | datamining | Proactive (one shortest path) | 8 | 0 | 27.20 / 90.56 | 0 | 0.3 | 1072 | - |
| fattree-k4 | datamining | Proactive (ECMP) | 8 | 0 | 9.72 / 64.44 | 0 | 0.4 | 1072 | - |
| abilene | isp | Reactive (learning + spanning tree) | 8 | 0 | 99.67 / 347.99 | 593 | 32.7 | 7273 | - |
| abilene | isp | Proactive (one shortest path) | 8 | 0 | 45.47 / 173.45 | 0 | 0.2 | 386 | - |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 9 | 0 | 34.08 / 77.75 | 2445 | 74.6 | 10810 | - |
| tree-d2-f4 | university | Proactive (one shortest path) | 9 | 0 | 1.29 / 37.31 | 0 | 0.1 | 624 | - |
| fattree-k4 | websearch | Reactive (learning + spanning tree) | 9 | 0 | 125.80 / 332.69 | 510 | 38.8 | 4740 | - |
| fattree-k4 | websearch | Proactive (one shortest path) | 9 | 0 | 65.77 / 262.04 | 0 | 0.3 | 1072 | - |
| fattree-k4 | websearch | Proactive (ECMP) | 9 | 0 | 20.83 / 209.97 | 0 | 0.4 | 1072 | - |
| fattree-k4 | datamining | Reactive (learning + spanning tree) | 9 | 0 | 86.19 / 172.06 | 646 | 48.1 | 5667 | - |
| fattree-k4 | datamining | Proactive (one shortest path) | 9 | 0 | 25.28 / 77.96 | 0 | 0.3 | 1072 | - |
| fattree-k4 | datamining | Proactive (ECMP) | 9 | 0 | 9.10 / 64.45 | 0 | 0.3 | 1072 | - |
| abilene | isp | Reactive (learning + spanning tree) | 9 | 0 | 102.81 / 336.90 | 634 | 34.3 | 7509 | - |
| abilene | isp | Proactive (one shortest path) | 9 | 0 | 45.61 / 233.13 | 0 | 0.1 | 386 | - |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 10 | 0 | 33.45 / 90.25 | 2391 | 73.4 | 10709 | - |
| tree-d2-f4 | university | Proactive (one shortest path) | 10 | 0 | 1.29 / 42.32 | 0 | 0.1 | 624 | - |
| fattree-k4 | websearch | Reactive (learning + spanning tree) | 10 | 0 | 118.44 / 283.50 | 503 | 39.5 | 4182 | - |
| fattree-k4 | websearch | Proactive (one shortest path) | 10 | 0 | 55.95 / 224.72 | 0 | 0.2 | 1072 | - |
| fattree-k4 | websearch | Proactive (ECMP) | 10 | 0 | 18.07 / 241.76 | 0 | 0.3 | 1072 | - |
| fattree-k4 | datamining | Reactive (learning + spanning tree) | 10 | 0 | 91.83 / 205.23 | 700 | 50.7 | 5962 | - |
| fattree-k4 | datamining | Proactive (one shortest path) | 10 | 0 | 28.50 / 112.82 | 0 | 0.2 | 1072 | - |
| fattree-k4 | datamining | Proactive (ECMP) | 10 | 0 | 12.38 / 79.06 | 0 | 0.2 | 1072 | - |
| abilene | isp | Reactive (learning + spanning tree) | 10 | 0 | 106.58 / 339.91 | 606 | 28.4 | 7396 | - |
| abilene | isp | Proactive (one shortest path) | 10 | 0 | 47.51 / 243.16 | 0 | 0.1 | 386 | - |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 11 | 0 | 25.52 / 74.83 | 2364 | 65.4 | 10680 | - |
| tree-d2-f4 | university | Proactive (one shortest path) | 11 | 0 | 1.25 / 44.76 | 0 | 0.1 | 624 | - |
| fattree-k4 | websearch | Reactive (learning + spanning tree) | 11 | 0 | 91.69 / 273.68 | 484 | 30.5 | 4122 | - |
| fattree-k4 | websearch | Proactive (one shortest path) | 11 | 0 | 52.64 / 230.07 | 0 | 0.2 | 1072 | - |
| fattree-k4 | websearch | Proactive (ECMP) | 11 | 0 | 13.88 / 176.33 | 0 | 0.2 | 1072 | - |
| fattree-k4 | datamining | Reactive (learning + spanning tree) | 11 | 0 | 65.04 / 154.60 | 686 | 41.6 | 5842 | - |
| fattree-k4 | datamining | Proactive (one shortest path) | 11 | 0 | 25.18 / 93.00 | 0 | 0.1 | 1072 | - |
| fattree-k4 | datamining | Proactive (ECMP) | 11 | 0 | 7.01 / 69.32 | 0 | 0.2 | 1072 | - |
| abilene | isp | Reactive (learning + spanning tree) | 11 | 0 | 96.82 / 371.19 | 604 | 29.3 | 7316 | - |
| abilene | isp | Proactive (one shortest path) | 11 | 0 | 45.64 / 192.89 | 0 | 0.1 | 386 | - |
