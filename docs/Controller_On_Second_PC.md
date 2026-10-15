# Controller on a second PC (Review I point 3: "multiple PCs")

On one PC, POX, Mininet's switches and the traffic generators all compete for
the same CPU, and the switch-to-controller link has no latency. Both make the
single-PC numbers different from a real network, where the controller is a
separate machine reached over a real LAN. This setup moves POX to a second PC.
The switches, hosts and traffic stay on the first PC, and OpenFlow travels
over the LAN.

```
 PC A: Mininet PC (needs root)                PC B: controller PC (no root)
 run_traffic_experiments.py                   controller_agent.py
   --controller-host <PC B's IP>   -- TCP 6000 ->  starts/stops POX, sends its
                                                   stats and CPU time back
 OVS switches   ------ OpenFlow, TCP 6633 ---->  POX
```

`experiments/controller_agent.py` runs on PC B. For every run, the harness on
PC A asks the agent to:

1. start POX with the right modules (it sends along the topology file, and
   the pairs file in oracle mode);
2. read POX's statistics and CPU time during the run;
3. stop POX and send back its log and final statistics.

Those are stored in PC A's results folder exactly as in a single-PC run. The
agent only starts the POX modules of this project (`ALLOWED_MODULES` in the
script).

What changes in the results:

- **Controller CPU %** is now the CPU time of POX on PC B, so it no longer
  competes with Mininet.
- **FCT and PACKET_IN timings** include the real LAN round trip from switch
  to controller.
- **The `traffic.md` header** says where the controller ran, its host name
  and CPUs, and the measured round-trip time. The RTT is the median time of
  20 TCP handshakes with the agent. Windows drops ping by default, so ping is
  not used.

**Status (15 Oct 2026):** tested with the agent on the same machine
(`--controller-host 127.0.0.1`): starting and stopping POX, stats, CPU time,
log copy-back and repeats all work. It has **not yet been run across two
real PCs**, so the networking steps below are untested on our laptops.

## 1. Network between the two PCs

- Put both PCs on the same LAN. Ethernet through one switch or router is
  best. Wi-Fi works but adds jitter; write down which one you used.
- PC A only makes outgoing connections, so PC A needs no change.
- **PC B must accept incoming TCP 6633 (OpenFlow) and TCP 6000 (agent).**

### PC B runs Linux natively (or dual-boot)

```bash
sudo ufw allow 6633/tcp && sudo ufw allow 6000/tcp     # only if ufw is enabled
```

### PC B runs WSL2 (Windows)

By default, WSL2 sits behind NAT, so other machines cannot reach it. Use
mirrored networking, which needs Windows 11 22H2 or newer:

1. In Windows, create or edit `%UserProfile%\.wslconfig`:

   ```ini
   [wsl2]
   networkingMode=mirrored
   ```

2. In PowerShell, run `wsl --shutdown`, then open WSL again. WSL now has the
   PC's own LAN IP; check with `ip addr`.
3. Open the two ports. Run PowerShell as Administrator:

   ```powershell
   New-NetFirewallHyperVRule -Name SA7-POX -DisplayName "SA7 POX + agent" -Direction Inbound `
       -VMCreatorId '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}' -Protocol TCP -LocalPorts 6633,6000
   New-NetFirewallRule -DisplayName "SA7 POX + agent" -Direction Inbound -Protocol TCP `
       -LocalPort 6633,6000 -Action Allow
   ```

If you are on Windows 10 (no mirrored mode), forward the ports from Windows
to WSL instead. Run as Administrator, with `<WSL-IP>` from `hostname -I`
inside WSL:

```powershell
netsh interface portproxy add v4tov4 listenport=6633 listenaddress=0.0.0.0 connectport=6633 connectaddress=<WSL-IP>
netsh interface portproxy add v4tov4 listenport=6000 listenaddress=0.0.0.0 connectport=6000 connectaddress=<WSL-IP>
```

Also add the `New-NetFirewallRule` line above. Port forwarding adds a relay
inside Windows, so it adds some latency to every OpenFlow message. Mention it
if you use it.

## 2. Run

On **PC B**, the controller PC. It needs the repository with `pox/` and
Python 3; Mininet is not needed.

```bash
cd Openflow_SDN
python3 experiments/controller_agent.py          # leave it running; Ctrl-C when done
```

On **PC A**, the Mininet PC. Check that PC B is reachable, then run:

```bash
python3 -c "import socket; socket.create_connection(('192.168.1.20', 6000), 3); print('agent reachable')"
sudo python3 experiments/run_traffic_experiments.py --controller-host 192.168.1.20
sudo python3 experiments/run_traffic_experiments.py --controller-host 192.168.1.20 \
    --scenarios tree-d2-f4:university --budget-sweep --pair-zipf 1
```

Replace `192.168.1.20` with PC B's IP, from `ip addr` on PC B. All other
options (`--repeats`, `--budget-sweep`, `--scenarios`, ...) work as usual.

## 3. What to compare

Run the same command once with POX on PC A (no `--controller-host`) and once
with POX on PC B, with the same seed, so the traffic is identical. Then
compare:

| Question | Where to look |
| --- | --- |
| Does reactive get faster when POX has its own CPU? | small-flow FCT, controller CPU % |
| How much does the LAN round trip add to every new flow? | small-flow p50 of reactive minus the single-PC value, against the RTT in the header |
| Does proactive care at all? | proactive FCT should be unchanged: it does not talk to the controller during the run |

If one PC A run loses flows and the other does not, say so; it means PC A was
overloaded in the single-PC run.

## Troubleshooting

| Message | Cause |
| --- | --- |
| `ConnectionRefusedError` / `timed out` at the start | agent not running on PC B, wrong IP, or port 6000 blocked |
| `Switches did not connect to POX at <ip>:6633` | port 6633 blocked on PC B (firewall, or WSL without mirrored mode / port forwarding) |
| `controller agent ...: POX did not start` | the POX log is in the message; usually `pox/` missing on PC B (set `POX_DIR`) |
| `module(s) not allowed` | PC B has an older copy of the repository; pull it |
