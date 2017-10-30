#coding=utf-8
from input import MainDemo as Main
from actor import *
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
def normal(v):
	l = np.sqrt((v**2).sum())
	if l != 0.0:
		l = 1.0 / l
	return v * l
class Alive:
	def __init__(self, pos):
		self.pos = pos
		self.hurt = 0.0
		self.life = Value(10)
		self.power = Value(10)
		self.move = np.zeros(pos.shape)
	def move(self, aim):
		to = aim - self.pos
		to = normal(to)
		self.move = to
	