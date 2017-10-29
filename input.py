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
		self.curr=''
		self.cond=threading.Condition()
		self.wait_sec=wait_sec
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
	def __call__(self,time_out = True):
		return self.input(time_out)
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
# 主架构，循环获取按键输入
class MainDemo(InputThread):
	def __init__(self,waittime=1):
		InputThread.__init__(self,wait_sec=waittime)
	def update(self,gets):
		print "demo",gets
	def init(self):
		print "init"
	def finish(self):
		print "finish"
	def stop(self):
		self.running=False
	def run(self,auto_continue=True):
		self.init()
		self.running=True
		crt=True
		get=None
		while self.running:
			self.update(get)
			if auto_continue:
				if crt:
					self.single_start(getch=True);
				get=InputThread.input(self)
				if get is None:
					crt=False
					continue
				crt=True
			sys.stdout.write(":")
			self.single_start(getch=False)
			get=InputThread.input(self,time_out=False)
		self.finish()
