#coding=utf-8
import sys
Coding='utf-8'
def show(context,step=1,wait=0.1,decode=True,coding=None):
	from time import sleep
	if decode:
		if coding is not None:
			context=context.decode(coding).encode('gbk')
		else:
			context=context.decode(Coding).encode('gbk')
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
		if step>0 and (index+1) % step == 0:
			sleep(wait)
		index+=1

if __name__ == "__main__":
	show("你好，欢迎使用本输出法...",step = 1, wait=0.2)