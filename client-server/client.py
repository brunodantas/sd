import socket
import sys

message = ""
if len(sys.argv) > 1:
	message = sys.argv[1]

s = socket.socket()
host = socket.gethostname()
port = 12345

s.connect((host,port))
s.send(message)
print "waiting response"
print "response: ",s.recv(1024)
s.close