import socket
import struct
import time

TIME1997 = 2208988800
NTP_SERVER = "pool.ntp.org"

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

data = b"\x1b" + 47 * b"\0"
client.sendto(data, (NTP_SERVER, 123))
data, address = client.recvfrom(1024)
print("response received from server:", address)

ts = struct.unpack("!12L", data)
t = ts[10]
t -= TIME1997
print(time.ctime(t))
