n=6
alpha,belta=0.7,0.3
forget=0.1
update_ant=5.0
nodes=[]
pathmx=[
[0, 1, 3, 2, 4, 100],
[2, 0, 5, 0, 7, 9],
[7, 4, 0, 1, 4, 6],
[5, 7, 6, 0, 3, 7],
[3, 5, 6, 7, 0, 5],
[1, 0, 2, 1, 2, 0],
]
def matrix(size):
	global n
	n=size
	global pathmx 
	import numpy as np
	pathmx=np.random.rand(size,size)
	for i in xrange(n):
		pathmx[i][i]=0;
class Node:
	def __init__(self,cost):
		self.adv=1.0
		self.cost=cost
	def fin(self):
		return alpha*self.adv+belta/self.cost
	def update(self,adv):
		self.adv=(1-forget)*self.adv+adv
def init():
	for i in xrange(n):
		nodes.append({})
	for fromid in xrange(n):
		path=pathmx[fromid]
		for toid in xrange(n):
			if path[toid]>0:
				nodes[fromid][toid]=Node(path[toid])
def initmx(size):
	matrix(size)
	init()
def show_adv():
	for i in xrange(n):
		for j in xrange(n):
			if j in nodes[i]:
				print "%.3f"%(nodes[i][j].adv,),
			else:
				print "None ",
		print ""

def show_cost():
	for i in xrange(n):
		for j in xrange(n):
			if j in nodes[i]:
				print "%.3f"%(nodes[i][j].cost,),
			else:
				print "None ",
		print ""
import random
class Ant:
	def __init__(self,node=0):
		self.forbid=[node]
		self.node=node
		self.cost=0
		self.passed=False
	def move(self):
		if self.node==n-1:
			self.passed=True
			return False;
		node=nodes[self.node]
		total=0
		for i in node:
			if i in self.forbid:continue;
			total+=node[i].fin()
		if total==0:return False;
		chs=random.random()*total
		for i in node:
			if i in self.forbid:continue;
			chs-=node[i].fin()
			if chs<=0:
				chs=i
				break
		self.node=chs
		self.cost+=node[chs].cost
		self.forbid.append(self.node)
		return True;
	def adv(self):
		cost=self.cost
		if self.passed:
			cost*=0.125
		return update_ant/(cost)
	def has(self,i,j):
		f=self.forbid
		if i == f[-1]:return False;
		if i in f:
			id=f.index(i)
			return f[id+1]==j;
		else:
			return False;
def Ants(ants):
	out=[]
	for i in xrange(ants):
		out.append(Ant())
	return out
from time import time 
def cal(maxloop,nants):
	mini=None
	start=time()
	for i in xrange(maxloop):
		ants=Ants(nants)
		#print "start ant move"
		for ant in ants:
			while ant.move():pass;
		#print "start adv update"
		tmini=None
		for j in xrange(n):
			for k in nodes[j]:
			#for k in xrange(n):
				adv=0
				for ant in ants:
					if ant.has(j,k):
						adv+=ant.adv()
				#if k in nodes[j]:
				nodes[j][k].update(adv)
		#print "start mini update"
		for ant in ants:
			if ant.passed:
				if tmini is None or tmini.cost>ant.cost:
					tmini=ant
		#if tmini is not None:
		#	print "loop",i,"mini path:",tmini.forbid,tmini.cost
		# print i,",",
		# if tmini is not None:
		# 	print "%.3f"%(tmini.cost,),",",
		# else:
		# 	print "None,",
		if mini is None or mini.cost>tmini.cost:
			mini=tmini
			print "loop",i,"update mini",mini.cost
	print "";
	print "mini:",mini.forbid,mini.cost
	print "time cost:",time()-start
	return mini
def cost(path):
	l=len(path);
	cost=0
	for i in xrange(l-1):
		f,t=path[i],path[i+1]
		cost+=nodes[f][t].cost
	return cost
"""
n=6
alpha,belta=0.7,0.5
forget=0.3
update_ant=5.0
nodes=[]
pathmx=[
[0, 1, 3, 2, 4, 100],
[2, 0, 5, 0, 7, 9],
[7, 4, 0, 1, 4, 6],
[5, 7, 6, 0, 3, 7],
[3, 5, 6, 7, 0, 5],
[1, 0, 2, 1, 2, 0],
]
paths=[(1,2,3)]
def init():
	for i in xrange(n):
		nodes.append(Node())
	for fromid in xrange(n):
		path=pathmx[fromid]
		for toid in xrange(n):
			if path[toid]>0:
				nodes[fromid].to[toid]=path[toid]

class Node:
	def __init__(self):
		self.adv=1.0
		self.to={}
	def fin(self,to):
		return alpha*nodes[to].adv+belta/self.to[to]
	def update(self,adv):
		self.adv=(1-forget)*self.adv+adv
import random
class Ant:
	def __init__(self,node=0):
		self.forbid=[node]
		self.node=node
		self.cost=0
		self.passed=False
	def move(self):
		if self.node==n-1:
			self.passed=True
			return False;
		node=nodes[self.node]
		total=0
		for i in node.to:
			if i in self.forbid:continue;
			total+=node.fin(i)
		if total==0:return False;
		chs=random.random()*total
		for i in node.to:
			if i in self.forbid:continue;
			chs-=node.fin(i)
			if chs<=0:
				chs=i
				break
		self.node=chs
		self.cost+=node.to[chs]
		self.forbid.append(self.node)
		return True;
	def adv(self):
		cost=self.cost
		if self.passed:
			cost*=0.125
		return update_ant/(cost+1)
def Ants(ants):
	out=[]
	for i in xrange(ants):
		out.append(Ant())
	return out
def cal(maxloop,nants):
	mini=None
	for i in xrange(maxloop):
		ants=Ants(nants)
		for ant in ants:
			while ant.move():pass;
		tmini=None
		for j in xrange(n):
			adv=0
			for ant in ants:
				if j in ant.forbid:
					adv+=ant.adv()
			nodes[j].update(adv)
		for ant in ants:
			if ant.passed:
				if tmini is None or tmini.cost>ant.cost:
					tmini=ant
		if tmini is not None:
			print "loop",i,"mini path:",tmini.forbid,tmini.cost
		if mini is None or mini.cost>tmini.cost:
			mini=tmini
			print "loop",i,"update mini"
	return mini
"""