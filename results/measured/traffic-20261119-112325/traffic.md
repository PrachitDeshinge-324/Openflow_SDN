# Realistic traffic results (traffic-20261119-112325)

Testbed: Linux Harikrushna 6.18.58.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Tue Oct 27 00:24:11 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 10 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: uniform

Controller: same machine as Mininet

## Traffic generated (identical for every controller)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Benson et al., IMC 2010 (university data centres) | 1944 | 194.4 | 75.9 (5%) | 0 | 79% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Proactive (one shortest path) | 1944 / 0 | 4.26 / 1.19 / 36.03 | 121.4 | - |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 1944 / 0 | 4.45 / 1.16 / 35.87 | 121.7 | - |
| tree-d2-f4 | university | Forward first, tell the controller (destination rules + SYN/FIN copies) | 1944 / 0 | 4.54 / 1.20 / 36.65 | 122.7 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Proactive (one shortest path) | 0 | 0 | 0.1 | 624 | 192 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 9 | 8 | 0.5 | 80 | 16 |
| tree-d2-f4 | university | Forward first, tell the controller (destination rules + SYN/FIN copies) | 559 | 0 | 16.8 | 128 | 28 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 0 of 240 | 98.7 | 0 | 0 |
| tree-d2-f4 | university | Forward first, tell the controller (destination rules + SYN/FIN copies) | 0 of 240 | 100.0 | 0 | 0 |
