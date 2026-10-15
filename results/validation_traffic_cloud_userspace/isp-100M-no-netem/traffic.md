# Realistic traffic results (tr-isp)

Testbed: Linux vm 6.18.44-fc-v114 #1 SMP PREEMPT_DYNAMIC @0 x86_64 | Python 3.11.15 | ovs-vsctl (Open vSwitch) 3.3.9 | datapath=user | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB

## Traffic generated (identical for every controller)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Abilene traffic matrices (Zhang et al., IMC 2005) + SURGE flow sizes | 1761 | 58.7 | 27.5 (3%) | 0 | 100% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Reactive (learning + spanning tree) | 1761 / 0 | 203.47 / 136.61 / 1334.25 | 483.1 | - |
| abilene | isp | Proactive (one shortest path) | 1761 / 0 | 18.10 / 8.15 / 115.60 | 112.2 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Reactive (learning + spanning tree) | 604 | 604 | 27.9 | 7102 | 1042 |
| abilene | isp | Proactive (one shortest path) | 0 | 0 | 0.1 | 386 | 62 |
