import numpy as np 

# adapt:
class MemoryManager:
	mark_int=1
	mark_float=2
	mark_double=3
	remark={mark_int:np.int32,mark_float:np.float32,mark_double:np.float64}
	mark_size={mark_int:4,mark_float:4,mark_double:8}
	current_memory=0
	total_memory=1024**3
	bound_memory=3*1024**3/4
	@staticmethod
	def mem_used(*args):
		total=0
		for dt in args:
			if dt is None:
				continue
			mark=MemoryManager.get_mark(dt.dtype)
			unit_sz=mark_size[mark]
			total+=dt.size*unit_sz
		return total
	@staticmethod
	def total_used(net):
		total=0
		while net is not None:
			total+=net.memused()
			net=net.next
		return total
	@staticmethod
	def need_save():
		return current_memory>bound_memory
	@staticmethod
	def save(net):
		tnet=net
		while tnet.prev is not None:tnet=tnet.prev;
		MemoryManager.current_memory=MemoryManager.total_used(tnet)
		while net is not None and MemoryManager.need_save():
			m=net.memused()
			net.memsave()
			current_memory-=m 
			net=net.prev
	@staticmethod
	def get_mark(dtype):
		for mark in MemoryManager.remark:
			if MemoryManager.remark[mark]==dtype:
				return mark
		raise Exception("not such dtype in mark: "+str(dtype))
	@staticmethod
	def npsave(dt_wt,*args):
		l=len(args)
		dt_wt.puti(l);
		out=[]
		for i in xrange(l):
			dt=args[i]
			if dt is None:
				dt_wt.puti(0)
				continue
			li=len(dt.shape)
			dt_wt.puti(li)
			dt_wt.putis(dt.shape)
			if dt.dtype==np.float32:
				puts=dt_wt.putfs
				mark=MemoryManager.mark_float
			elif dt.dtype==np.float64:
				puts=dt_wt.putds
				mark=MemoryManager.mark_double
			elif dt.dtype==np.int32:
				puts=dt_wt.putis
				mark=MemoryManager.mark_int
			else:
				raise Exception("error save numpy dtype: "+str(dt.dtype)+" for index "+str(i))
			dt_wt.puti(mark)
			puts(dt.reshape(dt.size))
			out.append(None)
		return out
	@staticmethod
	def nprestore(dt_rd):
		l=dt_rd.geti()
		out=[]
		for i in xrange(l):
			li=dt_rd.geti()
			if li == 0:
				out.append(None)
				continue
			shape=range(li)
			dt_rd.getis(li,shape)
			mark=dt_rd.geti()
			dtype=MemoryManager.remark[mark]
			dt=np.empty(shape,dtype=mark)
			if dtype==np.float32:
				gets=dt_wt.getfs
			elif dtype==np.float64:
				gets=dt_wt.getds
			elif dtype==np.int32:
				gets=dt_wt.getis
			else:
				raise Exception("error restore numpy dtype: "+str(dt.dtype)+" for index "+str(i))
			gets(dt.size,dt.reshape(dt.size))
			out.append(dt)
		return out
class LinkNet(object):
	def memsave(self):
		pass
	def memrestore(self):
		pass
	def memused(self):
		return 0
	def checkmem(self):
		if self.memused()==0:
			self.memrestore()
#adapt done
class BatchNormalNet(LinkNet):
	@staticmethod
	def get_title(dt_rd,prev):
		epsilon=dt_rd.getf()
		return BatchNormalNet(prev,epsilon)
	def put_title(self,dt_wt):
		dt_wt.putf(self.epsilon)
	def get_contents(self,dt_rd):
			gets=dt_rd.getfs
		else:
			gets=dt_rd.getds
		gets(self.gamma.size,self.gamma.reshape(self.gamma.size))
		gets(self.beta.size,self.beta.reshape(self.beta.size))
	def put_contents(self,dt_wt):
		if gpunet.GPU.float32():
			puts=dt_wt.putfs
		else:
			puts=dt_wt.putds
		puts(self.gamma.reshape(self.gamma.size))
		puts(self.beta.reshape(self.beta.size))
	def __init__(self,prev,epsilon):
		LinkNet.__init__(self,prev)
		self.size=prev.size
		self.gamma=np.ones((prev.shape[0],),dtype=gpunet.GPU.float)
		self.beta=np.zeros((prev.shape[0],),dtype=gpunet.GPU.float)
		self.feedbacks_gamma=np.zeros((prev.shape[0],),dtype=gpunet.GPU.float)
		self.feedbacks_beta=np.zeros((prev.shape[0],),dtype=gpunet.GPU.float)
		if len(prev.shape)>1:
			self.feedbacks_gamma.shape=(prev.shape[0],1,1)
			self.feedbacks_beta.shape=(prev.shape[0],1,1)
			self.gamma.shape=(prev.shape[0],1,1)
			self.beta.shape=(prev.shape[0],1,1)
		self.E=None
		self.Var=None
		self.shape=prev.shape
		self.cnt=0.0
		self.epsilon=epsilon
	def normalization(self):
		prev=self.prev
		ins=prev.outs
		num=prev.outs.size/prev.size
		# ins: batch, deep or size [, height, width]
		if len(prev.shape)==1:
			mean=ins.mean(axis=0)
			# mean[i]=ins[:,i].mean()
		else:
			mean=ins.mean(axis=(0,2,3),keepdims=True)[0]
			# mean[i]=ins[:,i,:,:].mean()
		if len(prev.shape)==1:
			var=ins.var(axis=0)
		else:
			var=ins.var(axis=(0,2,3),keepdims=True)[0]
		if self.cnt==0.0:
			self.E=mean
			self.Var=var
			self.cnt+=num
		else:
			p=self.cnt/(self.cnt+num)
			self.E=self.E*p+mean*(1.0-p)
			self.Var=self.Var*p+var*(1.0-p)
			self.cnt+=num
		self.normal=(ins-mean)/np.sqrt(var+self.epsilon)

	def work(self):
		ins=prev.outs
		self.normal=(ins-self.E)/np.sqrt(self.Var+self.epsilon)
		self.outs=self.normal*self.gamma+self.beta
		self.normal=None
	def learn_forward(self,first=True):
		self.normalization()
		self.outs=self.normal*self.gamma+self.beta
		self.normal=None
	def learn_reverse(self,reverse,first=True,chg_range=0.0,l2c=0.0):
		if first:
			self.feedbacks_beta[:]=0
			self.feedbacks_gamma[:]=0
		if len(prev.shape)==1:
			tmp_rvs=reverse.sum(axis=0)
		else:
			tmp_rvs=reverse.sum(axis=(0,2,3),keepdims=True)[0]
		self.feedbacks_beta+=tmp_rvs
		self.normalization()
		tmp_rvs=self.normal*reverse
		if len(prev.shape)==1:
			tmp_rvs=tmp_rvs.sum(axis=0)
		else:
			tmp_rvs=tmp_rvs.sum(axis=(0,2,3),keepdims=True)[0]
		self.feedbacks_gamma+=tmp_rvs
		if l2c!=0.0:
			self.feedbacks_gamma+=l2c*self.gamma
			self.feedbacks_beta+=l2c*self.beta
		out_rvs=self.gamma*reverse
		self.outs=[]
		self.normal=None
		return out_rvs
	def learn(self,alpha,inv_n,chg_range=0.0):
		self.cnt=0.0
		inv_n*=-alpha;
		self.gamma+=self.feedbacks_gamma*inv_n
		self.beta+=self.feedbacks_beta*inv_n
