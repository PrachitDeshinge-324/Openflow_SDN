# Realistic traffic results (B-cap20-tree)

Testbed: Linux Nisarg 6.18.58.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Tue Oct 27 00:24:11 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet
CPU: AMD Ryzen AI 7 350 w/ Radeon 860M, 16 threads | code: commit e9d41c2984


**Every value is the mean of 3 runs (seeds 7 to 9, a new flow schedule each time) ± the half-width of its 95% confidence interval (Student's t).**

## Traffic generated (identical for every controller within one seed)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Benson et al., IMC 2010 (university data centres) | 6090 ± 83 | 203.0 ± 2.8 | 89.8 ± 28.9 (6%) | 0 ± 0 | 87 ± 6% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 6090 ± 83 / 0 ± 0 | 2791.69 ± 3043.62 / 615.60 ± 1383.95 / 12800.56 ± 11840.32 | 10939.4 ± 8665.7 | - |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 6090 ± 83 / 0 ± 0 | 5.89 ± 1.77 / 1.13 ± 0.30 / 43.78 ± 6.75 | 155.7 ± 39.6 | - |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 6090 ± 83 / 0 ± 0 | 365.50 ± 1427.80 / 34.74 ± 50.18 / 2810.90 ± 11082.90 | 1961.8 ± 7222.2 | - |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 6090 ± 83 / 0 ± 0 | 6.03 ± 1.62 / 1.12 ± 0.34 / 45.76 ± 4.38 | 155.8 ± 32.9 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 9662 ± 566 | 9661 ± 566 | 99.9 ± 0.7 | 100 ± 0 | 20 ± 0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 2 ± 1 | 1 ± 1 | 0.2 ± 0.0 | 80 ± 0 | 16 ± 0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 4419 ± 2797 | 5423 ± 3209 | 73.3 ± 27.1 | 100 ± 0 | 20 ± 0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 4 ± 3 | 3 ± 3 | 0.3 ± 0.1 | 80 ± 0 | 16 ± 0 |

## Capped tables (--table-cap 20 rules per switch, Open vSwitch refuses beyond it)

| Network | Workload | Controller | Hit rate % | Refused installs | Evictions | PACKET_INs at a full table | Samples with a full switch % | SmartTime cost (installs + evictions) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 5.0 ± 21.6 | 283647 ± 10038 | 0 ± 0 | 76407 ± 8234 | 100.0 ± 0.0 | 9664 ± 8039 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 99.5 ± 0.1 | 0 ± 0 | 0 ± 0 | 0 ± 0 | 0.0 ± 0.0 | 205 ± 78 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 40.0 ± 16.9 | 0 ± 0 | 30585 ± 12103 | 30585 ± 12103 | 100.0 ± 0.0 | 165281 ± 92842 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 99.3 ± 0.2 | 0 ± 0 | 0 ± 0 | 0 ± 0 | 0.0 ± 0.0 | 270 ± 48 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 0 of 240 | 5.0 ± 21.6 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 0 of 240 | 99.5 ± 0.1 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 0 of 240 | 40.0 ± 16.9 | 0 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 0 of 240 | 99.3 ± 0.2 | 0 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 7 | 0 | 569.13 / 13175.28 | 9861 | 100.1 | 100 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 7 | 0 | 1.15 / 46.88 | 1 | 0.2 | 80 | 99.6 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 7 | 0 | 58.06 / 7962.14 | 5717 | 85.8 | 100 | 32.7 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 7 | 0 | 1.12 / 47.71 | 4 | 0.3 | 80 | 99.3 |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 8 | 0 | 1194.45 / 17368.12 | 9712 | 100.1 | 100 | 0.0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 8 | 0 | 1.23 / 42.62 | 1 | 0.2 | 80 | 99.5 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 8 | 0 | 22.66 / 235.44 | 3831 | 67.3 | 100 | 46.2 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 8 | 0 | 1.27 / 45.27 | 5 | 0.3 | 80 | 99.3 |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 9 | 0 | 83.22 / 7858.27 | 9413 | 99.6 | 100 | 15.0 |
| tree-d2-f4 | university | Reactive on shortest paths, destination rules | 9 | 0 | 1.00 / 41.83 | 2 | 0.2 | 80 | 99.5 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 9 | 0 | 23.51 / 235.12 | 3709 | 66.6 | 100 | 41.0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, destination rules | 9 | 0 | 0.99 / 44.29 | 3 | 0.3 | 80 | 99.4 |
