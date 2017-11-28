#coding=utf-8
import numpy as np
import sys
from time import sleep
import threading
"""
Getch:
	若要无阻断的获取键盘按键，生成一个Getch对象然后直接调用：
	getc = Getch();
	c = getc()
InputThread:
	新建线程来获取输入
	input = InputThread(wait_sec:设置监听多久进行返回)
	
	input.single_start(getch:是否没有阻断的获取按键监听) 
	该函数创建的线程仅获取一次按键输入，并且会在明确的获取到非空按键后才结束
	
	 gets = input(time_out:是否无限等待，False：无限等待直到获取到按键，True：超时后返回None)
	 input.wait_time():设置和获取timeout
MainDemo(InputThread):
	runner = MainDemo(wait_sec:同InputThread)
	可重写方法：
	init(),finish(),update(gets)
	__init__(wait_sec):需要记得调用MainDemo.__init__(wait_sec)
	可调用方法：
	stop(),run(auto_continue)
	运行逻辑代码
	run():
		init()
		while(running):
			update(gets)
		finish()
	stop():结束run()的内循环，可在init和update里调用（在finish里调用没用）
	run(auto_continue)：启动运行，仅调用一次，auto_continue=True：在获取输入超时后调用update(None)，在获取按键后获取输入，调用update(gets)
											  auto_continue=False：直到获取非空输入后，调用update(gets)
"""

# 没有阻断的获取键盘按键输入
# 使用方法，生成一个对象然后直接调用： getc = Getch(); return getc();
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

# 新建一个线程用以获取键盘输入，使获取键盘输入的同时还可以继续做其它事
class InputThread:
	def __init__(self,wait_sec=1):
		self.gets=[]
		self.cond=threading.Condition()
		self.wait_sec=wait_sec
		self.getch=False
		self.getchar=Getch()
	def __put(self,cts):
		if len(self.gets)<10:
			self.gets.append(cts)
	def __pop(self):
		if len(self.gets)==0:
			return None
		cts=self.gets[0]
		del self.gets[0]
		return cts
	def __call__(self,time_out = True):
		return self.input(time_out)
	@staticmethod
	def thrun(self):
		#print "thread start:",threading.currentThread().ident
		if self.getch:
			ch=self.getchar() 
		else:
			ch=sys.stdin.readline()[:-1]
		with self.cond:
			self.__put(ch)
			self.cond.notify()
		#print "thread end:",threading.currentThread().ident
	def wait_time(self,wait_sec=None):
		if wait_sec is None:
			return self.wait_sec
		else:
			self.wait_sec=wait_sec
	def stop(self):
		self.on=False
	def single_start(self,getch=False):
		self.getch=getch
		tmpthd=threading.Thread(target=InputThread.thrun, args=(self,))
		tmpthd.start()
	def input(self,time_out=True):
		#print "ingets:",self.gets
		wait_sec=self.wait_sec
		if time_out==False:
			wait_sec=None
		out = None
		with self.cond:
			p=self.__pop()
			if p is not None:
				out = p
			else:
				self.cond.wait(wait_sec)
				out = self.__pop()
		return out
class MachineState:
	def __init__(self,unblock_gets=False,block_gets=False,wait_adjust=False,wait_time=1.0):
		self.unblock_gets=unblock_gets
		self.block_gets=block_gets
		self.wait_adjust=wait_adjust
		self.wait_time=wait_time
class CallException(Exception):
	pass
# class BaseData:
# 	pass
# class BaseDemo:
# 	def call(self,key):
# 		self.machine.call(key)
# 	def done_call(self):
# 		self.machine.done_call()

# 	def __init__(self,main,data):
# 		self.machine=main
# 		self.data=data

# 	# wait for implement:

# 	def update(self,gets,sec):
# 		print "update demo"
# 	def init(self):
# 		print "init demo"
# 	def finish(self):
# 		print "finish demo"
# 	def default_state(self):
# 		return MachineState(block_gets=True)
# class RunDemo(BaseDemo):
# 	def __init__(self,*args):
# 		BaseDemo.__init__(self,*args)
# 	def default_state(self):
# 		return MachineState(block_gets=True)
# 	def deal_input(self,gets):
# 		if gets == "exit":
# 			self.done_call()
# 		elif gets == "base":
# 			self.call("base")
# 		elif gets == "set":
# 			self.call("setting")
# 		else:
# 			return
# 		raise CallException()
# 	def update(self,gets,sec):
# 		self.deal_input(gets)
# 		print "RunDemo"
# def run():
# 	data=BaseData()
# 	main=MainDemo((data,))
# 	main.regist("setting",BaseDemo)
# 	main.regist("run",RunDemo)
# 	main.call("run")
# 	main()
# 主架构，循环获取按键输入
class MainDemo(InputThread):
	def __init__(self,regist_data=(),waittime=1.0):
		InputThread.__init__(self,wait_sec=waittime)
		self.__updates = []
		self.state=MachineState(False,True,False,waittime)
		self.current_call=None
		self.call_stack=[]
		self.regist_map={}
		self.regist_data=regist_data
	def regist(self,key,value):
		self.regist_map[key]=value
	def call(self,key,state=None):
		if self.regist_map.has_key(key):
			if self.current_call is not None:
				self.call_stack.append((self.current_call,self.state))
			#regist_data=self.regist_data
			self.current_call=self.regist_map[key](self,*self.regist_data)
			if state is None:
				state=self.current_call.default_state()
			self.state=state
			self.wait_time(state.wait_time)
			self.current_call.init()
		else:
			raise Exception("No Such Key on Regist Map by Call: \""+str(key)+"\"")
	def done_call(self):
		self.current_call.finish()
		if len(self.call_stack)==0:
			self.shutdown()
			return
		dt=self.call_stack.pop()
		self.current_call=dt[0]
		self.state=dt[1]
		self.wait_time(self.state.wait_time)
	def update(self,gets,time):
		if self.current_call is None:
			print "main update",gets
			if gets == "exit":
				self.shutdown()
		else:
			self.current_call.update(gets,time)
	def init(self):
		if self.current_call is None:
			print "main init"
		else:
			self.current_call.init()
	def finish(self):
		if self.current_call is None:
			print "main finish"
		else:
			self.current_call.finish()

	def shutdown(self):
		self.running=False

	def run(self):
		#print "main start:",threading.currentThread().ident
		#self.init()
		self.running=True
		crt=True
		get=None
		import time
		_tm=time.time()
		while self.running:
			_tm=time.time()-_tm
			try:
				self.update(get,_tm)
			except CallException,e:
				pass
			_tm=time.time()
			if not self.running:
				break
			if self.state.unblock_gets:
				if crt:
					self.single_start(getch=True);
				get=InputThread.input(self)
				if get is None:
					crt=False
					continue
				crt=True
			elif self.state.block_gets:
				sys.stdout.write(":")
				self.single_start(getch=False)
				get=InputThread.input(self,time_out=False)
			elif self.state.wait_adjust:
				import time
				time.sleep(self.wait_time())
		#self.finish()
		#print "main end:",threading.currentThread().ident
	def __call__(self):
		self.run()
		
