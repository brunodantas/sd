import socket

s = socket.socket()
host = socket.gethostname()
port = 12345
s.bind((host,port))

s.listen(5)
while True:
	c, addr = s.accept()
	print "connection from ", addr
	print "received: ", c.recv(1024)
	message = raw_input("write a response: ")
	c.send(message)
	print "sent"
	c.close