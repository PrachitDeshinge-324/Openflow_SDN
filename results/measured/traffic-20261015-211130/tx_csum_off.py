
import array, fcntl, socket, struct, sys
buf = array.array('B', struct.pack('II', 0x17, 0))   # ETHTOOL_STXCSUM, off
ifr = struct.pack('16sP', sys.argv[1].encode(), buf.buffer_info()[0])
fcntl.ioctl(socket.socket(socket.AF_INET, socket.SOCK_DGRAM), 0x8946, ifr)   # SIOCETHTOOL
