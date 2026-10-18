# Realistic traffic results (traffic-20261017-231017)

Testbed: Linux Harikrushna 6.18.33.2-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Thu Jun 18 21:54:43 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: uniform

Controller: same machine as Mininet

**Every value is the mean of 5 runs (seeds 7 to 11, a new flow schedule each time) ± the half-width of its 95% confidence interval (Student's t).**

## Traffic generated (identical for every controller within one seed)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Abilene traffic matrices (Zhang et al., IMC 2005) + SURGE flow sizes | 1749 ± 43 | 58.3 ± 1.4 | 28.5 ± 2.9 (3%) | 0 ± 0 | 100 ± 0% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Random 10% of pairs (no knowledge) | 1749 ± 43 / 0 ± 0 | 69.32 ± 3.27 / 55.09 ± 2.35 / 222.89 ± 33.77 | 187.7 ± 12.0 | 1459.9 ± 338.8 |
| abilene | isp | Random 25% of pairs (no knowledge) | 1749 ± 43 / 0 ± 0 | 66.74 ± 3.90 / 53.25 ± 3.29 / 218.70 ± 34.89 | 185.1 ± 11.0 | 1457.6 ± 355.7 |
| abilene | isp | Random 50% of pairs (no knowledge) | 1749 ± 43 / 0 ± 0 | 62.90 ± 4.20 / 49.08 ± 2.16 / 212.88 ± 31.53 | 181.1 ± 9.8 | 1461.4 ± 347.4 |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Random 10% of pairs (no knowledge) | 405 ± 36 | 403 ± 36 | 20.2 ± 2.0 | 4873 ± 316 | 747 ± 71 |
| abilene | isp | Random 25% of pairs (no knowledge) | 334 ± 19 | 332 ± 19 | 17.7 ± 1.2 | 4012 ± 227 | 643 ± 24 |
| abilene | isp | Random 50% of pairs (no knowledge) | 205 ± 48 | 204 ± 48 | 11.5 ± 1.9 | 2701 ± 345 | 446 ± 121 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Random 10% of pairs (no knowledge) | 11 of 110 | 9.6 ± 4.8 | 11 ± 0 | 0 ± 0 |
| abilene | isp | Random 25% of pairs (no knowledge) | 28 of 110 | 24.5 ± 4.8 | 28 ± 0 | 0 ± 0 |
| abilene | isp | Random 50% of pairs (no knowledge) | 55 of 110 | 54.1 ± 5.4 | 55 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| abilene | isp | Random 10% of pairs (no knowledge) | 7 | 0 | 56.89 / 207.33 | 417 | 20.0 | 4914 | 9.0 |
| abilene | isp | Random 25% of pairs (no knowledge) | 7 | 0 | 53.55 / 202.73 | 328 | 16.6 | 4009 | 28.4 |
| abilene | isp | Random 50% of pairs (no knowledge) | 7 | 0 | 48.25 / 196.78 | 217 | 11.5 | 2982 | 53.2 |
| abilene | isp | Random 10% of pairs (no knowledge) | 8 | 0 | 51.86 / 190.99 | 399 | 19.6 | 4772 | 10.5 |
| abilene | isp | Random 25% of pairs (no knowledge) | 8 | 0 | 51.03 / 185.90 | 357 | 17.9 | 4240 | 18.2 |
| abilene | isp | Random 50% of pairs (no knowledge) | 8 | 0 | 47.31 / 186.67 | 180 | 10.6 | 2506 | 58.6 |
| abilene | isp | Random 10% of pairs (no knowledge) | 9 | 0 | 55.60 / 249.68 | 449 | 23.0 | 5280 | 3.5 |
| abilene | isp | Random 25% of pairs (no knowledge) | 9 | 0 | 51.09 / 238.42 | 337 | 17.1 | 3944 | 24.2 |
| abilene | isp | Random 50% of pairs (no knowledge) | 9 | 0 | 48.31 / 234.55 | 243 | 13.0 | 2825 | 50.2 |
| abilene | isp | Random 10% of pairs (no knowledge) | 10 | 0 | 55.45 / 252.82 | 380 | 18.7 | 4597 | 14.3 |
| abilene | isp | Random 25% of pairs (no knowledge) | 10 | 0 | 57.55 / 255.77 | 316 | 19.2 | 3754 | 25.1 |
| abilene | isp | Random 50% of pairs (no knowledge) | 10 | 0 | 51.78 / 245.01 | 235 | 12.8 | 2873 | 49.9 |
| abilene | isp | Random 10% of pairs (no knowledge) | 11 | 0 | 55.66 / 213.63 | 379 | 19.9 | 4801 | 10.7 |
| abilene | isp | Random 25% of pairs (no knowledge) | 11 | 0 | 53.05 / 210.67 | 330 | 17.6 | 4115 | 26.6 |
| abilene | isp | Random 50% of pairs (no knowledge) | 11 | 0 | 49.75 / 201.39 | 152 | 9.4 | 2317 | 58.9 |
