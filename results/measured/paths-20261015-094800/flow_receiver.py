
import socket, sys, time
port, wait, w = int(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])
s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', port)); s.listen(1); s.settimeout(wait)
c, _ = s.accept(); c.settimeout(1)
n, t0 = 0, time.time()
while time.time() - t0 < w:
    try:
        b = c.recv(65536)
    except socket.timeout:
        continue
    if not b:
        break
    if 1 <= time.time() - t0 <= w - 1:
        n += len(b)
print(n, w - 2)
