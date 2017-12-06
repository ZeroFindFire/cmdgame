#coding=utf-8
import listnet as ln
import gpunet as gn
import trainnp as tr
from gpu import GPU
import gpuconv as gc
import bn
GPU.gpu(0)
def full():
	net=ln.ListNet()
	net.push(gn.ArrayInput,28*28)
	net.push(gn.FullNet,28*28,100)
	net.push(gn.FuncNet,gn.ReLu)
	net.push(gn.FullNet,100,10)
	net.push(gn.FuncNet,gn.SoftmaxOut)
	net.push(gn.FuncOutput,gn.DiffForSoftmax)
	train=tr.Train(net,"./digitfull.net",0.1,0.000001)
	train.work(5)
	return train
def conv():
	net=ln.ListNet()
	net.push(gc.ImageInput,1,28,28)
	cv=net.push(gc.ConvNet,1,28,28,10,3,3)
	net.push(bn.BatchNormalNet,cv.shape,0.00000001)
	d,h,w=cv.shape
	mp=net.push(gc.MaxPoolingNet,d,h,w,2,2)
	net.push(gn.FuncNet,gn.ReLu)

	d,h,w=mp.shape
	cv=net.push(gc.ConvNet,d,h,w,10*2,3,3)
	net.push(bn.BatchNormalNet,cv.shape,0.00000001)
	d,h,w=cv.shape
	mp=net.push(gc.MaxPoolingNet,d,h,w,2,2)
	net.push(gn.FuncNet,gn.ReLu)

	#net.push(gn.FuncNet,gn.ReLu)
	net.push(gn.FullNet,mp.size,10)
	net.push(gn.FuncNet,gn.SoftmaxOut)
	net.push(gn.FuncOutput,gn.DiffForSoftmax)
	train=tr.Train(net,"./digitconv.net",0.1,0.000001)
	train.work(5)
	return train
def conv_same():
	net=ln.ListNet()
	net.push(gc.ImageInput,1,28,28)
	cv=net.push(gc.ConvNet,1,28,28,10,3,3,gc.ConvNet.Same)
	net.push(bn.BatchNormalNet,cv.shape,0.00000001)
	d,h,w=cv.shape
	mp=net.push(gc.MaxPoolingNet,d,h,w,2,2)
	net.push(gn.FuncNet,gn.ReLu)

	d,h,w=mp.shape
	cv=net.push(gc.ConvNet,d,h,w,10*2,3,3,gc.ConvNet.Same)
	net.push(bn.BatchNormalNet,cv.shape,0.00000001)
	d,h,w=cv.shape
	mp=net.push(gc.MaxPoolingNet,d,h,w,2,2)
	net.push(gn.FuncNet,gn.ReLu)

	#net.push(gn.FuncNet,gn.ReLu)
	net.push(gn.FullNet,mp.size,10)
	net.push(gn.FuncNet,gn.SoftmaxOut)
	net.push(gn.FuncOutput,gn.DiffForSoftmax)
	train=tr.Train(net,"./digitconv.net",0.1,0.000001)
	train.work(5)
	return train
def go_net(sizes,num):

	net=ln.ListNet()
	insize=sizes[0]*sizes[1]*num
	net.push(gn.ArrayInput,insize)
	net.push(gn.FullNet,insize,100*num)
	net.push(bn.BatchNormalNet,[100*num],0.00000001)
	net.push(gn.FuncNet,gn.ReLu)

	net.push(gn.FullNet,100*num,100*num)
	net.push(bn.BatchNormalNet,[100*num],0.00000001)
	net.push(gn.FuncNet,gn.ReLu)



	net.push(ln.SeperateNet_Copy,2)

	pnet=ln.ListNet()
	pnet.push(gn.FullNet,100*num,10*num)
	pnet.push(bn.BatchNormalNet,[10*num],0.00000001)
	pnet.push(gn.FuncNet,gn.ReLu)
	pnet.push(gn.FullNet,10*num,sizes[0]*sizes[1]+1)
	pnet.push(bn.BatchNormalNet,[sizes[0]*sizes[1]+1],0.00000001)
	pnet.push(gn.FuncNet,gn.SigmodOut)
	pnet.push(gn.FuncOutput,gn.DiffForSigmod)

	vnet=ln.ListNet()
	vnet.push(gn.FullNet,100*num,10*num)
	vnet.push(bn.BatchNormalNet,[10*num],0.00000001)
	vnet.push(gn.FuncNet,gn.ReLu)
	vnet.push(gn.FullNet,10*num,10)
	vnet.push(bn.BatchNormalNet,[10],0.00000001)
	vnet.push(gn.FuncNet,gn.ReLu)
	vnet.push(gn.FullNet,10,1)
	vnet.push(gn.FuncNet,gn.SigmodOut)
	vnet.push(gn.FuncOutput,gn.DiffForSigmod)

	net.push(ln.MultiNet,pnet,vnet)
	train=tr.Train(net,"./go.net",0.1,0.000001)
	return train

def full_bn():
	net=ln.ListNet()
	net.push(gn.ArrayInput,28*28)
	net.push(gn.FullNet,28*28,100)
	net.push(bn.BatchNormalNet,[100],0.00000001)
	net.push(gn.FuncNet,gn.ReLu)
	net.push(gn.FullNet,100,10)
	net.push(bn.BatchNormalNet,[10],0.00000001)
	net.push(gn.FuncNet,gn.SoftmaxOut)
	net.push(gn.FuncOutput,gn.DiffForSoftmax)
	train=tr.Train(net,"./digitfull.net",0.1,0.000001)
	train.work(5)
	return train
