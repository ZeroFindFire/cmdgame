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
class RunDemo(BaseDemo):
	def __init__(self,*args):
		self.play_cnt = 0
		BaseDemo.__init__(self,*args)
		self.cnt = 0
		self.__enter = True
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
			self.mc_state.unblock_gets = not tf
			self.mc_state.block_gets = tf 
			self.__enter = tf

	def run_order(self,gets):
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
	def run_update(self,gets):
		self.__turnon(False)
		self.out.insert(s)
		self.__order(gets)
	def update(self,gets):
		#self.wait_time(0.2)
		rb = self.__turnon()
		self.out.insert("CNT: "+str(self.play_cnt)+"		SPF: "+str(self.wait_time())+" sec")
		self.play_cnt += 1
		try:
			self.run_update(gets)
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
class IO:
	def __init__(self,mc):
		self.machine=mc
	def output(self):
		print "1,exit\n"
	def deal_input(self,gets):
		if gets == "1":
			self.machine.done_call()
		else:
			pass
		self.call_excpet()
Player:
	can obtain tools, has iotools to connect with user
	iotools should be inheritable or adaptable
	objs has names and parmaters
	viewtools: get info of near objs
	feeltools: get info of self
	movetools: be moveable
	iotools: get info of self and nearby
	slots: connect with tools 
	adaptertools: maintain tools self
	inserttools: 
	thinktools: deal with tools, like iotools
	battery: contain of powers
	lines: power trans, info trans
	encapeslot: put tools, remove tools, power trans, info trans, objs trans, tools list, empty slot number
		every sec, battery out energy and get left energy
		view every tools, pwoer nppo, matain
	buildtools: build things, put objs & energy, out objs
	burntools: put objs & energy, out energy
	bagtools: 
World:
	Ojbects act

"""