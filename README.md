# SDN Project SA7: Reactive vs. Proactive Flow Installation

Scripts, controller modules and documentation for **CS G525 Advanced Computer Networks - Research Project SA7**:
an evaluation of reactive vs. proactive OpenFlow flow installation on Mininet + Open vSwitch + POX.

## Project Contents

| Path | What it is |
| --- | --- |
| `controllers/reactive_eval.py` | POX module: reactive (on-demand) flow installation, instrumented |
| `controllers/proactive_eval.py` | POX module: proactive flow installation from a known topology, instrumented |
| `controllers/sa7_common.py` | Shared stats/topology helpers for both modules |
| `experiments/run_experiments.py` | **Measured** evaluation: latency, flow-table occupancy, controller load under churn |
| `experiments/plot_results.py` | Plots for a measured run |
| `experiments/topologies/tree-d2-f2.json` | Topology file for running `proactive_eval` by hand on the 4-host tree |
| `sdn_benchmark_suite.py` | **Analytical model** (expected values, not measurements); writes `results/*.png` |
| `smoke_test.py` | Checks that Python 3, Mininet, Open vSwitch and POX are installed |
| `run_live_pox_benchmark.py`, `run_pox_openflow_test.py` | Simulated OpenFlow 1.0 switch that handshakes with POX and times its reply to one PACKET_IN |
| `results/` | Model charts; measured runs go to `results/measured/<timestamp>/` |
| `docs/Progress_Review_1.md` | Progress Review I report (30 Sep 2026) |
| `Project_SA7_Final_Report.md` | Report draft (Section 4 = analytical model) |
| `pox/` | POX controller checkout (not stored in this repo, see setup) |

---

## 1. Setup

### Ubuntu (VM or WSL2 on Windows)
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

Inside the Mininet CLI, `h1 ping -c 10 h4` shows first-packet vs steady-state latency and `sh ovs-ofctl dump-flows s1` lists the installed rules.

---

## 4. Analytical Model

```bash
cd ~/Openflow_SDN
python3 sdn_benchmark_suite.py
```
Generates the expected-value charts in `results/` from a parametric model (seeded, so output is reproducible).
These are **not measurements**; they state the hypothesis numerically for comparison with Section 2.
