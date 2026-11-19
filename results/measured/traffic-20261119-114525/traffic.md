# Realistic traffic results (traffic-20261119-114525)

Testbed: Linux Harikrushna 6.18.58.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Tue Oct 27 00:24:11 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet

**Every value is the mean of 5 runs (seeds 7 to 11, a new flow schedule each time) ± the half-width of its 95% confidence interval (Student's t).**

## Traffic generated (identical for every controller within one seed)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Benson et al., IMC 2010 (university data centres) | 6073 ± 41 | 202.4 ± 1.4 | 85.5 ± 14.1 (5%) | 0 ± 0 | 83 ± 8% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 6073 ± 41 / 0 ± 0 | 37.77 ± 6.54 / 35.70 ± 5.73 / 96.15 ± 16.51 | 185.0 ± 26.6 | - |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 6073 ± 41 / 0 ± 0 | 5.34 ± 1.34 / 1.01 ± 0.47 / 37.62 ± 5.37 | 147.5 ± 22.5 | - |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 6073 ± 41 / 0 ± 0 | 5.16 ± 1.34 / 0.93 ± 0.37 / 38.14 ± 4.71 | 146.5 ± 22.9 | - |
| tree-d2-f4 | university | Proactive (one shortest path) | 6073 ± 41 / 0 ± 0 | 5.18 ± 1.35 / 0.94 ± 0.37 / 37.90 ± 5.59 | 147.0 ± 21.8 | - |
| tree-d2-f4 | university | Forward first, tell the controller (destination rules + SYN/FIN copies) | 6073 ± 41 / 0 ± 0 | 5.15 ± 1.31 / 1.01 ± 0.37 / 37.53 ± 5.09 | 145.8 ± 20.4 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 2486 ± 141 | 2486 ± 141 | 74.8 ± 3.0 | 10983 ± 652 | 3446 ± 318 |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 31 ± 12 | 30 ± 12 | 1.3 ± 0.4 | 624 ± 0 | 192 ± 0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 3 ± 4 | 3 ± 4 | 0.2 ± 0.1 | 80 ± 0 | 16 ± 0 |
| tree-d2-f4 | university | Proactive (one shortest path) | 0 ± 0 | 0 ± 0 | 0.1 ± 0.0 | 624 ± 0 | 192 ± 0 |
| tree-d2-f4 | university | Forward first, tell the controller (destination rules + SYN/FIN copies) | 602 ± 11 | 0 ± 0 | 14.3 ± 2.3 | 128 ± 0 | 28 ± 0 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 0 of 240 | 0.0 ± 0.1 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 0 of 240 | 97.9 ± 0.0 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 0 of 240 | 99.6 ± 0.1 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Forward first, tell the controller (destination rules + SYN/FIN copies) | 0 of 240 | 100.0 ± 0.0 | 0 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 7 | 0 | 39.71 / 108.58 | 2417 | 76.1 | 11152 | 0.1 |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 7 | 0 | 1.38 / 44.54 | 24 | 1.3 | 624 | 97.9 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 7 | 0 | 1.39 / 43.57 | 1 | 0.2 | 80 | 99.6 |
| tree-d2-f4 | university | Proactive (one shortest path) | 7 | 0 | 1.39 / 44.77 | 0 | 0.1 | 624 | - |
| tree-d2-f4 | university | Forward first, tell the controller (destination rules + SYN/FIN copies) | 7 | 0 | 1.38 / 42.03 | 601 | 17.5 | 128 | 100.0 |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 8 | 0 | 40.19 / 111.22 | 2461 | 76.2 | 11258 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 8 | 0 | 1.45 / 38.12 | 33 | 1.7 | 624 | 97.9 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 8 | 0 | 1.08 / 39.18 | 5 | 0.2 | 80 | 99.5 |
| tree-d2-f4 | university | Proactive (one shortest path) | 8 | 0 | 1.12 / 39.02 | 0 | 0.1 | 624 | - |
| tree-d2-f4 | university | Forward first, tell the controller (destination rules + SYN/FIN copies) | 8 | 0 | 1.30 / 41.18 | 606 | 14.5 | 128 | 100.0 |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 9 | 0 | 35.37 / 93.79 | 2639 | 76.0 | 11392 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 9 | 0 | 0.77 / 37.44 | 48 | 1.6 | 624 | 97.9 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 9 | 0 | 0.76 / 38.84 | 1 | 0.2 | 80 | 99.5 |
| tree-d2-f4 | university | Proactive (one shortest path) | 9 | 0 | 0.77 / 37.49 | 0 | 0.1 | 624 | - |
| tree-d2-f4 | university | Forward first, tell the controller (destination rules + SYN/FIN copies) | 9 | 0 | 0.82 / 37.29 | 614 | 13.7 | 128 | 100.0 |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 10 | 0 | 34.44 / 85.08 | 2558 | 75.3 | 11042 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 10 | 0 | 0.73 / 33.57 | 25 | 1.1 | 624 | 97.9 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 10 | 0 | 0.74 / 33.96 | 1 | 0.1 | 80 | 99.6 |
| tree-d2-f4 | university | Proactive (one shortest path) | 10 | 0 | 0.74 / 32.73 | 0 | 0.1 | 624 | - |
| tree-d2-f4 | university | Forward first, tell the controller (destination rules + SYN/FIN copies) | 10 | 0 | 0.80 / 32.44 | 592 | 13.0 | 128 | 100.0 |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 11 | 0 | 28.82 / 82.09 | 2354 | 70.5 | 10073 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 11 | 0 | 0.70 / 34.43 | 25 | 1.0 | 624 | 97.9 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 11 | 0 | 0.68 / 35.13 | 8 | 0.3 | 80 | 99.7 |
| tree-d2-f4 | university | Proactive (one shortest path) | 11 | 0 | 0.70 / 35.48 | 0 | 0.0 | 624 | - |
| tree-d2-f4 | university | Forward first, tell the controller (destination rules + SYN/FIN copies) | 11 | 0 | 0.76 / 34.73 | 595 | 13.1 | 128 | 100.0 |
