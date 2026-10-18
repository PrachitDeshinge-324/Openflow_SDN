# Realistic traffic results (traffic-20261017-224052)

Testbed: Linux Harikrushna 6.18.33.2-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Thu Jun 18 21:54:43 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 100 Mbit/s | 30 s of arrivals | target load 30% (websearch/datamining) | flows capped at 20 MB | pair popularity: Zipf 1.0

Controller: same machine as Mininet

**Every value is the mean of 5 runs (seeds 7 to 11, a new flow schedule each time) ± the half-width of its 95% confidence interval (Student's t).**

## Traffic generated (identical for every controller within one seed)

| Network | Workload | Source | Flows | Flows/s | Offered Mbit/s (% of host capacity) | Capped flows | Leave edge switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Benson et al., IMC 2010 (university data centres) | 6073 ± 41 | 202.4 ± 1.4 | 85.5 ± 14.1 (5%) | 0 ± 0 | 83 ± 8% |
| fattree-k4 | websearch | DCTCP, SIGCOMM 2010 / pFabric web search workload | 1121 ± 27 | 37.4 ± 0.9 | 477.6 ± 19.1 (30%) | 14 ± 6 | 92 ± 10% |

## Flow completion time (ms)

| Network | Workload | Controller | Done / failed | Small < 100 KB: mean / p50 / p99 | Medium: mean | Large > 10 MB: mean |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Random 10% of pairs (no knowledge) | 6073 ± 41 / 0 ± 0 | 23.61 ± 2.54 / 23.19 ± 2.26 / 62.48 ± 4.78 | 167.0 ± 21.2 | - |
| tree-d2-f4 | university | Random 25% of pairs (no knowledge) | 6073 ± 41 / 0 ± 0 | 19.13 ± 2.64 / 19.22 ± 2.55 / 59.60 ± 10.72 | 163.2 ± 19.9 | - |
| tree-d2-f4 | university | Random 50% of pairs (no knowledge) | 6073 ± 41 / 0 ± 0 | 12.85 ± 3.63 / 11.54 ± 5.75 / 49.67 ± 5.90 | 156.5 ± 20.6 | - |
| fattree-k4 | websearch | Random 10% of pairs (no knowledge) | 1121 ± 27 / 0 ± 0 | 79.06 ± 10.09 / 59.88 ± 5.01 / 315.04 ± 48.40 | 2424.9 ± 524.1 | 9535.9 ± 4760.6 |
| fattree-k4 | websearch | Random 25% of pairs (no knowledge) | 1121 ± 27 / 0 ± 0 | 74.19 ± 11.47 / 55.28 ± 8.38 / 308.76 ± 52.04 | 2388.6 ± 497.0 | 9288.9 ± 4392.1 |
| fattree-k4 | websearch | Random 50% of pairs (no knowledge) | 1121 ± 27 / 0 ± 0 | 64.76 ± 9.76 / 45.35 ± 5.08 / 301.00 ± 40.32 | 2369.4 ± 447.9 | 9299.7 ± 4799.0 |

## Controller load and rules

| Network | Workload | Controller | PACKET_IN/s | FLOW_MOD/s | Controller CPU % | Peak rules (all switches) | Peak rules (one switch) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Random 10% of pairs (no knowledge) | 2266 ± 233 | 2265 ± 233 | 62.7 ± 3.6 | 9955 ± 914 | 3115 ± 372 |
| tree-d2-f4 | university | Random 25% of pairs (no knowledge) | 1872 ± 166 | 1871 ± 166 | 56.1 ± 3.7 | 8556 ± 861 | 2682 ± 310 |
| tree-d2-f4 | university | Random 50% of pairs (no knowledge) | 1167 ± 365 | 1166 ± 365 | 40.6 ± 9.3 | 6049 ± 1627 | 1922 ± 571 |
| fattree-k4 | websearch | Random 10% of pairs (no knowledge) | 446 ± 35 | 441 ± 35 | 25.8 ± 1.8 | 3557 ± 361 | 351 ± 42 |
| fattree-k4 | websearch | Random 25% of pairs (no knowledge) | 389 ± 49 | 384 ± 49 | 22.3 ± 3.3 | 3282 ± 570 | 321 ± 76 |
| fattree-k4 | websearch | Random 50% of pairs (no knowledge) | 260 ± 48 | 255 ± 48 | 15.5 ± 3.0 | 2665 ± 380 | 286 ± 45 |

## Budgeted hybrid (hit rate = new connections whose first packet found a rule)

| Network | Workload | Controller | Budget (pairs) | Hit rate % | Pair installs | Wasted installs |
| --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Random 10% of pairs (no knowledge) | 24 of 240 | 9.8 ± 7.1 | 24 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Random 25% of pairs (no knowledge) | 60 of 240 | 23.9 ± 7.8 | 60 ± 0 | 0 ± 0 |
| tree-d2-f4 | university | Random 50% of pairs (no knowledge) | 120 of 240 | 49.8 ± 12.3 | 120 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | Random 10% of pairs (no knowledge) | 24 of 240 | 8.4 ± 3.2 | 24 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | Random 25% of pairs (no knowledge) | 60 of 240 | 19.3 ± 9.0 | 60 ± 0 | 0 ± 0 |
| fattree-k4 | websearch | Random 50% of pairs (no knowledge) | 120 of 240 | 43.5 ± 6.7 | 120 ± 0 | 0 ± 0 |

## Every run

| Network | Workload | Controller | Seed | Failed | Small p50 / p99 (ms) | PACKET_IN/s | CPU % | Peak rules | Hit rate % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tree-d2-f4 | university | Random 10% of pairs (no knowledge) | 7 | 0 | 20.28 / 63.35 | 1938 | 57.6 | 8897 | 19.7 |
| tree-d2-f4 | university | Random 25% of pairs (no knowledge) | 7 | 0 | 21.55 / 73.38 | 2028 | 59.3 | 9489 | 18.1 |
| tree-d2-f4 | university | Random 50% of pairs (no knowledge) | 7 | 0 | 12.16 / 49.29 | 1120 | 40.2 | 6000 | 51.1 |
| fattree-k4 | websearch | Random 10% of pairs (no knowledge) | 7 | 0 | 57.02 / 321.43 | 445 | 25.6 | 3578 | 9.0 |
| fattree-k4 | websearch | Random 25% of pairs (no knowledge) | 7 | 0 | 53.97 / 320.82 | 436 | 24.3 | 3694 | 12.9 |
| fattree-k4 | websearch | Random 50% of pairs (no knowledge) | 7 | 0 | 42.40 / 287.47 | 278 | 16.8 | 2897 | 40.2 |
| tree-d2-f4 | university | Random 10% of pairs (no knowledge) | 8 | 0 | 25.24 / 66.75 | 2388 | 64.8 | 10745 | 6.0 |
| tree-d2-f4 | university | Random 25% of pairs (no knowledge) | 8 | 0 | 20.95 / 56.67 | 1929 | 56.7 | 9036 | 21.4 |
| tree-d2-f4 | university | Random 50% of pairs (no knowledge) | 8 | 0 | 15.14 / 56.55 | 1351 | 45.4 | 6958 | 43.7 |
| fattree-k4 | websearch | Random 10% of pairs (no knowledge) | 8 | 0 | 61.92 / 317.85 | 488 | 27.3 | 3582 | 12.3 |
| fattree-k4 | websearch | Random 25% of pairs (no knowledge) | 8 | 0 | 52.96 / 309.98 | 382 | 20.7 | 2990 | 31.3 |
| fattree-k4 | websearch | Random 50% of pairs (no knowledge) | 8 | 0 | 48.31 / 292.71 | 316 | 18.7 | 3007 | 39.1 |
| tree-d2-f4 | university | Random 10% of pairs (no knowledge) | 9 | 0 | 23.89 / 64.68 | 2374 | 63.8 | 10449 | 9.5 |
| tree-d2-f4 | university | Random 25% of pairs (no knowledge) | 9 | 0 | 16.60 / 60.10 | 1702 | 52.0 | 7874 | 31.3 |
| tree-d2-f4 | university | Random 50% of pairs (no knowledge) | 9 | 0 | 6.67 / 49.29 | 855 | 32.8 | 4702 | 61.7 |
| fattree-k4 | websearch | Random 10% of pairs (no knowledge) | 9 | 0 | 63.36 / 363.19 | 433 | 25.5 | 3821 | 8.2 |
| fattree-k4 | websearch | Random 25% of pairs (no knowledge) | 9 | 0 | 61.41 / 365.27 | 382 | 22.8 | 3544 | 18.9 |
| fattree-k4 | websearch | Random 50% of pairs (no knowledge) | 9 | 0 | 48.34 / 341.62 | 238 | 14.0 | 2395 | 51.9 |
| tree-d2-f4 | university | Random 10% of pairs (no knowledge) | 10 | 0 | 23.18 / 56.77 | 2346 | 63.9 | 10120 | 8.5 |
| tree-d2-f4 | university | Random 25% of pairs (no knowledge) | 10 | 0 | 17.94 / 49.73 | 1766 | 54.2 | 7976 | 29.9 |
| tree-d2-f4 | university | Random 50% of pairs (no knowledge) | 10 | 0 | 16.78 / 50.08 | 1568 | 50.5 | 7726 | 36.5 |
| fattree-k4 | websearch | Random 10% of pairs (no knowledge) | 10 | 0 | 54.24 / 254.21 | 411 | 23.6 | 3070 | 6.4 |
| fattree-k4 | websearch | Random 25% of pairs (no knowledge) | 10 | 0 | 45.84 / 248.85 | 331 | 18.5 | 2618 | 19.3 |
| fattree-k4 | websearch | Random 50% of pairs (no knowledge) | 10 | 0 | 39.60 / 258.89 | 217 | 12.4 | 2306 | 40.5 |
| tree-d2-f4 | university | Random 10% of pairs (no knowledge) | 11 | 0 | 23.36 / 60.84 | 2284 | 63.3 | 9566 | 5.5 |
| tree-d2-f4 | university | Random 25% of pairs (no knowledge) | 11 | 0 | 19.06 / 58.13 | 1933 | 58.3 | 8404 | 18.6 |
| tree-d2-f4 | university | Random 50% of pairs (no knowledge) | 11 | 0 | 6.93 / 43.15 | 941 | 34.0 | 4860 | 55.9 |
| fattree-k4 | websearch | Random 10% of pairs (no knowledge) | 11 | 0 | 62.85 / 318.51 | 452 | 26.9 | 3733 | 6.0 |
| fattree-k4 | websearch | Random 25% of pairs (no knowledge) | 11 | 0 | 62.25 / 298.86 | 412 | 24.9 | 3562 | 14.2 |
| fattree-k4 | websearch | Random 50% of pairs (no knowledge) | 11 | 0 | 48.08 / 324.32 | 249 | 15.9 | 2718 | 45.8 |
