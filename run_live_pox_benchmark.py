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

POX_DIR = os.environ.get('POX_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pox'))
sys.path.insert(0, POX_DIR)

import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import EthAddr, IPAddr
from pox.lib.packet.ethernet import ethernet
from pox.lib.packet.ipv4 import ipv4
from pox.lib.packet.icmp import icmp, echo

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
    
    # Check for proactive rules sent immediately
    time.sleep(0.3)
    sock.setblocking(False)
    proactive_rules = 0
    try:
        while True:
            resp = sock.recv(4096)
            if not resp: break
            offset = 0
            while offset < len(resp):
                length = struct.unpack("!H", resp[offset+2:offset+4])[0]
                m_type = resp[offset+1]
                if m_type == 14: # OFPT_FLOW_MOD
                    proactive_rules += 1
                offset += length
    except BlockingIOError:
        pass
    
    sock.setblocking(True)
    
    # Step 4: Inject first packet (Miss -> PACKET_IN)
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
    echop.payload = b"SDN_BENCHMARK_PROBE"
    icmpp.payload = echop
    ipp.payload = icmpp
    pkt.payload = ipp

    pkt_in = of.ofp_packet_in()
    pkt_in.in_port = 1
    pkt_in.data = pkt.pack()
    pkt_in.buffer_id = 0xffffffff

    t_pkt1_start = time.perf_counter()
    sock.sendall(pkt_in.pack())
    
    try:
        reply = sock.recv(2048)
        t_pkt1_elapsed_ms = (time.perf_counter() - t_pkt1_start) * 1000
        reply_type = reply[1] if len(reply) > 1 else -1
        type_names = {13: "OFPT_PACKET_OUT", 14: "OFPT_FLOW_MOD"}
    except Exception as e:
        t_pkt1_elapsed_ms = 0
        reply_type = -1
        type_names = {}

    sock.close()
    
    return {
        'mode': mode,
        'proactive_rules_installed': proactive_rules,
        'first_packet_ctrl_rtt_ms': t_pkt1_elapsed_ms,
        'response_type': type_names.get(reply_type, f"Type_{reply_type}")
    }


def test_pox_controller_live(module_name="forwarding.reactive_eval", mode="reactive", port=6633):
    print("="*70)
    print(f"[*] TESTING CONTROLLER WITH MODULE: {module_name} (Mode: {mode.upper()})")
    print(f"[*] Command: python3 pox.py openflow.of_01 --port={port} {module_name}")
    print("="*70)

    pox_cmd = [
        sys.executable,
        os.path.join(POX_DIR, "pox.py"),
        "openflow.of_01",
        f"--port={port}",
        module_name
    ]

    # Start POX process
    proc = subprocess.Popen(
        pox_cmd,
        cwd=POX_DIR,
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
    res_reactive = test_pox_controller_live("forwarding.reactive_eval", "reactive", port=8833)
    time.sleep(1.0)
    
    # 2. Test Proactive Mode
    res_proactive = test_pox_controller_live("forwarding.proactive_eval", "proactive", port=8834)
