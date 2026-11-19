# Realistic traffic results (traffic-20261119-120616)

Testbed: Linux Harikrushna 6.18.58.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Tue Oct 27 00:24:11 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet

**Every value is the mean of 5 runs (seeds 7 to 11, a new flow schedule each time) ± the half-width of its 95% confidence interval (Student's t).**

## Traffic generated (identical for every controller within one seed)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | DCTCP, SIGCOMM 2010 / pFabric web search workload | 1121 ± 27 | 37.4 ± 0.9 | 477.6 ± 19.1 (30%) | 14 ± 6 | 92 ± 10% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 1121 ± 27 / 0 ± 0 | 90.65 ± 12.51 / 74.23 ± 8.08 / 322.17 ± 48.32 | 2396.5 ± 514.8 | 9462.0 ± 4678.3 |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 1121 ± 27 / 0 ± 0 | 55.66 ± 10.89 / 32.77 ± 5.10 / 299.53 ± 48.96 | 2410.1 ± 563.5 | 9212.6 ± 4767.6 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 1121 ± 27 / 0 ± 0 | 55.98 ± 8.62 / 31.67 ± 4.64 / 303.44 ± 41.16 | 2369.5 ± 484.6 | 9269.1 ± 5048.4 |
| fattree-k4 | websearch | Proactive (ECMP) | 1121 ± 27 / 0 ± 0 | 53.53 ± 8.93 / 29.65 ± 5.52 / 301.25 ± 34.42 | 2401.2 ± 420.0 | 9103.1 ± 4802.4 |
| fattree-k4 | websearch | Forward first, tell the controller (destination rules + SYN/FIN copies) | 1121 ± 28 / 1 ± 2 | 62.17 ± 32.29 / 39.27 ± 21.90 / 346.64 ± 175.31 | 2954.4 ± 2065.8 | 10734.0 ± 7711.3 |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 494 ± 50 | 490 ± 50 | 33.1 ± 3.1 | 3764 ± 437 | 373 ± 53 |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 111 ± 52 | 107 ± 52 | 5.0 ± 0.7 | 827 ± 30 | 52 ± 2 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 60 ± 23 | 55 ± 23 | 2.1 ± 0.5 | 280 ± 6 | 16 ± 0 |
| fattree-k4 | websearch | Proactive (ECMP) | 0 ± 0 | 0 ± 0 | 0.2 ± 0.0 | 1072 ± 0 | 58 ± 0 |
| fattree-k4 | websearch | Forward first, tell the controller (destination rules + SYN/FIN copies) | 109 ± 3 | 0 ± 0 | 4.3 ± 0.3 | 368 ± 0 | 22 ± 0 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 0 of 240 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 0 of 240 | 86.1 ± 0.2 | 0 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 0 of 240 | 93.6 ± 0.7 | 0 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | Forward first, tell the controller (destination rules + SYN/FIN copies) | 0 of 240 | 100.0 ± 0.0 | 0 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 7 | 0 | 70.27 / 319.65 | 495 | 33.3 | 3833 | 0.0 |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 7 | 0 | 31.50 / 271.79 | 86 | 4.6 | 834 | 86.3 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 7 | 0 | 27.83 / 321.60 | 53 | 1.9 | 275 | 93.3 |
| fattree-k4 | websearch | Proactive (ECMP) | 7 | 0 | 25.90 / 306.47 | 0 | 0.2 | 1072 | - |
| fattree-k4 | websearch | Forward first, tell the controller (destination rules + SYN/FIN copies) | 7 | 0 | 29.98 / 319.58 | 112 | 4.4 | 368 | 100.0 |
| fattree-k4 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 8 | 0 | 76.59 / 321.05 | 550 | 35.4 | 4028 | 0.0 |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 8 | 0 | 28.79 / 303.53 | 102 | 4.9 | 836 | 86.0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 8 | 0 | 32.03 / 331.20 | 63 | 2.1 | 275 | 93.6 |
| fattree-k4 | websearch | Proactive (ECMP) | 8 | 0 | 25.18 / 308.30 | 0 | 0.2 | 1072 | - |
| fattree-k4 | websearch | Forward first, tell the controller (destination rules + SYN/FIN copies) | 8 | 3 | 70.30 / 587.18 | 107 | 4.0 | 368 | 100.0 |
| fattree-k4 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 9 | 0 | 79.67 / 366.69 | 488 | 33.4 | 3971 | 0.0 |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 9 | 0 | 39.51 / 353.85 | 184 | 6.0 | 803 | 86.1 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 9 | 0 | 37.15 / 323.75 | 78 | 2.8 | 283 | 93.1 |
| fattree-k4 | websearch | Proactive (ECMP) | 9 | 0 | 36.27 / 327.70 | 0 | 0.2 | 1072 | - |
| fattree-k4 | websearch | Forward first, tell the controller (destination rules + SYN/FIN copies) | 9 | 0 | 33.69 / 334.09 | 107 | 4.3 | 368 | 100.0 |
| fattree-k4 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 10 | 0 | 64.84 / 261.52 | 436 | 28.8 | 3153 | 0.0 |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 10 | 0 | 30.68 / 252.49 | 83 | 4.6 | 858 | 86.0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 10 | 0 | 28.54 / 251.76 | 31 | 1.5 | 285 | 93.4 |
| fattree-k4 | websearch | Proactive (ECMP) | 10 | 0 | 30.44 / 254.07 | 0 | 0.2 | 1072 | - |
| fattree-k4 | websearch | Forward first, tell the controller (destination rules + SYN/FIN copies) | 10 | 0 | 27.05 / 225.88 | 111 | 4.2 | 368 | 100.0 |
| fattree-k4 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 11 | 0 | 79.76 / 341.94 | 502 | 34.5 | 3833 | 0.0 |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 11 | 0 | 33.34 / 316.01 | 100 | 5.0 | 802 | 86.0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 11 | 0 | 32.80 / 288.88 | 72 | 2.0 | 281 | 94.5 |
| fattree-k4 | websearch | Proactive (ECMP) | 11 | 0 | 30.45 / 309.73 | 0 | 0.2 | 1072 | - |
| fattree-k4 | websearch | Forward first, tell the controller (destination rules + SYN/FIN copies) | 11 | 0 | 35.33 / 266.46 | 110 | 4.6 | 368 | 100.0 |
