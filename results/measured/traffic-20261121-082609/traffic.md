# Realistic traffic results (traffic-20261121-082609)

Testbed: Linux Harikrushna 6.18.58.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Tue Oct 27 00:24:11 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet
CPU: AMD Ryzen 7 8840HS w/ Radeon 780M Graphics, 16 threads | code: commit 369b32d226


**Every value is the mean of 5 runs (seeds 7 to 11, a new flow schedule each time) ± the half-width of its 95% confidence interval (Student's t).**

## Traffic generated (identical for every controller within one seed)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Abilene traffic matrices (Zhang et al., IMC 2005) + SURGE flow sizes | 1749 ± 43 | 58.3 ± 1.4 | 28.5 ± 2.9 (3%) | 0 ± 0 | 100 ± 0% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Reactive on shortest paths, destination rules | 1749 ± 43 / 0 ± 0 | 60.25 ± 3.62 / 47.00 ± 1.84 / 211.45 ± 33.56 | 180.5 ± 10.0 | 1475.5 ± 351.1 |
| abilene | isp | Proactive (one shortest path) | 1749 ± 43 / 0 ± 0 | 60.27 ± 3.44 / 47.07 ± 1.68 / 212.40 ± 40.61 | 180.1 ± 11.3 | 1472.6 ± 351.5 |
| abilene | isp | Proactive, one rule per destination (tap without its copy rules) | 1749 ± 43 / 0 ± 0 | 59.90 ± 2.80 / 46.95 ± 1.66 / 205.81 ± 30.99 | 178.2 ± 11.8 | 1472.4 ± 420.4 |
| abilene | isp | Forward first, tell the controller (destination rules + SYN/FIN copies) | 1749 ± 43 / 0 ± 0 | 59.98 ± 3.47 / 46.94 ± 1.65 / 208.68 ± 36.90 | 179.3 ± 10.4 | 1467.5 ± 356.2 |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Reactive on shortest paths, destination rules | 4 ± 0 | 2 ± 0 | 0.6 ± 0.0 | 120 ± 2 | 11 ± 0 |
| abilene | isp | Proactive (one shortest path) | 0 ± 0 | 0 ± 0 | 0.2 ± 0.0 | 386 ± 0 | 62 ± 0 |
| abilene | isp | Proactive, one rule per destination (tap without its copy rules) | 0 ± 0 | 0 ± 0 | 0.3 ± 0.0 | 121 ± 0 | 11 ± 0 |
| abilene | isp | Forward first, tell the controller (destination rules + SYN/FIN copies) | 173 ± 5 | 0 ± 0 | 8.2 ± 0.3 | 154 ± 0 | 14 ± 0 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Reactive on shortest paths, destination rules | 0 of 110 | 97.8 ± 0.3 | 0 ± 0 | 0 ± 0 |
| abilene | isp | Proactive, one rule per destination (tap without its copy rules) | 0 of 110 | 100.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| abilene | isp | Forward first, tell the controller (destination rules + SYN/FIN copies) | 0 of 110 | 100.0 ± 0.0 | 0 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Reactive on shortest paths, destination rules | 7 | 0 | 48.31 / 206.48 | 4 | 0.6 | 121 | 97.4 |
| abilene | isp | Proactive (one shortest path) | 7 | 0 | 48.18 / 195.09 | 0 | 0.2 | 386 | - |
| abilene | isp | Proactive, one rule per destination (tap without its copy rules) | 7 | 0 | 47.98 / 191.87 | 0 | 0.3 | 121 | 100.0 |
| abilene | isp | Forward first, tell the controller (destination rules + SYN/FIN copies) | 7 | 0 | 48.02 / 197.58 | 175 | 8.5 | 154 | 100.0 |
| abilene | isp | Reactive on shortest paths, destination rules | 8 | 0 | 45.51 / 177.15 | 4 | 0.6 | 118 | 97.9 |
| abilene | isp | Proactive (one shortest path) | 8 | 0 | 45.52 / 174.80 | 0 | 0.2 | 386 | - |
| abilene | isp | Proactive, one rule per destination (tap without its copy rules) | 8 | 0 | 45.59 / 175.21 | 0 | 0.3 | 121 | 100.0 |
| abilene | isp | Forward first, tell the controller (destination rules + SYN/FIN copies) | 8 | 0 | 45.54 / 172.81 | 172 | 8.1 | 154 | 100.0 |
| abilene | isp | Reactive on shortest paths, destination rules | 9 | 0 | 45.73 / 229.32 | 3 | 0.5 | 121 | 97.8 |
| abilene | isp | Proactive (one shortest path) | 9 | 0 | 45.88 / 245.68 | 0 | 0.2 | 386 | - |
| abilene | isp | Proactive, one rule per destination (tap without its copy rules) | 9 | 0 | 45.70 / 237.90 | 0 | 0.3 | 121 | 100.0 |
| abilene | isp | Forward first, tell the controller (destination rules + SYN/FIN copies) | 9 | 0 | 45.78 / 231.68 | 179 | 8.2 | 154 | 100.0 |
| abilene | isp | Reactive on shortest paths, destination rules | 10 | 0 | 48.78 / 246.37 | 3 | 0.6 | 121 | 98.1 |
| abilene | isp | Proactive (one shortest path) | 10 | 0 | 48.57 / 247.98 | 0 | 0.2 | 386 | - |
| abilene | isp | Proactive, one rule per destination (tap without its copy rules) | 10 | 0 | 48.58 / 223.30 | 0 | 0.3 | 121 | 100.0 |
| abilene | isp | Forward first, tell the controller (destination rules + SYN/FIN copies) | 10 | 0 | 48.55 / 246.24 | 170 | 8.1 | 154 | 100.0 |
| abilene | isp | Reactive on shortest paths, destination rules | 11 | 0 | 46.65 / 197.92 | 4 | 0.5 | 119 | 97.8 |
| abilene | isp | Proactive (one shortest path) | 11 | 0 | 47.18 / 198.47 | 0 | 0.2 | 386 | - |
| abilene | isp | Proactive, one rule per destination (tap without its copy rules) | 11 | 0 | 46.90 / 200.77 | 0 | 0.3 | 121 | 100.0 |
| abilene | isp | Forward first, tell the controller (destination rules + SYN/FIN copies) | 11 | 0 | 46.82 / 195.08 | 171 | 8.0 | 154 | 100.0 |
