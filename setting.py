#coding=utf-8
from basedata import *
class SettingDemo(BaseDemo):
	def __init__(self,*args):
		BaseDemo.__init__(self,*args)
	def update(self,gets,sec):
		if gets == '1':
			self.done_call()
			return;
		show("1，退出")

def IODemo(BaseDemo):
	def deal_input(self,gets):
		pass
	def output(self):
		return "IODemo"
	def update(self,gets,sec):
		self.deal_input(gets)
		show(self.output())