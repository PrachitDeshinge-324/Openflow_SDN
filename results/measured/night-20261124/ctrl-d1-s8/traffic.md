# Realistic traffic results (ctrl-d1-s8)

Testbed: Linux Harikrushna 6.18.58.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Tue Oct 27 00:24:11 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet, control channel delayed by 1 ms one way (netem on lo)
CPU: AMD Ryzen 7 8840HS w/ Radeon 780M Graphics, 16 threads | code: commit 2d76742349


## Traffic generated (identical for every controller)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Benson et al., IMC 2010 (university data centres) | 6057 | 201.9 | 95.7 (6%) | 0 | 88% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 6057 / 0 | 68.11 / 65.90 / 146.21 | 227.2 | - |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 6057 / 0 | 6.07 / 1.26 / 40.07 | 159.9 | - |
| tree-d2-f4 | university | Proactive (one shortest path) | 6057 / 0 | 6.00 / 1.29 / 39.12 | 158.1 | - |
| tree-d2-f4 | university | Forward first, tell the controller (destination rules + SYN/FIN copies) | 6057 / 0 | 6.05 / 1.31 / 39.86 | 159.3 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 2105 | 2105 | 72.0 | 11284 | 3597 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 6 | 5 | 0.3 | 80 | 16 |
| tree-d2-f4 | university | Proactive (one shortest path) | 0 | 0 | 0.1 | 624 | 192 |
| tree-d2-f4 | university | Forward first, tell the controller (destination rules + SYN/FIN copies) | 591 | 0 | 14.0 | 128 | 28 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 0 of 240 | 0.0 | 0 | 0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 0 of 240 | 99.5 | 0 | 0 |
| tree-d2-f4 | university | Forward first, tell the controller (destination rules + SYN/FIN copies) | 0 of 240 | 100.0 | 0 | 0 |
