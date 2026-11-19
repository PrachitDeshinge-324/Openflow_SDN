# Realistic traffic results (traffic-20261119-123520)

Testbed: Linux Harikrushna 6.18.58.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Tue Oct 27 00:24:11 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet

**Every value is the mean of 5 runs (seeds 7 to 11, a new flow schedule each time) ± the half-width of its 95% confidence interval (Student's t).**

## Traffic generated (identical for every controller within one seed)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Abilene traffic matrices (Zhang et al., IMC 2005) + SURGE flow sizes | 1749 ± 43 | 58.3 ± 1.4 | 28.5 ± 2.9 (3%) | 0 ± 0 | 100 ± 0% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Reactive on shortest paths (hybrid, budget 0%) | 1749 ± 43 / 0 ± 0 | 72.54 ± 3.83 / 57.77 ± 2.23 / 227.19 ± 34.66 | 190.9 ± 11.0 | 1475.4 ± 420.8 |
| abilene | isp | Reactive on shortest paths, pair rules | 1749 ± 43 / 0 ± 0 | 58.89 ± 3.50 / 46.16 ± 1.51 / 206.73 ± 37.55 | 177.3 ± 10.6 | 1454.9 ± 346.1 |
| abilene | isp | Reactive on shortest paths, destination rules | 1749 ± 43 / 0 ± 0 | 58.76 ± 3.46 / 46.10 ± 1.57 / 206.49 ± 36.79 | 177.3 ± 10.8 | 1454.9 ± 334.5 |
| abilene | isp | Proactive (one shortest path) | 1749 ± 43 / 0 ± 0 | 58.70 ± 3.47 / 45.99 ± 1.53 / 205.93 ± 37.61 | 176.9 ± 11.0 | 1454.1 ± 338.0 |
| abilene | isp | Forward first, tell the controller (destination rules + SYN/FIN copies) | 1749 ± 43 / 0 ± 0 | 58.82 ± 3.44 / 46.09 ± 1.51 / 205.33 ± 35.93 | 176.9 ± 10.5 | 1453.6 ± 320.7 |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Reactive on shortest paths (hybrid, budget 0%) | 452 ± 13 | 450 ± 13 | 23.9 ± 0.8 | 5319 ± 104 | 828 ± 30 |
| abilene | isp | Reactive on shortest paths, pair rules | 15 ± 0 | 13 ± 0 | 1.0 ± 0.0 | 379 ± 6 | 61 ± 2 |
| abilene | isp | Reactive on shortest paths, destination rules | 5 ± 0 | 3 ± 0 | 0.4 ± 0.0 | 120 ± 2 | 11 ± 0 |
| abilene | isp | Proactive (one shortest path) | 0 ± 0 | 0 ± 0 | 0.1 ± 0.0 | 386 ± 0 | 62 ± 0 |
| abilene | isp | Forward first, tell the controller (destination rules + SYN/FIN copies) | 174 ± 5 | 0 ± 0 | 5.0 ± 0.1 | 154 ± 0 | 14 ± 0 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Reactive on shortest paths (hybrid, budget 0%) | 0 of 110 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| abilene | isp | Reactive on shortest paths, pair rules | 0 of 110 | 96.5 ± 0.1 | 0 ± 0 | 0 ± 0 |
| abilene | isp | Reactive on shortest paths, destination rules | 0 of 110 | 97.8 ± 0.3 | 0 ± 0 | 0 ± 0 |
| abilene | isp | Forward first, tell the controller (destination rules + SYN/FIN copies) | 0 of 110 | 100.0 ± 0.0 | 0 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Reactive on shortest paths (hybrid, budget 0%) | 7 | 0 | 59.72 / 213.21 | 453 | 23.9 | 5336 | 0.0 |
| abilene | isp | Reactive on shortest paths, pair rules | 7 | 0 | 47.10 / 189.82 | 15 | 0.9 | 377 | 96.5 |
| abilene | isp | Reactive on shortest paths, destination rules | 7 | 0 | 47.14 / 189.93 | 5 | 0.4 | 121 | 97.4 |
| abilene | isp | Proactive (one shortest path) | 7 | 0 | 47.09 / 189.58 | 0 | 0.1 | 386 | - |
| abilene | isp | Forward first, tell the controller (destination rules + SYN/FIN copies) | 7 | 0 | 47.20 / 189.68 | 175 | 5.1 | 154 | 100.0 |
| abilene | isp | Reactive on shortest paths (hybrid, budget 0%) | 8 | 0 | 55.47 / 193.21 | 443 | 23.1 | 5202 | 0.0 |
| abilene | isp | Reactive on shortest paths, pair rules | 8 | 0 | 44.87 / 172.71 | 15 | 1.0 | 380 | 96.4 |
| abilene | isp | Reactive on shortest paths, destination rules | 8 | 0 | 44.73 / 172.86 | 5 | 0.4 | 118 | 97.9 |
| abilene | isp | Proactive (one shortest path) | 8 | 0 | 44.66 / 172.31 | 0 | 0.1 | 386 | - |
| abilene | isp | Forward first, tell the controller (destination rules + SYN/FIN copies) | 8 | 0 | 44.94 / 172.79 | 171 | 5.0 | 154 | 100.0 |
| abilene | isp | Reactive on shortest paths (hybrid, budget 0%) | 9 | 0 | 57.05 / 254.54 | 470 | 25.0 | 5430 | 0.0 |
| abilene | isp | Reactive on shortest paths, pair rules | 9 | 0 | 45.22 / 231.39 | 15 | 0.9 | 386 | 96.6 |
| abilene | isp | Reactive on shortest paths, destination rules | 9 | 0 | 45.17 / 231.87 | 5 | 0.4 | 121 | 97.8 |
| abilene | isp | Proactive (one shortest path) | 9 | 0 | 45.05 / 232.31 | 0 | 0.1 | 386 | - |
| abilene | isp | Forward first, tell the controller (destination rules + SYN/FIN copies) | 9 | 0 | 45.08 / 231.36 | 181 | 5.1 | 154 | 100.0 |
| abilene | isp | Reactive on shortest paths (hybrid, budget 0%) | 10 | 0 | 59.48 / 257.59 | 448 | 23.6 | 5341 | 0.0 |
| abilene | isp | Reactive on shortest paths, pair rules | 10 | 0 | 47.71 / 245.00 | 15 | 1.0 | 374 | 96.6 |
| abilene | isp | Reactive on shortest paths, destination rules | 10 | 0 | 47.67 / 242.93 | 5 | 0.4 | 120 | 98.1 |
| abilene | isp | Proactive (one shortest path) | 10 | 0 | 47.44 / 243.22 | 0 | 0.1 | 386 | - |
| abilene | isp | Forward first, tell the controller (destination rules + SYN/FIN copies) | 10 | 0 | 47.56 / 240.11 | 173 | 4.9 | 154 | 100.0 |
| abilene | isp | Reactive on shortest paths (hybrid, budget 0%) | 11 | 0 | 57.12 / 217.40 | 445 | 23.6 | 5285 | 0.0 |
| abilene | isp | Reactive on shortest paths, pair rules | 11 | 0 | 45.89 / 194.75 | 15 | 1.0 | 380 | 96.5 |
| abilene | isp | Reactive on shortest paths, destination rules | 11 | 0 | 45.78 / 194.87 | 6 | 0.4 | 119 | 97.8 |
| abilene | isp | Proactive (one shortest path) | 11 | 0 | 45.69 / 192.24 | 0 | 0.1 | 386 | - |
| abilene | isp | Forward first, tell the controller (destination rules + SYN/FIN copies) | 11 | 0 | 45.69 / 192.69 | 171 | 4.9 | 154 | 100.0 |
