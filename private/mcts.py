#coding=utf-8
import numpy as np
class Link:
	def __init__(self,up,rate,subtree=None):
		self.up=up
		self.cnt=0
		self.Quality=0
		self.rate=rate
		self.to=subtree
	@staticmethod
	def build(up,probilities):
		out=[]
		for p in probilities:
			out.append(Link(up,p))
		return out
class Node:
	def __init__(self,state,prev,value,rate,probilties):
		#self.rate=rate
		self.value=value
		self.prev=prev
		while prev is not None:
			prev.cnt+=1
			prev=prev.prev
			prev.childs.append(self)
		self.childs=[probilties]
		self.state=state
		pass
		self.cnt=1
		self.Quality=value 
	def updateQ(self):


def search(state,)