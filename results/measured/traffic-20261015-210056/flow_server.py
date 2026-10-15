
import socket, sys, threading
s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', int(sys.argv[1]))); s.listen(1024)
def handle(c):
    try:
        c.settimeout(120)
        while c.recv(65536):
            pass
        c.sendall(b'k')
    except OSError:
        pass
    c.close()
while True:
    c, _ = s.accept()
    threading.Thread(target=handle, args=(c,), daemon=True).start()
