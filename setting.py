#coding=utf-8
from basedata import *
class SettingDemo(BaseDemo):
	def __init__(self,*args):
		BaseDemo.__init__(self,*args)
	def update_setting(self,gets):
		if gets == '1':
			self.pop()
			return;
		show("1，退出")
