# SDN Project SA7: Reactive vs. Proactive Flow Installation

This directory contains the entire suite of scripts, the POX controller, and the documentation for **CS G525 Advanced Computer Networks - Research Project SA7**.

## Project Contents

- `pox/` : The customized POX controller repository (gar-experimental branch).
  - Includes `pox/pox/forwarding/proactive_eval.py` (Static $O(N^2)$ flow installation).
  - Includes `pox/pox/forwarding/reactive_eval.py` (Instrumented on-demand flow learning).
  - Contains the **Python 3 compatibility patch** inside `pox/pox/lib/packet/dns.py` to prevent DNS parsing crashes during background Linux activity.
- `smoke_test.py` : Automates the validation of Mininet, OVS, Python 3, and POX installations.
- `sdn_benchmark_suite.py` : The mathematical model that evaluates the trade-offs (Latency, TCAM Memory, and CPU Churn), generating visualizations.
- `results/` : Contains the high-resolution charts (`.png`) and raw metrics (`.json`) produced by the benchmark script.
- `Project_SA7_Final_Report.md` : The formal, comprehensive markdown report of the project, detailing the architecture, tests, and data analysis.

---

## How to Install and Run

### 1. Prerequisites
Ensure you have the following installed on your Ubuntu VM:
- Python 3
- Mininet (`sudo apt install mininet`)
- Open vSwitch

### 2. Running the Smoke Test
The smoke test verifies that all tools exist and checks the POX environment:
```bash
cd ~/Desktop/SDN_Project_SA7
python3 smoke_test.py
```

### 3. Running the Empirical Benchmark Suite
This suite runs the comparative analysis across varying network topologies and generates the performance plots found in the `results/` folder:
```bash
cd ~/Desktop/SDN_Project_SA7
python3 sdn_benchmark_suite.py
```
*(The charts will be output into the `results/` directory.)*

### 4. Running the Emulation with Mininet & POX

To test the actual software-defined network, you need two terminals.

#### Term 1: Start the POX Controller
Navigate to the `pox` directory and launch either the reactive or proactive module:

**To run the Reactive module:**
```bash
cd ~/Desktop/SDN_Project_SA7/pox
python3 pox.py forwarding.reactive_eval
```

**To run the Proactive module:**
```bash
cd ~/Desktop/SDN_Project_SA7/pox
python3 pox.py forwarding.proactive_eval
```

#### Term 2: Start the Mininet Topology
In a separate terminal, launch Mininet to connect to your running controller:
```bash
sudo mn --topo=tree,depth=2,fanout=2 --controller=remote,ip=127.0.0.1,port=6633 --test=pingall
```

**What you will see:**
Mininet will construct a tree topology with 3 switches and 4 hosts. It will run a `pingall` test. You will observe `0% packet loss`, proving full end-to-end routing. In Terminal 1, the POX controller will log the flow setup activity.
