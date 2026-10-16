# SDN Project SA7: Reactive vs. Proactive Flow Installation

Scripts, controller modules and documentation for **CS G525 Advanced Computer Networks - Research Project SA7**:
an evaluation of reactive vs. proactive OpenFlow flow installation on Mininet + Open vSwitch + POX.

## Project Contents

| Path | What it is |
| --- | --- |
| `controllers/reactive_eval.py` | POX module: reactive (on-demand) flow installation, instrumented |
| `controllers/proactive_eval.py` | POX module: proactive flow installation from a known topology, instrumented |
| `controllers/hybrid_eval.py` | POX module: budgeted hybrid (Step 4). Reactive on shortest paths, plus pair rules for the top K host pairs chosen by a weighted counter; or a fixed "oracle" list of pairs |
| `controllers/sa7_common.py` | Shared stats/topology helpers for the modules |
| `experiments/run_experiments.py` | **Measured** evaluation: latency, flow-table occupancy, controller load under churn |
| `experiments/plot_results.py` | Plots for a measured run |
| `experiments/run_path_experiments.py` | **Path quality** (Review II): path stretch, throughput and link balance on a fat-tree and the Abilene ISP map |
| `experiments/path_topologies.py`, `experiments/plot_paths.py` | Multi-path networks (fat-tree, Abilene, any Topology Zoo `.gml`) and plots for the path experiment |
| `experiments/run_traffic_experiments.py`, `experiments/workloads.py`, `experiments/plot_traffic.py` | **Realistic traffic** (Step 2): university, data-centre web search and data mining workloads from published measurements, and real Abilene ISP traffic |
| `experiments/repeats.py` | Mean and 95% confidence interval over repeated runs (`--repeats`) |
| `experiments/controller_agent.py` | Runs POX on a second PC for the traffic experiment (`--controller-host`) |
| `experiments/abilene_tm.py`, `data/abilene/` | Real Abilene traffic matrices (Zhang et al., IMC 2005) turned into hourly city-to-city traffic |
| `experiments/topologies/tree-d2-f2.json` | Topology file for running `proactive_eval` by hand on the 4-host tree |
| `sdn_benchmark_suite.py` | **Analytical model** (expected values, not measurements); writes `results/*.png` |
| `setup.sh`, `INSTALL.md`, `requirements.txt` | First-time installation: script, guide, Python libraries |
| `smoke_test.py` | Checks that Python 3, Mininet, Open vSwitch and POX are installed |
| `run_live_pox_benchmark.py`, `run_pox_openflow_test.py` | Simulated OpenFlow 1.0 switch that handshakes with POX and times its reply to one PACKET_IN |
| `results/` | Model charts; measured runs go to `results/measured/<timestamp>/` |
| `docs/Progress_Review_1.md` | Progress Review I report (30 Sep 2026) |
| `docs/Progress_Review_2.md` (+ `.pdf`) | **Progress Review II report (30 Oct 2026)**: everything since Review I with all measurements |
| `docs/Path_Quality_Experiment.md` | Path-quality experiment: why, how, metrics, results |
| `docs/Realism_Sources.md` | The paper behind every network, traffic pattern and parameter we use |
| `docs/Realistic_Traffic_Experiment.md` | Realistic-traffic experiment: workloads, metrics, results |
| `docs/Budgeted_Hybrid_Experiment.md` | Step 4: long timeouts, budgeted hybrid vs oracle, repeats with confidence intervals |
| `docs/Evaluation_Plan.md` | Every comparison we make, next to the closest paper and what that paper misses, with status and results |
| `docs/literature/` | Literature review (14 papers, PDFs in `papers/`) and the survey of 28 prediction/ML rule papers |
| `docs/Final_Report.md` | Final report (20 Nov): structure and finished sections, with `TODO (data)` where measurements are still to come |
| `docs/figures/` | Summary figures for the reports, and the script that makes them from the measured tables |
| `docs/Controller_On_Second_PC.md` | Step 4: how to run the controller on a second PC (incl. WSL2 networking) |
| `Project_SA7_Final_Report.md` | Report draft (Section 4 = analytical model) |
| `pox/` | POX 0.7.0 (`gar`, commit 5f82461), stored in this repo (Apache 2.0 licence, see `pox/LICENSE`) |

---

## 1. Setup

**First time?** Follow [INSTALL.md](INSTALL.md): requirements, installing Ubuntu/WSL2, and troubleshooting. The short version:
```bash
git clone https://github.com/PrachitDeshinge-324/Openflow_SDN.git
cd Openflow_SDN
bash setup.sh        # installs Mininet, Open vSwitch, POX and Python libraries, then verifies them
```

### Manual setup (what `setup.sh` does)
Run everything inside the Ubuntu terminal, in the Linux home folder (not under `/mnt/c`):
```bash
sudo apt update
sudo apt install -y git mininet openvswitch-switch openvswitch-testcontroller \
                    python3-numpy python3-matplotlib
sudo systemctl enable --now openvswitch-switch
sudo modprobe openvswitch        # if this fails, see "Userspace datapath" below

cd ~
git clone https://github.com/PrachitDeshinge-324/Openflow_SDN.git
git clone https://github.com/noxrepo/pox.git Openflow_SDN/pox
```
The repo only records which POX commit to use; it does not contain POX's files, so the second clone is required.

**Userspace datapath:** if the kernel has no `openvswitch` module, add `--switch ovs,datapath=user`
to `mn` commands and `--datapath user` to `run_experiments.py`. Latencies are higher in that mode, so report which one you used.
Run `sudo mn -c` to clean up after a crashed Mininet run.

### Check the installation
```bash
cd ~/Openflow_SDN
python3 smoke_test.py
```

---

## 2. Measured Evaluation (main experiment)

```bash
cd ~/Openflow_SDN
sudo python3 experiments/run_experiments.py --quick   # 4 hosts only, about 1-2 minutes
sudo python3 experiments/run_experiments.py           # 4, 8 and 16 hosts, about 10-15 minutes
```
For each topology (trees with 4, 8 and 16 hosts) and each controller mode, the script starts POX and Mininet and measures:

1. **Flow-setup latency:** ping RTT of packet 1, packet 2 and the steady state (packets 3..N) for sampled host pairs.
2. **Flow-table occupancy:** rules actually present in every switch (`ovs-ofctl dump-flows`) with 25/50/100% of host pairs active.
3. **Control-plane load under churn:** PACKET_IN/s, FLOW_MOD/s and POX CPU usage while new UDP flows arrive at 10-200 flows/s.

The output goes to `results/measured/<timestamp>/`:
- `results.md` has tables ready to paste into the report.
- `summary.csv` and `results.json` hold the raw data.
- `measured_*.png` are the plots.
- POX logs and per-run controller statistics are saved alongside.

Run `python3 experiments/run_experiments.py --help` for options (match granularity, timeouts, rates, number of pairs).

Both modes run under identical conditions: static ARP entries on every host (ARP stays out of the measurement), IPv6 disabled on hosts, and a fixed random seed for pair selection.

### Path quality: optimal path vs haphazard path

```bash
sudo python3 experiments/run_path_experiments.py --quick   # Abilene only, about 2 minutes
sudo python3 experiments/run_path_experiments.py           # fat-tree + Abilene, about 15 minutes
sudo python3 experiments/run_path_experiments.py --gml ~/Downloads/Geant2012.gml   # add a Topology Zoo map
```
Trees have only one path between two hosts, so this experiment uses networks with many paths: a k=4 fat-tree (data centre) and the Abilene backbone (ISP, link delays from city distances). It compares the reactive learning switch (over POX's spanning tree), proactive with one shortest path, and proactive with ECMP. It measures path stretch (path used compared with the best path), throughput with every host sending at once, and how evenly the links are loaded. Output goes to `results/measured/paths-<timestamp>/` (`paths.md`, `paths.json`, `paths_*.png`). The details are in [docs/Path_Quality_Experiment.md](docs/Path_Quality_Experiment.md).

### Realistic traffic: university, data centre and ISP

```bash
sudo python3 experiments/run_traffic_experiments.py --quick   # university traffic only, about 2 minutes
sudo python3 experiments/run_traffic_experiments.py           # 4 scenarios, about 12 minutes
```
This experiment pairs each network with traffic measured in that kind of network:
- university traffic (Benson et al., IMC 2010) on the campus tree;
- web search (DCTCP) and data mining (VL2) traffic on the fat-tree, using the published pFabric/PIAS flow-size tables;
- one day of real Abilene traffic matrices on the Abilene backbone.

Every controller gets exactly the same flows. The script measures flow completion times (small and large flows), failed flows, controller load and flow-table size. Output goes to `results/measured/traffic-<timestamp>/`. The details are in [docs/Realistic_Traffic_Experiment.md](docs/Realistic_Traffic_Experiment.md).

### Rule budget, repeats and a second PC (Step 4)

```bash
# reactive, reactive with long timeouts, hybrid and oracle at 10/25/50% of host pairs, proactive
sudo python3 experiments/run_traffic_experiments.py --scenarios tree-d2-f4:university --budget-sweep --pair-zipf 1
sudo python3 experiments/run_traffic_experiments.py --repeats 5          # mean +- 95% confidence interval
sudo python3 experiments/run_traffic_experiments.py --controller-host 192.168.1.20   # POX on another PC
```
The budget sweep asks how much a fixed budget of pre-installed pair rules buys when a simple weighted counter picks them, and how far that is from an oracle that knows the busiest pairs in advance. The details are in [docs/Budgeted_Hybrid_Experiment.md](docs/Budgeted_Hybrid_Experiment.md). For the second PC, first start `python3 experiments/controller_agent.py` on that PC, as described in [docs/Controller_On_Second_PC.md](docs/Controller_On_Second_PC.md).

---

## 3. Running the Controllers by Hand

You need two terminals. POX finds the modules through `PYTHONPATH`.

**Terminal 1, reactive controller:**
```bash
cd ~/Openflow_SDN/pox
PYTHONPATH=../controllers python3 pox.py reactive_eval
```
**Or terminal 1, proactive controller** (it needs the topology in advance):
```bash
cd ~/Openflow_SDN/pox
PYTHONPATH=../controllers python3 pox.py proactive_eval --topo=../experiments/topologies/tree-d2-f2.json
```

**Terminal 2, Mininet:**
```bash
sudo mn --topo=tree,depth=2,fanout=2 --mac --arp --controller=remote,ip=127.0.0.1,port=6633 --test=pingall
```
`--mac` gives hosts the MAC addresses listed in the topology file. `--arp` pre-fills ARP tables, which the proactive controller relies on because it drops unmatched broadcasts.
Expect `0% dropped (12/12 received)`.

Useful options:
- `reactive_eval --match=exact|pair|dst --idle_timeout=10 --hard_timeout=30 --stats_file=/tmp/r.json`
- `proactive_eval --granularity=pair|dst --miss=drop|controller --stats_file=/tmp/p.json`
- `hybrid_eval --topo=<file> --budget=0.25 --decay=0.97 --hysteresis=1.5 --paths=shortest|ecmp --stats_file=/tmp/h.json`

Inside the Mininet CLI, `h1 ping -c 10 h4` shows first-packet vs steady-state latency and `sh ovs-ofctl dump-flows s1` lists the installed rules.

---

## 4. Analytical Model

```bash
cd ~/Openflow_SDN
python3 sdn_benchmark_suite.py
```
Generates the expected-value charts in `results/` from a parametric model (seeded, so output is reproducible).
These are **not measurements**; they state the hypothesis numerically for comparison with Section 2.
