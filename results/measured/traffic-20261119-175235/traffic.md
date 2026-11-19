# Realistic traffic results (traffic-20261119-175235)

Testbed: Linux Harikrushna 6.18.58.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Tue Oct 27 00:24:11 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet

**Every value is the mean of 3 runs (seeds 7 to 9, a new flow schedule each time) ± the half-width of its 95% confidence interval (Student's t).**

## Traffic generated (identical for every controller within one seed)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Benson et al., IMC 2010 (university data centres) | 6090 ± 83 | 203.0 ± 2.8 | 89.8 ± 28.9 (6%) | 0 ± 0 | 87 ± 6% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 6090 ± 83 / 0 ± 0 | 1519.69 ± 1221.23 / 339.10 ± 1174.26 / 7102.70 ± 1170.52 | 1715.0 ± 1381.6 | - |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 6090 ± 83 / 0 ± 0 | 6.33 ± 1.66 / 1.44 ± 0.39 / 41.97 ± 8.64 | 161.2 ± 28.6 | - |
| tree-d2-f4 | university | Proactive (one shortest path) | 6090 ± 83 / 0 ± 0 | 6.42 ± 1.67 / 1.48 ± 0.43 / 42.07 ± 5.62 | 160.8 ± 38.1 | - |
| tree-d2-f4 | university | Forward first, tell the controller (destination rules + SYN/FIN copies) | 6090 ± 83 / 0 ± 0 | 6.31 ± 1.28 / 1.50 ± 0.41 / 42.27 ± 7.86 | 159.0 ± 37.1 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 2533 ± 177 | 2533 ± 177 | 69.4 ± 8.2 | 17859 ± 1541 | 5775 ± 892 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 8 ± 2 | 7 ± 2 | 0.3 ± 0.1 | 80 ± 0 | 16 ± 0 |
| tree-d2-f4 | university | Proactive (one shortest path) | 0 ± 0 | 0 ± 0 | 0.1 ± 0.0 | 624 ± 0 | 192 ± 0 |
| tree-d2-f4 | university | Forward first, tell the controller (destination rules + SYN/FIN copies) | 596 ± 9 | 0 ± 0 | 15.4 ± 0.4 | 128 ± 0 | 28 ± 0 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 0 of 240 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 0 of 240 | 99.6 ± 0.1 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Forward first, tell the controller (destination rules + SYN/FIN copies) | 0 of 240 | 100.0 ± 0.0 | 0 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 7 | 0 | 56.37 / 6737.69 | 2469 | 66.0 | 17268 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 7 | 0 | 1.52 / 45.84 | 7 | 0.2 | 80 | 99.6 |
| tree-d2-f4 | university | Proactive (one shortest path) | 7 | 0 | 1.52 / 44.22 | 0 | 0.1 | 624 | - |
| tree-d2-f4 | university | Forward first, tell the controller (destination rules + SYN/FIN copies) | 7 | 0 | 1.51 / 45.78 | 596 | 15.3 | 128 | 100.0 |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 8 | 0 | 884.77 / 7634.59 | 2522 | 72.5 | 18505 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 8 | 0 | 1.54 / 40.95 | 8 | 0.3 | 80 | 99.5 |
| tree-d2-f4 | university | Proactive (one shortest path) | 8 | 0 | 1.63 / 42.27 | 0 | 0.1 | 624 | - |
| tree-d2-f4 | university | Forward first, tell the controller (destination rules + SYN/FIN copies) | 8 | 0 | 1.66 / 39.63 | 593 | 15.5 | 128 | 100.0 |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 9 | 0 | 76.16 / 6935.83 | 2610 | 69.7 | 17805 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 9 | 0 | 1.26 / 39.11 | 8 | 0.3 | 80 | 99.5 |
| tree-d2-f4 | university | Proactive (one shortest path) | 9 | 0 | 1.29 / 39.71 | 0 | 0.1 | 624 | - |
| tree-d2-f4 | university | Forward first, tell the controller (destination rules + SYN/FIN copies) | 9 | 0 | 1.32 / 41.40 | 600 | 15.6 | 128 | 100.0 |
