#coding=utf-8
from setting import *
from random import random
import numpy as np
def f(flt,p=2):
	sp = "%."+str(p)+"f"
	return sp % flt
class SObj(object):
	def __init__(self,up,pos):
		self.__pos = np.asarray(pos,dtype = np.float64)
		self.spc = up
	def __setattr__(self,name,data):
		if name != 'pos' and name != 'abspos':
			object.__setattr__(self,name,data)
			return
		if name == 'abspos':
			data /= self.spc.size
		ps = np.maximum(np.minimum(data,1),-1)
		self.__pos = ps
	def __getattr__(self,name):
		if name != 'pos' and name != 'abspos':
			return object.__getattr__(self,name,data)
		if name == 'abspos':
			return self.__pos * self.spc.size
		return self.__pos

class Space(SObj):
	ID = 0
	def __init__(self, up, size, pos, chds = 0):
		SObj.__init__(self,up,size)
		self.size = size
		self.chds = []
		self.id = Space.ID
		Space.ID+=1
		self.objs = []
		if size < 20:return;
		for i in xrange(int(chds*0.1)):
			spc = Space(self, max(random()*0.1*size,10),np.random.rand(2),int(random() * chds / 2))
			self.chds.append(spc)
	def state(self):
		s = []
		for spc in self.chds:
			ps = spc.__pos * self.size
			s.append( "空间%d位于(%.2f,%.2f)处，占地%.3fx%.3f"%(spc.id,ps[0],ps[1],spc.size,spc.size))
		for obj in self.objs:
			s.append(obj.state())
		return s
	def near(self,obj,dst):
		s = []
		pos = obj.abspos
		for spc in self.chds:
			ps = spc.abspos
			if np.sqrt(((ps-pos)**2).sum())<dst:
				s.append( "空间%d位于(%.2f,%.2f)处，占地%.3fx%.3f"%(spc.id,ps[0],ps[1],spc.size,spc.size))
		for obj in self.objs:
			ps = obj.abspos
			if np.sqrt(((ps-pos)**2).sum())<dst:
				s.append(obj.state())
		return s

	def update(self,sec):
		for obj in self.objs:
			obj.update(sec)
		for spc in self.chds:
			spc.update(sec)
	def insert(self,obj):
		self.objs.append(obj)
def normal(vc):
	l = np.sqrt((vc**2).sum())
	if l != 0.0:
		l = 1.0 / l
	return vc*l
def strvec(vec):
	s = "("
	for v in vec:
		s+="%.2f"%v
		s+=", "
	s = s[:-2]+")"
	return s
def zsort(datas, prior):
	l = len(datas)
	for i in xrange(l):
		id = i 
		for j in xrange(i,l):
			if prior(datas[j],datas[id]):
				id = j 
		if id != i:
			tmp = datas[id]
			datas[id] = datas[i]
			datas[i] = tmp
	return datas 
class PosPrior:
	def __init__(self,obj):
		self.pos = obj.pos
	def __call__(self,a,b):
		pa = a.pos
		pb = b.pos 
		la = ((self.pos - pa) ** 2).sum()
		lb = ((self.pos - pb) ** 2).sum()
		return la <= lb
class LinkObj(SObj):
	#self.nspcs,nobjs = 10
	nspcs = 10
	nobjs = 10
	def update_lnk(self, objs, spcs ):
		pr = PosPrior(self)
		objs = zsort(objs, pr)
		spcs = zsort(spcs, pr)
		n = self.nobjs - len(self.objs):
		i = 0 
		l = len(objs)
		while n > 0 and i < l and n > (l - i):
			if random()>0.5 and not objs[i] in self.objs:
				self.objs.append(objs[i])
				n-=1
			i+=1
		for obj in objs:
			if n == 0 :break
			if not obj in self.objs:
				self.objs.append(obj)
				n-=1
		n = self.nspcs
		i = 0 
		l = len(spcs)
		while n > 0 and i < l and n > (l - i):
			if random()>0.5 and not spcs[i] in self.spcs:
				self.spcs.append(spcs[i])
				n-=1
			i+=1
		for spc in spcs:
			if n == 0 :break
			if not spc in self.spcs:
				self.spcs.append(spc)
				n-=1
class Alive(LinkObj):
	def __init__(self, spc, pos, v, name = ''):
		SObj.__init__(self,spc,pos)
		self.v = v
		self.move = np.zeros(2)
		self.name = name
		self.clock = 0
	def update(self,sec):
		if self.name != "你":
			self.clock += sec
			if self.clock > 10:
				self.move = normal(np.random.rand(2))
				self.clock = 0
		self.__pos += 1.0 * sec * self.move * self.v / self.spc.size
	def state(self):
		s = self.name + "在空间"+str(self.spc.id)+"里，坐标为"+strvec(self.pos * self.spc.size)
		if (self.move**2).sum()!=0:
			s+="，正在向"+strvec(self.move)+"方向移动"
		return s
class RunDemo(SettingDemo):
	def __init__(self,*args):
		SettingDemo.__init__(self,*args)
		self.cnt = 0
		self.space = Space(None, 1000, None, 2**5)
		self.player = Alive(self.space, np.array([0,0]),5.0,"你")
		for i in xrange(10):
			self.space.insert(Alive(self.space, np.random.rand(2),5.0,"robot"+str(i)))
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
		s = self.space.near(self.player,100)
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
		self.space.update(self.wait_time())
		self.player.update(self.wait_time())
		s = [self.player.state()]+s
		show(s,step = 0)
		#show("计数: "+str(self.cnt),step = 0)
