# Realistic traffic results (B-cap20-fattree)

Testbed: Linux Nisarg 6.18.58.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Tue Oct 27 00:24:11 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet
CPU: AMD Ryzen AI 7 350 w/ Radeon 860M, 16 threads | code: commit e9d41c2984


**Every value is the mean of 3 runs (seeds 7 to 9, a new flow schedule each time) ± the half-width of its 95% confidence interval (Student's t).**

## Traffic generated (identical for every controller within one seed)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | DCTCP, SIGCOMM 2010 / pFabric web search workload | 1124 ± 70 | 37.5 ± 2.3 | 476.5 ± 46.1 (30%) | 15 ± 12 | 95 ± 4% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 1123 ± 68 / 1 ± 2 | 1961.49 ± 1499.38 / 110.24 ± 78.90 / 17900.68 ± 8740.01 | 7372.5 ± 2544.1 | 18506.0 ± 14000.1 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 1124 ± 70 / 0 ± 0 | 60.87 ± 14.64 / 36.53 ± 15.09 / 313.40 ± 25.11 | 2530.1 ± 408.3 | 10468.5 ± 7430.0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 1124 ± 70 / 0 ± 0 | 112.16 ± 21.10 / 85.59 ± 20.22 / 498.45 ± 297.94 | 2764.8 ± 584.2 | 11523.8 ± 8479.1 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 1124 ± 70 / 0 ± 0 | 69.79 ± 18.59 / 49.55 ± 17.22 / 337.39 ± 53.82 | 2747.3 ± 642.5 | 10882.1 ± 9982.6 |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 8830 ± 1200 | 8825 ± 1199 | 96.3 ± 1.1 | 400 ± 0 | 20 ± 0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 67 ± 167 | 63 ± 167 | 1.8 ± 1.4 | 278 ± 9 | 16 ± 0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 1348 ± 665 | 1433 ± 704 | 35.4 ± 16.6 | 395 ± 7 | 20 ± 0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 65 ± 8 | 61 ± 8 | 3.1 ± 0.3 | 248 ± 14 | 16 ± 0 |

## Capped tables (--table-cap 20 rules per switch, Open vSwitch refuses beyond it)

| Network | Workload | Controller | Hit rate % | Refused installs | Evictions | PACKET_INs at a full table | Samples with a full switch % | SmartTime cost (installs + evictions) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 37.0 ± 21.8 | 259352 ± 24798 | 0 ± 0 | 38578 ± 7434 | 100.0 ± 0.0 | 16172 ± 7785 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 93.3 ± 0.6 | 0 ± 0 | 0 ± 0 | 0 ± 0 | 0.0 ± 0.0 | 1994 ± 5220 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 65.6 ± 3.8 | 0 ± 0 | 2686 ± 1464 | 2686 ± 1464 | 100.0 ± 0.0 | 43131 ± 20614 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 83.6 ± 1.9 | 0 ± 0 | 0 ± 0 | 0 ± 0 | 0.0 ± 0.0 | 1947 ± 242 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 0 of 240 | 37.0 ± 21.8 | 0 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 0 of 240 | 93.3 ± 0.6 | 0 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 0 of 240 | 65.6 ± 3.8 | 0 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 0 of 240 | 83.6 ± 1.9 | 0 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 7 | 2 | 74.52 / 14294.59 | 8491 | 96.2 | 400 | 39.3 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 7 | 0 | 32.49 / 302.59 | 26 | 1.5 | 277 | 93.3 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 7 | 0 | 76.20 / 446.53 | 1525 | 41.0 | 392 | 66.0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 7 | 0 | 41.67 / 315.12 | 67 | 3.0 | 243 | 84.4 |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 8 | 1 | 120.90 / 21323.52 | 9383 | 96.8 | 400 | 27.3 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 8 | 0 | 33.59 / 315.00 | 30 | 1.6 | 275 | 93.5 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 8 | 0 | 90.65 / 413.24 | 1478 | 37.3 | 397 | 63.9 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 8 | 0 | 54.71 / 358.39 | 62 | 3.0 | 254 | 82.9 |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 9 | 0 | 135.30 / 18083.92 | 8615 | 95.9 | 400 | 44.4 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 9 | 0 | 43.52 / 322.62 | 145 | 2.5 | 282 | 93.0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 9 | 0 | 89.93 / 635.60 | 1040 | 28.0 | 396 | 66.8 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 9 | 0 | 52.28 / 338.65 | 67 | 3.2 | 247 | 83.4 |
