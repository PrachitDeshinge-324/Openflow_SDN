# Realistic traffic results (B-cap20-fattree)

Testbed: Linux Harikrushna 6.18.58.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Tue Oct 27 00:24:11 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet
CPU: AMD Ryzen 7 8840HS w/ Radeon 780M Graphics, 16 threads | code: commit e4e178e3b8


**Every value is the mean of 3 runs (seeds 7 to 9, a new flow schedule each time) ± the half-width of its 95% confidence interval (Student's t).**

## Traffic generated (identical for every controller within one seed)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | DCTCP, SIGCOMM 2010 / pFabric web search workload | 1124 ± 70 | 37.5 ± 2.3 | 476.5 ± 46.1 (30%) | 15 ± 12 | 95 ± 4% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 1124 ± 70 / 0 ± 0 | 2459.29 ± 1753.42 / 117.02 ± 81.36 / 21361.92 ± 5816.27 | 8027.8 ± 2988.5 | 19583.2 ± 16466.2 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 1124 ± 70 / 0 ± 0 | 62.16 ± 18.26 / 36.97 ± 13.62 / 321.83 ± 68.50 | 2521.0 ± 590.1 | 10457.8 ± 6606.5 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 1124 ± 70 / 0 ± 0 | 134.40 ± 23.71 / 92.15 ± 15.28 / 853.33 ± 162.58 | 2855.6 ± 1106.7 | 11226.8 ± 9159.6 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 1124 ± 70 / 0 ± 0 | 68.11 ± 23.94 / 47.78 ± 14.86 / 327.49 ± 97.49 | 2715.2 ± 990.2 | 10994.6 ± 9331.7 |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 6274 ± 560 | 6270 ± 560 | 96.1 ± 2.2 | 400 ± 0 | 20 ± 0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 108 ± 164 | 103 ± 164 | 3.0 ± 2.9 | 278 ± 7 | 16 ± 0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 1447 ± 823 | 1525 ± 866 | 43.5 ± 19.3 | 394 ± 9 | 20 ± 0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 68 ± 5 | 64 ± 5 | 3.3 ± 0.4 | 248 ± 19 | 16 ± 0 |

## Capped tables (--table-cap 20 rules per switch, Open vSwitch refuses beyond it)

| Network | Workload | Controller | Hit rate % | Refused installs | Evictions | PACKET_INs at a full table | Samples with a full switch % | SmartTime cost (installs + evictions) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 28.4 ± 36.9 | 183199 ± 16735 | 0 ± 0 | 34501 ± 7101 | 96.1 ± 8.5 | 12011 ± 942 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 93.4 ± 0.6 | 0 ± 0 | 0 ± 0 | 0 ± 0 | 0.0 ± 0.0 | 3207 ± 5123 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 65.7 ± 3.6 | 224 ± 965 | 2518 ± 1227 | 2518 ± 1227 | 92.8 ± 6.5 | 46042 ± 24027 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 83.6 ± 1.3 | 0 ± 0 | 0 ± 0 | 0 ± 0 | 0.0 ± 0.0 | 1976 ± 151 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 0 of 240 | 28.4 ± 36.9 | 0 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 0 of 240 | 93.4 ± 0.6 | 0 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 0 of 240 | 65.7 ± 3.6 | 0 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 0 of 240 | 83.6 ± 1.3 | 0 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 7 | 0 | 82.26 / 18708.13 | 6081 | 95.7 | 400 | 32.9 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 7 | 0 | 32.96 / 292.98 | 142 | 3.5 | 278 | 93.3 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 7 | 0 | 85.10 / 873.61 | 1484 | 46.3 | 390 | 66.1 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 7 | 0 | 40.98 / 282.50 | 67 | 3.5 | 242 | 84.1 |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 8 | 0 | 121.49 / 23135.10 | 6522 | 97.1 | 400 | 11.9 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 8 | 0 | 34.74 / 324.59 | 31 | 1.7 | 275 | 93.6 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 8 | 0 | 94.97 / 780.14 | 1758 | 49.5 | 397 | 64.1 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 8 | 0 | 50.14 / 345.35 | 70 | 3.3 | 257 | 83.1 |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 9 | 0 | 147.30 / 22242.52 | 6220 | 95.4 | 400 | 40.6 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 9 | 0 | 43.22 / 347.91 | 149 | 3.7 | 281 | 93.1 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 9 | 0 | 96.39 / 906.23 | 1098 | 34.7 | 394 | 66.9 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 9 | 0 | 52.22 / 354.63 | 66 | 3.2 | 246 | 83.5 |
