#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import glob
import sys
# import pickle
import os.path
import time
import threading
from rwlock.rwlock import RWLock
sys.path.append('gen-py')
sys.path.insert(0, glob.glob('./lib*')[0])
from graph import Graph
from graph.ttypes import NotFound

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
import hashlib
from pysyncobj import SyncObj
from pysyncobj.batteries import ReplCounter, ReplDict

class GraphHandler(SyncObj):
	def __init__(self, my_addr, partners_addrs):
		self.log = {}
		self.al = ReplDict() #adjacency list
		self.lock = threading.Lock()
		self.rwlock = RWLock()
		self.interfaces = dict() #for talking with other servers
		syncObj = SyncObj(my_addr, partners_addrs, consumers=[self.al])
		# if os.path.isfile("graph.pickle"):
		# 	with open('graph.pickle', 'rb') as f:
		# 		self.al = pickle.load(f)
		# 	print("loaded data from graph.pickle")
		# else:
		# 	self.al = dict()
		# 	with open('graph.pickle', 'wb') as f:
		# 		pickle.dump(self.al,f)
		# 	print("created graph.pickle")


	def init_interface(self, port):
		transport = TSocket.TSocket('localhost', port)
		# Buffering is critical. Raw sockets are very slow
		transport = TTransport.TBufferedTransport(transport)
		# Wrap in a protocol
		protocol = TBinaryProtocol.TBinaryProtocol(transport)
		# Create a client to use the protocol encoder
		client = Graph.Client(protocol)
		# Connect!
		transport.open()
		self.interfaces[port] = client
		

	def hash(self, vertex):
		h = hashlib.md5(str(vertex).encode('utf-8')).hexdigest()
		return int(h, 16) % cluster_qty


	def check_remote(self, vertex):
		cluster = self.hash(vertex)
		server = server_index
		if cluster != my_cluster:
			for i in range(total_replicas):
				server = self.check_replica(i,cluster)
				if server != -1:
					return server
			if server == -1:
				print("error requesting cluster{}".format(cluster))
				x = NotFound()
				x.dsc = "falha no servidor"
				raise x
		return server


	def check_replica(self,replica,cluster):
		server = get_server_port(cluster,replica)
		try:
			if server not in self.interfaces:
				self.init_interface(server)
			self.interfaces[server].ping()
		except Exception as e:
			print("server{} from cluster{} is unreachable".format(server%1000,cluster))
			server = -1
		return server


	def ping(self):
		print('ping()')


	def add_upd_vertex(self, nome, cor, desc, peso):
		server = self.check_remote(nome)
		if server != server_index:
			print("add/update vertex {}: requesting server{}".format(nome,server))
			res = self.interfaces[server].add_upd_vertex(nome, cor, desc, peso)
			print(res)
			return res

		print("add/update vertex {}".format(nome))
		self.rwlock.acquire_write()

		if nome not in self.al:
			self.al.set(nome,Vertex(nome, cor, desc, peso),sync=True)
			res = "vertice {} criado".format(nome)
		else:
			self.al.set(nome,Vertex(nome, cor, desc, peso),sync=True)
			res = "vertice {} alterado".format(nome)

		# with open('graph.pickle', 'wb') as f:
		# 	pickle.dump(self.al,f)
		self.rwlock.release()

		print(res)
		return res

	def add_upd_edge(self, v1, v2, peso, bi_flag):
		try:
			self.get_vertex(v1)
			self.get_vertex(v2)
		except Exception as e:
			print(str(e))
			raise e
		res = self.add_upd_edge2(v1, v2, peso, bi_flag)
		self.add_edge_in(v1, v2, peso, bi_flag)
		if bi_flag:
			self.add_upd_edge2(v2, v1, peso, bi_flag)
			self.add_edge_in(v2, v1, peso, bi_flag)
		return res


	def add_upd_edge2(self, v1, v2, peso, bi_flag):
		server = self.check_remote(v1)
		if server != server_index:
			print("add/update edge {},{}: requesting server{}".format(v1,v2,server))
			res = self.interfaces[server].add_upd_edge2(v1, v2, peso, bi_flag)
			print(res)
			return res

		print("add/update edge {},{}".format(v1,v2))

		self.rwlock.acquire_write()
		ver1 = self.al[v1]
		if v2 not in ver1.edges_out:
			ver1.edges_out[v2] = Edge(v1, v2, peso, bi_flag)
			self.al.set(v1,ver1,sync=True)
			self.rwlock.release()
			res = "aresta {},{} criada".format(v1,v2)
		else:
			ver1.edges_out[v2].set_att(v1, v2, peso, bi_flag)
			self.al.set(v1,ver1,sync=True)
			self.rwlock.release()
			res = "aresta {},{} alterada".format(v1,v2)
		# if bi_flag:
		# 	print(ver1.edges_out[v2])
		# 	self.rwlock.acquire_write()
		# 	ver1.edges_in[v2] = ver1.edges_out[v2]
		# 	self.rwlock.release()
		# 	self.add_edge_bi(v1, v2, peso, bi_flag)

		# with open('graph.pickle', 'wb') as f:
		# 		pickle.dump(self.al,f)

		print(res)
		return res

	
	def add_edge_in(self, v1, v2, peso, bi_flag):
		server = self.check_remote(v2)
		if server != server_index:
			print("edge_in {},{}: requesting server{}".format(v1,v2,server))
			res = self.interfaces[server].add_edge_in(v1, v2, peso, bi_flag)
			return res
		print("edge_in {},{}".format(v1,v2))
		self.rwlock.acquire_write()
		ver2 = self.al[v2]
		ver2.edges_in[v1] = Edge(v1, v2, peso, bi_flag)
		self.al.set(v2,ver2,sync=True)
		self.rwlock.release()
		return "ok"


	def get_vertex(self, v):
		server = self.check_remote(v)
		if server != server_index:
			print("get vertex {}: requesting server{}".format(v,server))
			res = self.interfaces[server].get_vertex(v)
			print(res)
			return res

		print("get vertex {}".format(v))
		self.rwlock.acquire_read()

		#time.sleep(5)
		if v not in self.al:
			x = NotFound()
			x.dsc = "vertice não encontrado"
			self.rwlock.release()
			print(x.dsc)
			raise x
		res = str(self.al[v])
		self.rwlock.release()
		print(res)
		return res

	def get_edge(self, v1, v2):
		server = self.check_remote(v1)
		if server != server_index:
			print("get edge {},{}: requesting server{}".format(v1,v2,server))
			res = self.interfaces[server].get_edge(v1,v2)
			print(res)
			return res

		print("get edge {},{}".format(v1,v2))
		self.rwlock.acquire_read()

		if v1 not in self.al or v2 not in self.al[v1].edges_out:
			x = NotFound()
			x.dsc = "aresta não encontrada"
			self.rwlock.release()
			print(str(x))
			raise x
		res = str(self.al[v1].edges_out[v2])
		self.rwlock.release()
		print(res)
		return res


	def del_vertex(self, v):
		try:
			edges_out = eval( self.list_neighbors(v))
			edges_in = eval( self.list_neighbors_in(v))
		except Exception as e:
			print(str(e))
			raise e

		for v2 in edges_out:
			try: self.del_edge2(v,v2)
			except: pass
			try: self.del_edge_in(v,v2)
			except: pass
		for v2 in edges_in:
			try: self.del_edge2(v2,v)
			except: pass
			try: self.del_edge_in(v2,v)
			except: pass

		res = self.del_vertex2(v)
		return res


	def del_vertex2(self, v):
		server = self.check_remote(v)
		if server != server_index:
			print("delete vertex {}: requesting server{}".format(v,server))
			res = self.interfaces[server].del_vertex(v)
			print(res)
			return res

		print("delete vertex {}".format(v))
		self.rwlock.acquire_read()

		if v not in self.al:
			x = NotFound()
			x.dsc = "vertice não encontrado"
			self.rwlock.release()
			raise x

		self.rwlock.release()
		self.rwlock.acquire_write()

		self.al.pop(v,sync=True)
		# with open('graph.pickle', 'wb') as f:
		# 		pickle.dump(self.al,f)

		self.rwlock.release()
		res = "vertice {} deletado".format(v)
		print(res)
		return res


	def del_edge(self, v1, v2):
		try:
			bi_flag = eval( self.get_edge(v1,v2) + "[-1]")
			res = self.del_edge2(v1, v2)
		except Exception as e:
			print(str(e))
			raise e

		try:
			self.del_edge_in(v1, v2)
			if bi_flag:
				print("delete edge {},{} (bidirectional)".format(v2,v1))
				self.del_edge2(v2, v1)
				self.del_edge_in(v2, v1)
		except: pass

		return res


	def del_edge2(self, v1, v2):
		server = self.check_remote(v1)
		if server != server_index:
			print("delete edge {},{}: requesting server{}".format(v1,v2,server))
			res = self.interfaces[server].del_edge2(v1,v2)
			print(res)
			return res

		print("delete edge {},{}".format(v1,v2))
		self.rwlock.acquire_read()

		if v1 not in self.al or v2 not in self.al[v1].edges_out:
			x = NotFound()
			x.dsc = "aresta não encontrada"
			self.rwlock.release()
			raise x

		self.rwlock.release()
		self.rwlock.acquire_write()

		ver1 = self.al[v1]
		ver1.edges_out.pop(v2,None)
		self.al.set(v1,ver1,sync=True)
		# with open('graph.pickle', 'wb') as f:
		# 		pickle.dump(self.al,f)

		self.rwlock.release()
		res = "aresta {},{} deletada".format(v1,v2)
		print(res)
		return res


	def del_edge_in(self, v1, v2):
		server = self.check_remote(v2)
		if server != server_index:
			print("del edge_in {},{}: requesting server{}".format(v1,v2,server))
			res = self.interfaces[server].del_edge_in(v1, v2)
			return res
		print("edge_in {},{}".format(v1,v2))
		self.rwlock.acquire_write()
		ver2 = self.al[v2]
		ver2.edges_in.pop(v1,None)
		self.al.set(v2,ver2,sync=True)
		self.rwlock.release()
		return "ok"

	def list_edges(self, v):
		server = self.check_remote(v)
		if server != server_index:
			print("list edges from vertex {}: requesting server{}".format(v,server))
			res = self.interfaces[server].list_edges(v)
			print(res)
			return res

		print("list edges from vertex {}".format(v))
		self.rwlock.acquire_read()

		if v not in self.al:
			x = NotFound()
			x.dsc = "vertice não encontrado"
			self.rwlock.release()
			raise x

		res = str([self.al[v].edges_out[x] for x in self.al[v].edges_out])
		self.rwlock.release()
		print(res)
		return res

	def list_vertices(self, v1, v2):
		server = self.check_remote(v1)
		if server != server_index:
			print("list vertices of edge {},{}: requesting server{}".format(v1,v2,server))
			self.interfaces[server].get_edge(v1,v2)
			res = [self.interfaces[server].get_vertex(v1)]
		else:
			print("list vertices of edge {},{}".format(v1,v2))
			self.rwlock.acquire_read()
			self.get_edge(v1,v2)
			res = [self.get_vertex(v1)]
			self.rwlock.release()

		server = self.check_remote(v2)
		if server != server_index:
			res.append(self.interfaces[server].get_vertex(v2))
		else:
			self.rwlock.acquire_read()
			res.append(self.get_vertex(v2))
			self.rwlock.release()

		print(res)
		return str(res)

	def list_neighbors(self, v):
		server = self.check_remote(v)
		if server != server_index:
			print("list neighbors of vertex {}: requesting server{}".format(v,server))
			res = self.interfaces[server].list_neighbors(v)
			print(res)
			return res

		print("list neighbors of vertex {}".format(v))
		self.rwlock.acquire_read()

		if v not in self.al:
			x = NotFound()
			x.dsc = "vertice não encontrado"
			self.rwlock.release()
			raise x

		res = str([x for x in self.al[v].edges_out])
		self.rwlock.release()
		print(res)
		return res

	def list_neighbors_in(self,v):
		server = self.check_remote(v)
		if server != server_index:
			print("list neighbors_in of vertex {}: requesting server{}".format(v,server))
			res = self.interfaces[server].list_neighbors_in(v)
			print(res)
			return res

		print("list neighbors_in of vertex {}".format(v))
		self.rwlock.acquire_read()

		if v not in self.al:
			x = NotFound()
			x.dsc = "vertice não encontrado"
			self.rwlock.release()
			raise x

		res = str([x for x in self.al[v].edges_in])
		self.rwlock.release()
		print(res)
		return res

	#dijkstra
	def shortest_path(self,v1,v2):
		Q = [v1]
		dist = dict()
		prev = dict()
		visited = dict()
		dist[v1] = 0

		while Q != []:
			u = Q.pop(0)
			visited[u] = 1
			neighbors = eval(self.list_neighbors(u))
			for n in neighbors:
				edge = eval(self.get_edge(u,n))
				length = edge[2]
				alt = dist[u] + length
				if n not in dist or alt < dist[n]:
					dist[n] = alt
					prev[n] = u
				if n not in visited:
					Q.append(n)
					Q.sort()

		if(v2 not in dist):
			res = "nao existe caminho entre {} e {}".format(v1,v2)
		else:
			u = v2
			path = []
			while u != v1:
				path.append(u)
				u = prev[u]
			path.append(v1)
			res = "menor caminho: {}\ndistancia total: {}".format(path[::-1],dist[v2])
		print(res)
		return res






class Vertex:
	def __init__(self, nome, cor, desc, peso):
		self.set_att(nome, cor, desc, peso)
		self.edges_out = dict()
		self.edges_in = dict()

	def __str__(self):
		return "(%d, %d, %s, %s)" % (self.nome, self.cor, self.desc, self.peso)

	__repr__ = __str__

	def set_att(self, nome, cor, desc, peso):
		self.nome = nome
		self.cor = cor
		self.desc = desc
		self.peso = peso


class Edge:
	def __init__(self, v1, v2, peso, bi_flag):
		self.set_att(v1, v2, peso, bi_flag)

	def __str__(self):
		return "(%d, %d, %s, %s)" % (self.v1, self.v2, self.peso, self.bi_flag)

	__repr__ = __str__

	def set_att(self, v1, v2, peso, bi_flag):
		self.v1 = v1
		self.v2 = v2
		self.peso = peso
		self.bi_flag = bi_flag

get_port = lambda cluster,server: 2000 + 1000 * cluster + server
get_server_port = lambda cluster,replica: 9000 + total_replicas * cluster + replica

if __name__ == '__main__':
	global server_index
	global my_cluster
	global cluster_qty #replicated clusters
	global total_replicas
	total_replicas = 3
	server_index = int(sys.argv[1])
	cluster_qty = int(sys.argv[2])
	my_cluster = server_index // total_replicas

	#replication:
	my_port = get_port(my_cluster,server_index % total_replicas)
	partners = ['localhost:%d' % get_port(my_cluster, p) for p in range(total_replicas) if get_port(my_cluster,p) != my_port]
	handler = GraphHandler('localhost:%d'%my_port, partners)
	print('Replication on cluster {} via port {} with partners {}'.format(my_cluster,my_port,partners))

	#server:
	server_port = 9000 + server_index
	processor = Graph.Processor(handler)
	transport = TSocket.TServerSocket(port=server_port)
	tfactory = TTransport.TBufferedTransportFactory()
	pfactory = TBinaryProtocol.TBinaryProtocolFactory()

	server = TServer.TThreadedServer(processor, transport, tfactory, pfactory)

	# You could do one of these for a multithreaded server
	# server = TServer.TThreadedServer(
	#     processor, transport, tfactory, pfactory)
	# server = TServer.TThreadPoolServer(
	#     processor, transport, tfactory, pfactory)

	print('Starting server on port {}...'.format(server_port))
	server.serve()
	print('done.')
