#coding=utf-8
import numpy as np 

class Value(object):
	def __init__(self, maxval, minval=0, curr = None):
		if minval > maxval:
			maxval = minval
		if curr is None:
			curr = maxval
		else:
			curr = max(minval,min(maxval,curr))
		self._max = maxval * 1.0
		self._curr= curr * 1.0
		self._min = minval * 1.0
	def __setattr__(self, name, value):
		if name == 'val':
			self._curr = max(self._min,min(value, self._max))
		if name == 'max':
			value = max(value, self._min)
			self._curr = min(value, self._curr)
			self._max = value
		if name == 'min':
			value = min(value, self._max)
			self._curr = max(value, self._curr)
			self._min = value
		return object.__setattr__(self, name, value)
	def __call__(self, val = None):
		if val is None:
			return (self._curr - self._min) / (self._max - self._min)
		else:
			if val > 1.0:
				val = 1.0
			elif val < 0.0:
				val = 0.0
			self._curr = val * (self._max - self._min) + self._min

class GObject(object):
	def __init__(self, pos, weight, volumn):
		self.pos = np.array(pos)
		self.weight = weight
		self.volumn = volumn
def Life(GObject):
	def __init__(self, gobj):
		pass