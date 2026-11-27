# Realistic traffic results (check-cap)

Testbed: Linux Nisarg 6.18.58.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Tue Oct 27 00:24:11 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 10 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet
CPU: AMD Ryzen AI 7 350 w/ Radeon 860M, 16 threads | code: commit e9d41c2984


## Traffic generated (identical for every controller)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Benson et al., IMC 2010 (university data centres) | 1990 | 199.0 | 79.7 (5%) | 0 | 84% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 1990 / 0 | 1988.71 / 1065.91 / 8056.40 | 9492.7 | - |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 1990 / 0 | 3524.18 / 3167.87 / 10340.15 | 13727.8 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 8596 | 8595 | 99.8 | 30 | 6 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 6517 | 8506 | 100.2 | 30 | 6 |

## Capped tables (--table-cap 6 rules per switch, Open vSwitch refuses beyond it)

| Network | Workload | Controller | Hit rate % | Refused installs | Evictions | PACKET_INs at a full table | Samples with a full switch % | SmartTime cost (installs + evictions) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 0.0 | 83220 | 0 | 23398 | 100.0 | 3346 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 0.0 | 0 | 20750 | 20750 | 100.0 | 89368 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths, pair rules | 0 of 240 | 0.0 | 0 | 0 |
| tree-d2-f4 | university | SmartTime-style adaptive timeout, pair rules | 0 of 240 | 0.0 | 0 | 0 |
