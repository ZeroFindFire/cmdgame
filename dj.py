import numpy as np
import sys
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