#coding=utf-8
def zsort(datas, prior):
	l = len(datas)
	for i in xrange(l):
		id = i 
		for j in xrange(i,l):
			if prior(datas[j],datas[id]):
				id = j 
		if id != i:
			tmp = datas[id]
			datas[id] = datas[i]
			datas[i] = tmp
	return datas 