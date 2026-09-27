# Installing SA7 for the First Time

This guide takes a fresh machine to a working testbed: Mininet + Open vSwitch + POX, able to run every
script in this repo. It takes about 15 minutes, most of it downloads.

## Requirements

**Machine**

| | Minimum | Notes |
| --- | --- | --- |
| OS | Ubuntu 22.04 or newer | Directly, in a VM, or in WSL2 on Windows. Mininet does **not** run on Windows or macOS directly. |
| CPU | 2 cores, x86_64 or ARM64 | |
| RAM | 4 GB | |
| Disk | 2 GB free | |
| Access | `sudo` rights and internet | Mininet must run as root. |

**Software** (installed by `setup.sh`; tested versions)

| Package | Tested version | Installed from |
| --- | --- | --- |
| Python 3 | 3.11, 3.14 | apt (`python3`) |
| numpy, matplotlib | distro versions | apt (`python3-numpy`, `python3-matplotlib`); also in `requirements.txt` |
| Mininet | 2.3.0 | apt (`mininet`) |
| Open vSwitch | 3.3.9, 3.7.1 | apt (`openvswitch-switch`, `openvswitch-testcontroller`) |
| POX | 0.7.0 `gar`, commit `5f82461` | `git clone` from github.com/noxrepo/pox |
| git, ping, iproute2 | distro versions | apt |

Our results were produced on Windows 11 + WSL2 with Ubuntu 26.04.1 (kernel 6.18 WSL2), Mininet 2.3.0,
Open vSwitch 3.7.1 (kernel datapath), POX 0.7.0 and Python 3.14.4.

---

## Step 0: Get Ubuntu

**Windows 10/11 (WSL2).** Open **PowerShell as Administrator** and run:
```powershell
wsl --install -d Ubuntu
```
Restart when asked, then open **Ubuntu** from the Start menu and choose a username and password.
That password is what `sudo` asks for later. Check that systemd is on:
```bash
cat /etc/wsl.conf        # should contain:  [boot]  systemd=true
```
If it doesn't, add those two lines (`sudo nano /etc/wsl.conf`), then run `wsl --shutdown` in PowerShell and reopen Ubuntu.

**macOS.** Create an Ubuntu VM (for example with UTM or Multipass) and do everything inside it.

**Linux.** Use Ubuntu 22.04+ directly or in a VM.

> In WSL, keep the project in the Linux home folder (`~`), not under `/mnt/c`. Mininet and Open vSwitch misbehave on Windows drives.
> From Windows you can still see the files at `\\wsl.localhost\Ubuntu\home\<user>\Openflow_SDN`, or run `explorer.exe .` in the folder.

## Step 1: Clone the repository

```bash
sudo apt update && sudo apt install -y git
cd ~
git clone https://github.com/PrachitDeshinge-324/Openflow_SDN.git
cd Openflow_SDN
```
Cloning needs no login. To **push** changes (collaborators only), log in once with the GitHub CLI:
```bash
sudo apt install -y gh
gh auth login      # GitHub.com -> HTTPS -> Yes -> Login with a web browser
```
In WSL no browser opens by itself. Open https://github.com/login/device in Windows and type the code shown.

## Step 2: Run the setup script

```bash
bash setup.sh
```
It installs the packages above, starts Open vSwitch, checks for the Open vSwitch kernel module, clones POX
into `pox/` at the tested commit, and finishes with the smoke test and a 2-host ping test. It ends with
**Setup complete** and the command to run next. The script is safe to run again.

## Step 3: First run

```bash
sudo python3 experiments/run_experiments.py --quick
```
It takes about 2 minutes and measures the 4-host network with both controllers. Results go to
`results/measured/<timestamp>/`. If `setup.sh` reported no kernel module, add `--datapath user`.

The full run (4, 8 and 16 hosts, about 15 minutes) is the same command without `--quick`. README.md
explains the options and how to run the controllers by hand.

**Optional editor:** install VS Code on Windows with the **WSL** extension, then run `code .` in the
project folder. Its built-in terminal (Ctrl+`) is an Ubuntu terminal.

---

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `modprobe: FATAL: Module openvswitch not found` | The kernel has no Open vSwitch module. Everything still works in userspace: add `--switch ovs,datapath=user` to `mn` and `--datapath user` to `run_experiments.py`. Latencies are higher; say which datapath you used. |
| `ovs-vsctl: ... database connection failed` | Open vSwitch isn't running: `sudo systemctl start openvswitch-switch` (without systemd: `sudo /usr/share/openvswitch/scripts/ovs-ctl start`). |
| `POX did not start` or `Unable to contact the remote controller` in a manual run | Another POX is still using port 6633. Find it with `sudo ss -ltnp \| grep 6633` and stop it (Ctrl+C in its terminal or `sudo kill <pid>`). |
| Mininet errors like `RTNETLINK answers: File exists` | A previous run crashed. Clean up with `sudo mn -c`. |
| POX prints `POX requires one of the following versions of Python: 3.6 ... 3.9` | Harmless warning; everything in this project works on newer Python. |
| `pip install` says `externally-managed-environment` | Use the apt packages (`setup.sh` does), or a virtual environment: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`. |
| `pox/` is empty after cloning | Expected: the repo only records which POX commit to use. `setup.sh` clones it; manually: `git clone https://github.com/noxrepo/pox.git pox`. |
| `git push` returns 403 or asks for a password | Run `gh auth login` (Step 1) with an account that has access to the repo. |
