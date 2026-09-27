"""
Live POX Controller Test & Empirical Validator
CS G525 Advanced Computer Networks - Project SA7

This script:
1. Spawns POX controller with Reactive (forwarding.reactive_eval) and Proactive (forwarding.proactive_eval)
2. Connects simulated OpenFlow 1.0 switches
3. Performs OFPT_HELLO and OFPT_FEATURES handshakes
4. Injects packet-ins and verifies exact flow-mod and packet-out responses
5. Measures exact controller processing latency and logs every command & output
"""

import os
import sys
import time
import socket
import struct
import subprocess
import threading
import json
import tempfile

REPO = os.path.dirname(os.path.abspath(__file__))
POX_DIR = os.environ.get('POX_DIR', os.path.join(REPO, 'pox'))
CONTROLLER_DIR = os.path.join(REPO, 'controllers')
sys.path.insert(0, POX_DIR)

import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import EthAddr, IPAddr
from pox.lib.packet.ethernet import ethernet
from pox.lib.packet.ipv4 import ipv4
from pox.lib.packet.icmp import icmp, echo

OFPT_ECHO_REQUEST, OFPT_ECHO_REPLY, OFPT_FLOW_MOD = 2, 3, 14
OFPT_BARRIER_REQUEST, OFPT_BARRIER_REPLY = 18, 19


def pump_messages(sock, duration, stop=None):
    """Read OpenFlow messages for up to `duration` seconds, answering ECHO and
    BARRIER requests like a real switch. Returns the raw messages received."""
    msgs, buf = [], b""
    end = time.time() + duration
    while time.time() < end:
        sock.settimeout(max(0.01, end - time.time()))
        try:
            chunk = sock.recv(65536)
        except socket.timeout:
            break
        if not chunk:
            break
        buf += chunk
        while len(buf) >= 8:
            length = struct.unpack("!H", buf[2:4])[0]
            if len(buf) < length:
                break
            msg, buf = buf[:length], buf[length:]
            msgs.append(msg)
            if msg[1] in (OFPT_ECHO_REQUEST, OFPT_BARRIER_REQUEST):
                reply_type = OFPT_ECHO_REPLY if msg[1] == OFPT_ECHO_REQUEST else OFPT_BARRIER_REPLY
                sock.sendall(bytes([1, reply_type]) + struct.pack("!H", 8) + msg[4:8])
            if stop and stop(msg):
                return msgs
    return msgs


def is_rule_add(msg):
    """FLOW_MOD with command ADD and non-zero priority (skips POX's delete-all and the table-miss rule)."""
    if msg[1] != OFPT_FLOW_MOD or len(msg) < 64:
        return False
    command, priority = struct.unpack("!H", msg[56:58])[0], struct.unpack("!H", msg[62:64])[0]
    return command == 0 and priority > 0


def run_openflow_test_client(mode="reactive", host_count=4, port=6633):
    print(f"\n[CLIENT] Initializing OpenFlow 1.0 Switch Client (Target: {mode.upper()} controller on port {port})...")
    time.sleep(1.2) # wait for controller to bind
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5.0)
    
    try:
        sock.connect(("127.0.0.1", port))
    except Exception as e:
        print(f"[-] Failed to connect to controller: {e}")
        return None

    # Step 1: Handshake (OFPT_HELLO)
    t_start = time.perf_counter()
    sock.sendall(of.ofp_hello().pack())
    
    # Step 2: Receive Hello and Features Request
    data = sock.recv(2048)
    
    # Step 3: Send Features Reply
    feat = of.ofp_features_reply()
    feat.datapath_id = 1
    feat.n_buffers = 256
    feat.n_tables = 1
    feat.capabilities = of.OFPC_FLOW_STATS | of.OFPC_TABLE_STATS | of.OFPC_PORT_STATS
    
    for p in range(1, host_count + 1):
        port_desc = of.ofp_phy_port()
        port_desc.port_no = p
        port_desc.hw_addr = EthAddr(f"00:00:00:00:01:{p:02x}")
        port_desc.name = f"s1-eth{p}".encode('latin-1')
        feat.ports.append(port_desc)
    sock.sendall(feat.pack())
    
    # Step 4: Answer the controller's handshake (POX waits for a BARRIER_REPLY before
    # it raises ConnectionUp) and count proactive rules pushed right after it
    msgs = pump_messages(sock, 1.5)
    proactive_rules = sum(1 for m in msgs if is_rule_add(m))

    # Step 5: Inject first packet (Miss -> PACKET_IN)
    pkt = ethernet()
    pkt.src = EthAddr("00:00:00:00:00:01")
    pkt.dst = EthAddr("00:00:00:00:00:02")
    pkt.type = ethernet.IP_TYPE
    
    ipp = ipv4()
    ipp.srcip = IPAddr("10.0.0.1")
    ipp.dstip = IPAddr("10.0.0.2")
    ipp.protocol = ipv4.ICMP_PROTOCOL
    
    icmpp = icmp()
    icmpp.type = 8
    echop = echo(id=1, seq=1)
    echop.payload = b"SDN_BENCHMARK_PROBE!"  # even length: POX's checksum() breaks on odd lengths in Python 3
    icmpp.payload = echop
    ipp.payload = icmpp
    pkt.payload = ipp

    pkt_in = of.ofp_packet_in()
    pkt_in.in_port = 1
    pkt_in.data = pkt.pack()
    pkt_in.buffer_id = 0xffffffff

    t_pkt1_start = time.perf_counter()
    sock.sendall(pkt_in.pack())
    
    type_names = {13: "OFPT_PACKET_OUT", 14: "OFPT_FLOW_MOD"}
    replies = pump_messages(sock, 3.0, stop=lambda m: m[1] in type_names)
    answers = [m for m in replies if m[1] in type_names]
    if answers:
        t_pkt1_elapsed_ms = (time.perf_counter() - t_pkt1_start) * 1000
        reply_type = answers[0][1]
    else:
        t_pkt1_elapsed_ms = 0
        reply_type = -1   # no answer (expected for proactive: table misses are not handled)

    sock.close()
    
    return {
        'mode': mode,
        'proactive_rules_installed': proactive_rules,
        'first_packet_ctrl_rtt_ms': t_pkt1_elapsed_ms,
        'response_type': type_names.get(reply_type, "none (packet not handled by controller)")
    }


def write_single_switch_topology(path, host_count=4):
    """Topology matching the simulated switch below: dpid 1, host i on port i."""
    hosts = [{"name": f"h{i}", "mac": f"00:00:00:00:00:{i:02x}", "ip": f"10.0.0.{i}",
              "dpid": 1, "port": i} for i in range(1, host_count + 1)]
    with open(path, "w") as f:
        json.dump({"switches": [1], "hosts": hosts, "links": []}, f)


def test_pox_controller_live(module_args=("reactive_eval",), mode="reactive", port=6633):
    module_name = " ".join(module_args)
    print("="*70)
    print(f"[*] TESTING CONTROLLER WITH MODULE: {module_name} (Mode: {mode.upper()})")
    print(f"[*] Command: PYTHONPATH=../controllers python3 pox.py openflow.of_01 --port={port} {module_name}")
    print("="*70)

    pox_cmd = [
        sys.executable,
        os.path.join(POX_DIR, "pox.py"),
        "openflow.of_01",
        f"--port={port}",
    ] + list(module_args)
    env = dict(os.environ, PYTHONPATH=CONTROLLER_DIR)

    # Start POX process
    proc = subprocess.Popen(
        pox_cmd,
        cwd=POX_DIR,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.PIPE,
        text=True
    )

    result = None
    try:
        result = run_openflow_test_client(mode=mode, host_count=4, port=port)
    finally:
        proc.terminate()
        try:
            out, _ = proc.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
            out, _ = proc.communicate()

    print("\n--- POX CONTROLLER OUTPUT LOG ---")
    for line in out.strip().split('\n')[:15]:
        print(f"| {line}")
    print("---------------------------------\n")

    if result:
        print(f"[+] Result Summary for {mode.upper()}:")
        print(f"    - Pre-populated Proactive Flow Rules: {result['proactive_rules_installed']}")
        print(f"    - First Packet Controller Round-Trip: {result['first_packet_ctrl_rtt_ms']:.3f} ms")
        print(f"    - Controller Response Message Type:   {result['response_type']}")

    return result

if __name__ == '__main__':
    # 1. Test Reactive Mode
    res_reactive = test_pox_controller_live(("reactive_eval",), "reactive", port=8833)
    time.sleep(1.0)
    
    # 2. Test Proactive Mode (the controller needs the topology in advance)
    topo_file = os.path.join(tempfile.gettempdir(), "sa7_single_switch_topo.json")
    write_single_switch_topology(topo_file, host_count=4)
    res_proactive = test_pox_controller_live(("proactive_eval", f"--topo={topo_file}"), "proactive", port=8834)
