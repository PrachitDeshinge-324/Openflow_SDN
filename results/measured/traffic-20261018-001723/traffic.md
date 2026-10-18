# Realistic traffic results (traffic-20261018-001723)

Testbed: Linux Harikrushna 6.18.33.2-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Thu Jun 18 21:54:43 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet

**Every value is the mean of 5 runs (seeds 7 to 11, a new flow schedule each time) ± the half-width of its 95% confidence interval (Student's t).**

## Traffic generated (identical for every controller within one seed)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Benson et al., IMC 2010 (university data centres) | 6073 ± 41 | 202.4 ± 1.4 | 85.5 ± 14.1 (5%) | 0 ± 0 | 83 ± 8% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 6073 ± 41 / 0 ± 0 | 16.76 ± 1.55 / 15.45 ± 1.82 / 54.83 ± 6.58 | 159.7 ± 19.7 | - |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 6073 ± 41 / 0 ± 0 | 10.09 ± 0.94 / 7.03 ± 0.94 / 47.06 ± 8.11 | 151.7 ± 21.8 | - |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 1630 ± 248 | 1640 ± 249 | 52.0 ± 5.1 | 7275 ± 669 | 2255 ± 241 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 850 ± 150 | 867 ± 151 | 32.1 ± 4.2 | 4559 ± 521 | 1400 ± 169 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 24 of 240 | 34.9 ± 6.8 | 81 ± 5 | 50 ± 3 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 60 of 240 | 62.1 ± 4.5 | 153 ± 12 | 64 ± 11 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 7 | 0 | 13.66 / 62.36 | 1354 | 46.0 | 6613 | 43.0 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 7 | 0 | 7.13 / 57.57 | 743 | 29.8 | 4234 | 66.0 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 8 | 0 | 15.28 / 53.66 | 1543 | 50.3 | 6964 | 29.7 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 8 | 0 | 7.10 / 48.10 | 743 | 28.8 | 4383 | 63.8 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 9 | 0 | 16.85 / 54.13 | 1742 | 54.2 | 7894 | 35.2 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 9 | 0 | 7.20 / 44.07 | 905 | 34.2 | 4821 | 62.9 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 10 | 0 | 14.47 / 47.65 | 1629 | 52.6 | 7153 | 36.6 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 10 | 0 | 5.83 / 40.16 | 832 | 30.9 | 4193 | 61.5 |
| tree-d2-f4 | university | Hybrid, counter keeps top 10% of pairs | 11 | 0 | 17.00 / 56.37 | 1882 | 56.8 | 7752 | 30.1 |
| tree-d2-f4 | university | Hybrid, counter keeps top 25% of pairs | 11 | 0 | 7.92 / 45.41 | 1030 | 36.9 | 5163 | 56.3 |
