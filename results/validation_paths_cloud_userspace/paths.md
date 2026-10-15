# Path quality results (paths-full)

Testbed: Linux vm 6.18.44-fc-v114 #1 SMP PREEMPT_DYNAMIC @0 x86_64 | Python 3.11.15 | ovs-vsctl (Open vSwitch) 3.3.9 | datapath=user | every link 10 Mbit/s

Link delays emulated with netem: no (kernel has no netem). Path RTT is computed from the map's link delays along the traced path; measured RTT is ping (it includes the delays only when emulated).

## A: path stretch (1.00 = best possible path)

| Network | Controller | Pairs traced | Hop stretch mean / max | Pairs on a longer path | Delay stretch mean / max | Path RTT (ms) | Best path RTT (ms) | Measured RTT (ms) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | Reactive (learning + spanning tree) | 40 / 40 | 1.11 / 1.50 | 22% | - | - | - | 4.84 |
| fattree-k4 | Proactive (one shortest path) | 40 / 40 | 1.00 / 1.00 | 0% | - | - | - | 4.09 |
| fattree-k4 | Proactive (ECMP) | 40 / 40 | 1.00 / 1.00 | 0% | - | - | - | 4.08 |
| abilene | Reactive (learning + spanning tree) | 40 / 40 | 1.40 / 3.00 | 70% | 1.58 / 4.47 | 39.3 | 25.7 | 2.45 |
| abilene | Proactive (one shortest path) | 40 / 40 | 1.02 / 1.33 | 0% | 1.00 / 1.00 | 25.7 | 25.7 | 1.75 |
| abilene | Proactive (ECMP) | 40 / 40 | 1.02 / 1.33 | 0% | 1.00 / 1.00 | 25.7 | 25.7 | 1.87 |

## B: throughput and link balance (mean +/- std over permutations)

| Network | Controller | Total Mbit/s (ideal) | Mean flow Mbit/s | Slowest flow Mbit/s | Busiest link % | Jain index over links | Links unused % |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fattree-k4 | Reactive (learning + spanning tree) | 46.0 +/- 4.0 (160) | 2.87 +/- 0.25 | 0.43 +/- 0.60 | 98.2 +/- 2.2 | 0.33 +/- 0.02 | 59.4 +/- 0.0 |
| fattree-k4 | Proactive (one shortest path) | 52.6 +/- 7.3 (160) | 3.29 +/- 0.45 | 0.93 +/- 0.20 | 99.1 +/- 0.6 | 0.33 +/- 0.01 | 62.5 +/- 0.0 |
| fattree-k4 | Proactive (ECMP) | 62.2 +/- 7.6 (160) | 3.89 +/- 0.47 | 1.06 +/- 0.80 | 98.9 +/- 1.4 | 0.53 +/- 0.11 | 21.9 +/- 4.1 |
| abilene | Reactive (learning + spanning tree) | 35.9 +/- 2.6 (110) | 3.27 +/- 0.23 | 0.79 +/- 0.46 | 99.8 +/- 0.1 | 0.59 +/- 0.04 | 28.6 +/- 0.0 |
| abilene | Proactive (one shortest path) | 53.4 +/- 16.5 (110) | 4.86 +/- 1.50 | 1.60 +/- 0.41 | 99.9 +/- 0.1 | 0.56 +/- 0.02 | 19.0 +/- 9.0 |
| abilene | Proactive (ECMP) | 54.0 +/- 12.5 (110) | 4.91 +/- 1.14 | 1.14 +/- 0.35 | 100.0 +/- 0.0 | 0.54 +/- 0.01 | 20.2 +/- 9.0 |
