# Realistic traffic results (traffic-20261119-125611)

Testbed: Linux Harikrushna 6.18.58.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Tue Oct 27 00:24:11 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 5% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet

**Every value is the mean of 3 runs (seeds 7 to 9, a new flow schedule each time) ± the half-width of its 95% confidence interval (Student's t).**

## Traffic generated (identical for every controller within one seed)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k6 | websearch | DCTCP, SIGCOMM 2010 / pFabric web search workload | 642 ± 114 | 21.4 ± 3.8 | 270.8 ± 73.3 (5%) | 10 ± 5 | 98 ± 2% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| fattree-k6 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 642 ± 114 / 0 ± 0 | 58.85 ± 13.28 / 51.93 ± 8.39 / 180.02 ± 35.15 | 359.8 ± 124.3 | 1787.3 ± 46.2 |
| fattree-k6 | websearch | Reactive on shortest paths, pair rules | 642 ± 114 / 0 ± 0 | 26.89 ± 9.58 / 23.26 ± 8.69 / 137.18 ± 13.80 | 328.7 ± 115.6 | 1745.9 ± 102.6 |
| fattree-k6 | websearch | Reactive on shortest paths, destination rules | 642 ± 114 / 0 ± 0 | 19.83 ± 4.90 / 12.69 ± 3.97 / 140.64 ± 71.59 | 315.6 ± 108.5 | 1722.9 ± 61.2 |
| fattree-k6 | websearch | Proactive (ECMP) | 642 ± 114 / 0 ± 0 | 13.03 ± 3.40 / 4.98 ± 0.69 / 132.99 ± 51.00 | 310.1 ± 104.7 | 1729.0 ± 21.3 |
| fattree-k6 | websearch | Forward first, tell the controller (destination rules + SYN/FIN copies) | 642 ± 114 / 0 ± 0 | 14.19 ± 4.71 / 5.31 ± 1.07 / 153.84 ± 70.31 | 332.2 ± 120.5 | 1908.1 ± 611.3 |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k6 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 362 ± 27 | 355 ± 28 | 21.0 ± 3.4 | 2163 ± 397 | 139 ± 88 |
| fattree-k6 | websearch | Reactive on shortest paths, pair rules | 212 ± 36 | 205 ± 37 | 10.4 ± 3.5 | 1242 ± 238 | 51 ± 6 |
| fattree-k6 | websearch | Reactive on shortest paths, destination rules | 154 ± 26 | 147 ± 26 | 6.5 ± 1.4 | 775 ± 69 | 25 ± 2 |
| fattree-k6 | websearch | Proactive (ECMP) | 0 ± 0 | 0 ± 0 | 0.4 ± 0.0 | 13230 ± 0 | 312 ± 0 |
| fattree-k6 | websearch | Forward first, tell the controller (destination rules + SYN/FIN copies) | 63 ± 11 | 0 ± 0 | 2.8 ± 0.6 | 2592 ± 0 | 63 ± 0 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| fattree-k6 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 0 of 2862 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| fattree-k6 | websearch | Reactive on shortest paths, pair rules | 0 of 2862 | 50.8 ± 5.0 | 0 ± 0 | 0 ± 0 |
| fattree-k6 | websearch | Reactive on shortest paths, destination rules | 0 of 2862 | 59.3 ± 2.2 | 0 ± 0 | 0 ± 0 |
| fattree-k6 | websearch | Forward first, tell the controller (destination rules + SYN/FIN copies) | 0 of 2862 | 100.0 ± 0.0 | 0 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k6 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 7 | 0 | 52.08 / 174.60 | 357 | 20.8 | 2115 | 0.0 |
| fattree-k6 | websearch | Reactive on shortest paths, pair rules | 7 | 0 | 23.84 / 131.68 | 202 | 10.1 | 1178 | 51.2 |
| fattree-k6 | websearch | Reactive on shortest paths, destination rules | 7 | 0 | 13.13 / 126.87 | 145 | 6.4 | 772 | 58.9 |
| fattree-k6 | websearch | Proactive (ECMP) | 7 | 0 | 4.92 / 121.33 | 0 | 0.5 | 13230 | - |
| fattree-k6 | websearch | Forward first, tell the controller (destination rules + SYN/FIN copies) | 7 | 0 | 5.43 / 180.88 | 62 | 2.8 | 2592 | 100.0 |
| fattree-k6 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 8 | 0 | 48.47 / 169.39 | 355 | 19.7 | 2032 | 0.0 |
| fattree-k6 | websearch | Reactive on shortest paths, pair rules | 8 | 0 | 19.50 / 137.07 | 205 | 9.1 | 1195 | 52.6 |
| fattree-k6 | websearch | Reactive on shortest paths, destination rules | 8 | 0 | 10.91 / 121.29 | 152 | 6.0 | 749 | 60.4 |
| fattree-k6 | websearch | Proactive (ECMP) | 8 | 0 | 4.73 / 120.95 | 0 | 0.5 | 13230 | - |
| fattree-k6 | websearch | Forward first, tell the controller (destination rules + SYN/FIN copies) | 8 | 0 | 4.83 / 124.42 | 60 | 2.5 | 2592 | 100.0 |
| fattree-k6 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 9 | 0 | 55.23 / 196.08 | 375 | 22.4 | 2341 | 0.0 |
| fattree-k6 | websearch | Reactive on shortest paths, pair rules | 9 | 0 | 26.43 / 142.78 | 229 | 11.9 | 1352 | 48.6 |
| fattree-k6 | websearch | Reactive on shortest paths, destination rules | 9 | 0 | 14.02 / 173.75 | 165 | 7.2 | 804 | 58.7 |
| fattree-k6 | websearch | Proactive (ECMP) | 9 | 0 | 5.28 / 156.69 | 0 | 0.4 | 13230 | - |
| fattree-k6 | websearch | Forward first, tell the controller (destination rules + SYN/FIN copies) | 9 | 0 | 5.67 / 156.23 | 68 | 3.1 | 2592 | 100.0 |
