# Path Quality: Optimal Path vs Haphazard Path

CS G525 Advanced Computer Networks, Project SA7, Group 2. Added after Progress Review I, in answer to the feedback point "Parameters for evaluation: optimal path vs haphazard path".

## 1. Why a new experiment

All the networks in Review I were trees. A tree has exactly one path between any two hosts, so every controller used the same path, and path quality could not be compared.

Real networks have many paths:
- **Data centres** use fat-trees, which have several equal-length paths between racks.
- **ISP backbones** are meshes, where one route can be much longer than another.

This experiment uses both kinds of network and checks which path each controller actually picks.

## 2. Networks

| Network | Kind | Switches | Hosts | Switch links | Paths between two hosts |
| --- | --- | --- | --- | --- | --- |
| `fattree-k4` | Data centre (Al-Fares et al., SIGCOMM 2008) | 20 (4 core, 8 aggregation, 8 edge) | 16 | 32 | Up to 4 equal-length paths between pods |
| `abilene` | ISP: US Internet2/Abilene backbone (Internet Topology Zoo) | 11 cities | 11, one per city | 14 | Several, of different lengths |
| `--gml file.gml` | Any Topology Zoo map, e.g. GÉANT (`Geant2012.gml`) | as in the file | one per city | as in the file | |

- **Bandwidth:** every link has the same bandwidth (`--bw`, 10 Mbit/s by default), so only the choice of path makes a difference.
- **Abilene link delays:** each delay is the straight-line distance between the two cities at the speed of light in fibre, about 200 km per ms. For example, Seattle–Denver is 1,640 km, so its delay is 8.2 ms. Real fibre routes are longer, so these delays are a lower bound.
- **How the delays are applied:** the delays are emulated with Linux `netem` when the kernel has it. If it doesn't (the cloud VM used for the validation run doesn't), the script still computes each path's delay from the map. It says which case applied in `paths.md`.

## 3. Controllers compared

| Name | How it chooses a path | Why it's in the test |
| --- | --- | --- |
| **Reactive** (learning + spanning tree) | `reactive_eval` (exact match, as in Review I) plus POX `openflow.discovery` and `openflow.spanning_tree`. In a network with loops, plain flooding would circulate forever (a broadcast storm), so floods are allowed only on a spanning tree. The learning switch then learns host locations from those floods, so traffic follows the tree. | The "haphazard" path. Nobody chose it for being short; it is whatever the tree, rooted at the lowest switch number, happens to give. This is how a plain reactive L2 network behaves. |
| **Proactive** (one shortest path) | `proactive_eval --paths=shortest`. One rule per host pair along the lowest-cost path (cost = link delay, or 1 per hop). When paths tie, it always takes the same one (lowest switch numbers). | The optimal path, chosen in advance from the topology. |
| **Proactive (ECMP)** | `proactive_eval --paths=ecmp`. The same lowest-cost paths, but each host pair is hashed onto one of the tied paths, like ECMP in real data centres. | Shows that "shortest" alone is not enough: the paths also have to be spread out. |

## 4. What is measured

**Experiment A: path stretch and delay.** For 40 sampled host pairs (the same pairs for every controller), the script pings 6 times. It then follows the installed rules switch by switch (`ovs-ofctl dump-flows`) to find the path the packets actually took.

| Metric | Meaning |
| --- | --- |
| Hop stretch | hops on the path used ÷ fewest hops possible (1.00 = best) |
| Delay stretch (ISP) | delay of the path used ÷ lowest possible delay (1.00 = best) |
| Pairs on a longer path | % of pairs not on a best path |
| Path RTT | round trip over the map's link delays along the path used |
| Measured RTT | ping (it includes the link delays only when netem is available) |

**Experiment B: throughput and link balance.** Every host sends one TCP flow to another host at the same time. The script uses a random permutation, so each host sends one flow and receives one, and repeats this for 3 permutations of 10 s each. Bytes are counted in the steady part of each run, from second 1 to second 9, both at the receivers and on every switch link.

| Metric | Meaning |
| --- | --- |
| Total throughput | sum over all flows, compared with the ideal (every host at full link speed) |
| Slowest flow | the worst flow: does someone starve? |
| Busiest link | utilisation of the most loaded link |
| Jain index over links | 1.0 = every link carries the same traffic; close to 1/n = everything on a few links |
| Links unused | % of link directions carrying almost nothing (< 0.1 Mbit/s) |

## 5. How to run

```bash
cd ~/Openflow_SDN
sudo python3 experiments/run_path_experiments.py --quick    # Abilene only, about 2 minutes
sudo python3 experiments/run_path_experiments.py            # fat-tree + Abilene, about 15 minutes
sudo python3 experiments/run_path_experiments.py --gml ~/Downloads/Geant2012.gml   # add GÉANT
```

- **Output:** results go to `results/measured/paths-<timestamp>/`. That folder holds `paths.md` (tables), `paths.json` (raw data), `paths_stretch.png`, `paths_throughput.png`, `paths_link_balance.png`, and the POX logs.
- **Without the kernel module:** if `modprobe openvswitch` fails, add `--datapath user`.
- **GÉANT map:** the Topology Zoo `.gml` files are at <http://www.topology-zoo.org/dataset.html>; download one in a browser.

## 6. Results

**Report run:** laptop, Windows 11 + WSL2 (kernel 6.18.33.2), Open vSwitch 3.7.1 kernel datapath, POX 0.7.0, Python 3.14.4. Every link was 10 Mbit/s, and **netem was available, so the Abilene city-to-city delays were really emulated**. Run 15 Oct 2026; files are in [`results/measured/paths-20261015-094800/`](../results/measured/paths-20261015-094800/).

### A: path stretch (40 host pairs, the same pairs for every controller; all 40 traced, 0 packets lost)

| Network | Controller | Hop stretch mean / max | Delay stretch mean / max | Pairs on a longer path | Path RTT from map (ms) | **Measured ping RTT (ms)** |
| --- | --- | --- | --- | --- | --- | --- |
| fat-tree | Reactive (learning + tree) | **1.11 / 1.50** | - | **22%** | - | 0.14 |
| fat-tree | Proactive (one shortest path) | 1.00 / 1.00 | - | 0% | - | 0.13 |
| fat-tree | Proactive (ECMP) | 1.00 / 1.00 | - | 0% | - | 0.13 |
| Abilene | Reactive (learning + tree) | **1.40 / 3.00** | **1.58 / 4.47** | **70%** | 39.3 | **40.51** |
| Abilene | Proactive (one shortest path) | 1.02 / 1.33 | 1.00 / 1.00 | 0% | 25.7 | 26.90 |
| Abilene | Proactive (ECMP) | 1.02 / 1.33 | 1.00 / 1.00 | 0% | 25.7 | 26.24 |

![Path stretch](../results/measured/paths-20261015-094800/paths_stretch.png)

### B: throughput and link balance (16 or 11 TCP flows at once, 3 permutations, mean ± std)

| Network | Controller | Total Mbit/s (ideal) | Slowest flow Mbit/s | Jain index over links | Links unused |
| --- | --- | --- | --- | --- | --- |
| fat-tree | Reactive (learning + tree) | 63.6 ± 10.7 (160) | 1.21 | 0.36 | 59% |
| fat-tree | Proactive (one shortest path) | 61.7 ± 9.8 (160) | 0.50 | 0.33 | 63% |
| fat-tree | Proactive (ECMP) | **95.3 ± 3.3** (160) | 0.52 | **0.58** | **16%** |
| Abilene | Reactive (learning + tree) | 42.1 ± 2.6 (110) | 0.89 | 0.56 | 29% |
| Abilene | Proactive (one shortest path) | **60.7 ± 17.4** (110) | 0.86 | 0.52 | 20% |
| Abilene | Proactive (ECMP) | **60.6 ± 16.3** (110) | 0.93 | 0.52 | 20% |

The busiest link was at 100% in every run, so the links themselves are the bottleneck, not the switches or the controller. All three controllers got the same 3 traffic permutations. The large ± in Abilene comes from the permutations, not from the controllers: permutation 2 was hard for all three (41 / 43 / 45 Mbit/s).

![Throughput](../results/measured/paths-20261015-094800/paths_throughput.png)
![Link balance](../results/measured/paths-20261015-094800/paths_link_balance.png)

### What this shows

1. **Reactive takes slower paths in the ISP network, and real pings confirm it.** In Abilene, 70% of host pairs are on a slower path than necessary. On average the path has 58% more delay, and in the worst case 4.5 times the best delay. Measured pings are **40.5 ms for reactive against 26.2–26.9 ms for proactive, about 51% slower**. The cause is the spanning tree: Abilene has 14 links, the tree keeps 10, and traffic has to go around the 4 that are switched off.
2. **The measured pings match the map.** The map predicts 39.3 / 25.7 ms; pings measured 40.5 / 26.9 ms. The extra ~1.2 ms is switching and the controller, so the path-tracing method is sound.
3. **In the fat-tree, reactive adds hops.** 22% of pairs take a longer path, up to 1.5 times the hops (6 instead of 4). Delays inside a data centre are tiny, so this shows as 0.14 against 0.13 ms; the real cost is the links it wastes (point 5).
4. **Proactive always uses a best path.** Delay stretch is 1.00. In Abilene, the lowest-delay path sometimes has one more hop than the fewest-hop path (hop stretch 1.02), which is expected: a short, slow-looking route can beat a longer straight one.
5. **"Shortest" is not enough in a data centre; paths must also be spread.** With one fixed shortest path the fat-tree gets no more throughput than reactive (62 against 64 Mbit/s). Both leave about 60% of link directions idle, because all traffic between pods goes through the same core switch. **ECMP uses the other equal paths: only 16% of links are idle, the balance index rises to 0.58, and total throughput is 50% higher (95 against 64 Mbit/s)**, with the most stable result of all (± 3.3).
6. **In Abilene, both proactive versions carry 44% more traffic than reactive** (61 against 42 Mbit/s). There are few equal-cost ties in Abilene, so ECMP is no better than one shortest path there.
7. **Nobody reaches the ideal.** Even ECMP is at 60% of 160 Mbit/s, because ECMP on host pairs sometimes hashes two flows onto the same link (the collision problem described by Al-Fares 2008 and Hedera, NSDI 2010).

**Reproducibility:** the paths (part A) were identical in a separate validation run on a cloud VM (userspace datapath, no netem; files in [`results/validation_paths_cloud_userspace/`](../results/validation_paths_cloud_userspace/)). That is expected, because the same network, pairs and tree always give the same paths. Throughput there was lower (ECMP 62 Mbit/s) because the userspace switches are slower, but the ranking was the same.

**One-line conclusion:** reactive costs more than first-packet delay. Its paths are chosen by flooding, not by quality: 51% longer pings in an ISP network and 60% of links wasted in a data centre. Proactive with a known map picks the best paths, and spreading pairs over equal-cost paths (ECMP) is what turns those paths into throughput.

## 7. Notes and limits

- **Reactive paths depend on the tree.** The reactive controller's paths depend on where the spanning tree is rooted. POX roots it at the lowest switch number: core switch 1 in the fat-tree, Seattle in Abilene. A different root gives different, but still not chosen-for-quality, paths.
- **The tree also wastes links.** Ports switched off by the tree carry no floods, and because MAC learning follows the floods, they carry no unicast either. That is why reactive leaves many links idle even when the network is busy.
- **Proactive's advantage is the map.** The proactive controller is optimal because it knows the whole topology in advance. A reactive controller could also use shortest paths if it were given the map (as POX's `l2_multi` is), but it would still pay the first-packet cost measured in Review I.
- **Real ECMP balances per flow.** ECMP here is per host pair, because our rules match MAC pairs. Real switches hash every TCP/UDP flow, which spreads load more evenly still.
- **Commit the laptop run.** The report numbers come from the laptop run, so commit its folder `results/measured/paths-20261015-094800/` with the doc; the charts above link to it.
