﻿# coding=utf-8
import numpy as np
import sys
from time import sleep
# 物体有位置，体积（可为多面体），更新函数
# 物体之间需要相互作用，
# 1，物体内部处理相互作用
# 2，物体外部处理相互作用
# 
class Object(object):
	@staticmethod
	def class2str(obj):
		try:
			name=obj.__name__
		except Exception,e:
			name=obj.__class__.__name__
		return (obj.__module__,name)
	@staticmethod
	def str2class(str_md,name):
		__import__(str_md)
		md=sys.modules[str_md]
		Construct=getattr(md,name)
		return Construct
	def __init__(self):
		self.pos=np.zeros(3)
		self.phy=PhyModel()
		self.show=ShowModel()
	def getName(self):
		return ""
	def update(self,time,objs=None):
		pass
	def getView(self):
		return None
	def phyModel(self):
		return self.phy

class PhyModel:
	def phyModel(self):
		return self
	def outBox(self):
		return self
	def outOrb(self):
		return self

class Orb(PhyModel):
	def __init__(self,pos=np.zeros(3),r=1.0):
		self.pos=np.array(pos)
		self.r=r
	def outBox(self):
		return Box(self.pos-r,self.pos+r)
def vec_zero():
	return np.zeros(3)
class Box(PhyModel):
	def __init__(self,v0=vec_zero(),v1=vec_zero()):
		self.pos=(np.minimum(v0,v1),np.maximum(v0,v1))
	def outOrb(self):
		pos=(self.pos[0]+self.pos[1])*0.5
		r=np.abs(self.pos[1]-self.pos[0]).max()
		return Orb(pos,r)
	def contain(self,box):
		return (self.pos[0] <= box.pos[0]).all() and (self.pos[1] >= box.pos[1]).all()
	def left(self):
		return self.pos[0]
	def right(self):
		return self.pos[1]
	def cmp(self,id,val):
		pos=self.pos
		if pos[0][id] >= val:
			return -1
		elif pos[1][id] <= val:
			return 1
		else:
			return 0
"""
sqrt(a^2-h^2)+sqrt(b^2-h^2)=c
a2-h2=c2+(b2-h2)-2c.sqrt(b2-h2)
2c.sqrt(b2-h2)=c2+b2-h2-a2+h2=c2+b2-a2
4c2(b2-h2)=(c2+b2-a2)2
b2-h2=(c2+b2-a2)2/4c2
h2=b2-(c2+b2-a2)2/4c2
=(4c2b2-(c2+b2-a2)2)/4c2
=(2c2b2+2c2a2+2a2b2-(c4+b4+a4))/4c2


(c2+b2-a2)2=(c2+b2)2-2a2(c2+b2)+a4=c4+2c2b2+b4+a4-2c2a2-2a2b2
"""
def OrbCross(c1, c2):
	dst=(c1.pos-c2.pos)**2
	dst=dst.sum()
	std=(c1.r+c2.r)**2
	if dst > std:
		return None
	else:
		r1,r2=c1.r**2,c2.r**2
		vec=c2.pos-c1.pos
		h2=(2*(r1*r2+r1*dst+r2*dst)-(r1*r1+r2*r2+dst*dst))/4*dst
		vec*=np.sqrt(1.0/dst)
		pos=c1.pos+vec*np.sqrt(r1-h2)
		return (pos,vec)
class Collision(object):
	cross_maps={"orb":{"orb":OrbCross}}
	@staticmethod
	def append(name, fcmap):
		Collision.cross_maps[name]=fcmap
	@staticmethod
	def cross(model_a, model_b):
		n_a, n_b = model_a.CName(), model_b.CName()
		if cross_maps.has_key(n_a) and cross_maps[n_a].has_key(n_b) :
			return cross_maps[n_a][n_b](model_a, model_b);
		elif cross_maps.has_key(n_b) and cross_maps[n_b].has_key(n_a) :
			crr = cross_maps[n_b][n_a](model_b, model_a);
			if crr is not None:
				crr = (crr[0], -crr[1])
			return crr
# 容器，用链表或树结构之类的存储节点
class Container(Object):
	def __init__(self):
		pass
	def insert(self,obj):
		pass
	def remove(self,obj):
		pass
	def find(self,name):
		return None
	# spc:
	#  cross(obj):bool
	def spc_find(self,spc):
		return self
	def __iter__(self):
		return []
class MapContainer(Container):
	def __init__(self):
		self.map={}
	def insert(self,obj):
		self.map[obj.getName()]=obj
	def remove(self,obj):
		self.map.pop(obj.getName())
	def find(self,name):
		if self.map.has_key(name):
			return self.map[name]
		else:
			return None
	def update(self,sec,objs=None):
		if objs is None:
			objs=self
		for key in self.map:
			obj=self.map[key]
			view=obj.getView()
			ct=objs.spc_find(view)
			obj.update(sec,ct)
class BSPContainer(Container):
	def __init__(self):
		self.box = Box()
		self.left, self.right = None, None
		self.max=10
		self.contain=[]
	def insert(self,obj):
		box=obj.phyModel().outBox()
		if self.left is not None and self.left.box.contain(box):
			self.left.insert(obj)
		elif self.right is not None and self.right.box.contain(box):
			self.right.insert(obj)
		else:
			self.contain.append(obj)
	def updateShape(self):
		contain=self.contain
		if self.left is None and self.right is None and len(contain)>self.max:
			pos=vec_zero()
			for obj in contain:
				box=obj.phyModel().outBox()
				pos+=(box.left()+box.right())*0.5
			pos/=len(contain)
			cnt = np.zeros([2,len(pos)])
			rg=xrange(len(pos))
			for obj in contain:
				box=obj.phyModel().outBox()
				for i in rg:
					jg = box.cmp(i, pos[i])
					if jg == -1:
						cnt[0][i]+=1
					elif jg == 1:
						cnt[1][i]+=1
			id, val = 0, 0
			for i in rg:
				tval=min(cnt[0][i],cnt[1][i])
				if tval > val:
					id = i
			
class World(Object):
	def __init__(self):
			pass
class Getch:
	def __init__(self):
		import platform
		ossys=platform.system()
		if ossys=="Windows":
			 self.call=Getch.wncall
		else:
			self.call=Getch.lxcall
	@staticmethod
	def wncall():
		import msvcrt
		return msvcrt.getch()
	@staticmethod
	def lxcall():
		import sys, termios
		fd = sys.stdin.fileno()
		old_settings = termios.tcgetattr(fd)  
		new = termios.tcgetattr(fd)
		new[3] = new[3] & ~termios.ECHO
		new[3] = new[3] & ~termios.ICANON
		try:  
			termios.tcsetattr(fd, termios.TCSADRAIN, new) 
			ch = sys.stdin.read(1)  
		finally:
			termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)  
		return ch
	def __call__(self):
		return self.call()
import threading as td
class InputThread(td.Thread):
	def __init__(self,test=False):
		self.gets=[]
		self.curr=''
		self.on=True
		self.cond=td.Condition()
		td.Thread.__init__(self)
		self.wait_sec=1
		self.test=test
		self.getch=False
		self.getchar=Getch()
	def put(self,cts):
		if len(self.gets)<10:
			self.gets.append(cts)
	def pop(self):
		if len(self.gets)==0:
			return None
		cts=self.gets[0]
		del self.gets[0]
		return cts
	def run(self):
		getchar=Getch()
		while self.on:
			if self.getch:
				ch=getchar() 
				#print "by getchar:",ch
			else:
				ch=sys.stdin.readline()[:-1]
				#print "by readline:",ch
			self.curr=ch
			with self.cond:
				self.notify=True
				self.cond.notify()
				self.put(ch)
			if self.test and ch == 'q':break;
	@staticmethod
	def thrun(self):
		if self.getch:
			ch=self.getchar() 
		else:
			ch=sys.stdin.readline()[:-1]
		self.curr=ch
		with self.cond:
			self.notify=True
			self.cond.notify()
			self.put(ch)
	def stop(self):
		self.on=False
	def single_start(self,getch=False):
		self.getch=getch
		tmpthd=td.Thread(target=InputThread.thrun, args=(self,))
		tmpthd.start()
	def input(self,time_out=True):
		wait_sec=self.wait_sec
		if time_out==False:
			wait_sec=None
		with self.cond:
			self.notify=False
			p=self.pop()
			if p is not None:
				return p
			self.cond.wait(wait_sec)
			return self.pop()
def test():
	ins=InputThread(True)
	ins.start()
	while True:
		get=ins.input()
		print "get:",get

def testst():
	ins=InputThread(True)
	ins.start()
	cts="按回车键来进行操作\n"
	while True:
		show(cts,coding='utf-8')
		get=ins.input()
		if get is None:
			continue
		sys.stdout.write(":")
		get=ins.input(time_out=False)
		print "order:",get
		if get=='quit' or get == 'exit':
			break
def tests():
	ins=InputThread(True)
	#ins.start()
	cts="按回车键来进行操作\n"
	crt=True
	while True:
		if crt:
			ins.single_start(getch=True);
		show(cts,coding='utf-8')
		get=ins.input()
		if get is None:
			crt=False
			continue
		crt=True
		sys.stdout.write(":")
		ins.single_start(getch=False)
		get=ins.input(time_out=False)
		print "order:",get
		if get=='quit' or get == 'exit':
			break
wait=0.9
import sys
def show(context,step=1,wait=0.1,coding=sys.getfilesystemencoding()):
	from time import sleep
	if coding is not None:
		context=context.decode(coding).encode('gbk')
	else:
		context=context.encode('gbk')
	ct_mx='\x7f'
	tp=sys.getfilesystemencoding()
	i=0
	while i < len(context):
		c=context[i]
		if c<ct_mx:
			sys.stdout.write(c)
			i+=1
		else:
			ct=context[i:i+2]
			ct=ct.decode('gbk').encode(tp)
			sys.stdout.write(ct)
			i+=2
		if i % step == step-1:
			sleep(wait)
def test123():
	dst=10.0
	chg=0.5
	while dst>0:
			show("敌人离你还有",stp=3,dcd="utf-8")
			show(str(dst))
			show("米",stp=3,dcd="utf-8")
			print ""
			tm.sleep(wait)
			dst-=chg
'''
container:tree(parent)
	def same_node
object:
	container
a object refer to a container?
util:
	create(name,parmeters):object
	destroy(object)
object:
	pass
world:
	sky: space, clouds, sky_livings, flying_animals
	ground: blocks, 
	water: blocks, 
	
'''