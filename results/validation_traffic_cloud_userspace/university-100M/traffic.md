# Realistic traffic results (tr-full)

Testbed: Linux vm 6.18.44-fc-v114 #1 SMP PREEMPT_DYNAMIC @0 x86_64 | Python 3.11.15 | ovs-vsctl (Open vSwitch) 3.3.9 | datapath=user | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB

## Traffic generated (identical for every controller)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Benson et al., IMC 2010 (university data centres) | 6102 | 203.4 | 92.9 (6%) | 0 | 81% |
| fattree-k4 | websearch | DCTCP, SIGCOMM 2010 / pFabric web search workload | 1159 | 38.6 | 498.3 (31%) | 19 | 94% |
| fattree-k4 | datamining | VL2, SIGCOMM 2009 / pFabric data mining workload | 1707 | 56.9 | 496.3 (31%) | 77 | 93% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 6094 / 8 | 1677.93 / 484.06 / 15569.53 | 5747.0 | - |
| tree-d2-f4 | university | Proactive (one shortest path) | 6102 / 0 | 141.16 / 40.89 / 1802.45 | 694.5 | - |
| fattree-k4 | websearch | Reactive (learning + spanning tree) | 567 / 477 | 8351.50 / 5378.38 / 33871.22 | 18182.8 | 35626.9 |
| fattree-k4 | websearch | Proactive (one shortest path) | 660 / 360 | 6821.91 / 3586.82 / 30831.89 | 14997.6 | 38029.0 |
| fattree-k4 | websearch | Proactive (ECMP) | 771 / 131 | 8009.14 / 5288.48 / 30378.60 | 21739.3 | - |
| fattree-k4 | datamining | Reactive (learning + spanning tree) | 1392 / 239 | 5461.61 / 2400.22 / 30655.27 | 15254.6 | 41330.5 |
| fattree-k4 | datamining | Proactive (one shortest path) | 1447 / 174 | 4290.22 / 1590.01 / 29500.50 | 12864.9 | 37137.1 |
| fattree-k4 | datamining | Proactive (ECMP) | 1553 / 43 | 2772.22 / 1259.95 / 25306.20 | 10731.0 | 62005.2 |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 1100 | 1100 | 34.5 | 12333 | 3855 |
| tree-d2-f4 | university | Proactive (one shortest path) | 0 | 0 | 0.1 | 624 | 192 |
| fattree-k4 | websearch | Reactive (learning + spanning tree) | 356 | 356 | 14.9 | 7501 | 1244 |
| fattree-k4 | websearch | Proactive (one shortest path) | 0 | 0 | 0.3 | 1072 | 192 |
| fattree-k4 | websearch | Proactive (ECMP) | 0 | 0 | 0.3 | 1072 | 58 |
| fattree-k4 | datamining | Reactive (learning + spanning tree) | 505 | 505 | 19.9 | 8649 | 1490 |
| fattree-k4 | datamining | Proactive (one shortest path) | 0 | 0 | 0.3 | 1072 | 192 |
| fattree-k4 | datamining | Proactive (ECMP) | 0 | 0 | 0.2 | 1072 | 58 |
