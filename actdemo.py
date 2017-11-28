#coding=utf-8
import numpy as np 
from zmath import *
from algorithm import *
class SObj(object):
	manage_maps = ['pos','abspos','up','spc','space']
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
			return object.__getattribute__(self,name)
		if name == 'abspos':
			return self.__pos * self.spc.size
		return self.__pos
	@staticmethod
	def chk_range(pos):
		return np.maximum(np.minimum(pos,1),-1)

class Space(SObj):
	ID = 0
	def __abspos(self,pos):
		return pos * self.size
	def __init__(self, up, size, pos, chds = 0, pos_up = None):
		if pos_up is None:
			pos_up = vec_empty()
		self.up_pos = self.chk_range(pos_up)
		SObj.__init__(self,up,pos)
		self.size = size
		self.chds = []
		self.spc_map = {}
		if up is not None:
			self.spc_map[up.id]=up
		self.id = Space.ID
		Space.ID+=1
		self.objs = []
		if size < 20:return;
		for i in xrange(int(chds*0.1)):
			spc = Space(self, max(random()*0.1*size,10),vec_rand(),int(random() * chds / 2))
			self.chds.append(spc)
			self.spc_map[spc.id]=spc
	def state(self):
		s = []
		for spc in self.chds:
			ps = spc.abspos
			s.append( "空间%d位于(%.2f,%.2f)处，占地%.3fx%.3f"%(spc.id,ps[0],ps[1],spc.size,spc.size))
		if self.spc is not None:
			spc = self.spc 
			ps = self.__abspos(self.up_pos)
			s.append( "母空间%d位于(%.2f,%.2f)处，占地%.3fx%.3f"%(spc.id,ps[0],ps[1],spc.size,spc.size))
		for obj in self.objs:
			s.append(obj.state())
		return s
	def near(self,obj,dst):
		spcs = []
		objs = []
		crr = obj
		pos = obj.abspos
		for spc in self.chds:
			ps = spc.abspos
			if np.sqrt(((ps-pos)**2).sum())<dst:
				spcs.append(spc)
		for obj in self.objs:
			if obj == crr:continue;
			ps = obj.abspos
			if np.sqrt(((ps-pos)**2).sum())<dst:
				objs.append(obj)
		return (objs,spcs)

	def update(self,sec):
		for obj in self.objs:
			obj.update(sec)
		for spc in self.chds:
			spc.update(sec)
	def insert(self,obj):
		self.objs.append(obj)
	def space(self,id):
		if self.spc_map.has_key(id) ==False:
			return None
		return self.spc_map[id]
	def apply(self,obj,spc):
		obj_ps = obj.abspos
		if spc == self.spc:
			spc_ps = self.__abspos(self.up_pos)
		else:
			spc_ps = spc.abspos
		dst = sqrdst(obj_ps - spc_ps)
		return dst < 5**2
def strvec(vec):
	s = "("
	for v in vec:
		s+="%.2f"%v
		s+=", "
	s = s[:-2]+")"
	return s

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
	def __init__(self,*args):
		SObj.__init__(self,*args)
		self.spcs = []
		self.objs = []
	nspcs = 10
	nobjs = 10
	# objs初始为空
	# 每次update，清除已经远离的obj，随机概率清除obj
	lv_dst = 100.0**3
	lv_rate = 0.1
	is_rate = 0.5
	def lnk(self,obj):
		if obj in self.objs:return;
		self.objs.append(obj)
		obj.objs.append(self)
	def unlnk(self,obj):
		if not obj in self.objs:return;
		self.objs.remove(obj)
		obj.objs.remove(self)
	def __prev_update(self):
		for obj in self.objs:
			if sqrdst(self.pos - obj.pos) > self.lv_dst**2 or random()<self.lv_rate:
				self.unlnk(obj)
		for spc in self.spcs:
			if sqrdst(self.pos - spc.pos) > self.lv_dst**2 or random()<self.lv_rate:
				self.spcs.remove(spc)
	def update_lnk(self, objs, spcs ):
		pr = PosPrior(self)
		objs = zsort(objs, pr)
		spcs = zsort(spcs, pr)
		self.__prev_update()
		n = self.nobjs - len(self.objs)
		i = 0 
		l = len(objs)
		while n > 0 and i < l and n > (l - i):
			if random()>self.is_rate and not objs[i] in self.objs:
				self.lnk(objs[i])
				n-=1
			i+=1
		for obj in objs:
			if n == 0 :break
			if not obj in self.objs:
				self.lnk(obj)
				n-=1
		n = self.nspcs - len(self.spcs)
		i = 0 
		l = len(spcs)
		while n > 0 and i < l and n > (l - i):
			if random()>self.is_rate and not spcs[i] in self.spcs:
				self.spcs.append(spcs[i])
				n-=1
			i+=1
		for spc in spcs:
			if n == 0 :break
			if not spc in self.spcs:
				self.spcs.append(spc)
				n-=1
		self.objs = zsort(self.objs,pr)
		self.spcs = zsort(self.spcs,pr)
class Alive(LinkObj):
	def __init__(self, spc, pos, v, name = ''):
		LinkObj.__init__(self,spc,pos)
		self.v = v
		self.move = vec_empty()
		self.name = name
		self.clock = 0
	def to_space(self,spc):
		self.spc.objs.remove(self)
		self.spc = spc
		spc.objs.append(self)
		self.pos = self.spc.up_pos

	def update(self,sec):
		objs,spcs = self.spc.near(self,self.lv_dst)
		self.update_lnk(objs,spcs)
		if self.name != "你":
			self.clock += sec
			if self.clock > 10:
				self.move = normal(vec_rand()-0.5)
				self.clock = 0
		self.pos += 1.0 * sec * self.move * self.v / self.spc.size
	def state(self):
		s = self.name + "在空间" + str(self.spc.id)+"里，坐标为"+strvec(self.pos * self.spc.size)
		if (self.move**2).sum()!=0:
			s+="，正在向"+strvec(self.move)+"方向移动"
		return s
	def view(self):
		s = []
		for spc in self.spcs:
			ps = spc.abspos
			s.append( "空间%d位于(%.2f,%.2f)处，占地%.2fx%.2f"%(spc.id,ps[0],ps[1],spc.size,spc.size))
		for obj in self.objs:
			s.append(obj.state())
		return s