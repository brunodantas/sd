#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import sys
import glob
from inspect import signature
sys.path.append('gen-py')
sys.path.insert(0, glob.glob('./lib*')[0])

from graph import Graph
from graph.ttypes import NotFound

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

import hashlib

try: input = raw_input
except NameError: pass

name_hash = lambda name: int(hashlib.md5(name.encode('utf-8')).hexdigest(),16) % 2**31
pessoa, filme, grupo, cast = 0, 1, 2, 3
cst = 0

def main():
	p = sys.argv[1]
	# Make socket
	transport = TSocket.TSocket('localhost', p)

	# Buffering is critical. Raw sockets are very slow
	transport = TTransport.TBufferedTransport(transport)

	# Wrap in a protocol
	protocol = TBinaryProtocol.TBinaryProtocol(transport)

	# Create a client to use the protocol encoder
	client = Graph.Client(protocol)

	# Connect!
	transport.open()
	client.ping()

	print(client.add_upd_vertex(name_hash("Alice"),pessoa,"Alice",0))
	print(client.add_upd_vertex(name_hash("Bob"),pessoa,"Bob",0))
	print(client.add_upd_vertex(name_hash("Carla"),pessoa,"Carla",0))
	print(client.add_upd_vertex(name_hash("Dan"),pessoa,"Dan",0))
	print(client.add_upd_vertex(name_hash("Eve"),pessoa,"Eve",0))

	print(client.add_upd_vertex(name_hash("Blade Runner"),filme,"Blade Runner",0))
	print(client.add_upd_vertex(name_hash("Terminator 2"),filme,"Terminator 2",0))
	print(client.add_upd_vertex(name_hash("The Matrix"),filme,"The Matrix",0))
	print(client.add_upd_vertex(name_hash("Ex Machina"),filme,"Ex Machina",0))
	print(client.add_upd_vertex(name_hash("Her"),filme,"Her",0))

	print(client.add_upd_vertex(name_hash("Harrison Ford"),cast,"Harrison Ford",0))
	print(client.add_upd_vertex(name_hash("Arnold Schwarzenegger"),cast,"Arnold Schwarzenegger",0))
	print(client.add_upd_vertex(name_hash("Keanu Reeves"),cast,"Keanu Reeves",0))
	print(client.add_upd_vertex(name_hash("Domhnall Gleeson"),cast,"Domhnall Gleeson",0))
	print(client.add_upd_vertex(name_hash("Joaquin Phoenix"),cast,"Joaquin Phoenix",0))

	print(client.add_upd_vertex(name_hash("oldschool"),grupo,"oldschool",0))
	print(client.add_upd_vertex(name_hash("scifi"),grupo,"scifi",0))

	print(client.add_upd_edge(name_hash("Blade Runner"),name_hash("Harrison Ford"),cst,True))
	print(client.add_upd_edge(name_hash("Terminator 2"),name_hash("Arnold Schwarzenegger"),cst,True))
	print(client.add_upd_edge(name_hash("The Matrix"),name_hash("Keanu Reeves"),cst,True))
	print(client.add_upd_edge(name_hash("Ex Machina"),name_hash("Domhnall Gleeson"),cst,True))
	print(client.add_upd_edge(name_hash("Her"),name_hash("Joaquin Phoenix"),cst,True))

	print(client.add_upd_edge(name_hash("Alice"),name_hash("Terminator 2"),91.0,True))
	print(client.add_upd_edge(name_hash("Alice"),name_hash("Ex Machina"),79.0,True))
	print(client.add_upd_edge(name_hash("Bob"),name_hash("The Matrix"),90.0,True))
	print(client.add_upd_edge(name_hash("Carla"),name_hash("Her"),75.0,True))
	print(client.add_upd_edge(name_hash("Dan"),name_hash("Blade Runner"),75.0,True))
	print(client.add_upd_edge(name_hash("Dan"),name_hash("Terminator 2"),80.0,True))
	print(client.add_upd_edge(name_hash("Dan"),name_hash("The Matrix"),79.0,True))
	print(client.add_upd_edge(name_hash("Eve"),name_hash("Ex Machina"),60.0,True))

	print(client.add_upd_edge(name_hash("scifi"),name_hash("Alice"),0,False))
	print(client.add_upd_edge(name_hash("scifi"),name_hash("Bob"),0,False))
	print(client.add_upd_edge(name_hash("scifi"),name_hash("Carla"),0,False))
	print(client.add_upd_edge(name_hash("scifi"),name_hash("Dan"),0,False))
	print(client.add_upd_edge(name_hash("oldschool"),name_hash("Alice"),0,False))
	print(client.add_upd_edge(name_hash("oldschool"),name_hash("Dan"),0,False))

	# Close!
	transport.close()


if __name__ == '__main__':
	try:
		main()
	except Thrift.TException as tx:
		print('%s' % tx.message)
