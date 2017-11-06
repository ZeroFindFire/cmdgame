#coding=utf-8
import sys
Coding='utf-8'
import os
import platform
ossys=platform.system()
def cls():
	if ossys=="Windows":
		os.system("cls")
	else:
		os.system("clear")
import ctypes
class COORD(ctypes.Structure):
    _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

STD_OUTPUT_HANDLE= -11
std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
cls()
def top():
	dwCursorPosition = COORD()
	dwCursorPosition.X = 0
	dwCursorPosition.Y = 0
	ctypes.windll.kernel32.SetConsoleCursorPosition(std_out_handle,dwCursorPosition)
"""
Linux:
import curses
pad = curses.newpad(100, 100)
#  These loops fill the pad with letters; this is
# explained in the next section
for y in range(0, 100):
    for x in range(0, 100):
        try: pad.addch(y,x, ord('a') + (x*x+y*y) % 26 )
        except curses.error: pass

#  Displays a section of the pad in the middle of the screen
pad.refresh( 0,0, 5,5, 20,75)

"""
old_ctx = None 
def show(context,step=1,wait=0.1,decode=True,coding=None,clean=True):
	if clean:
		top()
	if not isinstance(context,list) and not isinstance(context,tuple):
		context = (context,)
	global old_ctx
	tmp = context
	if old_ctx is not None:
		l = min(len(old_ctx),len(context))
		i = 0
		out = []
		while i < l:
			oc = old_ctx[i]
			cc = context[i]
			lo = len(oc)
			lc = len(cc)
			if lo <= lc:
				out.append(cc)
			else:
				ept = ''
				for k in xrange(lo-lc):
					ept += ' '
				out.append(cc+ept)
			i+=1
		lo = len(old_ctx)
		lc = len(context)
		if lo >= lc:
			l = lo
			while i < l:
				oc = old_ctx[i]
				ept = ''
				for k in xrange(len(oc)):
					ept += ' '
				i+=1
				out.append(ept)
			out.append("                                    ")
		else:
			l = lc
			while i < l:
				out.append(context[i])
				i+=1
		context = out
	old_ctx = tmp
	if isinstance(context,list) or isinstance(context,tuple):
		tmp = ""
		for ct in context:
			tmp+=ct+"\n"
		context = tmp[:-1]
	context += '\n'
	from time import sleep
	if decode:
		if coding is not None:
			context=context.decode(coding).encode('gbk')
		else:
			context=context.decode(Coding).encode('gbk')
	if step == 0:
		sys.stdout.write(context)
		return;
	ct_mx='\x7f'
	tp=sys.getfilesystemencoding()
	i=0
	index=0
	while i < len(context):
		c=context[i]
		if c<ct_mx:
			sys.stdout.write(c)
			i+=1
		else:
			ct=context[i:i+2]
			ct=ct.decode('gbk').encode(tp)
			sys.stdout.write(ct)
			i+=2
		if c!= ' ' and step>0 and (index+1) % step == 0:
			sleep(wait)
		index+=1

if __name__ == "__main__":
	show("你好，欢迎使用本输出法...",step = 1, wait=0.2)