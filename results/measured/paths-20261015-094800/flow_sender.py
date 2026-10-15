
import socket, sys, time
s = socket.create_connection((sys.argv[1], int(sys.argv[2])), timeout=10)
buf = b'x' * 65536; end = time.time() + float(sys.argv[3])
try:
    while time.time() < end:
        s.sendall(buf)
except OSError:
    pass   # the receiver stops when its window ends
