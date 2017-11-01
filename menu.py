#coding=utf-8
from run import *

class MenuDemo(RunDemo):
	def __init__(self,*args):
		RunDemo.__init__(self,*args)
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
