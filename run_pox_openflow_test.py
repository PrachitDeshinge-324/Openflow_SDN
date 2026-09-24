"""
OpenFlow 1.0 Switch Handshake & Verification Test
CS G525 Advanced Computer Networks - Project SA7

Connects as an OpenFlow 1.0 switch to POX controller, performs OFPT_HELLO / FEATURES handshake,
and injects OFPT_PACKET_IN to measure exact controller reaction time and flow mod generation.
"""

import sys
import time
import socket
import struct

# POX path
sys.path.insert(0, '/home/prachit/.gemini/antigravity/brain/27ff7fac-be84-4a82-b303-29827febfd33/scratch/pox')
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import EthAddr, IPAddr
from pox.lib.packet.ethernet import ethernet
from pox.lib.packet.ipv4 import ipv4
from pox.lib.packet.icmp import icmp, echo

def test_openflow_switch_handshake(controller_ip="127.0.0.1", controller_port=6633):
    print(f"[*] Connecting to OpenFlow Controller at {controller_ip}:{controller_port}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5.0)
    
    try:
        sock.connect((controller_ip, controller_port))
    except Exception as e:
        print(f"[-] Connection failed: {e}")
        return False

    print("[+] TCP Connection established.")
    
    # 1. Send OFPT_HELLO
    hello = of.ofp_hello()
    sock.sendall(hello.pack())
    print("[+] Sent OFPT_HELLO (version=1.0, type=0)")

    # 2. Receive OFPT_HELLO & OFPT_FEATURES_REQUEST from controller
    data = sock.recv(2048)
    msg_type = data[1]
    print(f"[+] Received message from controller: length={len(data)} bytes, type={msg_type}")

    # 3. Respond with OFPT_FEATURES_REPLY
    feat = of.ofp_features_reply()
    feat.datapath_id = 1
    feat.n_buffers = 256
    feat.n_tables = 1
    feat.capabilities = of.OFPC_FLOW_STATS | of.OFPC_TABLE_STATS | of.OFPC_PORT_STATS
    
    # Add switch ports 1, 2, 3, 4
    for p in range(1, 5):
        port = of.ofp_phy_port()
        port.port_no = p
        port.hw_addr = EthAddr(f"00:00:00:00:01:0{p}")
        port.name = f"s1-eth{p}".encode('latin-1')
        feat.ports.append(port)

    sock.sendall(feat.pack())
    print("[+] Sent OFPT_FEATURES_REPLY (DPID=1, 4 ports: s1-eth1..s1-eth4)")

    # Receive any initial flow mods (e.g. from proactive installer)
    time.sleep(0.5)
    sock.setblocking(False)
    proactive_rules_received = 0
    try:
        while True:
            resp = sock.recv(4096)
            if not resp:
                break
            # Count flow_mods in response (OFPT_FLOW_MOD is type 14)
            offset = 0
            while offset < len(resp):
                length = struct.unpack("!H", resp[offset+2:offset+4])[0]
                m_type = resp[offset+1]
                if m_type == 14: # OFPT_FLOW_MOD
                    proactive_rules_received += 1
                offset += length
    except BlockingIOError:
        pass

    print(f"[+] Proactive FLOW_MOD rules received on connection: {proactive_rules_received}")

    # 4. Inject synthetic PACKET_IN (h1 pinging h2: 00:00:00:00:00:01 -> 00:00:00:00:00:02)
    pkt = ethernet()
    pkt.src = EthAddr("00:00:00:00:00:01")
    pkt.dst = EthAddr("00:00:00:00:00:02")
    pkt.type = ethernet.IP_TYPE
    
    ipp = ipv4()
    ipp.srcip = IPAddr("10.0.0.1")
    ipp.dstip = IPAddr("10.0.0.2")
    ipp.protocol = ipv4.ICMP_PROTOCOL
    
    icmpp = icmp()
    icmpp.type = 8 # Echo request
    icmpp.payload = echo(id=1, seq=1, data=b"SDN_BENCHMARK_PROBE")
    ipp.payload = icmpp
    pkt.payload = ipp

    pkt_in = of.ofp_packet_in()
    pkt_in.in_port = 1
    pkt_in.data = pkt.pack()
    pkt_in.buffer_id = 0xffffffff # NO_BUFFER

    print("\n[*] Injecting OFPT_PACKET_IN from h1 (port 1) -> h2 (port 2)...")
    t0 = time.perf_counter()
    sock.sendall(pkt_in.pack())

    # Wait for controller response
    sock.setblocking(True)
    sock.settimeout(2.0)
    try:
        reply = sock.recv(2048)
        t_elapsed_ms = (time.perf_counter() - t0) * 1000
        reply_type = reply[1]
        type_names = {13: "OFPT_PACKET_OUT", 14: "OFPT_FLOW_MOD"}
        print(f"[+] Controller Response received in {t_elapsed_ms:.3f} ms! Message Type: {reply_type} ({type_names.get(reply_type, 'OTHER')})")
    except socket.timeout:
        print("[-] Timed out waiting for controller response.")

    sock.close()
    print("[+] Test completed cleanly.\n")
    return True

if __name__ == '__main__':
    test_openflow_switch_handshake()
