# Realistic traffic results (traffic-20261015-113417)

Testbed: Linux Harikrushna 6.18.33.2-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Thu Jun 18 21:54:43 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB

## Traffic generated (identical for every controller)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Benson et al., IMC 2010 (university data centres) | 6102 | 203.4 | 92.9 (6%) | 0 | 81% |
| fattree-k4 | websearch | DCTCP, SIGCOMM 2010 / pFabric web search workload | 1159 | 38.6 | 498.3 (31%) | 19 | 94% |
| fattree-k4 | datamining | VL2, SIGCOMM 2009 / pFabric data mining workload | 1707 | 56.9 | 496.3 (31%) | 77 | 93% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 6102 / 0 | 58.79 / 55.72 / 126.00 | 221.6 | - |
| tree-d2-f4 | university | Proactive (one shortest path) | 6102 / 0 | 5.60 / 1.27 / 37.92 | 163.1 | - |
| fattree-k4 | websearch | Reactive (learning + spanning tree) | 1159 / 0 | 156.09 / 155.34 / 343.53 | 2985.7 | 12160.8 |
| fattree-k4 | websearch | Proactive (one shortest path) | 1159 / 0 | 72.89 / 62.60 / 241.96 | 2663.8 | 12808.1 |
| fattree-k4 | websearch | Proactive (ECMP) | 1159 / 0 | 30.29 / 19.22 / 170.79 | 669.9 | 3547.9 |
| fattree-k4 | datamining | Reactive (learning + spanning tree) | 1707 / 0 | 113.63 / 112.97 / 244.15 | 712.9 | 10882.5 |
| fattree-k4 | datamining | Proactive (one shortest path) | 1707 / 0 | 27.27 / 24.90 / 111.03 | 640.8 | 10719.9 |
| fattree-k4 | datamining | Proactive (ECMP) | 1707 / 0 | 15.53 / 11.51 / 67.73 | 314.3 | 3593.8 |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 2379 | 2378 | 86.4 | 10928 | 3377 |
| tree-d2-f4 | university | Proactive (one shortest path) | 0 | 0 | 0.1 | 624 | 192 |
| fattree-k4 | websearch | Reactive (learning + spanning tree) | 514 | 491 | 44.3 | 4623 | 779 |
| fattree-k4 | websearch | Proactive (one shortest path) | 0 | 0 | 0.3 | 1072 | 192 |
| fattree-k4 | websearch | Proactive (ECMP) | 0 | 0 | 0.3 | 1072 | 58 |
| fattree-k4 | datamining | Reactive (learning + spanning tree) | 738 | 715 | 56.3 | 6083 | 1003 |
| fattree-k4 | datamining | Proactive (one shortest path) | 0 | 0 | 0.3 | 1072 | 192 |
| fattree-k4 | datamining | Proactive (ECMP) | 0 | 0 | 0.3 | 1072 | 58 |
