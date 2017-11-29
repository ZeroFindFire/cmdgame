#coding=utf-8
from input import MachineState
#from actor import *
import numpy as np
from output import *
class BaseData:
	pass
class BaseDemo:
	def call(self,key):
		self.machine.call(key)
	def done_call(self):
		self.machine.done_call()
	def call_excpet(self):
		raise CallException(self.__class__.__name__)
	def __init__(self,main,data):
		self.machine=main
		self.data=data

	# wait for implement:

	def update(self,gets,sec):
		print "update demo"
	def init(self):
		print "init demo"
	def finish(self):
		print "finish demo"
	def default_state(self):
		return MachineState(block_gets=True)
	@property
	def mc_state(self):
		return self.machine.state