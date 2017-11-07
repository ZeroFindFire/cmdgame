#coding=utf-8
from menu import *

class Demo(MenuDemo):
	def __init__(self,*args):
		MenuDemo.__init__(self,*args)
	def init(self):
		self.clear_updates()
		self.auto_continue(False)
		show("初始化");
		self.update = self.update_menu
	def finish(self):
		show("清理中...                                           ",rd=True);
a = Demo()
if __name__ == "__main__":
	a.run()
"""
一个地点的obj，随机性相遇，
obj对其余objs建立连接，其余objs对剩余objs建立连接
obj运动时随机删除与建立连接
为连接的建立设置一些影响因素
一般距离相近都建立连接，但当连接数过多，不再建立连接，随机性相遇只为了减少连接
地方：可建造，消耗资源和能量和时间，规划大小，可破坏，消耗能量，可修复，消耗能量
大地：可扩张

"""