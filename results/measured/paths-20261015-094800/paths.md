# Path quality results (paths-20261015-094800)

Testbed: Linux Harikrushna 6.18.33.2-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Thu Jun 18 21:54:43 UTC 2026 x86_64 | Python 3.14.4 | ovs-vsctl (Open vSwitch) 3.7.1 | datapath=kernel | every link 10 Mbit/s

Link delays emulated with netem: yes. Path RTT is computed from the map's link delays along the traced path; measured RTT is ping (it includes the delays only when emulated).

## A: path stretch (1.00 = best possible path)

| Network | Controller | Pairs traced | Hop stretch mean / max | Pairs on a longer path | Delay stretch mean / max | Path RTT (ms) | Best path RTT (ms) | Measured RTT (ms) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | Reactive (learning + spanning tree) | 40 / 40 | 1.11 / 1.50 | 22% | - | - | - | 0.14 |
| fattree-k4 | Proactive (one shortest path) | 40 / 40 | 1.00 / 1.00 | 0% | - | - | - | 0.13 |
| fattree-k4 | Proactive (ECMP) | 40 / 40 | 1.00 / 1.00 | 0% | - | - | - | 0.13 |
| abilene | Reactive (learning + spanning tree) | 40 / 40 | 1.40 / 3.00 | 70% | 1.58 / 4.47 | 39.3 | 25.7 | 40.51 |
| abilene | Proactive (one shortest path) | 40 / 40 | 1.02 / 1.33 | 0% | 1.00 / 1.00 | 25.7 | 25.7 | 26.90 |
| abilene | Proactive (ECMP) | 40 / 40 | 1.02 / 1.33 | 0% | 1.00 / 1.00 | 25.7 | 25.7 | 26.24 |

## B: throughput and link balance (mean +/- std over permutations)

| Network | Controller | Total Mbit/s (ideal) | Mean flow Mbit/s | Slowest flow Mbit/s | Busiest link % | Jain index over links | Links unused % |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | Reactive (learning + spanning tree) | 63.6 +/- 10.7 (160) | 3.98 +/- 0.67 | 1.21 +/- 0.50 | 100.0 +/- 0.0 | 0.36 +/- 0.02 | 59.4 +/- 0.0 |
| fattree-k4 | Proactive (one shortest path) | 61.7 +/- 9.8 (160) | 3.86 +/- 0.61 | 0.50 +/- 0.20 | 100.0 +/- 0.0 | 0.33 +/- 0.02 | 62.5 +/- 0.0 |
| fattree-k4 | Proactive (ECMP) | 95.3 +/- 3.3 (160) | 5.95 +/- 0.21 | 0.52 +/- 0.07 | 100.0 +/- 0.0 | 0.58 +/- 0.02 | 15.6 +/- 1.6 |
| abilene | Reactive (learning + spanning tree) | 42.1 +/- 2.6 (110) | 3.83 +/- 0.24 | 0.89 +/- 0.18 | 99.9 +/- 0.1 | 0.56 +/- 0.05 | 28.6 +/- 0.0 |
| abilene | Proactive (one shortest path) | 60.7 +/- 17.4 (110) | 5.52 +/- 1.58 | 0.86 +/- 0.22 | 100.0 +/- 0.0 | 0.52 +/- 0.02 | 20.2 +/- 7.4 |
| abilene | Proactive (ECMP) | 60.6 +/- 16.3 (110) | 5.51 +/- 1.48 | 0.93 +/- 0.17 | 100.0 +/- 0.0 | 0.52 +/- 0.01 | 20.2 +/- 7.4 |
