import numpy as np 
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
		self.outs=None
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
		self.normal=None
		return out_rvs
	def learn(self,alpha,inv_n,chg_range=0.0):
		self.cnt=0.0
		inv_n*=-alpha;
		self.gamma+=self.feedbacks_gamma*inv_n
		self.beta+=self.feedbacks_beta*inv_n
