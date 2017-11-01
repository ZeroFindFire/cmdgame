#coding=utf-8
from setting import *
from random import random
import numpy as np
class Space(object):
	ID = 0
	def __init__(self, up, size, pos, chds = 0):
		self.up = up
		self.pos =  pos
		self.size = size
		self.chds = []
		self.id = Space.ID
		Space.ID+=1
		self.objs = []
		if size < 20:return;
		for i in xrange(int(chds*0.3)):
			spc = Space(self, max(random()*0.1*size,10),np.random.rand(2),int(random() * chds / 2))
			self.chds.append(spc)
	def state(self):
		s = []
		for spc in self.chds:
			ps = spc.pos * self.size
			s.append( "空间%d位于(%f,%f)处，占地%fx%f"%(spc.id,ps[0],ps[1],spc.size,spc.size))
		return s
class Alive(object):
	def __init__(self, spc, pos, v, name = ''):
		self.spc = spc
		self.pos = np.asarray(pos,dtype = np.float64)
		self.v = v
		self.move = np.zeros(2)
		self.name = name
	def update(self):
		self.pos += 1.0 * self.move * self.v / self.spc.size
	def state(self):
		s = self.name + "在空间"+str(self.spc.id)+"里，坐标为"+str(self.pos*self.spc.size)
		if (self.move**2).sum()!=0:
			s+="，正在向"+str(self.move)+"方向移动"
		return s
class RunDemo(SettingDemo):
	def __init__(self,*args):
		SettingDemo.__init__(self,*args)
		self.cnt = 0
		self.space = Space(None, 1000, None, 2**7)
		self.player = Alive(self.space, np.array([0,0]),5.0,"你")
	def move(self,gets):
		p = self.player
		if gets == 'a':
			p.move = np.array([-1,0])
		elif gets == 'd':
			p.move = np.array([1,0])
		elif gets == 'w':
			p.move = np.array([0,1])
		elif gets == 's':
			p.move = np.array([0,-1])
		elif gets == 'p':
			p.move = np.zeros(2)
	def update_run(self,gets):
		self.move(gets)
		self.auto_continue(True)
		self.readline(False)
		s = []
		if gets == "e":
			self.stop()
		elif gets == "-":
			self.cnt-=1
		elif gets == "set":
			self.push(self.update_setting,False,True)
			return
		elif gets == "+":
			self.cnt+=1
		elif gets == "r":
			self.pop()
			return;
		elif gets == 'x':
			s = self.space.state()
			self.auto_continue(False)
			self.readline(True)
		elif gets == ":":
			self.auto_continue(False)
			self.readline(True)

		self.player.update()
		s = [self.player.state()]+s
		show(s,step = 0)
		#show("计数: "+str(self.cnt),step = 0)
