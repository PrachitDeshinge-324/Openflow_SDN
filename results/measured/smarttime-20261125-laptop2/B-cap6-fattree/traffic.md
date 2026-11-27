# Realistic traffic results (B-cap6-fattree)

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
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 663 ± 90 / 460 ± 55 | 9842.58 ± 2515.16 / 5313.39 ± 3156.90 / 38763.48 ± 1805.98 | 8946.0 ± 6060.5 | 11572.1 ± 17883.9 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 819 ± 46 / 304 ± 67 | 7156.08 ± 5200.74 / 1453.80 ± 2302.71 / 36731.59 ± 6794.57 | 8914.7 ± 4415.2 | 10997.3 ± 4290.3 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 587 ± 214 / 536 ± 158 | 11280.10 ± 5482.45 / 7248.26 ± 9013.31 / 38130.27 ± 3623.96 | 13680.5 ± 6261.5 | 8756.3 ± 3574.9 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 980 ± 235 / 144 ± 167 | 4435.01 ± 4715.43 / 1556.56 ± 2682.41 / 26896.18 ± 14560.65 | 14079.3 ± 7184.5 | 30485.7 ± 33807.6 |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 11167 ± 272 | 11162 ± 272 | 99.9 ± 0.2 | 120 ± 0 | 6 ± 0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 10965 ± 883 | 10961 ± 883 | 99.2 ± 2.0 | 120 ± 0 | 6 ± 0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 9742 ± 301 | 10810 ± 556 | 99.2 ± 1.3 | 120 ± 0 | 6 ± 0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 9932 ± 1956 | 10383 ± 2104 | 98.2 ± 4.1 | 120 ± 0 | 6 ± 0 |

## Capped tables (--table-cap 6 rules per switch, Open vSwitch refuses beyond it)

| Network | Workload | Controller | Hit rate % | Refused installs | Evictions | PACKET_INs at a full table | Samples with a full switch % | SmartTime cost (installs + evictions) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 0.0 ± 0.0 | 320402 ± 5543 | 0 ± 0 | 71185 ± 14610 | 100.0 ± 0.0 | 17552 ± 1244 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 0.0 ± 0.0 | 318181 ± 20090 | 0 ± 0 | 43661 ± 10181 | 100.0 ± 0.0 | 19645 ± 8977 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 0.0 ± 0.0 | 0 ± 0 | 32396 ± 7759 | 32396 ± 7759 | 100.0 ± 0.0 | 326650 ± 15655 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 23.6 ± 34.4 | 0 ± 0 | 13906 ± 4323 | 13906 ± 4323 | 100.0 ± 0.0 | 316871 ± 51733 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 0 of 240 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 0 of 240 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 0 of 240 | 0.0 ± 0.0 | 0 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 0 of 240 | 23.6 ± 34.4 | 0 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 7 | 463 | 3847.50 / 37966.19 | 11189 | 99.9 | 120 | 0.0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 7 | 326 | 484.60 / 33575.98 | 11233 | 100.0 | 120 | 0.0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 7 | 478 | 5662.43 / 38056.49 | 9666 | 99.5 | 120 | 0.0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 7 | 67 | 420.71 / 21385.46 | 9042 | 96.8 | 120 | 36.1 |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 8 | 437 | 5990.61 / 39389.49 | 11048 | 99.9 | 120 | 0.0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 8 | 313 | 1545.21 / 38417.05 | 10562 | 98.4 | 120 | 0.0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 8 | 604 | 11399.24 / 39624.47 | 9881 | 99.5 | 120 | 0.0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 8 | 192 | 2569.68 / 33053.75 | 10537 | 100.0 | 120 | 8.7 |
| fattree-k4 | websearch | Reactive on shortest paths, pair rules | 9 | 481 | 6102.05 / 38934.78 | 11263 | 100.0 | 120 | 0.0 |
| fattree-k4 | websearch | Reactive on shortest paths, destination rules | 9 | 274 | 2331.61 / 38201.74 | 11100 | 99.3 | 120 | 0.0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, pair rules | 9 | 527 | 4683.10 / 36709.83 | 9678 | 98.6 | 120 | 0.0 |
| fattree-k4 | websearch | SmartTime-style adaptive timeout, destination rules | 9 | 172 | 1679.28 / 26249.34 | 10216 | 97.7 | 120 | 26.0 |
