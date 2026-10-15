# Realistic traffic results (traffic-20261015-204208)

Testbed: Linux Harikrushna 6.18.33.2-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Thu Jun 18 21:54:43 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet

## Traffic generated (identical for every controller)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Benson et al., IMC 2010 (university data centres) | 6088 | 202.9 | 97.3 (6%) | 0 | 84% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 6088 / 0 | 57.68 / 53.40 / 137.24 | 216.2 | - |
| tree-d2-f4 | university | Reactive, long timeouts | 6088 / 0 | 63.44 / 59.14 / 154.23 | 221.7 | - |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 6088 / 0 | 57.99 / 53.70 / 169.04 | 219.9 | - |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 6088 / 0 | 34.89 / 32.54 / 99.42 | 201.4 | - |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 6088 / 0 | 17.16 / 12.78 / 76.62 | 179.9 | - |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 6088 / 0 | 11.35 / 4.10 / 61.87 | 173.4 | - |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 6088 / 0 | 19.50 / 16.65 / 67.68 | 190.0 | - |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 6088 / 0 | 14.21 / 7.39 / 67.59 | 184.7 | - |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 6088 / 0 | 9.57 / 2.96 / 52.77 | 173.4 | - |
| tree-d2-f4 | university | Proactive (one shortest path) | 6088 / 0 | 6.99 / 1.67 / 43.85 | 174.0 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 2371 | 2371 | 83.6 | 11170 | 3523 |
| tree-d2-f4 | university | Reactive, long timeouts | 2327 | 2326 | 83.6 | 32644 | 10232 |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 2329 | 2329 | 82.7 | 11159 | 3523 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 1685 | 1694 | 74.4 | 7588 | 2365 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 861 | 876 | 48.2 | 5010 | 1563 |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 365 | 380 | 28.3 | 2340 | 738 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 1022 | 1022 | 55.1 | 5312 | 1656 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 572 | 572 | 39.7 | 3287 | 1012 |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 274 | 274 | 22.0 | 1987 | 622 |
| tree-d2-f4 | university | Proactive (one shortest path) | 0 | 0 | 0.1 | 624 | 192 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 0 of 240 | 0.0 | 0 | 0 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 24 of 240 | 24.5 | 80 | 53 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 60 of 240 | 62.3 | 153 | 71 |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 120 of 240 | 80.5 | 206 | 55 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 24 of 240 | 51.6 | 24 | 0 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 60 of 240 | 70.6 | 60 | 0 |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 120 of 240 | 85.7 | 120 | 0 |
