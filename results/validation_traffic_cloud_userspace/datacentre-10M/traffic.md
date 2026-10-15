# Realistic traffic results (tr-dc)

Testbed: Linux vm 6.18.44-fc-v114 #1 SMP PREEMPT_DYNAMIC @0 x86_64 | Python 3.11.15 | ovs-vsctl (Open vSwitch) 3.3.9 | datapath=user | every link 10 Mbit/s | 60 s of arrivals | target load 30% (websearch/datamining) | flows capped at 5 MB

## Traffic generated (identical for every controller)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | DCTCP, SIGCOMM 2010 / pFabric web search workload | 340 | 5.7 | 48.8 (30%) | 34 | 95% |
| fattree-k4 | datamining | VL2, SIGCOMM 2009 / pFabric data mining workload | 997 | 16.6 | 49.0 (31%) | 51 | 93% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive (learning + spanning tree) | 329 / 11 | 3862.97 / 853.04 / 61713.48 | 26203.8 | - |
| fattree-k4 | websearch | Proactive (one shortest path) | 324 / 16 | 3002.57 / 914.19 / 52434.40 | 25912.2 | - |
| fattree-k4 | websearch | Proactive (ECMP) | 340 / 0 | 698.87 / 205.36 / 8130.01 | 9714.8 | - |
| fattree-k4 | datamining | Reactive (learning + spanning tree) | 980 / 17 | 1538.78 / 311.32 / 15921.50 | 20441.7 | - |
| fattree-k4 | datamining | Proactive (one shortest path) | 983 / 14 | 2061.84 / 506.51 / 30868.13 | 18520.4 | - |
| fattree-k4 | datamining | Proactive (ECMP) | 996 / 1 | 575.50 / 81.16 / 7258.35 | 6753.0 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive (learning + spanning tree) | 62 | 62 | 7.4 | 1195 | 201 |
| fattree-k4 | websearch | Proactive (one shortest path) | 0 | 0 | 0.3 | 1072 | 192 |
| fattree-k4 | websearch | Proactive (ECMP) | 0 | 0 | 0.2 | 1072 | 58 |
| fattree-k4 | datamining | Reactive (learning + spanning tree) | 171 | 171 | 14.5 | 2490 | 414 |
| fattree-k4 | datamining | Proactive (one shortest path) | 0 | 0 | 0.2 | 1072 | 192 |
| fattree-k4 | datamining | Proactive (ECMP) | 0 | 0 | 0.3 | 1072 | 58 |
