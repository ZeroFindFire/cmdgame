#coding=utf-8
from setting import *
from random import random
import numpy as np
from zmath import *
from algorithm import *
from order import *
def f(flt,p=2):
	sp = "%."+str(p)+"f"
	return sp % flt
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
class RDExcept(Exception):
	pass
class StrShow(object):
	def __init__(self):
		self.__s = []
		pass
	def cls(self):
		self.__s = []
	def insert(self,cts):
		if isinstance(cts,list):
			self.__s+=cts
		else:
			self.__s.append(cts)
	def write(self,rd ):
		s = self.__s 
		show(s, step = 0, clean = True,rd=rd)
	def __call__(self,*args ):
		self.write(*args )
	def set(self,cts):
		self.cls()
		self.insert(cts)
class RunDemo(SettingDemo):
	def __init__(self,*args):
		self.play_cnt = 0
		SettingDemo.__init__(self,*args)
		self.cnt = 0
		self.__enter = True
		self.space = Space(None, 1000, None, 2**5)
		self.player = Alive(self.space, vec_empty(),5.0,"你")
		self.space.insert(self.player)
		for i in xrange(10):
			self.space.insert(Alive(self.space, vec_rand(),5.0,"robot"+str(i)))
		self.out = StrShow()
	def __move(self,gets):
		p = self.player
		if gets == 'a':
			p.move = Move.left()
		elif gets == 'd':
			p.move = Move.right()
		elif gets == 'w':
			p.move = Move.up()
		elif gets == 's':
			p.move = Move.down()
		elif gets == 'p':
			p.move = vec_empty()
	def __out(self):
		raise RDExcept("")
	def __turnon(self, tf = None):
		if tf is None:
			return self.__enter
		if tf ^ self.__enter:
			self.auto_continue(not tf)
			self.readline(tf)
			self.__enter = tf

	def __order(self,gets):
		if gets is None:
			return
		ords = get_order(gets)
		if len(ords)==0:return;
		ords=ords[0]
		gets = ords[0]
		if gets == "exit":
			self.stop()
			self.__out()
		elif gets == ":":
			self.__turnon(True)
		elif gets == 'detail':
			self.out.insert(self.player.spc.state())
			self.__turnon(True)
		elif gets == "set":
			self.push(self.update_setting,False,True)
			raise RDExcept()
		elif gets == "return":
			self.push(self.update_menu,False,True)
			raise RDExcept()
		elif gets == "goto":
			if len(ords)!=2:
				return
			spc_id = int(ords[1])
			player = self.player
			spc = player.spc.space(spc_id)
			if spc is None:
				self.out.set("不存在的空间编号")
			jg = player.spc.apply(player,spc)
			if not jg:
				self.out.set("尝试失败")
			player.to_space(spc)
			self.out.set("进入空间"+str(spc_id))
		else:
			self.__move(gets)
	def __update(self,gets):
		self.__turnon(False)
		s = [self.player.state()]+self.player.view()
		self.out.insert(s)
		self.__order(gets)
		self.space.update(self.wait_time())
	def update_run(self,gets):
		#self.wait_time(0.2)
		rb = self.__turnon()
		self.out.insert("CNT: "+str(self.play_cnt)+"		SPF: "+str(self.wait_time())+" sec")
		self.play_cnt += 1
		try:
			self.__update(gets)
			self.out(rb)
		except RDExcept,e:
			pass
		self.out.cls()

#class SpaceTr(Object):
#	pass 
"""
space connect:
space translate: 
	cost: time, energy, can't move
楼梯：双向的，
地名：包含在最大的地名中，最大地名没有向上通道，
位置传输：有点与范围，在范围内的可以走到另一个地名的点的范围的随机位置上，若范围被占满，则不能走过去

"""