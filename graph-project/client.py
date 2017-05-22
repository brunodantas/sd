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

try: input = raw_input
except NameError: pass

opt = "0 client.ping()\n1 client.add_upd_vertex( nome, cor, desc, peso)\n2 client.add_upd_edge( v1, v2, peso, bi_flag)\n3 client.get_vertex( v)\n4 client.get_edge( v1, v2)\n5 client.del_vertex( v)\n6 client.del_edge( v1, v2)\n7 client.list_edges( v)\n8 client.list_vertices( v1, v2)\n9 client.list_neighbors( v)\n\n"

def main():

	# Make socket
	transport = TSocket.TSocket('localhost', 9090)

	# Buffering is critical. Raw sockets are very slow
	transport = TTransport.TBufferedTransport(transport)

	# Wrap in a protocol
	protocol = TBinaryProtocol.TBinaryProtocol(transport)

	# Create a client to use the protocol encoder
	client = Graph.Client(protocol)

	# Connect!
	transport.open()
	client.ping()
	f = [client.ping,client.add_upd_vertex,client.add_upd_edge,client.get_vertex,client.get_edge,client.del_vertex,client.del_edge,client.list_edges,client.list_vertices,client.list_neighbors]

	while 1:
		choice = input(opt)
		choice = int(choice)

		if choice == 0:
			client.ping()
			continue
		args = input(str(signature(f[choice]))+'\n')
		args = args.split()
		args[0] = int(args[0])
		if len(args) > 1:
			args[1] = int(args[1])
		if choice == 1:
			args[3] = float(args[3])
		elif choice == 2:
			args[2] = float(args[2])
			args[3] = bool(args[3])
		try:
			print(f[choice](*args))
			print('\n')
		except NotFound as e:
			print(e.dsc)

	# Close!
	transport.close()


if __name__ == '__main__':
	try:
		main()
	except Thrift.TException as tx:
		print('%s' % tx.message)