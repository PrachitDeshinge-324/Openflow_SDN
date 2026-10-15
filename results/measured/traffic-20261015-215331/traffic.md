# Realistic traffic results (traffic-20261015-215331)

Testbed: Linux Harikrushna 6.18.33.2-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Thu Jun 18 21:54:43 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: uniform

Controller: same machine as Mininet

## Traffic generated (identical for every controller)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Abilene traffic matrices (Zhang et al., IMC 2005) + SURGE flow sizes | 1761 | 58.7 | 27.5 (3%) | 0 | 100% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Reactive (learning + spanning tree) | 1761 / 0 | 133.96 / 117.48 / 402.09 | 287.7 | - |
| abilene | isp | Reactive, long timeouts | 1761 / 0 | 133.91 / 116.56 / 409.96 | 287.5 | - |
| abilene | isp | Reactive on shortest paths (hybrid, budget 0%) | 1761 / 0 | 87.48 / 73.36 / 242.40 | 208.2 | - |
| abilene | isp | Hybrid, counter keeps top 10% of pairs | 1761 / 0 | 77.54 / 68.45 / 232.06 | 194.7 | - |
| abilene | isp | Hybrid, counter keeps top 25% of pairs | 1761 / 0 | 69.59 / 62.71 / 217.65 | 187.3 | - |
| abilene | isp | Hybrid, counter keeps top 50% of pairs | 1761 / 0 | 62.88 / 52.31 / 206.21 | 181.0 | - |
| abilene | isp | Oracle, busiest 10% of pairs (upper bound) | 1761 / 0 | 75.43 / 67.18 / 231.84 | 193.6 | - |
| abilene | isp | Oracle, busiest 25% of pairs (upper bound) | 1761 / 0 | 66.20 / 60.54 / 202.77 | 183.1 | - |
| abilene | isp | Oracle, busiest 50% of pairs (upper bound) | 1761 / 0 | 60.95 / 50.07 / 194.32 | 177.6 | - |
| abilene | isp | Proactive (one shortest path) | 1761 / 0 | 59.05 / 47.81 / 191.35 | 176.6 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Reactive (learning + spanning tree) | 619 | 613 | 44.3 | 7167 | 1049 |
| abilene | isp | Reactive, long timeouts | 603 | 597 | 43.4 | 16440 | 2424 |
| abilene | isp | Reactive on shortest paths (hybrid, budget 0%) | 484 | 482 | 37.1 | 5331 | 846 |
| abilene | isp | Hybrid, counter keeps top 10% of pairs | 321 | 324 | 28.3 | 3798 | 636 |
| abilene | isp | Hybrid, counter keeps top 25% of pairs | 207 | 212 | 20.8 | 2628 | 437 |
| abilene | isp | Hybrid, counter keeps top 50% of pairs | 84 | 92 | 10.1 | 1147 | 211 |
| abilene | isp | Oracle, busiest 10% of pairs (upper bound) | 300 | 299 | 26.7 | 3759 | 636 |
| abilene | isp | Oracle, busiest 25% of pairs (upper bound) | 172 | 170 | 16.1 | 2386 | 386 |
| abilene | isp | Oracle, busiest 50% of pairs (upper bound) | 64 | 62 | 6.4 | 1115 | 201 |
| abilene | isp | Proactive (one shortest path) | 0 | 0 | 0.2 | 386 | 62 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Reactive on shortest paths (hybrid, budget 0%) | 0 of 110 | 0.0 | 0 | 0 |
| abilene | isp | Hybrid, counter keeps top 10% of pairs | 11 of 110 | 28.3 | 30 | 17 |
| abilene | isp | Hybrid, counter keeps top 25% of pairs | 28 of 110 | 52.2 | 59 | 19 |
| abilene | isp | Hybrid, counter keeps top 50% of pairs | 55 of 110 | 78.1 | 91 | 30 |
| abilene | isp | Oracle, busiest 10% of pairs (upper bound) | 11 of 110 | 33.3 | 11 | 0 |
| abilene | isp | Oracle, busiest 25% of pairs (upper bound) | 28 of 110 | 59.1 | 28 | 0 |
| abilene | isp | Oracle, busiest 50% of pairs (upper bound) | 55 of 110 | 83.2 | 55 | 0 |
