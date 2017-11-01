#coding=utf-8
from input import MainDemo as Main
from actor import *
import numpy as np
from output import *
class BaseDemo(Main):
	def __init__(self):
		Main.__init__(self,1.0)
class SettingDemo(BaseDemo):
	def __init__(self):
		BaseDemo.__init__(self)
	def update_setting(self,gets):
		if gets == '1':
			self.pop()
			return;
		show("1，退出")

class RunDemo(SettingDemo):
	def __init__(self):
		SettingDemo.__init__(self)
		self.cnt = 0
	def update_run(self,gets):
		if gets == "e":
			self.stop()
		if gets == "-":
			self.cnt-=1
		elif gets == "+":
			self.cnt+=1
		elif gets == "s":
			self.push(self.update_setting,False,True)
			return;
		elif gets == "r":
			self.pop()
			return;
		import numpy as np
		c = max(self.cnt,0)
		a=np.random.rand(c,c)
		show(str(a),step = 0)
		#show("计数: "+str(self.cnt),step = 0)

class Demo(RunDemo):
	def __init__(self):
		#self.player
		#self.objs
		RunDemo.__init__(self)
	def init(self):
		self.clear_updates()
		self.auto_continue(False)
		show("初始化");
		self.update = self.update_menu
	def finish(self):
		show("清理中...");
	def update_menu(self,gets):
		slts = ['1','2','3']
		if gets in slts:
			if gets == '3':
				self.stop()
				return;
			elif gets == '1':
				self.push(self.update_run,True,False)
				return;
			else:
				self.push(self.update_setting,False,True)
				return;
		menu = ("1，启动","2，设置","3，退出")
		show(menu,step = 0)
def __call__():
	return Demo()
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
	


"""
一个地点的obj，随机性相遇，
obj对其余objs建立连接，其余objs对剩余objs建立连接
obj运动时随机删除与建立连接
为连接的建立设置一些影响因素
地方：可建造，消耗资源和能量和时间，规划大小，可破坏，消耗能量，可修复，消耗能量
大地：可扩张

"""