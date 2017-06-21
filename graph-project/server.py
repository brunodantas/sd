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


class GraphHandler:
	def __init__(self):
		self.log = {}
		self.al = dict() #adjacency list
		self.lock = threading.Lock()
		self.rwlock = RWLock()
		# if os.path.isfile("graph.pickle"):
		# 	with open('graph.pickle', 'rb') as f:
		# 		self.al = pickle.load(f)
		# 	print("loaded data from graph.pickle")
		# else:
		# 	self.al = dict()
		# 	with open('graph.pickle', 'wb') as f:
		# 		pickle.dump(self.al,f)
		# 	print("created graph.pickle")


	def ping(self):
		print('ping()')

	def add_upd_vertex(self, nome, cor, desc, peso):
		self.rwlock.acquire_write()

		if nome not in self.al:
			self.al[nome] = Vertex(nome, cor, desc, peso)
			res = "vertice criado"
		else:
			self.al[nome].set_att(nome, cor, desc, peso)
			res = "vertice alterado"

		# with open('graph.pickle', 'wb') as f:
		# 	pickle.dump(self.al,f)
		self.rwlock.release()

		return res

	def add_upd_edge(self, v1, v2, peso, bi_flag):
		self.rwlock.acquire_write()

		if v1 not in self.al or v2 not in self.al:
			x = NotFound()
			x.dsc = "vertice não encontrado"
			self.rwlock.release()
			raise x

		ver1 = self.al[v1]
		ver2 = self.al[v2]
		if v2 not in ver1.edges_out:
			ver1.edges_out[v2] = Edge(v1, v2, peso, bi_flag)
			ver2.edges_in[v1] = ver1.edges_out[v2]
			res = "aresta criada"
		else:
			ver1.edges_out[v2].set_att(v1, v2, peso, bi_flag)
			res = "aresta alterada"
		if bi_flag:
				ver1.edges_in[v2] = ver1.edges_out[v2]
				ver2.edges_out[v1] = ver1.edges_out[v2]
		# with open('graph.pickle', 'wb') as f:
		# 		pickle.dump(self.al,f)

		self.rwlock.release()

		return res

	def get_vertex(self, v):
		self.rwlock.acquire_read()

		#time.sleep(5)
		if v not in self.al:
			x = NotFound()
			x.dsc = "vertice não encontrado"
			self.rwlock.release()
			raise x

		self.rwlock.release()
		return str(self.al[v])

	def get_edge(self, v1, v2):
		self.rwlock.acquire_read()

		if v1 not in self.al or v2 not in self.al or v2 not in self.al[v1].edges_out:
			x = NotFound()
			x.dsc = "aresta não encontrada"
			self.rwlock.release()
			raise x

		self.rwlock.release()
		return str(self.al[v1].edges_out[v2])

	def del_vertex(self, v):
		self.rwlock.acquire_read()

		if v not in self.al:
			x = NotFound()
			x.dsc = "vertice não encontrado"
			self.rwlock.release()
			raise x

		self.rwlock.release()
		self.rwlock.acquire_write()

		ver = self.al[v]
		outs = [x for x in ver.edges_out]
		ins = [x for x in ver.edges_in]
		for o in outs:
			try:
				self.del_edge(v,o)
			except:
				pass
		for i in ins:
			try:
				self.del_edge(i,v)
			except:
				pass
		del self.al[v]
		# with open('graph.pickle', 'wb') as f:
		# 		pickle.dump(self.al,f)

		self.rwlock.release()
		return "vertice deletado"

	def del_edge(self, v1, v2):
		self.rwlock.acquire_read()

		if v1 not in self.al or v2 not in self.al or v2 not in self.al[v1].edges_out:
			x = NotFound()
			x.dsc = "aresta não encontrada"
			self.rwlock.release()
			raise x

		self.rwlock.release()
		self.rwlock.acquire_write()

		bi = self.al[v1].edges_out[v2].bi_flag
		del self.al[v1].edges_out[v2]
		del self.al[v2].edges_in[v1]
		if bi:
			del self.al[v2].edges_out[v1]
			del self.al[v1].edges_in[v2]
		# with open('graph.pickle', 'wb') as f:
		# 		pickle.dump(self.al,f)

		self.rwlock.release()
		return "aresta deletada"

	def list_edges(self, v):
		self.rwlock.acquire_read()

		if v not in self.al:
			x = NotFound()
			x.dsc = "vertice não encontrado"
			self.rwlock.release()
			raise x

		self.rwlock.release()
		return str([self.al[v].edges_out[x] for x in self.al[v].edges_out])

	def list_vertices(self, v1, v2):
		self.rwlock.acquire_read()

		if v1 not in self.al or v2 not in self.al or v2 not in self.al[v1].edges_out:
			x = NotFound()
			x.dsc = "aresta não encontrada"
			self.rwlock.release()
			raise x

		self.rwlock.release()
		return str((self.al[v1], self.al[v2]))

	def list_neighbors(self, v):
		self.rwlock.acquire_read()

		if v not in self.al:
			x = NotFound()
			x.dsc = "vertice não encontrado"
			self.rwlock.release()
			raise x

		self.rwlock.release()
		return str([self.al[x] for x in self.al[v].edges_out])


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


if __name__ == '__main__':
    handler = GraphHandler()
    processor = Graph.Processor(handler)
    transport = TSocket.TServerSocket(port=9090)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TThreadedServer(processor, transport, tfactory, pfactory)

    # You could do one of these for a multithreaded server
    # server = TServer.TThreadedServer(
    #     processor, transport, tfactory, pfactory)
    # server = TServer.TThreadPoolServer(
    #     processor, transport, tfactory, pfactory)

    print('Starting the server...')
    server.serve()
    print('done.')
