#coding=utf-8
import re
import numpy as np
"""
指令获取：
模式：
order args; order args;
先用";"号进行分割
再用" "进行分割，首字符为命令，其它为参数

"""
class Order:
	epts = " \t\n\r"
	@staticmethod
	def empty(s):
		if s is None:
			return True
		for c in s:
			if not c in Order.epts:
				return False
		return True
	@staticmethod
	def trim(arr):
		out = []
		for i in arr:
			if not Order.empty(i):
				out.append(i)
		return out
	
def get_order(orders):
	ods = Order.trim(orders.split(";"))
	out = []
	for od in ods:
		crr = Order.trim(od.split(" "))
		out.append(crr)
	return out
	
def get_vec(vec):
	flt = "(\d*[\d\.]\d*)"
	mtch = "(%s\s*,\s*)"%flt
	pt = "%s+%s"%(mtch,flt)
	r=re.search(pt,vec)
	if r is None:
		return r 
	s = r.group()
	s = Order.trim(s.split(","))
	out = []
	for c in s:
		out.append(float(c))
	return np.array(out)

