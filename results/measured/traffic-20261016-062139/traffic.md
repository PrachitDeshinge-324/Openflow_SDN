# Realistic traffic results (traffic-20261016-062139)

Testbed: Linux Harikrushna 6.18.33.2-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Thu Jun 18 21:54:43 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 20 s of arrivals | target load 5% (websearch/datamining) | flows capped at 20 MB | pair popularity: uniform

Controller: same machine as Mininet

## Traffic generated (identical for every controller)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k6 | websearch | DCTCP, SIGCOMM 2010 / pFabric web search workload | 411 | 20.6 | 283.6 (5%) | 6 | 97% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| fattree-k6 | websearch | Proactive (ECMP) | 411 / 0 | 9.82 / 5.71 / 66.88 | 261.6 | 1668.7 |
| fattree-k6 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 411 / 0 | 47.45 / 41.97 / 105.54 | 299.2 | 1658.6 |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k6 | websearch | Proactive (ECMP) | 0 | 0 | 0.5 | 13230 | 312 |
| fattree-k6 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 369 | 358 | 19.4 | 2058 | 80 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| fattree-k6 | websearch | Reactive on shortest paths (hybrid, budget 0%) | 0 of 2862 | 0.0 | 0 | 0 |
