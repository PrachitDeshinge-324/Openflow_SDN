
import random, socket, sys, time
dsts = sys.argv[1].split(','); rate = float(sys.argv[2]); dur = float(sys.argv[3])
n = int(rate * dur); t0 = time.time()
for i in range(n):
    d = t0 + i / rate - time.time()
    if d > 0:
        time.sleep(d)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   # new socket = new source port = new flow
    s.sendto(b'sa7-churn', (random.choice(dsts), 9))
    s.close()
print(n, time.time() - t0)
