#!/usr/bin/env bash
# First-time setup for CS G525 Project SA7 on Ubuntu (VM or WSL2).
#
# Usage, from the repository root:
#   bash setup.sh
#
# Installs Mininet, Open vSwitch and the Python libraries with apt, starts
# Open vSwitch, clones POX at the commit this repo was tested with, and checks
# that everything works. Safe to run again.

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
POX_URL="https://github.com/noxrepo/pox.git"
POX_COMMIT="5f82461e01f8822bd7336603b361bff4ffbd2380"   # POX 0.7.0 (gar), same as the pox/ entry in git

APT_PACKAGES=(
  git                          # clone this repo and POX
  python3                      # runs everything
  python3-numpy                # analytical model
  python3-matplotlib           # plots
  mininet                      # network emulator (includes the Python bindings)
  openvswitch-switch           # the OpenFlow switch Mininet uses
  openvswitch-testcontroller   # reference controller; Mininet expects it to exist
  iputils-ping                 # ping, used for latency measurements
  iproute2                     # ip / network namespaces, used by Mininet
)

step() { printf '\n\033[1m[%s] %s\033[0m\n' "$1" "$2"; }
ok()   { printf '    \033[32mOK\033[0m  %s\n' "$1"; }
warn() { printf '    \033[33m!!\033[0m  %s\n' "$1"; }

if [ ! -f /etc/os-release ] || ! grep -qi ubuntu /etc/os-release; then
  warn "This script is written for Ubuntu. Continuing, but package names may differ."
fi

step 1/5 "Installing system packages (asks for your password)"
sudo apt-get update || warn "apt-get update reported errors (often a broken third-party PPA); continuing"
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y "${APT_PACKAGES[@]}"
ok "apt packages installed"

step 2/5 "Starting Open vSwitch"
if command -v systemctl >/dev/null && sudo systemctl enable --now openvswitch-switch 2>/dev/null; then
  ok "openvswitch-switch service enabled and running"
else
  # No systemd (e.g. WSL without systemd): start the daemons directly
  sudo /usr/share/openvswitch/scripts/ovs-ctl start --system-id=random
  warn "Started Open vSwitch without systemd; repeat this step after every reboot:"
  warn "  sudo /usr/share/openvswitch/scripts/ovs-ctl start"
fi
sudo ovs-vsctl show >/dev/null && ok "ovs-vsctl can talk to Open vSwitch"

step 3/5 "Checking the Open vSwitch kernel module"
DATAPATH=kernel
if sudo modprobe openvswitch 2>/dev/null; then
  ok "kernel datapath available (fast, used for the reported results)"
else
  DATAPATH=user
  warn "No openvswitch kernel module. Use the userspace datapath instead:"
  warn "  mn ... --switch ovs,datapath=user"
  warn "  sudo python3 experiments/run_experiments.py --datapath user"
fi

step 4/5 "Getting POX"
if [ -f "$REPO/pox/pox.py" ]; then
  ok "POX already present in pox/"
else
  # pox/ is only a pointer in this repo, so a fresh clone leaves it empty
  rmdir "$REPO/pox" 2>/dev/null || true
  git clone -q "$POX_URL" "$REPO/pox"
  ok "cloned POX into pox/"
fi
git -C "$REPO/pox" checkout -q "$POX_COMMIT" 2>/dev/null \
  && ok "POX at tested commit ${POX_COMMIT:0:7}" \
  || warn "could not check out ${POX_COMMIT:0:7}; using POX's current version"

step 5/5 "Verifying the installation"
python3 "$REPO/smoke_test.py"
sudo mn -c >/dev/null 2>&1 || true
# Standalone OVS bridge, no controller: checks Mininet + OVS on their own
MN_OUT="$(sudo mn --switch "ovsbr,datapath=$DATAPATH" --controller none --topo single,2 --test pingall 2>&1 || true)"
if grep -q " 0% dropped" <<<"$MN_OUT"; then
  ok "Mininet + Open vSwitch forward packets (2-host ping test passed)"
else
  warn "Mininet ping test failed. Run 'sudo mn -c' and try again, or see INSTALL.md > Troubleshooting."
  exit 1
fi

printf '\n\033[1mSetup complete.\033[0m Next steps:\n'
printf '  sudo python3 experiments/run_experiments.py --quick%s   # 2-minute measured run\n' \
  "$([ "$DATAPATH" = user ] && echo ' --datapath user')"
printf '  See README.md for running the controllers by hand.\n'
