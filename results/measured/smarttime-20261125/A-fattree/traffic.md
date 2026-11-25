# Realistic traffic results (A-fattree)

Testbed: Linux Harikrushna 6.18.58.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Tue Oct 27 00:24:11 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet
CPU: AMD Ryzen 7 8840HS w/ Radeon 780M Graphics, 16 threads | code: commit e4e178e3b8


**Every value is the mean of 5 runs (seeds 7 to 11, a new flow schedule each time) ± the half-width of its 95% confidence interval (Student's t).**

## Traffic generated (identical for every controller within one seed)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | DCTCP, SIGCOMM 2010 / pFabric web search workload | 1121 ± 27 | 37.4 ± 0.9 | 477.6 ± 19.1 (30%) | 14 ± 6 | 92 ± 10% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 1121 ± 27 / 0 ± 0 | 56.31 ± 9.66 / 33.01 ± 4.10 / 310.56 ± 53.30 | 2401.9 ± 527.8 | 9241.1 ± 4957.9 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 1121 ± 27 / 0 ± 0 | 55.35 ± 8.64 / 32.07 ± 4.21 / 292.91 ± 37.89 | 2324.5 ± 469.7 | 9513.9 ± 4958.1 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, exact-match rules | 1121 ± 27 / 0 ± 0 | 92.23 ± 11.57 / 74.72 ± 9.18 / 337.72 ± 52.87 | 2454.6 ± 424.5 | 9293.6 ± 4921.2 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 1121 ± 27 / 0 ± 0 | 58.51 ± 9.72 / 35.88 ± 5.87 / 304.37 ± 42.45 | 2425.3 ± 522.4 | 9204.1 ± 4562.6 |
| fattree-k4 | websearch | Proactive (ECMP) | 1121 ± 27 / 0 ± 0 | 53.42 ± 8.94 / 29.15 ± 5.48 / 309.11 ± 45.50 | 2375.4 ± 445.2 | 9338.6 ± 4699.8 |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 111 ± 55 | 106 ± 55 | 5.3 ± 0.9 | 829 ± 38 | 52 ± 2 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 45 ± 17 | 41 ± 17 | 1.9 ± 0.7 | 280 ± 6 | 16 ± 0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, exact-match rules | 495 ± 50 | 491 ± 50 | 39.6 ± 3.4 | 894 ± 252 | 125 ± 33 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 156 ± 7 | 152 ± 7 | 9.8 ± 0.5 | 567 ± 17 | 38 ± 1 |
| fattree-k4 | websearch | Proactive (ECMP) | 0 ± 0 | 0 ± 0 | 0.2 ± 0.0 | 1072 ± 0 | 58 ± 0 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 0 of 240 | 86.1 ± 0.2 | 0 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 0 of 240 | 93.6 ± 0.7 | 0 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, exact-match rules | 0 of 240 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 0 of 240 | 71.9 ± 0.9 | 0 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 7 | 0 | 29.43 / 291.59 | 120 | 5.6 | 844 | 86.3 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 7 | 0 | 28.66 / 291.74 | 30 | 1.4 | 275 | 93.3 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, exact-match rules | 7 | 0 | 77.64 / 350.21 | 503 | 41.6 | 1080 | 0.0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 7 | 0 | 34.21 / 288.43 | 157 | 10.1 | 570 | 72.8 |
| fattree-k4 | websearch | Proactive (ECMP) | 7 | 0 | 26.31 / 299.77 | 0 | 0.3 | 1072 | - |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 8 | 0 | 30.66 / 355.94 | 88 | 5.3 | 836 | 86.0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 8 | 0 | 32.01 / 316.58 | 51 | 2.0 | 275 | 93.6 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, exact-match rules | 8 | 0 | 72.14 / 323.50 | 554 | 40.4 | 887 | 0.0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 8 | 0 | 30.56 / 321.30 | 163 | 9.5 | 564 | 71.9 |
| fattree-k4 | websearch | Proactive (ECMP) | 8 | 0 | 23.36 / 332.77 | 0 | 0.2 | 1072 | - |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 9 | 0 | 37.78 / 349.26 | 185 | 6.3 | 798 | 86.1 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 9 | 0 | 37.47 / 329.62 | 56 | 2.8 | 283 | 93.1 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, exact-match rules | 9 | 0 | 84.22 / 387.57 | 491 | 40.6 | 1057 | 0.0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 9 | 0 | 43.25 / 353.17 | 152 | 9.1 | 546 | 72.2 |
| fattree-k4 | websearch | Proactive (ECMP) | 9 | 0 | 34.77 / 342.22 | 0 | 0.2 | 1072 | - |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 10 | 0 | 32.64 / 252.16 | 81 | 4.3 | 868 | 86.1 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 10 | 0 | 29.80 / 257.70 | 30 | 1.5 | 285 | 93.4 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, exact-match rules | 10 | 0 | 64.10 / 273.33 | 440 | 34.9 | 572 | 0.0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 10 | 0 | 34.25 / 263.43 | 158 | 10.1 | 582 | 70.9 |
| fattree-k4 | websearch | Proactive (ECMP) | 10 | 0 | 30.32 / 250.01 | 0 | 0.2 | 1072 | - |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 11 | 0 | 34.56 / 303.84 | 79 | 4.9 | 798 | 86.0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 11 | 0 | 32.41 / 268.92 | 59 | 1.9 | 281 | 94.5 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, exact-match rules | 11 | 0 | 75.51 / 354.00 | 490 | 40.8 | 873 | 0.0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 11 | 0 | 37.12 / 295.51 | 149 | 10.0 | 572 | 71.8 |
| fattree-k4 | websearch | Proactive (ECMP) | 11 | 0 | 31.00 / 320.77 | 0 | 0.2 | 1072 | - |
