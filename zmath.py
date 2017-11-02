#coding=utf-8
import numpy as np 
def normal(vc):
	l = dst(vc)
	if l != 0.0:
		l = 1.0 / l
	return vc*l
def sqrdst(vc):
	return (vc**2).sum()
def dst(vc):
	return np.sqrt(sqrdst(vc))

def vector(*args):
	return np.array(args,dtype = np.float64)
def vec_empty():
	return np.zeros(2)
def vec_rand():
	return np.random.rand(2)
class Move:
	@staticmethod
	def up():
		return np.array([0,1],dtype = np.float64)
	@staticmethod
	def down():
		return np.array([0,-1],dtype = np.float64)
	@staticmethod
	def left():
		return np.array([-1,0],dtype = np.float64)
	@staticmethod
	def right():
		return np.array([1,0],dtype = np.float64)