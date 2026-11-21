# Realistic traffic results (traffic-20261121-075657)

Testbed: Linux Harikrushna 6.18.58.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Tue Oct 27 00:24:11 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet
CPU: AMD Ryzen 7 8840HS w/ Radeon 780M Graphics, 16 threads | code: commit 369b32d226


**Every value is the mean of 5 runs (seeds 7 to 11, a new flow schedule each time) ± the half-width of its 95% confidence interval (Student's t).**

## Traffic generated (identical for every controller within one seed)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | DCTCP, SIGCOMM 2010 / pFabric web search workload | 1121 ± 27 | 37.4 ± 0.9 | 477.6 ± 19.1 (30%) | 14 ± 6 | 92 ± 10% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 1121 ± 27 / 0 ± 0 | 57.35 ± 9.34 / 33.35 ± 3.36 / 319.73 ± 45.82 | 2507.0 ± 577.5 | 9327.4 ± 4846.7 |
| fattree-k4 | websearch | Proactive (ECMP) | 1121 ± 27 / 0 ± 0 | 54.46 ± 9.18 / 30.00 ± 5.50 / 311.80 ± 51.05 | 2451.1 ± 447.3 | 9586.7 ± 4744.8 |
| fattree-k4 | websearch | Proactive, one rule per destination (tap without its copy rules) | 1120 ± 28 / 1 ± 4 | 64.38 ± 33.52 / 39.80 ± 23.08 / 353.08 ± 167.79 | 3063.3 ± 2115.4 | 9898.2 ± 5868.6 |
| fattree-k4 | websearch | Forward first, tell the controller (destination rules + SYN/FIN copies) | 1120 ± 28 / 1 ± 4 | 64.30 ± 33.64 / 40.59 ± 22.81 / 350.79 ± 183.87 | 3050.0 ± 2129.3 | 10088.8 ± 5708.4 |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 109 ± 70 | 106 ± 70 | 5.0 ± 1.7 | 279 ± 6 | 16 ± 0 |
| fattree-k4 | websearch | Proactive (ECMP) | 0 ± 0 | 0 ± 0 | 0.4 ± 0.1 | 1072 ± 0 | 58 ± 0 |
| fattree-k4 | websearch | Proactive, one rule per destination (tap without its copy rules) | 0 ± 0 | 0 ± 0 | 0.5 ± 0.1 | 320 ± 0 | 16 ± 0 |
| fattree-k4 | websearch | Forward first, tell the controller (destination rules + SYN/FIN copies) | 108 ± 2 | 0 ± 0 | 7.5 ± 1.0 | 368 ± 0 | 22 ± 0 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 0 of 240 | 93.6 ± 0.7 | 0 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | Proactive, one rule per destination (tap without its copy rules) | 0 of 240 | 100.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | Forward first, tell the controller (destination rules + SYN/FIN copies) | 0 of 240 | 100.0 ± 0.0 | 0 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 7 | 0 | 30.51 / 305.96 | 64 | 3.8 | 275 | 93.3 |
| fattree-k4 | websearch | Proactive (ECMP) | 7 | 0 | 30.72 / 287.12 | 0 | 0.4 | 1072 | - |
| fattree-k4 | websearch | Proactive, one rule per destination (tap without its copy rules) | 7 | 0 | 29.74 / 298.61 | 0 | 0.5 | 320 | 100.0 |
| fattree-k4 | websearch | Forward first, tell the controller (destination rules + SYN/FIN copies) | 7 | 0 | 31.08 / 310.23 | 109 | 8.4 | 368 | 100.0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 8 | 0 | 32.33 / 331.91 | 125 | 5.6 | 274 | 93.6 |
| fattree-k4 | websearch | Proactive (ECMP) | 8 | 0 | 23.93 / 349.45 | 0 | 0.4 | 1072 | - |
| fattree-k4 | websearch | Proactive, one rule per destination (tap without its copy rules) | 8 | 7 | 72.73 / 590.78 | 0 | 0.6 | 320 | 100.0 |
| fattree-k4 | websearch | Forward first, tell the controller (destination rules + SYN/FIN copies) | 8 | 7 | 72.85 / 605.19 | 105 | 7.7 | 368 | 100.0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 9 | 0 | 37.62 / 369.92 | 200 | 7.1 | 282 | 93.0 |
| fattree-k4 | websearch | Proactive (ECMP) | 9 | 0 | 36.38 / 354.46 | 0 | 0.5 | 1072 | - |
| fattree-k4 | websearch | Proactive, one rule per destination (tap without its copy rules) | 9 | 0 | 33.25 / 331.99 | 0 | 0.6 | 320 | 100.0 |
| fattree-k4 | websearch | Forward first, tell the controller (destination rules + SYN/FIN copies) | 9 | 0 | 34.08 / 338.16 | 106 | 7.8 | 368 | 100.0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 10 | 0 | 32.20 / 268.87 | 66 | 4.2 | 286 | 93.5 |
| fattree-k4 | websearch | Proactive (ECMP) | 10 | 0 | 29.46 / 257.82 | 0 | 0.3 | 1072 | - |
| fattree-k4 | websearch | Proactive, one rule per destination (tap without its copy rules) | 10 | 0 | 28.44 / 274.84 | 0 | 0.5 | 320 | 100.0 |
| fattree-k4 | websearch | Forward first, tell the controller (destination rules + SYN/FIN copies) | 10 | 0 | 27.70 / 228.11 | 109 | 6.4 | 368 | 100.0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 11 | 0 | 34.08 / 322.01 | 91 | 4.3 | 278 | 94.5 |
| fattree-k4 | websearch | Proactive (ECMP) | 11 | 0 | 29.51 / 310.15 | 0 | 0.3 | 1072 | - |
| fattree-k4 | websearch | Proactive, one rule per destination (tap without its copy rules) | 11 | 0 | 34.83 / 269.19 | 0 | 0.4 | 320 | 100.0 |
| fattree-k4 | websearch | Forward first, tell the controller (destination rules + SYN/FIN copies) | 11 | 0 | 37.24 / 272.25 | 108 | 7.0 | 368 | 100.0 |
