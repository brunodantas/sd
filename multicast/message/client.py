import socket
import struct


multicast_addr = '224.2.2.3'
port = 8888
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

while True:
	message = raw_input()
	sock.sendto(message, (multicast_addr, port))
	
sock.close()

