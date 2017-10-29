#coding=utf-8
from input import MainDemo as Main
import numpy as np
class Demo(Main):
	def __init__(self):
		Main.__init__(self,1.0)
		self.cnt = 0
	def init(self):
		print "program start to run"
	def finish(self):
		print "cleaning..."
	def update(self,gets):
		if gets == "exit":
			self.stop()
		if gets == "-":
			self.cnt-=1
		elif gets == "+":
			self.cnt+=1
		print "Count:", self.cnt
class Food:
	pass
class Value(object):
	def __init__(self,max):
		self._max=max*1.0
		self._curr=max*1.0
	def __call__(self, val = None):
		if val is None:
			return self._curr
		else:
			self._curr = val*1.0
	def rate():
		return self._curr/self._max
	def max(self, val = None):
		if val is None:
			return self._max
		else:
			self._max = val*1.0
	def full(self):
		return self._max
class Alive:
	def __init__(self,pos):
		self.pos = pos
		self.hurt = 0.0
		self.life = Value(10)
		self.power = Value(10)
		self.move = np.zeros(2)
	