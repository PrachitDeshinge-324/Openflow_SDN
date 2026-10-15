# Realistic traffic results (traffic-20261015-210056)

Testbed: Linux Harikrushna 6.18.33.2-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Thu Jun 18 21:54:43 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: uniform

Controller: same machine as Mininet

## Traffic generated (identical for every controller)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Benson et al., IMC 2010 (university data centres) | 6102 | 203.4 | 92.9 (6%) | 0 | 81% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 6102 / 0 | 73.36 / 63.63 / 217.39 | 235.2 | - |
| tree-d2-f4 | university | Reactive, long timeouts | 6102 / 0 | 74.25 / 68.15 / 180.08 | 235.4 | - |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 6102 / 0 | 68.03 / 62.18 / 184.97 | 229.9 | - |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 6102 / 0 | 54.63 / 52.36 / 133.78 | 215.6 | - |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 6102 / 0 | 47.77 / 43.07 / 158.34 | 209.4 | - |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 6102 / 0 | 24.30 / 21.78 / 86.46 | 184.6 | - |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 6102 / 0 | 51.42 / 50.11 / 143.85 | 212.6 | - |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 6102 / 0 | 32.29 / 33.12 / 93.61 | 184.2 | - |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 6102 / 0 | 16.57 / 11.35 / 62.49 | 164.9 | - |
| tree-d2-f4 | university | Proactive (one shortest path) | 6102 / 0 | 5.71 / 1.26 / 38.80 | 165.1 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive (learning + spanning tree) | 2329 | 2329 | 88.2 | 10898 | 3374 |
| tree-d2-f4 | university | Reactive, long timeouts | 2294 | 2294 | 86.5 | 31852 | 9820 |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 2327 | 2326 | 86.9 | 10984 | 3394 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 2176 | 2186 | 84.0 | 9898 | 3069 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 1902 | 1925 | 82.1 | 8494 | 2655 |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 1275 | 1296 | 65.9 | 5949 | 1849 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 2051 | 2050 | 82.2 | 9631 | 3010 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 1625 | 1625 | 72.8 | 7812 | 2424 |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 928 | 928 | 52.1 | 4993 | 1520 |
| tree-d2-f4 | university | Proactive (one shortest path) | 0 | 0 | 0.1 | 624 | 192 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Reactive on shortest paths (hybrid, budget 0%) | 0 of 240 | 0.0 | 0 | 0 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 24 of 240 | 9.7 | 78 | 50 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 60 of 240 | 24.5 | 167 | 100 |
| tree-d2-f4 | university | Hybrid, counter keeps top 50% of pairs | 120 of 240 | 47.7 | 244 | 86 |
| tree-d2-f4 | university | Oracle, busiest 10% of pairs (upper bound) | 24 of 240 | 12.7 | 24 | 0 |
| tree-d2-f4 | university | Oracle, busiest 25% of pairs (upper bound) | 60 of 240 | 29.9 | 60 | 0 |
| tree-d2-f4 | university | Oracle, busiest 50% of pairs (upper bound) | 120 of 240 | 56.0 | 120 | 0 |
