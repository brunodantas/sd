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

name_hash = lambda name: int(hashlib.md5(name.encode('utf-8')).hexdigest(),16) % 2**31
pessoa, filme, grupo, cast = 0, 1, 2, 3
cst = 0

try: input = raw_input
except NameError: pass

opt = "\n0 cadastrar pessoa (nome)\n1 cadastrar filme (título, cast)\n2 cadastrar grupo (nome)\n3 cadastrar avaliação (pessoa, filme, avaliação)\n4 adicionar pessoa a grupo (pessoa, grupo)\n5 filmes assistidos por (pessoa)\n6 filmes assistidos por (grupo)\n7 menor caminho entre (pessoa1, pessoa2)\n8 ver detalhes de (filme)\n\n\n"

def main():
	p = sys.argv[1]
	global client
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

	print("FILMEBOOK")

	options = {
		0: add_pessoa,
		1: add_filme,
		2: add_grupo,
		3: add_aval,
		4: pessoa_grupo,
		5: filmes_pessoa,
		6: filmes_grupo,
		7: caminho,
		8: filme_det
	}

	while 1:
		choice = input(opt)
		choice = int(choice)

		options[choice]()

	# Close!
	transport.close()


def add_pessoa():
	nome = input("digite o nome da pessoa\n")
	print(client.add_upd_vertex(name_hash(nome),pessoa,nome,0))

def add_grupo():
	nome = input("digite o nome do grupo\n")
	print(client.add_upd_vertex(name_hash(nome),grupo,nome,0))

def add_filme():
	nome = input("digite o nome do filme\n")
	client.add_upd_vertex(name_hash(nome),filme,nome,0)
	c = input("digite o cast do filme\n")
	client.add_upd_vertex(name_hash(c),cast,c,0)
	print(client.add_upd_edge(name_hash(nome),name_hash(c),cst,True))

def add_aval():
	nome = input("digite o nome do avaliador\n")
	try:
		v1 = eval(client.get_vertex(name_hash(nome)))
		if v1[1] != pessoa:
			raise NotFound
	except Exception as e:
		print("avaliador não encontrado\n")
		return
	f = input("digite o nome do filme\n")
	try:
		v2 = eval(client.get_vertex(name_hash(f)))
		if v2[1] != filme:
			raise NotFound
	except Exception as e:
		print("filme não encontrado\n")
		return
	nota = float(input("digite a nota\n"))
	print(client.add_upd_edge(v1[0],v2[0],nota,True))

def pessoa_grupo():
	nome = input("digite o nome da pessoa\n")
	try:
		v1 = eval(client.get_vertex(name_hash(nome)))
		if v1[1] != pessoa:
			raise NotFound
	except Exception as e:
		print("pessoa não encontrada")
		return
	g = input("digite o nome do grupo\n")
	try:
		v2 = eval(client.get_vertex(name_hash(g)))
		if v2[1] != grupo:
			raise NotFound
	except Exception as e:
		print("grupo não encontrado")
		return
	print(client.add_upd_edge(v2[0],v1[0],0,False))

def filmes_pessoa():
	nome = input("digite o nome da pessoa\n")
	try:
		neigh = eval(client.list_neighbors (name_hash(nome)))
	except Exception as e:
		print("pessoa não encontrada")
		return
	print(nome + " assistiu ")
	for i in neigh:
		try:
			print("\t" + eval(client.get_vertex(i))[2])
		except Exception as e:
			pass

def filmes_grupo():
	filmes = []
	nome = input("digite o nome do grupo\n")
	try:
		neigh = eval(client.list_neighbors (name_hash(nome)))
	except Exception as e:
		print("grupo não encontrado")
		return
	for i in neigh:
		try:
			p = eval(client.get_vertex(i))[0]
			fs = eval(client.list_neighbors(p))
			for f in fs:
				if f not in filmes:
					filmes.append(f)
		except Exception as e:
			pass
	print(nome + " assistiu ")
	for f in filmes:
		try:
			print("\t" + eval(client.get_vertex(f))[2])
		except Exception as e:
			pass

def caminho():
	try:
		nome = input("digite o nome da pessoa 1\n")
		v1 = eval(client.get_vertex(name_hash(nome)))
		if v1[1] != pessoa:
			raise NotFound

		nome2 = input("digite o nome da pessoa 2\n")
		v2 = eval(client.get_vertex(name_hash(nome2)))
		if v2[1] != pessoa:
			raise NotFound
	except Exception as e:
		print("pessoa não encontrada\n")
		return
	try:
		ls = eval(client.shortest_path(v1[0],v2[0]))
		print(ls)
		print("caminho:")
		for i in ls:
			print("\t" + eval(client.get_vertex(i))[2])
	except Exception as e:
		print("não existe caminho\n")
		return

def filme_det():
	nome = input("digite o nome do filme\n")
	try:
		neigh = eval(client.list_neighbors (name_hash(nome)))
	except Exception as e:
		print("filme não encontrado")
		return
	print("\nNome: " + nome + "\nCast: ")
	for i in neigh:
		try:
			c = eval(client.get_vertex(i))
			if c[1] == cast:
				print("\t" + c[2])
		except Exception as e:
			pass

if __name__ == '__main__':
	try:
		main()
	except Thrift.TException as tx:
		print('%s' % tx.message)
