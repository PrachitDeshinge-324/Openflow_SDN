# Realistic traffic results (traffic-20261121-084548)

Testbed: Linux Harikrushna 6.18.58.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Tue Oct 27 00:24:11 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 5% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet
CPU: AMD Ryzen 7 8840HS w/ Radeon 780M Graphics, 16 threads | code: commit 369b32d226


**Every value is the mean of 3 runs (seeds 7 to 9, a new flow schedule each time) ± the half-width of its 95% confidence interval (Student's t).**

## Traffic generated (identical for every controller within one seed)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k6 | websearch | DCTCP, SIGCOMM 2010 / pFabric web search workload | 642 ± 114 | 21.4 ± 3.8 | 270.8 ± 73.3 (5%) | 10 ± 5 | 98 ± 2% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| fattree-k6 | websearch | Reactive on shortest paths, destination rules | 642 ± 114 / 0 ± 0 | 23.88 ± 10.39 / 17.10 ± 8.41 / 151.84 ± 101.81 | 326.0 ± 109.9 | 1730.3 ± 83.1 |
| fattree-k6 | websearch | Proactive (ECMP) | 642 ± 114 / 0 ± 0 | 13.13 ± 3.15 / 5.46 ± 1.12 / 140.65 ± 35.76 | 314.2 ± 115.4 | 1740.8 ± 101.2 |
| fattree-k6 | websearch | Proactive, one rule per destination (tap without its copy rules) | 642 ± 114 / 0 ± 0 | 14.57 ± 4.21 / 5.32 ± 1.11 / 148.06 ± 4.70 | 333.0 ± 111.5 | 1936.6 ± 693.8 |
| fattree-k6 | websearch | Forward first, tell the controller (destination rules + SYN/FIN copies) | 642 ± 114 / 0 ± 0 | 14.71 ± 4.90 / 5.61 ± 1.22 / 145.14 ± 38.34 | 333.3 ± 112.7 | 1937.4 ± 710.7 |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k6 | websearch | Reactive on shortest paths, destination rules | 146 ± 30 | 139 ± 26 | 9.1 ± 4.1 | 773 ± 96 | 25 ± 1 |
| fattree-k6 | websearch | Proactive (ECMP) | 0 ± 0 | 0 ± 0 | 0.5 ± 0.4 | 13230 ± 0 | 312 ± 0 |
| fattree-k6 | websearch | Proactive, one rule per destination (tap without its copy rules) | 0 ± 0 | 0 ± 0 | 0.7 ± 0.3 | 2430 ± 0 | 54 ± 0 |
| fattree-k6 | websearch | Forward first, tell the controller (destination rules + SYN/FIN copies) | 63 ± 11 | 0 ± 0 | 3.7 ± 1.4 | 2592 ± 0 | 63 ± 0 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| fattree-k6 | websearch | Reactive on shortest paths, destination rules | 0 of 2862 | 59.4 ± 2.1 | 0 ± 0 | 0 ± 0 |
| fattree-k6 | websearch | Proactive, one rule per destination (tap without its copy rules) | 0 of 2862 | 100.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| fattree-k6 | websearch | Forward first, tell the controller (destination rules + SYN/FIN copies) | 0 of 2862 | 100.0 ± 0.0 | 0 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k6 | websearch | Reactive on shortest paths, destination rules | 7 | 0 | 20.38 / 135.04 | 133 | 10.9 | 755 | 58.9 |
| fattree-k6 | websearch | Proactive (ECMP) | 7 | 0 | 5.89 / 138.85 | 0 | 0.7 | 13230 | - |
| fattree-k6 | websearch | Proactive, one rule per destination (tap without its copy rules) | 7 | 0 | 5.64 / 146.61 | 0 | 0.8 | 2430 | 100.0 |
| fattree-k6 | websearch | Forward first, tell the controller (destination rules + SYN/FIN copies) | 7 | 0 | 5.88 / 154.58 | 61 | 4.3 | 2592 | 100.0 |
| fattree-k6 | websearch | Reactive on shortest paths, destination rules | 8 | 0 | 13.62 / 121.93 | 147 | 7.6 | 746 | 60.4 |
| fattree-k6 | websearch | Proactive (ECMP) | 8 | 0 | 5.00 / 127.25 | 0 | 0.5 | 13230 | - |
| fattree-k6 | websearch | Proactive, one rule per destination (tap without its copy rules) | 8 | 0 | 4.81 / 150.20 | 0 | 0.6 | 2430 | 100.0 |
| fattree-k6 | websearch | Forward first, tell the controller (destination rules + SYN/FIN copies) | 8 | 0 | 5.04 / 127.33 | 60 | 3.1 | 2592 | 100.0 |
| fattree-k6 | websearch | Reactive on shortest paths, destination rules | 9 | 0 | 17.30 / 198.55 | 157 | 8.9 | 817 | 58.8 |
| fattree-k6 | websearch | Proactive (ECMP) | 9 | 0 | 5.50 / 155.86 | 0 | 0.4 | 13230 | - |
| fattree-k6 | websearch | Proactive, one rule per destination (tap without its copy rules) | 9 | 0 | 5.51 / 147.36 | 0 | 0.6 | 2430 | 100.0 |
| fattree-k6 | websearch | Forward first, tell the controller (destination rules + SYN/FIN copies) | 9 | 0 | 5.90 / 153.51 | 68 | 3.8 | 2592 | 100.0 |
