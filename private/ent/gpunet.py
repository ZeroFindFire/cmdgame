# encoding=utf-8
from bpnet import DataReader,DataWriter,BaseNet,InputNet,OutputNet,xrand,Demo,ObjectManager
import numpy as np
from gpu import GPU,xrands
#GPU.float=np.float64

class Sigmod(object):
	mod=None
	@staticmethod
	def typeupdate():
		Sigmod.mod=None
	@staticmethod
	def GPUOn():
		if GPU.Load()==False:return False;
		if Sigmod.mod is not None:return True;
		Sigmod.workstr=GPU.floatstr+GPU.idstr+"""
		__global__ void sigmod_work(Gfloat* out, const Gfloat* vt,int* sizes){
			int thdId=idint();
			if(thdId>=sizes[0])return;
			Gfloat rst=vt[thdId];
			rst=1.0+exp(-1.0*rst);
			rst=1.0/rst;
			out[thdId]=rst;
		}
		__global__ void sigmod_feedback(Gfloat *out, const Gfloat *vt, const Gfloat *rvs, int *sizes){
			int thdId=idint();
			if(thdId>=sizes[0])return;
			Gfloat rst=vt[thdId];
			rst=1.0+exp(-1.0*rst);
			rst=1.0/rst;
			out[thdId]=rst*(1.0-rst)*rvs[thdId];
		}
		"""
		Sigmod.mod=GPU.SourceModule(Sigmod.workstr)
		Sigmod.gpu_work=Sigmod.mod.get_function("sigmod_work")
		Sigmod.gpu_feedback=Sigmod.mod.get_function("sigmod_feedback")
		return True
	@staticmethod
	def work(vt,out=None):
		if not Sigmod.GPUOn():
			out=np.exp(-1*vt,out)
			out+=1.0
			tmp=out.reshape(1,out.size)
			tmp[0]=1.0/tmp[0]
		else:
			if out is None:
				out=np.array(vt)
				out.shape=vt.shape
			size=vt.size
			GPU.cal(Sigmod.gpu_work,(
				GPU.Out(out.reshape(size)),
				GPU.In(vt.reshape(size)),
				GPU.In(np.array([size],dtype=np.int32))
				),size)
		return out
	@staticmethod
	def feedback(vt,rvs,out=None):
		if not Sigmod.GPUOn():
			out=Sigmod.work(vt,out)
			out*=(1.0-out)
			out*=rvs
		else:
			if out is None:
				out=np.array(vt)
				out.shape=vt.shape
			size=vt.size
			GPU.cal(Sigmod.gpu_feedback,(
				GPU.Out(out.reshape(size)),
				GPU.In(vt.reshape(size)),
				GPU.In(rvs.reshape(size)),
				GPU.In(np.array([size],dtype=np.int32))
				),size)
		return out

class SigmodOut(object):
	mod=None
	@staticmethod
	def typeupdate():
		SigmodOut.mod=None
	@staticmethod
	def GPUOn():
		if GPU.Load()==False:return False;
		if SigmodOut.mod is not None:return True;
		SigmodOut.workstr=GPU.floatstr+GPU.idstr+"""
		__global__ void sigmodout_work(Gfloat* out, const Gfloat* vt,int* sizes){
			int thdId=idint();
			if(thdId>=sizes[0])return;
			Gfloat rst=vt[thdId];
			rst=1.0+exp(-1.0*rst);
			rst=1.0/rst;
			out[thdId]=rst;
		}
		__global__ void sigmodout_feedback(Gfloat *out, const Gfloat *vt, const Gfloat *rvs, int *sizes){
			int thdId=idint();
			if(thdId>=sizes[0])return;
			Gfloat rst=vt[thdId];
			rst=1.0+exp(-1.0*rst);
			rst=1.0/rst;
			out[thdId]=rst-rvs[thdId];
		}
		"""
		SigmodOut.mod=GPU.SourceModule(SigmodOut.workstr)
		SigmodOut.gpu_work=SigmodOut.mod.get_function("sigmodout_work")
		SigmodOut.gpu_feedback=SigmodOut.mod.get_function("sigmodout_feedback")
		return True
	@staticmethod
	def work(vt,out=None):
		if not SigmodOut.GPUOn():
			out=np.exp(-1*vt,out)
			out+=1.0
			tmp=out.reshape(1,out.size)
			tmp[0]=1.0/tmp[0]
		else:
			if out is None:
				out=np.array(vt)
				out.shape=vt.shape
			size=vt.size
			GPU.cal(SigmodOut.gpu_work,(
				GPU.Out(out.reshape(size)),
				GPU.In(vt.reshape(size)),
				GPU.In(np.array([size],dtype=np.int32))
				),size)
		return out
	@staticmethod
	def feedback(vt,rvs,out=None):
		if not SigmodOut.GPUOn():
			out=SigmodOut.work(vt,out)
			out-=rvs
		else:
			if out is None:
				out=np.array(vt)
				out.shape=vt.shape
			size=vt.size
			GPU.cal(SigmodOut.gpu_feedback,(
				GPU.Out(out.reshape(size)),
				GPU.In(vt.reshape(size)),
				GPU.In(rvs.reshape(size)),
				GPU.In(np.array([size],dtype=np.int32))
				),size)
		dv=1.0/len(out)
		out*=dv
		return out

class DiffForSigmod:
	@staticmethod
	def typeupdate():
		pass
	@staticmethod
	def work(outs,stds):
		#print "DiffForSigmod"
		#print outs.shape,stds.shape
		rst = stds*np.log(outs)
		#print rst.shape
		rst += (1-stds)*np.log(1-outs)
		rst *= -1
		rst /= outs.shape[0]
		#print rst.shape
		return rst
	@staticmethod
	def feedback(outs,stds):
		return stds


class ReLu(object):
	mod=None
	gpuon=False
	@staticmethod
	def typeupdate():
		ReLu.mod=None
	@staticmethod
	def GPUOn():
		if GPU.Load()==False:return False;
		if ReLu.gpuon==False:return False;
		if ReLu.mod is not None:return True;
		ReLu.workstr=GPU.floatstr+GPU.idstr+"""
		//sizes: num, netsize
		__global__ void relu_work(Gfloat* out, const Gfloat* vt,int* sizes){
			int tid=idint();
			if(tid>=sizes[0])return;
			out[tid]=vt[tid];
			if (out[tid] < 0) {
				out[tid] = 0;
			}
		}
		__global__ void relu_feedback(Gfloat *out, const Gfloat *sums, const Gfloat *rvs, int *sizes){
			int tid=idint();
			if(tid>=sizes[0])return;
			out[tid]=(sums[tid]>0.0)*rvs[tid];
		}
		"""
		ReLu.mod=GPU.SourceModule(ReLu.workstr)
		ReLu.gpu_work=ReLu.mod.get_function("relu_work")
		ReLu.gpu_feedback=ReLu.mod.get_function("relu_feedback")
		return True
	@staticmethod
	def work(vt,out=None):
		if ReLu.GPUOn():
			if out is None:
				out=np.array(vt)
			size=vt.size
			GPU.cal(ReLu.gpu_work,(
				GPU.Out(out.reshape(size)),
				GPU.In(vt.reshape(size)),
				GPU.In(np.array([size],dtype=np.int32))
				),size)
		else:
			out = np.maximum(vt,0,out)
		return out
	@staticmethod
	def feedback(sums,rvs,out=None):
		# np.greater(sums,0.0,out)
		if ReLu.GPUOn():
			if out is None:
				out=np.array(sums)
			size=sums.size
			GPU.cal(ReLu.gpu_feedback,(
				GPU.Out(out.reshape(size)),
				GPU.In(sums.reshape(size)),
				GPU.In(rvs.reshape(size)),
				GPU.In(np.array([size],dtype=np.int32))
				),size)
		else:
			if out is None:
				out=(sums>0).astype(GPU.float)
			else:
				out[:]=(sums>0)
			out*=rvs
		return out
class Softmax(object):
	mod=None
	@staticmethod
	def typeupdate():
		Softmax.mod=None
	@staticmethod
	def GPUOn():
		if GPU.Load()==False:return False;
		if Softmax.mod is not None:return True;
		Softmax.workstr=GPU.floatstr+GPU.idstr+"""
		//sizes: num, netsize
		__global__ void softmax_work(Gfloat* out, const Gfloat* vt,int* sizes){
			int tid=idint();
			if(tid>=sizes[0])return;
			out=out+(tid*sizes[1]);
			vt=vt+(tid*sizes[1]);
			int i;
			Gfloat total=0;
			for( i=0; i < sizes[1]; ++i){
				out[i]=exp(vt[i]);
				total+=out[i];
			}
			total=1.0/total;
			for( i=0; i < sizes[1]; ++i){
				out[i]*=total;
			}
		}
		__global__ void softmax_feedback(Gfloat *out, const Gfloat *vt, const Gfloat *rvs, int *sizes){
			int tid=idint();
			if(tid>=sizes[0])return;
			out=out+(tid*sizes[1]);
			vt=vt+(tid*sizes[1]);
			rvs=rvs+(tid*sizes[1]);
			int i;
			Gfloat total=0;
			for( i=0; i < sizes[1]; ++i){
				out[i]=exp(vt[i]);
				total+=out[i];
			}
			total=1.0/total;
			Gfloat rtotal=0;
			for( i=0; i < sizes[1]; ++i){
				out[i]*=total;
				rtotal+=out[i]*rvs[i];
				//out[i]*=(1.0-out[i])*rvs[i];
			}
			for( i=0; i < sizes[1]; ++i){
				out[i]*= rvs[i]- rtotal;
			}
		}
		"""
		Softmax.mod=GPU.SourceModule(Softmax.workstr)
		Softmax.gpu_work=Softmax.mod.get_function("softmax_work")
		Softmax.gpu_feedback=Softmax.mod.get_function("softmax_feedback")
		return True
	@staticmethod
	def work(vt,out=None):
		if Softmax.GPUOn():
			if out is None:
				out=np.array(vt,dtype=vt.dtype)
				out.shape=vt.shape
			size=vt.size
			GPU.cal(Softmax.gpu_work,(
				GPU.Out(out.reshape(size)),
				GPU.In(vt.reshape(size)),
				GPU.In(np.array([vt.shape[0],vt.shape[1]],dtype=np.int32))
				),vt.shape[0])
		else:
			out=np.exp(vt,out)
			for o in out:
				o/=o.sum()
		return out
	@staticmethod
	def feedback(vt,rvs,out=None):
		if Softmax.GPUOn():
			if out is None:
				out=np.array(vt,dtype=vt.dtype)
				out.shape=vt.shape
			size=vt.size
			GPU.cal(Softmax.gpu_feedback,(
				GPU.Out(out.reshape(size)),
				GPU.In(vt.reshape(size)),
				GPU.In(rvs.reshape(size)),
				GPU.In(np.array([vt.shape[0],vt.shape[1]],dtype=np.int32))
				),vt.shape[0])
		else:
			out=np.exp(vt,out)
			#out/=out.sum()
			for o in out:
				o/=o.sum()
			num=out.shape[0]
			for n in xrange(num):
				o=out[n]
				r=rvs[n]
				o*=r-((o*r).sum())
		return out
		

class FuncNet(BaseNet):
	def typeupdate(self):
		self.cal_func.typeupdate()
	def __init__(self,cal):
		BaseNet.__init__(self)
		self.cal_func=cal
	def set_cal(self,cal):
		self.cal_func=cal
	def put_title(self,dt_wt):
		BaseNet.put_title(self,dt_wt)
		ObjectManager.save(dt_wt,self.cal_func)
	@staticmethod
	def get_title(dt_rd):
		fc=ObjectManager.load(dt_rd)
		return FuncNet(fc)
	def work(self,ins):
		self.outs=self.cal_func.work(ins)
	def learn_reverse(self,ins,reverse,first=True,l2c=0.0):
		if reverse.shape!=ins.shape:
			reverse=reverse.reshape(ins.shape)
		reverse=self.cal_func.feedback(ins,reverse)
		if reverse.shape!=ins.shape:
			reverse=reverse.reshape(ins.shape)
		self.out_rvs=reverse
		return reverse

class FullNet(BaseNet):
	mod=None
	def typeupdate(self):
		FullNet.mod=None
		self.nets=self.nets.astype(GPU.float)
		self.feedbacks=self.feedbacks.astype(GPU.float)
		self.bs=self.bs.astype(GPU.float)
		self.bs_feedback=self.bs_feedback.astype(GPU.float)
		self.sums=self.sums.astype(GPU.float)
		self.outs=self.outs.astype(GPU.float)
	def put_title(self,dt_wt):
		BaseNet.put_title(self,dt_wt)
		dt_wt.puti(self.upsize)
		dt_wt.puti(self.size)
	def put_contents(self,dt_wt):
		nets=self.nets.reshape(self.nets.size);
		bs=self.bs.reshape(self.bs.size)
		nets=nets.reshape(nets.size)
		if GPU.float!=np.float32:
			dt_wt.putds(nets,nets.size)
			dt_wt.putds(bs,bs.size)
		else:
			dt_wt.putfs(nets,nets.size)
			dt_wt.putfs(bs,bs.size)
	@staticmethod
	def get_title(dt_rd):
		upsize=dt_rd.geti();
		size=dt_rd.geti();
		cal = FullNet(upsize,size)
		return cal
	def get_contents(self,dt_rd):
		nets=self.nets.reshape(self.nets.size);
		bs=self.bs.reshape(self.bs.size)
		if GPU.float!=np.float32:
			dt_rd.getds(nets.size,nets)
			dt_rd.getds(bs.size,bs)
		else:
			dt_rd.getfs(nets.size,nets)
			dt_rd.getfs(bs.size,bs)
	@staticmethod
	def GPUOn():
		if GPU.Load()==False:return False;
		if FullNet.mod != None:return True;
		FullNet.mod=GPU.SourceModule(GPU.floatstr+GPU.dotstr+"""
		#include <curand_kernel.h>
		extern "C"{
			// mx_a(ins)  : num*insize
			// mx_b(nets) : insize*size or size*insize??
			// sizes: num,insize,size
			__global__ void fullnet_work(Gfloat *sums, const Gfloat *ins, const Gfloat *nets, const Gfloat *bs , const int *sizes)
			{
				const int blkId=blockIdx.x+blockIdx.y*gridDim.x+blockIdx.z*gridDim.x*gridDim.y;
				int thdId=threadIdx.x+threadIdx.y*blockDim.x+threadIdx.z*blockDim.x*blockDim.y+blkId*blockDim.x*blockDim.y*blockDim.z;
				const int o_row=thdId/sizes[2];
				const int o_col=thdId%sizes[2];
				if (o_row>sizes[0] || o_col>sizes[2]) {
					return;
				}
				dot(sums,ins,nets,sizes,o_row,o_col);
				sums[o_row*sizes[2]+o_col]+=bs[o_col];
			}
			__global__ void fullnet_feedback(
				Gfloat *feedbacks, Gfloat *bs_feedback, Gfloat *ups,
				const Gfloat *infeedbacks,const Gfloat *inbs_feed,
				const Gfloat *ins,
				const Gfloat *nets,
				const Gfloat *reverse,
				const int *sizes,
				const Gfloat *chg_ranges)
			{
				//sizes  = [inputsize, currsize]
				//sizes  = [num, insize, size]
				//ins    = [num,insize]
				//reverse= [num,size]
				//nets   = [insize,size]
				//ups    = [num, insize]
				//tid: netsid[i,j] or upsid[i,j]
				const long blkId=blockIdx.x+blockIdx.y*gridDim.x+blockIdx.z*gridDim.x*gridDim.y;
				long thdId=threadIdx.x+threadIdx.y*blockDim.x+threadIdx.z*blockDim.x*blockDim.y+blkId*blockDim.x*blockDim.y*blockDim.z;
				int fbnum=sizes[1]*sizes[2];
				int upnum=sizes[0]*sizes[1];
				if(thdId>=(fbnum+upnum))return;
				if (thdId>=fbnum) {
					// cal for outreverse, thdId mean single input id( outreverse id)
					thdId-=fbnum;
					int nid=thdId/sizes[1];
					int inid=thdId%sizes[1];
					int szs[3]={sizes[0],sizes[2],sizes[1]};
					dotCT(ups,reverse,nets,szs,nid,inid);
				} else {
					Gfloat tmp;
					int upid=thdId/sizes[2];
					int cid=thdId%sizes[2];
					feedbacks=feedbacks+(upid*sizes[2]);
					infeedbacks=infeedbacks+(upid*sizes[2]);
					if(chg_ranges[0]==0.0){
						tmp=0;
						for( int i=0; i<sizes[0]; ++i){
							tmp+=reverse[i*sizes[2]+cid]*ins[i*sizes[1]+upid];
						}
						feedbacks[cid]=tmp+infeedbacks[cid];
						if (upid == 0) {
							tmp=0;
							for( int i=0; i<sizes[0]; ++i){
								tmp+=reverse[i*sizes[2]+cid];
							}
							bs_feedback[cid]=inbs_feed[cid]+tmp;
						}
					}else{
					    unsigned int seed = thdId+clock(); 
					    curandState s; 
					    curand_init(seed, 0, 0, &s);
					    Gfloat chg;
					    tmp=0;
						for(int i=0; i<sizes[0]; ++i){
							chg=(curand_uniform(&s)-0.5f)*chg_ranges[0]+1;
							tmp+=reverse[i*sizes[2]+cid]*ins[i*sizes[1]+upid]*chg;
						}
						feedbacks[cid]=tmp+infeedbacks[cid];
						if (upid == 0) {
							tmp=0;
							for( int i=0; i<sizes[0]; ++i){
								chg=(curand_uniform(&s)-0.5f)*chg_ranges[0]+1;
								tmp+=reverse[i*sizes[2]+cid]*chg;
							}
							bs_feedback[cid]=inbs_feed[cid]+tmp;
						}
					}
					if(chg_ranges[1]!=0.0){
						nets=nets+(upid*sizes[2]);
						feedbacks[cid]=feedbacks[cid]+nets[cid]*chg_ranges[1];
					}
				}
			}
		}
		""",no_extern_c=True)
		FullNet.gpu_work=FullNet.mod.get_function("fullnet_work")
		FullNet.gpu_feedback=FullNet.mod.get_function("fullnet_feedback")
		return True
	def __init__(self,upsize,size,rg=2.0):
		BaseNet.__init__(self)
		self.upsize = upsize
		self.size=size;
		self.feedbacks=np.zeros([upsize,size],dtype=GPU.float)
		self.bs_feedback=np.zeros([size],dtype=GPU.float)
		self.tmp_mx=np.zeros([upsize,size],dtype=GPU.float)
		if rg==0:
			tmp=max(1.0*upsize,1.0)
			rg=1.0/np.sqrt(tmp)
		self.nets=xrands(rg,(upsize,size)) 
		self.bs=xrands(rg,(size,)) 
		self.outs=np.array([0],dtype=GPU.float)
		self.sums=np.array([0],dtype=GPU.float)
		self.revs=np.array([0],dtype=GPU.float)
		self.out_rvs=np.array([0],dtype=GPU.float)
	def work(self,ins):
		nets=self.nets
		insize=self.upsize
		num=ins.size/insize
		if self.GPUOn():
			self.sums=np.zeros([num,self.size],dtype=GPU.float)
			GPU.cal(
				self.gpu_work,(
				GPU.Out(self.sums.reshape(self.sums.size)),
				GPU.In(ins.reshape(ins.size)),
				GPU.In(nets.reshape(nets.size)),
				GPU.In(self.bs),
				GPU.In(np.array([num,insize,self.size],dtype=np.int32))
				),num*self.size)
			if len(ins.shape)==1:
				self.sums=self.sums.reshape(self.sums.size)
		else:
			if len(ins.shape)!=1:
				ins=ins.reshape(num,insize)
			self.sums=np.dot(ins,nets)
			self.sums+=self.bs
		self.outs=self.sums
	def learn_reverse(self,ins,reverse,first=True,l2c=0.0):
		nets,sums,feedbacks,size=self.nets,self.sums,self.feedbacks,self.size
		chg_range=0.0
		insize=self.upsize
		num=ins.size/insize
		tmp_mx=self.tmp_mx
		bs_feedback=self.bs_feedback
		if first:
			feedbacks[:]=0
			bs_feedback[:]=0
		self.revs=reverse
		if l2c!=0.0:
			l2c/=num
		if self.GPUOn():
			out_rvs=np.zeros([num,insize],dtype=GPU.float)
			GPU.cal(self.gpu_feedback,(
				GPU.Out(feedbacks.reshape(feedbacks.size)),
				GPU.Out(bs_feedback),
				GPU.Out(out_rvs.reshape(out_rvs.size)),
				GPU.In(feedbacks.reshape(feedbacks.size)),
				GPU.In(bs_feedback),
				GPU.In(ins.reshape(ins.size)),
				GPU.In(nets.reshape(nets.size)),  
				GPU.In(reverse.reshape(reverse.size)), 
				GPU.In(np.array([num,insize,self.size],dtype=np.int32)), 
				GPU.In(np.array([chg_range,l2c],dtype=GPU.float))
				),num*insize+insize*self.size)
			self.out_rvs=out_rvs
			return out_rvs
		else:
			ins=ins.reshape(num,insize)
			for n in xrange(num):
				tmp=reverse[n]*ins[n].reshape(insize,1)
				tb=reverse[n]
				bs_feedback+=tb
				feedbacks+=tmp
			if l2c!=0.0:
				np.multiply(self.nets,l2c,tmp_mx)
				feedbacks+=tmp_mx
			self.out_rvs=np.dot(reverse,nets.T);
			return self.out_rvs
	def learn(self,alpha,inv_n,momentum=1.0):
		nets,feedbacks,size=self.nets,self.feedbacks,self.size
		inv_n*=-alpha;
		nets*=momentum
		self.bs*=momentum
		nets+=feedbacks*inv_n
		self.bs+=self.bs_feedback*inv_n

class ArrayInput(InputNet):
	def put_title(self,dt_wt):
		BaseNet.put_title(self,dt_wt)
		dt_wt.puti(self.size)
	def put_contents(self,dt_wt):pass;
	@staticmethod
	def get_title(dt_rd):
		size=dt_rd.geti();
		return ArrayInput(size);
	def get_contents(self,dt_rd):pass;
	def __init__(self,size):
		InputNet.__init__(self);
		self.size=size;
		self.buildshapeSize()
	def input(self,ins):
		#print "get ins:",ins
		#print "size:",self.size
		self.outs=np.array(ins,dtype=GPU.float)
		#print "outs.shape:",self.outs.shape
		
class SqrDiff(object):
	@staticmethod
	def typeupdate():
		pass
	@staticmethod
	def work(outs,stds):
		wk= 0.5*((outs-stds)**2)
		if len(wk.shape)>1:
			wk/=wk.shape[0]
		return wk
	@staticmethod
	def feedback(outs,stds):
		diff=(outs-stds)
		if len(diff.shape)>1:
			diff/=diff.shape[0]
		return diff


class CrossDiff(object):
	@staticmethod
	def typeupdate():
		pass
	@staticmethod
	def work(outs,stds):
		return -1*(stds*np.log(outs)+(1-stds)*np.log(1-outs))/outs.shape[0]
	@staticmethod
	def feedback(outs,stds):
		CrossDiff.outs=outs
		CrossDiff.stds=stds
		return (outs-stds)/(outs*(1-outs)*outs.shape[0])

# undoneCross

err=None
class LogDiff(object):
	@staticmethod
	def typeupdate():
		pass
	@staticmethod
	def work(outs,stds):
		wk=outs*stds+(1.0-stds)
		wk=-stds*np.log(outs)/len(outs)
		return wk
	@staticmethod
	def feedback(outs,stds):
		wk=(outs+(1.0-stds))
		wk=-stds/(wk*len(wk))
		return wk
	
class FuncOutput(OutputNet):
	def typeupdate(self):
		self.cal_func.typeupdate()
	def checkFloat(self):
		nan=np.isnan(self.invdiff).sum()
		inf=np.isinf(self.invdiff).sum()
		if nan > 0:
			print "Get Nan in Output:",nan
		if inf > 0:
			print "Get Inf in Output:",inf
		return nan+inf
	def put_title(self,dt_wt):
		BaseNet.put_title(self,dt_wt)
		dt_wt.putstring(self.cal_func.__name__)
	def set_cal(self,cal):
		self.cal_func=cal
	@staticmethod
	def get_title(dt_rd):
		cal=dt_rd.getstring()
		fc=globals()[cal]
		out= FuncOutput();
		out.cal_func=fc
		return out
	def __init__(self,cal_func=SqrDiff):
		OutputNet.__init__(self)
		self.cal_func=cal_func
		self.invdiff=np.array([0],dtype=GPU.float)
		self.outs = None
	def work(self,ins):
		self.outs = ins
	def diff(self,std):
		#print "shape:",self.outs.shape
		stds=np.array(std,dtype=GPU.float).reshape(self.outs.shape)
		return self.cal_func.work(self.outs,stds)
	def learn_reverse(self,ins,reverse,first=True,l2c=0.0):
		reverse=np.array(reverse,dtype=GPU.float)
		self.invdiff= self.cal_func.feedback(ins,reverse)
		self.stds=reverse
		return self.invdiff

class SoftmaxOut(object):
	mod=None
	@staticmethod
	def typeupdate():
		SoftmaxOut.mod=None
	@staticmethod
	def GPUOn():
		if GPU.Load()==False:return False;
		if SoftmaxOut.mod is not None:return True;
		SoftmaxOut.workstr=GPU.floatstr+GPU.idstr+"""
		//sizes: num, netsize
		__global__ void softmaxout_work(Gfloat* out, const Gfloat* vt,int* sizes){
			int tid=idint();
			if(tid>=sizes[0])return;
			out=out+(tid*sizes[1]);
			vt=vt+(tid*sizes[1]);
			int i;
			Gfloat total=0;
			for( i=0; i < sizes[1]; ++i){
				out[i]=exp(vt[i]);
				total+=out[i];
			}
			total=1.0/total;
			for( i=0; i < sizes[1]; ++i){
				out[i]*=total;
			}
		}
		__global__ void softmaxout_feedback(Gfloat *out, const Gfloat *vt, const Gfloat *rvs, int *sizes){
			int tid=idint();
			if(tid>=sizes[0])return;
			out=out+(tid*sizes[1]);
			vt=vt+(tid*sizes[1]);
			rvs=rvs+(tid*sizes[1]);
			int i;
			Gfloat total=0;
			for( i=0; i < sizes[1]; ++i){
				out[i]=exp(vt[i]);
				total+=out[i];
			}
			total=1.0/total;
			//Gfloat rtotal=0;
			for( i=0; i < sizes[1]; ++i){
				out[i]*=total;
				out[i]-=rvs[i];
			}
		}
		"""
		SoftmaxOut.mod=GPU.SourceModule(SoftmaxOut.workstr)
		SoftmaxOut.gpu_work=SoftmaxOut.mod.get_function("softmaxout_work")
		SoftmaxOut.gpu_feedback=SoftmaxOut.mod.get_function("softmaxout_feedback")
		return True
	@staticmethod
	def work(vt,out=None):
		if SoftmaxOut.GPUOn():
			if out is None:
				out=np.array(vt,dtype=vt.dtype)
				out.shape=vt.shape
			size=vt.size
			GPU.cal(SoftmaxOut.gpu_work,(
				GPU.Out(out.reshape(size)),
				GPU.In(vt.reshape(size)),
				GPU.In(np.array([vt.shape[0],vt.shape[1]],dtype=np.int32))
				),vt.shape[0])
		else:
			out=np.exp(vt,out)
			for o in out:
				o/=o.sum()
		return out
	@staticmethod
	def feedback(vt,rvs,out=None):
		if SoftmaxOut.GPUOn():
			if out is None:
				out=np.array(vt,dtype=vt.dtype)
				out.shape=vt.shape
			size=vt.size
			GPU.cal(SoftmaxOut.gpu_feedback,(
				GPU.Out(out.reshape(size)),
				GPU.In(vt.reshape(size)),
				GPU.In(rvs.reshape(size)),
				GPU.In(np.array([vt.shape[0],vt.shape[1]],dtype=np.int32))
				),vt.shape[0])
		else:
			out=np.exp(vt,out)
			for o in out:
				o/=o.sum()
			out-=rvs
		dv=1.0/len(out)
		out*=dv
		return out
class SoftmaxCross(object):
	mod=None
	@staticmethod
	def typeupdate():
		SoftmaxCross.mod=None
	@staticmethod
	def GPUOn():
		if GPU.Load()==False:return False;
		if SoftmaxCross.mod is not None:return True;
		SoftmaxCross.workstr=GPU.floatstr+GPU.idstr+"""
		//sizes: num, netsize
		__global__ void softmaxcross_work(Gfloat* out, const Gfloat* vt,int* sizes){
			int tid=idint();
			if(tid>=sizes[0])return;
			out=out+(tid*sizes[1]);
			vt=vt+(tid*sizes[1]);
			int i;
			Gfloat total=0;
			for( i=0; i < sizes[1]; ++i){
				out[i]=exp(vt[i]);
				total+=out[i];
			}
			total=1.0/total;
			for( i=0; i < sizes[1]; ++i){
				out[i]*=total;
			}
		}
		__global__ void softmaxcross_feedback(Gfloat *out, const Gfloat *vt, const Gfloat *rvs, int *sizes){
			int tid=idint();
			if(tid>=sizes[0])return;
			out=out+(tid*sizes[1]);
			vt=vt+(tid*sizes[1]);
			rvs=rvs+(tid*sizes[1]);
			int i;
			Gfloat total=0;
			Gfloat left_total = 0;
			int fb_i = 0;
			for (; rvs[fb_i] == 0.0 && fb_i < sizes[1]; ++fb_i);
			if (fb_i == sizes[1]) {
				fb_i = 0;
			}
			for( i=0; i < sizes[1]; ++i){
				out[i]=exp(vt[i]);
				total+=out[i];
				if (i != fb_i) {
					left_total += out[i];
				}
			}
			total = 1.0 / total;
			left_total = 1.0 / left_total;
			Gfloat urv = out[fb_i] * total - rvs[fb_i];
			out[fb_i] = urv;
			//urv *= 0.1;
			for( i=0; i < sizes[1]; ++i){
				if (i == fb_i) {
					continue;
				} 
				out[i] = - urv * out[i] * left_total;
			}
		}
		"""
		SoftmaxCross.mod=GPU.SourceModule(SoftmaxCross.workstr)
		SoftmaxCross.gpu_work=SoftmaxCross.mod.get_function("softmaxcross_work")
		SoftmaxCross.gpu_feedback=SoftmaxCross.mod.get_function("softmaxcross_feedback")
		return True
	@staticmethod
	def work(vt,out=None):
		if SoftmaxCross.GPUOn():
			if out is None:
				out=np.array(vt,dtype=vt.dtype)
				out.shape=vt.shape
			size=vt.size
			GPU.cal(SoftmaxCross.gpu_work,(
				GPU.Out(out.reshape(size)),
				GPU.In(vt.reshape(size)),
				GPU.In(np.array([vt.shape[0],vt.shape[1]],dtype=np.int32))
				),vt.shape[0])
		else:
			out=np.exp(vt,out)
			for o in out:
				o/=o.sum()
		return out
	@staticmethod
	def feedback(vt,rvs,out=None):
		if SoftmaxCross.GPUOn():
			if out is None:
				out=np.array(vt,dtype=vt.dtype)
				out.shape=vt.shape
			size=vt.size
			GPU.cal(SoftmaxCross.gpu_feedback,(
				GPU.Out(out.reshape(size)),
				GPU.In(vt.reshape(size)),
				GPU.In(rvs.reshape(size)),
				GPU.In(np.array([vt.shape[0],vt.shape[1]],dtype=np.int32))
				),vt.shape[0])
		else:
			out=np.exp(vt,out)
			for i in xrange(len(out)):
				o = out[i]
				r = rvs[i]
				jg = (r == 0)
				left_sum = 1.0 / (o * jg).sum()
				oi_yi = (~jg * (o / o.sum())).sum() - r.max()
				out[i] = oi_yi * (-o * jg * left_sum * 1.0 + ~jg)
		dv=1.0/len(out)
		out*=dv
		return out

class DiffForSoftmax(object):
	@staticmethod
	def typeupdate():
		pass
	@staticmethod
	def work(outs,stds):
		wk=outs*stds+(1.0-stds)
		wk=-stds*np.log(outs)/len(outs)
		return wk
	@staticmethod
	def feedback(outs,stds):
		return stds	
