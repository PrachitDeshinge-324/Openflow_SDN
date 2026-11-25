# Realistic traffic results (A-abilene)

Testbed: Linux Harikrushna 6.18.58.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Tue Oct 27 00:24:11 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet
CPU: AMD Ryzen 7 8840HS w/ Radeon 780M Graphics, 16 threads | code: commit e4e178e3b8


**Every value is the mean of 5 runs (seeds 7 to 11, a new flow schedule each time) ± the half-width of its 95% confidence interval (Student's t).**

## Traffic generated (identical for every controller within one seed)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Abilene traffic matrices (Zhang et al., IMC 2005) + SURGE flow sizes | 1749 ± 43 | 58.3 ± 1.4 | 28.5 ± 2.9 (3%) | 0 ± 0 | 100 ± 0% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Reactive on shortest paths, pair rules | 1749 ± 43 / 0 ± 0 | 58.91 ± 3.46 / 46.11 ± 1.52 / 205.90 ± 37.75 | 177.0 ± 10.5 | 1453.5 ± 321.7 |
| abilene | isp | Reactive on shortest paths, destination rules | 1749 ± 43 / 0 ± 0 | 58.74 ± 3.45 / 46.04 ± 1.53 / 205.12 ± 36.24 | 176.9 ± 10.5 | 1454.0 ± 329.1 |
| abilene | isp | SmartTime-style adaptive timeout, exact-match rules | 1749 ± 43 / 0 ± 0 | 72.18 ± 3.13 / 57.72 ± 1.66 / 226.55 ± 35.18 | 190.9 ± 10.8 | 1475.1 ± 496.8 |
| abilene | isp | SmartTime-style adaptive timeout, pair rules | 1749 ± 43 / 0 ± 0 | 59.25 ± 3.50 / 46.40 ± 1.53 / 207.89 ± 37.34 | 177.6 ± 10.3 | 1455.0 ± 319.2 |
| abilene | isp | Proactive (one shortest path) | 1749 ± 43 / 0 ± 0 | 58.67 ± 3.47 / 46.02 ± 1.63 / 205.54 ± 37.53 | 176.8 ± 10.9 | 1457.4 ± 361.1 |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Reactive on shortest paths, pair rules | 15 ± 0 | 13 ± 0 | 0.9 ± 0.0 | 379 ± 6 | 61 ± 2 |
| abilene | isp | Reactive on shortest paths, destination rules | 5 ± 1 | 3 ± 1 | 0.4 ± 0.0 | 120 ± 2 | 11 ± 0 |
| abilene | isp | SmartTime-style adaptive timeout, exact-match rules | 454 ± 14 | 452 ± 14 | 30.5 ± 0.8 | 709 ± 135 | 112 ± 28 |
| abilene | isp | SmartTime-style adaptive timeout, pair rules | 40 ± 1 | 38 ± 1 | 2.7 ± 0.0 | 355 ± 13 | 56 ± 2 |
| abilene | isp | Proactive (one shortest path) | 0 ± 0 | 0 ± 0 | 0.1 ± 0.0 | 386 ± 0 | 62 ± 0 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Reactive on shortest paths, pair rules | 0 of 110 | 96.5 ± 0.1 | 0 ± 0 | 0 ± 0 |
| abilene | isp | Reactive on shortest paths, destination rules | 0 of 110 | 97.8 ± 0.3 | 0 ± 0 | 0 ± 0 |
| abilene | isp | SmartTime-style adaptive timeout, exact-match rules | 0 of 110 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| abilene | isp | SmartTime-style adaptive timeout, pair rules | 0 of 110 | 90.5 ± 0.1 | 0 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Reactive on shortest paths, pair rules | 7 | 0 | 47.09 / 190.48 | 15 | 1.0 | 376 | 96.5 |
| abilene | isp | Reactive on shortest paths, destination rules | 7 | 0 | 47.15 / 189.40 | 5 | 0.4 | 121 | 97.4 |
| abilene | isp | SmartTime-style adaptive timeout, exact-match rules | 7 | 0 | 58.65 / 210.74 | 459 | 30.5 | 872 | 0.0 |
| abilene | isp | SmartTime-style adaptive timeout, pair rules | 7 | 0 | 47.54 / 189.59 | 39 | 2.6 | 366 | 90.6 |
| abilene | isp | Proactive (one shortest path) | 7 | 0 | 47.16 / 189.43 | 0 | 0.1 | 386 | - |
| abilene | isp | Reactive on shortest paths, pair rules | 8 | 0 | 44.85 / 171.54 | 14 | 0.9 | 380 | 96.4 |
| abilene | isp | Reactive on shortest paths, destination rules | 8 | 0 | 44.77 / 171.17 | 5 | 0.4 | 118 | 97.9 |
| abilene | isp | SmartTime-style adaptive timeout, exact-match rules | 8 | 0 | 56.62 / 194.98 | 450 | 31.3 | 646 | 0.0 |
| abilene | isp | SmartTime-style adaptive timeout, pair rules | 8 | 0 | 44.96 / 175.92 | 40 | 2.7 | 350 | 90.5 |
| abilene | isp | Proactive (one shortest path) | 8 | 0 | 44.60 / 173.26 | 0 | 0.1 | 386 | - |
| abilene | isp | Reactive on shortest paths, pair rules | 9 | 0 | 45.15 / 232.48 | 14 | 0.9 | 386 | 96.6 |
| abilene | isp | Reactive on shortest paths, destination rules | 9 | 0 | 45.09 / 227.19 | 5 | 0.4 | 121 | 97.8 |
| abilene | isp | SmartTime-style adaptive timeout, exact-match rules | 9 | 0 | 56.82 / 258.35 | 471 | 31.0 | 631 | 0.0 |
| abilene | isp | SmartTime-style adaptive timeout, pair rules | 9 | 0 | 45.48 / 233.00 | 40 | 2.7 | 358 | 90.5 |
| abilene | isp | Proactive (one shortest path) | 9 | 0 | 45.05 / 232.43 | 0 | 0.1 | 386 | - |
| abilene | isp | Reactive on shortest paths, pair rules | 10 | 0 | 47.68 / 243.05 | 15 | 0.9 | 374 | 96.6 |
| abilene | isp | Reactive on shortest paths, destination rules | 10 | 0 | 47.52 / 242.80 | 5 | 0.4 | 120 | 98.1 |
| abilene | isp | SmartTime-style adaptive timeout, exact-match rules | 10 | 0 | 59.61 / 254.73 | 447 | 30.1 | 770 | 0.0 |
| abilene | isp | SmartTime-style adaptive timeout, pair rules | 10 | 0 | 47.76 / 246.10 | 40 | 2.7 | 340 | 90.6 |
| abilene | isp | Proactive (one shortest path) | 10 | 0 | 47.61 / 242.74 | 0 | 0.1 | 386 | - |
| abilene | isp | Reactive on shortest paths, pair rules | 11 | 0 | 45.79 / 191.96 | 15 | 0.9 | 380 | 96.5 |
| abilene | isp | Reactive on shortest paths, destination rules | 11 | 0 | 45.68 / 195.04 | 6 | 0.5 | 119 | 97.8 |
| abilene | isp | SmartTime-style adaptive timeout, exact-match rules | 11 | 0 | 56.91 / 213.93 | 441 | 29.7 | 627 | 0.0 |
| abilene | isp | SmartTime-style adaptive timeout, pair rules | 11 | 0 | 46.29 / 194.84 | 41 | 2.7 | 362 | 90.3 |
| abilene | isp | Proactive (one shortest path) | 11 | 0 | 45.69 / 189.85 | 0 | 0.1 | 386 | - |
