# Realistic traffic results (traffic-20261121-073853)

Testbed: Linux Harikrushna 6.18.58.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Tue Oct 27 00:24:11 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet
CPU: AMD Ryzen 7 8840HS w/ Radeon 780M Graphics, 16 threads | code: commit 369b32d226


**Every value is the mean of 5 runs (seeds 7 to 11, a new flow schedule each time) ± the half-width of its 95% confidence interval (Student's t).**

## Traffic generated (identical for every controller within one seed)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Benson et al., IMC 2010 (university data centres) | 6073 ± 41 | 202.4 ± 1.4 | 85.5 ± 14.1 (5%) | 0 ± 0 | 83 ± 8% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 6073 ± 41 / 0 ± 0 | 5.66 ± 1.00 / 1.35 ± 0.14 / 38.95 ± 4.51 | 148.7 ± 19.9 | - |
| tree-d2-f4 | university | Proactive (one shortest path) | 6073 ± 41 / 0 ± 0 | 5.56 ± 0.93 / 1.35 ± 0.13 / 37.89 ± 4.22 | 148.3 ± 20.6 | - |
| tree-d2-f4 | university | Proactive, one rule per destination (tap without its copy rules) | 6073 ± 41 / 0 ± 0 | 5.60 ± 0.97 / 1.38 ± 0.10 / 37.84 ± 4.62 | 146.7 ± 19.5 | - |
| tree-d2-f4 | university | Forward first, tell the controller (destination rules + SYN/FIN copies) | 6073 ± 41 / 0 ± 1 | 5.71 ± 1.01 / 1.46 ± 0.09 / 38.79 ± 4.84 | 148.4 ± 21.0 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 6 ± 8 | 5 ± 8 | 0.3 ± 0.2 | 80 ± 0 | 16 ± 0 |
| tree-d2-f4 | university | Proactive (one shortest path) | 0 ± 0 | 0 ± 0 | 0.1 ± 0.0 | 624 ± 0 | 192 ± 0 |
| tree-d2-f4 | university | Proactive, one rule per destination (tap without its copy rules) | 0 ± 0 | 0 ± 0 | 0.2 ± 0.1 | 80 ± 0 | 16 ± 0 |
| tree-d2-f4 | university | Forward first, tell the controller (destination rules + SYN/FIN copies) | 605 ± 6 | 0 ± 0 | 19.9 ± 2.8 | 128 ± 0 | 28 ± 0 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 0 of 240 | 99.6 ± 0.1 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Proactive, one rule per destination (tap without its copy rules) | 0 of 240 | 100.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Forward first, tell the controller (destination rules + SYN/FIN copies) | 0 of 240 | 100.0 ± 0.0 | 0 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 7 | 0 | 1.35 / 44.29 | 1 | 0.2 | 80 | 99.6 |
| tree-d2-f4 | university | Proactive (one shortest path) | 7 | 0 | 1.29 / 42.74 | 0 | 0.1 | 624 | - |
| tree-d2-f4 | university | Proactive, one rule per destination (tap without its copy rules) | 7 | 0 | 1.39 / 43.15 | 0 | 0.1 | 80 | 100.0 |
| tree-d2-f4 | university | Forward first, tell the controller (destination rules + SYN/FIN copies) | 7 | 0 | 1.49 / 44.58 | 601 | 17.3 | 128 | 100.0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 8 | 0 | 1.54 / 39.12 | 13 | 0.4 | 80 | 99.5 |
| tree-d2-f4 | university | Proactive (one shortest path) | 8 | 0 | 1.53 / 38.75 | 0 | 0.1 | 624 | - |
| tree-d2-f4 | university | Proactive, one rule per destination (tap without its copy rules) | 8 | 0 | 1.52 / 39.71 | 0 | 0.1 | 80 | 100.0 |
| tree-d2-f4 | university | Forward first, tell the controller (destination rules + SYN/FIN copies) | 8 | 0 | 1.57 / 40.66 | 600 | 17.5 | 128 | 100.0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 9 | 0 | 1.23 / 38.40 | 1 | 0.2 | 80 | 99.5 |
| tree-d2-f4 | university | Proactive (one shortest path) | 9 | 0 | 1.28 / 37.80 | 0 | 0.1 | 624 | - |
| tree-d2-f4 | university | Proactive, one rule per destination (tap without its copy rules) | 9 | 0 | 1.38 / 37.47 | 0 | 0.2 | 80 | 100.0 |
| tree-d2-f4 | university | Forward first, tell the controller (destination rules + SYN/FIN copies) | 9 | 1 | 1.45 / 37.58 | 613 | 21.9 | 128 | 100.0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 10 | 0 | 1.33 / 34.06 | 1 | 0.2 | 80 | 99.6 |
| tree-d2-f4 | university | Proactive (one shortest path) | 10 | 0 | 1.34 / 33.34 | 0 | 0.1 | 624 | - |
| tree-d2-f4 | university | Proactive, one rule per destination (tap without its copy rules) | 10 | 0 | 1.34 / 34.06 | 0 | 0.2 | 80 | 100.0 |
| tree-d2-f4 | university | Forward first, tell the controller (destination rules + SYN/FIN copies) | 10 | 0 | 1.43 / 34.65 | 605 | 21.5 | 128 | 100.0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 11 | 0 | 1.29 / 38.87 | 13 | 0.5 | 80 | 99.6 |
| tree-d2-f4 | university | Proactive (one shortest path) | 11 | 0 | 1.30 / 36.81 | 0 | 0.1 | 624 | - |
| tree-d2-f4 | university | Proactive, one rule per destination (tap without its copy rules) | 11 | 0 | 1.30 / 34.81 | 0 | 0.2 | 80 | 100.0 |
| tree-d2-f4 | university | Forward first, tell the controller (destination rules + SYN/FIN copies) | 11 | 0 | 1.37 / 36.50 | 603 | 21.4 | 128 | 100.0 |
