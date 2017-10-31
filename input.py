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
# 主架构，循环获取按键输入
class MainDemo(InputThread):
	def push(self,new_update,auto_ct = None,readline = None):
		self.__updates.append((self.update,self.auto_continue(),self.readline()))
		self.update = new_update
		if auto_ct is not None:
			self.auto_continue(auto_ct)
		if readline is not None:
			self.readline(readline)
		self.update(None)
	def pop(self):
		if len(self.__updates) == 0 :
			return
		out = self.__updates.pop()
		self.update = out[0]
		self.auto_continue(out[1])
		self.readline(out[2])
		self.update(None)
	def clear_updates(self):
		self.__updates = []
	def __init__(self,waittime=1):
		InputThread.__init__(self,wait_sec=waittime)
		self.__auto_continue = True
		self.__readline = True
		self.__updates = []
	def update(self,gets):
		print "demo",gets
	def init(self):
		print "init"
	def finish(self):
		print "finish"
	def stop(self):
		self.running=False
	def readline(self, tf = None):
		if tf is None:
			return self.__readline
		else:
			self.__readline = tf
	def auto_continue(self,tf = None):
		if tf is None:
			return self.__auto_continue
		else:
			self.__auto_continue = tf
	def run(self):
		#print "main start:",threading.currentThread().ident
		self.init()
		self.running=True
		crt=True
		get=None
		while self.running:
			self.update(get)
			if not self.running:
				break
			if self.__auto_continue:
				if crt:
					self.single_start(getch=True);
				get=InputThread.input(self)
				if get is None:
					crt=False
					continue
				crt=True
			if self.__readline:
				sys.stdout.write(":")
				self.single_start(getch=False)
				get=InputThread.input(self,time_out=False)
		self.finish()
		#print "main end:",threading.currentThread().ident
	def __call__(self):
		self.run()
		
