
import socket, sys, threading, time
sched, t0, port, timeout = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
flows = [l.split() for l in open(sched) if l.strip()]
lock, buf = threading.Lock(), b'x' * 65536
def run(start, dst, size):
    t = time.time(); ok = 0
    try:
        s = socket.create_connection((dst, port), timeout=timeout)
        s.settimeout(timeout)
        left = size
        while left > 0:
            n = min(left, len(buf)); s.sendall(buf[:n]); left -= n
        s.shutdown(socket.SHUT_WR)
        ok = 1 if s.recv(1) == b'k' else 0
        s.close()
    except OSError:
        pass
    with lock:
        print('%s %d %.6f %d %.6f' % (start, size, time.time() - t, ok, t - (t0 + float(start))), flush=True)
threads = []
for start, dst, size in flows:
    d = t0 + float(start) - time.time()
    if d > 0:
        time.sleep(d)
    th = threading.Thread(target=run, args=(start, dst, int(size)), daemon=True)
    th.start(); threads.append(th)
deadline = time.time() + timeout + 5
for th in threads:
    th.join(max(0, deadline - time.time()))
print('DONE', flush=True)
