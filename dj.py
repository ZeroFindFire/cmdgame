# coding=utf-8
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
import threading
class InputThread(threading.Thread):
	def __init__(self,test=False):
		self.gets=[]
		self.curr=''
		self.on=True
		self.cond=threading.Condition()
		threading.Thread.__init__(self)
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
		tmpthd=threading.Thread(target=InputThread.thrun, args=(self,))
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
Coding='utf-8'
def show(context,step=1,wait=0.1,decode=True,coding=None):
	from time import sleep
	if decode:
		if coding is not None:
			context=context.decode(coding).encode('gbk')
		else:
			context=context.decode(Coding).encode('gbk')
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
		if step>0 and (i+1) % step == 0:
			sleep(wait)
def binsearch(arr,start,end,cmp,ele):
	if end-start<2:
		return (start,end)
	md=(start+end)/2
	jg=cmp(ele,arr[md])
	#print "cmp:",md,arr[md],ele,jg
	if jg<0:
		return binsearch(arr,start,md,cmp,ele)
	elif jg>0:
		return binsearch(arr,md,end,cmp,ele)
	else:
		return (md,md)

def select_sort(arrs,cmp):
	pass
	l=len(arrs)
	for i in xrange(l):
		id=i 
		for j in xrange(i+1,l):
			if cmp(arrs[j],arrs[id])<0:
				id=j
		tmp=arrs[i]
		arrs[i]=arrs[id]
		arrs[id]=tmp 
	return arrs
class Place:
	# maps: {'time':'describe'}
	# arr: [time by order]
	# time format: hour:minite:sec
	def __init__(self,maps):
		self.maps=maps
		arrs=[]
		for key in maps:
			arrs.append(key)
		select_sort(arrs,self.timecmp)
		self.times=arrs
	def describe(self,time):
		maps=self.maps
		times=self.times 
		start,end=binsearch(times,0,len(times)-1,self.timecmp,time)
		#print start,end
		t1=times[start]
		t2=times[end]
		d1=self.dist(t1,time)
		d2=self.dist(time,t2)
		if start == len(times)-1 and end == start:
			end=0
			t2=times[end]
			d2=self.dist(time,t2)
			d2+=self.dist("00:00:00","24:00:00")
		if d1>d2:
			return maps[t2]
		else:
			return maps[t1]
	@staticmethod
	def dist(t1,t2):
		t1=Place.str2time(t1)
		t2=Place.str2time(t2)
		return t2-t1
	@staticmethod
	def str2time(time):
		t=time.split(":")
		return (int(t[0])*60+int(t[1]))*60+int(t[2])
	@staticmethod
	def time2str(time):
		sec=time%60
		time/=60
		mn=time%60
		hour=time/60
		return "%d:%d:%d"%(hour,mn,sec)
	@staticmethod
	def timecmp(t1,t2):
		t1=Place.str2time(t1)
		t2=Place.str2time(t2)
		if t1==t2:
			return 0
		elif t1<t2:
			return -1
		else:
			return 1
maps={	"00:00:00":"月亮高悬挂空中，乌云环绕，夜色幽深，一片寂静",
		"1:00:00":"乌云遮蔽了月亮，周围变的沉闷",
		"2:00:00":"雨淅淅沥沥的下着，树林里发出“沙沙”的声响",
		"3:00:00":"大雨倾盆，“噼里啪啦”的打在树林中，雷声阵阵",
		"5:00:00":"雨势渐小，地上泥泞，布满水坑",
		"6:00:00":"雨淅淅沥沥的下着，四周一片安静",
		"7:30:00":"夜色渐渐隐去，周围渐渐清晰，天上灰蒙蒙一片，雨依然在下着",
		"9:00:00":"阳光透过云层照射下来，雨越下越小",
		"10:00:00":"太阳高照，四周遍布着水坑",
		"12:00:00":"太阳高照，天气炎热",
		"17:00:00":"太阳挂在西边，火烧云染红半边天，天气变得不那么炎热",
		"19:00:00":"月亮挂在东边，天空慢慢暗了下来",
		"20:00:00":"月亮挂在东边，四周暗淡，寂静",
		"22:00:00":"月亮高挂，四周寂静"}
arrs=[]
for key in maps:
	arrs.append(key)
pl=Place(maps)
out=pl.describe
select_sort(arrs,Place.timecmp)
import random
def randtime():
	sec=int(random.random()*61)
	mn=int(random.random()*61)
	hour=int(random.random()*24)
	return "%d:%d:%d"%(hour,mn,sec)
def randsec(rang,start_time):
	sec=int(random.random()*3600*24*rang)
	t=Place.str2time(start_time)+sec
	t%=3600*24
	return Place.time2str(t)
start_time=randtime()
rang=0.1
def destest():
	global start_time
	start_time=randsec(rang,start_time)
	print "time:",start_time 
	print pl.describe(start_time).decode("utf-8")
wt=1.0
def testpl():
	from time import sleep
	global wt
	import os
	while True:
		os.system("cls")
		destest()
		sleep(wt)
class world:
	def __init__(self):
		self.maps=[]
'''
可描述场景
不同地点，时间有不同描述
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
class Describe:
	def relPos(main,obj):
		return "前方，后方，左边，右边，夹杂，里面，左前方，右前方，左后方，右后方"
	def detailRelPos(main,obj):
		return "前方5米处"

'''
容器包含物体和容器
几个同类型并且相距较近的物体组合成容器（几个，一片，树林，森林）
有的容器包含描述，有的描述所包含的物体
物体描述受环境以及自身状态影响：环境主要为天气？（晴天，雨天，白天黑夜，寒冷，炎热，
normal：树林静静悄悄的。
rain：雨水打在树叶上，哗啦啦的响着
snow：树上积满了雪，一片雪白
console农场：
几块可种植的土地，一袋种子（随机），一个农民（你），一栋屋子（一个厨房，一个地下储藏室，一个储物间，一间卧室）
更简单化：
几块可种植土地，一袋随机种子，一个农民（你），一口井，一个水缸（存水），
	屋子【一个卧室（睡觉），一个厨房（将食物变为熟食或将冷食加热），一个储藏室（存放农产品等）】，
	一个探索地（可选择探索，可发现种子），
	一辆牛车（可装载货物），
	农产品收购点，种子售卖点
	工具：
		锄头：锄草，开荒
		水桶：打水，灌溉
		水瓢：装水，灌溉
		锅：装东西，可被加热
		灶台：放置锅，将热量集中上升
		打火石：可点燃易燃物品
		火绳：易燃物品
		艾草：易燃物品

基本：可种植土地
植物：
小麦：
作用关系：
	阳光：光合作用，存储能量，消耗水
	自身：生长：消耗水和矿物质
	雨水：存储水，降雨量多大导致呼吸反应降低，降低生长作用，同时随机概率（概率=(rand()*sec*rang(rainfall))>?造成植物受伤
	风：随机概率造成植物受损

天气作用关系：
	太阳&月亮：受时间影响
	阳光&月光：受太阳&月亮与积云影响，积云密度随机减弱，遮蔽光线（随机性n秒产生一次）
	环境光：受太阳&月亮与积云影响，积云密度随机减弱环境光
	雨：受积云影响，积云密度随机导致降雨，降雨发生后积云密度随机导致雨停
	风：受季节，时间影响，n秒随机一次，产生后随机停止
	积云：受季节，时间影响，随机性同风
	温度：受光，积云，雨，风，季节，时间影响
天气块：
	不包含太阳&月亮
	其它因素增加所受影响：相邻天气块的相同因素诱使其同化
'''
date=0;
year=0;
clock=0;
rain_mini=1.0
rain_small=2.0
rain_middle=5.0
rain_big=10.0
rain_huge=20.0
class Scale:
	mini,small,middle,big,huge="mini","small","middle","big","huge"
	scales=["mini","small","middle","big","huge"]
	@staticmethod
	def scale(data,maps):
		for s in Scale.scales:
			if data<maps[s]:
				return s
		return Scale.scales[-1]
'''
data script:
weather describe:
	describe order
	i.e:
		sun,moon,rain,temperature,wind,snow
	简单描述
	详细描述
	更详细描述
	。。。
	level0:
	太阳&月亮：
		参数：
		角度：0,0.25,0.5,0.75,1.0
	阳光&月光：
		亮度：l0,l1,..ln
	环境光：
		亮度：l0,l1,..ln

	雨：
		雨量：l0..ln
	风：
		风向：东，西，南，北，东南，西北，东北，西南
		风速：l0..ln
	积云：
		密度：l0..ln
	雷声：
		小，中，大
		沉闷，响亮
	闪电：
		小，中，大。。。
	温度：
		极冷，冷，寒。。。极热
	雨淅淅沥沥的下着，风轻轻吹动，云层灰蒙蒙的，太阳挂在天上，阳光柔和，天气有些冷。
	简单：
	描述必须描述以及偏离正常值的数据：
	雨，雷，闪电，过冷或过热，较大的风，光线过强或过弱，积云浓厚
	匹配：寻找最多的匹配，将剩余的继续寻找最多的匹配，
	level1:

'''
class Util:
	@staticmethod
	def inrange(rang,data):
		return data >= rang[0] and data <= rang[1]
class Cloud:
	cloud_scale={
		Scale.mini:1.0,
		Scale.small:2.0,
		Scale.middle:3.0,
		Scale.big:5.0
	}
	def __init__(self):
		self.rate=0.0 # [0,1]
'''
	1lux=1lm/平方米=1cd×sr/平方米
	lx=lux
	夏季在阳光直接照射下，光照强度可达6万～10万lx，没有太阳的室外0.1万～1万lx，夏天明朗的室内100～550lx，夜间满月下为0.2lx。
	在不同光线情况下为：晴天阳光直射地面照度约为100000lx，晴天背阴处照度约为10000
	lx，晴天室内北窗附近照度约为2000lx，晴天室内中央照度约为200lx，晴天室内角落照
	度约为20lx，晴朗月夜照度约为0.2lx
	以下是各种环境照度值：单位lux 
	黑夜：0.001—0.02；月夜：0.02—0.3；阴天室内：5—50；阴天室外：50—500；晴天室内：100—1000；
	夏季中午太阳光下的照度：约为10*9次方；阅读书刊时所需的照度：50—60；家用摄像机标准照度：1400。
	夏季在阳光直接照射下，光照强度可达6万～10万lx，没有太阳的室外0.1万～1万lx，夏天明朗的室内100～550lx，夜间满月下为0.2lx。


	白炽灯每瓦大约可发出12.56 lx的光，但数值随灯泡大小而异，小灯泡能发出较多的流明，大灯泡较少。
	荧光灯的发光效率是白炽灯的3～4倍，寿命是白炽灯的9倍，但价格较高。
	一个不加灯罩的白炽灯泡所发出的光线中，约有30%的流明被墙壁、顶棚、设备等吸收；
	灯泡的质量差与阴暗又要减少许多流明，所以大约只有50%的流明可利用。
	一般在有灯罩、灯高度为2.0～2.4m(灯泡距离为高度的1.5倍)时，每0.37㎡面积上需1W灯泡、或1㎡面积上需2.7W灯泡可提供10.76 lx。
	灯泡安装的高度及有无灯罩对光照强度影响很大。
	普通日光灯光照强度是100lux左右。
	光照强度是一种物理术语，指单位面积上所接受可见光的能量。对生物的光合作用影响很大。可通过照度计来测量。
	勒克斯（lux，法定符号lx）照度单位，1 勒克斯等于 1流(lumen,lm)的光通量均匀分布于 1㎡ 面积上的光照度。
	照度是反映光照强度的一种单位，其物理意义是照射到单位面积上的光通量，照度的单位是每平方米的流明（Lm）数，也叫做勒克斯（Lux）： 1 lx=1 Lm/㎡上式中，Lm是光通量的单位，其定义是纯铂在熔化温度（约1770℃）时，其1/60平方米的表面面积于1球面度的立体角内所辐射的光量。
	为了对照度的量有一个感性的认识，下面举一例进行计算，一只100W的白炽灯，其发出的总光通量约为1200 Lm，若假定该光通量均匀地分布在一半球面上，则距该光源1m和5m处的光照度值可分别按下列步骤求得： 半径为1 m的半球面积为2π×1^2=6.28平方米 距光源1 m处的光照度值为： 1200Lm/6.28平方米=191 lx同理、半径为5 m的半球面积为:2π×5^2=157平方米 距光源5 m处的光照度值为： 1200Lm/157平方米=7.64 lx
	可见，从点光源发出的光照度是遵守平方反比律的。
	1 lx大约等于1烛光在1米距离的照度，我们在摄像机参数规格中常见的最低照度（MINIMUM.ILLUMINATION），表示该摄像机只需在所标示的LUX数值下，即能获取清晰的影像画面，此数值越小越好，说明CCD的灵敏度越高。同样条件下，黑白摄像机所需的照度远比尚须处理色彩浓度的彩色摄像机要低10倍。
	一般情况：夏日阳光下为100，000 lx；阴天室外为10000 lx；室内日光灯为100 lx；距60W台灯60CM桌面为300lx；电视台演播室为1000 lx；黄昏室内为10 lx；夜间路灯为0.1 lx；烛光搜索（20CM远处）10～15 lx。
'''
class Light:
	sun_scale={
		Scale.mini:1.0,
		Scale.small:2.0,
		Scale.middle:3.0,
		Scale.big:5.0
	}
	sun_season={
		Time.spring:0.7,
		Time.summer:0.85,
		Time.autumn:0.7,
		Time.winter:0.8
	}
	moon_season={
		Time.spring:0.7,
		Time.summer:0.85,
		Time.autumn:0.7,
		Time.winter:0.8
	}
	def sunshine(self,angle,cloud,season):
		maxlight=(1-cloud)*self.sun_season[season]*126800.0;
		return maxlight*(1.0-2*abs(angle*0.8+0.1-0.5))

	def moonlight(self,angle,cloud,season):
		maxlight=(1-cloud)*self.moon_season[season]*0.3;
		return maxlight*(1.0-2*abs(angle*0.8+0.1-0.5))
	def envlight(self,startlight,light_able):
		pass
		"""
		light_able==false:
			startlight*0.?
		else:
			startlight*0.9?
		"""
class Weather:
	rain_scale={
		Scale.mini:1.0,
		Scale.small:2.0,
		Scale.middle:3.0,
		Scale.big:5.0
	}
	cloud_scale={
		Scale.mini:1.0,
		Scale.small:2.0,
		Scale.middle:3.0,
		Scale.big:5.0
	}
	wind_scale={
		Scale.mini:1.0,
		Scale.small:2.0,
		Scale.middle:3.0,
		Scale.big:5.0
	}
	sun_scale={
		Scale.mini:1.0,
		Scale.small:2.0,
		Scale.middle:3.0,
		Scale.big:5.0
	}
	moon_scale={
		Scale.mini:1.0,
		Scale.small:2.0,
		Scale.middle:3.0,
		Scale.big:5.0
	}
	light_scale={
		Scale.mini:1.0,
		Scale.small:2.0,
		Scale.middle:3.0,
		Scale.big:5.0
	}
	clouds=0.0
	def __init__(self):
		self.cloud=0.0 #[0,1]

class Time:
	spring="spring"
	summer="summer"
	autumn="autumn"
	winter="winter"
	months=[31,28,31,30,31,30,31,31,30,31,30,31];
	sun_range={spring:(7,12+7),
		summer:(6,12+7),
		autumn:(7,12+7),
		winter:(8,12+6)}
	moon_range={spring:(12+7,24+6),
		summer:(12+7,24+6),
		autumn:(12+7,24+6),
		winter:(12+7,24+6)}
	@staticmethod
	def day_angle(rang,clock):
		_hour=clock/3600.0
		if Util.inrange(rang,clock):
			return (clock-rang[0])/(rang[1]-rang[0])
		elif Util.inrange(rang,clock+24):
			return (clock+24-rang[0])/(rang[1]-rang[0])
		else:
			return None
	def month(self):
		date=self.date
		cnt=0;
		while date>0:
			date-=self.months[cnt]
			cnt+=1
		return cnt
	def vdate(date):
		cnt=0;
		while date>0:
			date-=self.months[cnt]
			cnt+=1
		date+=self.months[cnt-1]
		return (cnt,date)

	def vtime(self):
		clock=self.clock
		sec=clock%60
		clock/=60
		mn=clock%60
		hour=clock/60
		return (hour,mn,sec)

	def hour(self):
		return 1.0*self.clock/3600

	def season(self):
		mon=self.month()
		if mon<3 or mon==12:
			return self.winter;
		elif mon<6:
			return self.spring;
		elif mon<9:
			return self.summer;
		else:
			return self.autumn;
	def __init__(self):
		self.clock=0
		self.date=1
		self.year=0
	def update(self,sec):
		self.clock+=clock
		if self.clock>=3600*24:
			cnt=self.clock/(3600*24)
			self.clock-=3600*24*cnt
			self.date+=cnt
			if self.date>365:
				tnc=self.date/365
				self.date-=365*tnc
				self.year+=tnc
	def sun_angle(self):
		s=season(self.date)
		srange=self.sun_range(s)
		return self.day_angle(srange,self.clock)
	def moon_angle(self):
		s=season(self.date)
		mrange=self.moon_range(s)
		return self.day_angle(mrange,self.clock)

class Demo():
	pass
class Weather:
	def __init__(self):
		pass
class Describe:
	@staticmethod
	def strcmb(a,b,point="，"):
		if a is None or a=="":return b;
		if b is None or b=="":return a;
		return a+point+b;
	@staticmethod
	def dirstr(vec):
		out=""
		if vec is None:return out;
		x,y=vec[0],vec[1]
		if x>0:
			out+="东"
		elif x<0:
			out+="西"
		if y>0:
			out+="北"
		elif y<0:
			out+="南"
		return out

	@staticmethod
	def numstr(num,unit):
		if num<5:
			return str(num)+unit
		elif num<10:
			return "几"+unit
		elif num<20:
			return "十几"+unit
		elif num<100:
			return "很多"
		elif num<1000:
			return "大量"
		else:
			return "数不清的"
	WaterDecrease=1.0/100.0
class Plant:
	Fruit=0
	Seed=1
	Seeding=2
	Young=3
	Flower=4
	Bear=5
	Old=6
	@staticmethod
	def state_describe(state):
		dest={Plant.Fruit:"果子",Plant.Seed:"种子",Plant.Seeding:"幼苗",
			Plant.Young:"植株",Plant.Flower:"开花",Plant.Bear:"结果",Plant.Old:"老"}
		return dest[state]
	def __init__(self,num,area):
		self.others=[]
		self.num=num
		self.age=0.0
		self.state=self.Seed
		self.area=area
	def name(self):
		return "不知名植物"
	def run(sec,place,weather):
		self.age+=sec
		for plant in self.others:
			plant.run(sec,place,weather)
	def seed(self,plt):
		if plt.age!=self.age:
			self.others.append(plt)
		else:
			self.area+=plt.area
			self.num+=plt.num
			for p in plt.others:
				self.others.append(p)
	def same(self,plant):
		return plant.__class__.__name__==self.__class__.__name__
	def waterSave(self):
		return 0.1
	def describe(self,place,weather):
		out=str(self.num)+"株"+str(int(self.age))+"岁的"+self.name()+self.state_describe(self.state)+"扎根在土中"
		for other in self.others:
			out+="，"+other.describe(place,weather)
		return out
class Weather:
	def __init__(self):
		self.temperature=0.0
		self.rain=False
		self.snow=False
		self.wind=False
		self.clouds=0.1
		self.rainfall=0.0
		self.windpower=0.0
		self.winddirect=None
		self.snowdown=0.0
		self.sun=False
		self.moon=False
		self.sunshine=0.0
		self.sunangle=0
		self.moonangle=0
		self.moonlight=0.0
		self.stars=0.0
	def set_rain(self,rain,rainfall=0.0):
		self.rain=rain
		self.rainfall=rainfall
	def set_wind(self,wind,windpower=0.0,winddirect=[0.0,0.0]):
		self.wind=wind
		self.windpower=windpower
		self.winddirect=winddirect
	def set_sun(self,sun,light=0.0,angle=0.0):
		self.sun=sun
		self.sunshine=light
		self.sunangle=angle
	def set_moon(self,moon,light=0.0,angle=0.0):
		self.moon=moon
		self.moonlight=light
		self.moonangle=angle
	def describe_sun(self):
		if self.sun==False or self.sunshine==0.0:
			return ""
		out="太阳"
		if self.sunangle<30.0:
			out+="挂在东边"
		elif self.sunangle>60.0:
			out+="挂在西边"
		else:
			out+="高挂"
		out+="，"
		if self.sunshine<0.3:
			out+="阳光柔和"
		elif self.sunshine<0.6:
			out+="阳光明媚"
		else:
			out+="阳光猛烈地照射下来"
		return out;
	def describe_moon(self):
		if self.moon==False or self.moonlight==0.0:
			return ""
		out="月亮"
		if self.moonangle<30.0:
			out+="挂在东边"
		elif self.moonangle>60.0:
			out+="挂在西边"
		else:
			out+="挂在半空中"
		out+="，"
		if self.moonlight<0.3:
			out+="月光微微洒落"
		elif self.moonlight<0.6:
			out+="月光皎洁"
		else:
			out+="月光明媚"
		return out;
	def describe_temp(self):
		tmp=self.temperature
		if tmp<-20.0:
			return "世界像是被冻住了"
		elif tmp<-10.0:
			return "气温低的吓人"
		elif tmp<0.0:
			return "天寒地冻"
		elif tmp<10.0:
			return "天气有些寒冷"
		elif tmp<20.0:
			return "天气有些凉"
		elif tmp<30.0:
			return "天气适中"
		elif tmp<30.0:
			return "天有些热"
		elif tmp<40.0:
			return "天气炎热"
		elif tmp<40.0:
			return "周围像火炉一样"
		else:
			return "世界像是在燃烧"
	def describe_wind(self):
		if self.wind==False:
			return ""
		elif self.windpower<1.0:
			return "微风轻轻吹拂"
		else:
			dct=Describe.dirstr(self.winddirect)
			out=dct+"风"
			if self.windpower<10.0:
				return out+"阵阵吹过"
			elif self.windpower<20.0:
				return out+"猛烈地刮动"
			else:
				return out+"在呼啸"
	def describe_rain(self):
		if self.rain== False:
			return ""
		elif self.rainfall<1.0:
			return "细雨濛濛"
		elif self.rainfall<10.0:
			return "雨淅淅沥沥的下着"
		elif self.rainfall<21.0:
			return "雨从天上打落"
		elif self.rainfall<31.0:
			return "大雨倾盆，电闪雷鸣"
		else:
			return "暴雨咆哮着扑来，雷声轰鸣，闪电撕裂天际"
	def describe(self):
		out=self.describe_sun()+self.describe_moon();
		out=Describe.strcmb(out,self.describe_temp())
		out=Describe.strcmb(out,self.describe_wind())
		out=Describe.strcmb(out,self.describe_rain())
		return out
class Wheat(Plant):
	def __init__(self):
		Plant.__init__(self)
		pass
	def name(self):
		return "小麦"
	def run(sec,place,weather):
		self.age+=sec
class FarmPlace:
	AreaFen=1.0/64
	def __init__(self):
		self.plants=[]
		self.shape=[8,8]
		self.water=1.0
		self.rich=1.0
	def area_left(self):
		total=self.area()
		for pt in self.plants:
			total-=pt.area
		return total
	def area(self):
		return self.shape[0]*self.shape[1]*self.AreaFen
	def mArea(self):
		return self.shape[0]*self.shape[1]
	def run(self,sec,weather):
		water_save=0.0
		for plant in self.plants:
			plant.run(sec,self,weather)
			water_save+=plant.waterSave()*plant.area/self.area()
		if weather.rain:
			self.water+=weather.rainfall*self.mArea()*sec
		elif weather.temperature>0.0:
			water_dec=sec*self.mArea()*self.water*weather.water_down()*(1.0-water_save)
			self.water-=water_dec
	def plant(self,seed):
		if self.area_left()<seed.area:
			return
		for plt in self.plants:
			if plt.same(seed):
				plt.seed(seed)
				return
		self.plants.append(seed)
	def describe(self,weather):
		if len(self.plants)==0:
			return "地里空空荡荡"
		out="地上长着"
		plants=self.plants
		l=len(plants)
		for i in xrange(l-1):
			out+=plants[i].name()+"、"
		if l>1:
			out+="和"
		out+=plants[l-1].name()+"，"
		for p in plants:
			out+=p.describe(self,weather)+"，"
		return out
class Object:
	def __init__(self):
		self.pas=0
class Places:
	def __init__(self):
		self.contain=[]