# encoding=utf-8
from bpnet import DataReader,DataWriter,BaseNet,InputNet,OutputNet,xrand,Demo,ObjectManager
import numpy as np
from gpu import GPU,xrands
class ImageInput(InputNet):
	def put_title(self,dt_wt):
		BaseNet.put_title(self,dt_wt)
		dt_wt.putis([self.deep,self.height,self.width])
	def put_contents(self,dt_wt):pass;
	@staticmethod
	def get_title(dt_rd):
		deep,height,width=dt_rd.getis(3);
		return ImageInput(deep,height,width);
	def get_contents(self,dt_rd):pass;
	def __init__(self,deep,height,width):
		InputNet.__init__(self);
		self.width,self.height,self.deep=width,height,deep
		self.shape = (deep,height,width)
		self.size=self.deep*self.width*self.height
	def input(self,ins):
		self.outs=np.array(ins,dtype=GPU.float)
		self.outs.shape=(self.outs.size/self.size,self.deep,self.height,self.width)
	
class FcEmpty:
	@staticmethod
	def typeupdate():
		pass
	@staticmethod
	def work(vt,out=None):
		if out is None:
			out=vt
		else:
			out[:]=vt
		return out
	@staticmethod
	def feedback(vt,rvs,out=None):
		if out is None:
			out=rvs
		else:
			out[:]=rvs
		return out
		
class MaxPoolingNet(BaseNet):
	def typeupdate(self):
		self.sums=self.sums.astype(GPU.float)
		self.outs=self.outs.astype(GPU.float)
		MaxPoolingNet.mod=None
	mod=None
	@staticmethod
	def GPUOn():
		if GPU.Load()==False:return False;
		if MaxPoolingNet.mod is not None:return True;
		MaxPoolingNet.workstr=GPU.floatstr+GPU.idstr+""" 
		//outs : numxdeep, outh  ,  outw
		//ins  : numxdeep, height, width
		//poolsize: poolh, poolw, outh, outw
		//sizes: numxdeep, height, width
		#define _poolheight poolsizes[0]
		#define _poolwidth poolsizes[1]
		#define _outheight poolsizes[2]
		#define _outwidth poolsizes[3]
		#define _num sizes[0]
		#define _height sizes[1]
		#define _width sizes[2]
		__global__ void mxpool_work(Gfloat *outs, const Gfloat *ins, const int *poolsizes, const int *sizes){
			long id = idlong();
			long total_out = _num * _outheight * _outwidth;
			if (id >= total_out) return;
			int nd_id = id % _num;
			ins = ins + nd_id * _height * _width;
			outs = outs + nd_id * _outheight * _outwidth;
			id /= _num;
			int out_h = id % _outheight;
			id /= _outheight;
			int out_w = id;
			Gfloat tmp = ins[out_h * _poolheight * _width + out_w * _poolwidth];
			for(int ih = 0; ih < _poolheight; ++ih){
				const Gfloat* tins = ins + (out_h * _poolheight + ih) * _width + out_w * _poolwidth;
				for(int iw = 0; iw < _poolwidth; ++iw){
					if (tins[iw] > tmp) {
						tmp = tins[iw];
					}
				}
			}
			outs[out_h * _outwidth + out_w] = tmp;
		}
		// backs: numxdeep, height, width
		// ins  : numxdeep, height, width
		// rvs  : numxdeep, rvsh  , rvsw
		// poolsizes: poolh, poolw, rvsh, rvsw
		// sizes: numxdeep, height, width
		__global__ void mxpool_feedback(Gfloat *backs, const Gfloat* ins, const Gfloat *rvs, const int *poolsizes, const int *sizes){
			long id = idlong();
			long total_out = _num * _outheight * _outwidth;
			if (id >= total_out) return;
			int nd_id = id % _num;
			rvs = rvs + nd_id * _outheight * _outwidth;
			ins = ins + nd_id * _height * _width;
			backs = backs + nd_id * _height * _width;
		
		
			id /= _num;
			int out_h = id % _outheight;
			id /= _outheight;
			int out_w = id;
		
			Gfloat tmp = ins[out_h * _poolheight * _width+out_w * _poolwidth];
			for(int ih = 0; ih < _poolheight; ++ih){
				const Gfloat* tins = ins + (out_h * _poolheight + ih) * _width + out_w * _poolwidth;
				for(int iw = 0; iw < _poolwidth; ++iw){
					if (tins[iw] > tmp) {
						tmp = tins[iw];
					}
				}
			}
			Gfloat rval= rvs[out_h * _poolwidth + out_w];
			for(int ih = 0; ih < _poolheight; ++ih){
				Gfloat* tbaks = backs + (out_h * _poolheight + ih) * _width + out_w * _poolwidth;
				const Gfloat* tins = ins + (out_h * _poolheight + ih) * _width + out_w * _poolwidth;
				for(int iw = 0; iw < _poolwidth; ++iw){
					if (tins[iw] == tmp) {
						tbaks[iw] = rval;
					} else {
						tbaks[iw] = 0;
					}
				}
			}
		}
		"""
		MaxPoolingNet.mod=GPU.SourceModule(MaxPoolingNet.workstr)
		MaxPoolingNet.gpu_work=MaxPoolingNet.mod.get_function("mxpool_work")
		MaxPoolingNet.gpu_feedback=MaxPoolingNet.mod.get_function("mxpool_feedback")
		return True
	def put_title(self,dt_wt):
		BaseNet.put_title(self,dt_wt)
		dt_wt.putis([self.deep,self.inwidth,self.inheight,self.poolw,self.poolh])
	@staticmethod
	def get_title(dt_rd):
		d,iw,ih,w,h=dt_rd.getis(5)
		out= MaxPoolingNet(d,iw,ih,w,h)
		return out
	def __init__(self,deep,width,height,poolw,poolh):
		BaseNet.__init__(self)
		self.poolw=poolw
		self.poolh=poolh
		self.deep=deep
		self.inwidth=width
		self.inheight=height
		self.width=(width-poolw)/poolw+1
		self.height=(height-poolh)/poolh+1
		self.size=self.width*self.height*self.deep
		self.buildshape3d()
		self.sums=np.zeros(1)
		self.outs=np.array([0],dtype=GPU.float)
		self.revs=np.array([0],dtype=GPU.float)
		self.out_rvs=np.array([0],dtype=GPU.float)
	def work(self,ins):
		num=ins.shape[0]
		sums=self.sums
		if sums.shape!=(num,self.deep,self.height,self.width):
			sums=np.zeros([num,self.deep,self.height,self.width],dtype=GPU.float)
		if self.GPUOn():
			n=GPU.subnum(sums[0].size+ins[0].size,num,7)
			curr_id=0
			while curr_id<num:
				tnum,tsums,tins=GPU.subbatch(curr_id,n,num,sums,ins)
				GPU.cal(self.gpu_work,(
					GPU.Out( tsums.reshape(tsums.size) ),
					GPU.In( tins.reshape(tins.size) ),
					GPU.In( np.array( [self.poolh, self.poolw, self.height, self.width], dtype = np.int32 ) ),
					GPU.In( np.array( [tnum*self.deep, self.inheight, self.inwidth], dtype = np.int32 ) )
					), tnum * self.deep * self.height * self.width)
				curr_id+=tnum
		else:
			for i_h in xrange(self.height):
				pos_h=i_h*self.poolh
				for i_w in xrange(self.width):
					pos_w=i_w*self.poolw
					cut_in=ins[:,:,pos_h:pos_h+self.poolh,pos_w:pos_w+self.poolw]#.reshape(num*self.deep,self.poolh,self.poolw)
					#tmp=np.array([t.max() for t in cut_in],dtype=GPU.float).reshape(num,self.deep)
					tmp = cut_in.max(axis=(2,3))
					sums[:,:,i_h,i_w]=tmp
		self.outs=sums
	def learn_forward(self,ins,first=True):
		self.work(ins)
	def learn_reverse(self,ins,reverse,first=True,l2c=0.0):
		num=reverse.shape[0]
		if l2c!=0.0:
			l2c/=num
		if len(reverse.shape)!=4:
			reverse=reverse.reshape(num,self.deep,self.height,self.width)
		self.revs=reverse
		curr_rvs=np.zeros([num,self.deep,self.inheight,self.inwidth],dtype=GPU.float)
		if self.GPUOn():
			n=GPU.subnum(curr_rvs[0].size+ins[0].size+reverse[0].size,num,7)
			curr_id=0
			while curr_id<num:
				tnum,tcurr_rvs,tins,treverse=GPU.subbatch(curr_id,n,num,curr_rvs,ins,reverse)
				GPU.cal(self.gpu_feedback,(
					GPU.Out( tcurr_rvs.reshape(tcurr_rvs.size) ),
					GPU.In( tins.reshape(tins.size) ),
					GPU.In( treverse.reshape(treverse.size) ),
					GPU.In( np.array( [self.poolh, self.poolw, self.height, self.width], dtype = np.int32 ) ),
					GPU.In( np.array( [tnum*self.deep, self.inheight, self.inwidth], dtype = np.int32 ) )
					), tnum * self.deep * self.height * self.width)
				curr_id+=tnum
		else:
			for i_h in xrange(self.height):
				pos_h=i_h*self.poolh
				for i_w in xrange(self.width):
					pos_w=i_w*self.poolw
					cut_in=ins[:,:,pos_h:pos_h+self.poolh,pos_w:pos_w+self.poolw]#.reshape(num*self.deep,self.poolh,self.poolw)
					#tmp=np.array([t==t.max() for t in cut_in],dtype=GPU.float).reshape(num,self.deep,self.poolh,self.poolw)
					tmp = cut_in.max(axis=(2,3))
					jg = cut_in == tmp.reshape(num,self.deep,1,1)
					self.tmp=tmp
					curr_rvs[:,:,pos_h:pos_h+self.poolh,pos_w:pos_w+self.poolw]=jg*reverse[:,:,i_h,i_w].reshape(num,self.deep,1,1)
		return curr_rvs

		
class AvgPoolingNet(BaseNet):
	def typeupdate(self):
		self.sums=self.sums.astype(GPU.float)
		self.outs=self.outs.astype(GPU.float)
		AvgPoolingNet.mod=None
	mod=None
	@staticmethod
	def GPUOn():
		if GPU.Load()==False:return False;
		if AvgPoolingNet.mod is not None:return True;
		AvgPoolingNet.workstr=GPU.floatstr+GPU.idstr+""" 
		//outs : numxdeep, outh  ,  outw
		//ins  : numxdeep, height, width
		//poolsize: poolh, poolw, outh, outw
		//sizes: numxdeep, height, width
		#define _poolheight poolsizes[0]
		#define _poolwidth poolsizes[1]
		#define _outheight poolsizes[2]
		#define _outwidth poolsizes[3]
		#define _num sizes[0]
		#define _height sizes[1]
		#define _width sizes[2]
		__global__ void avgpool_work(Gfloat *outs, const Gfloat *ins, const int *poolsizes, const int *sizes){
			long id = idlong();
			long total_out = _num * _outheight * _outwidth;
			if (id >= total_out) return;
			int nd_id = id % _num;
			ins = ins + nd_id * _height * _width;
			outs = outs + nd_id * _outheight * _outwidth;
			id /= _num;
			int out_h = id % _outheight;
			id /= _outheight;
			int out_w = id;
			Gfloat tmp = 0;//ins[out_h * _poolheight * _width + out_w * _poolwidth];
			for(int ih = 0; ih < _poolheight; ++ih){
				const Gfloat* tins = ins + (out_h * _poolheight + ih) * _width + out_w * _poolwidth;
				for(int iw = 0; iw < _poolwidth; ++iw){
					tmp += tins[iw];
				}
			}
			outs[out_h * _outwidth + out_w] = tmp/(_poolheight*_poolwidth);
		}
		// backs: numxdeep, height, width
		// ins  : numxdeep, height, width
		// rvs  : numxdeep, rvsh  , rvsw
		// poolsizes: poolh, poolw, rvsh, rvsw
		// sizes: numxdeep, height, width
		__global__ void avgpool_feedback(Gfloat *backs, const Gfloat* ins, const Gfloat *rvs, const int *poolsizes, const int *sizes){
			long id = idlong();
			long total_out = _num * _outheight * _outwidth;
			if (id >= total_out) return;
			int nd_id = id % _num;
			rvs = rvs + nd_id * _outheight * _outwidth;
			ins = ins + nd_id * _height * _width;
			backs = backs + nd_id * _height * _width;
		
		
			id /= _num;
			int out_h = id % _outheight;
			id /= _outheight;
			int out_w = id;
		
			Gfloat tmp = ins[out_h * _poolheight * _width+out_w * _poolwidth];
			for(int ih = 0; ih < _poolheight; ++ih){
				const Gfloat* tins = ins + (out_h * _poolheight + ih) * _width + out_w * _poolwidth;
				for(int iw = 0; iw < _poolwidth; ++iw){
					if (tins[iw] > tmp) {
						tmp = tins[iw];
					}
				}
			}
			Gfloat rval= rvs[out_h * _poolwidth + out_w]/(_poolheight*_poolwidth);
			for(int ih = 0; ih < _poolheight; ++ih){
				Gfloat* tbaks = backs + (out_h * _poolheight + ih) * _width + out_w * _poolwidth;
				//const Gfloat* tins = ins + (out_h * _poolheight + ih) * _width + out_w * _poolwidth;
				for(int iw = 0; iw < _poolwidth; ++iw){
					tbaks[iw] = rval;
				}
			}
		}
		"""
		AvgPoolingNet.mod=GPU.SourceModule(AvgPoolingNet.workstr)
		AvgPoolingNet.gpu_work=AvgPoolingNet.mod.get_function("avgpool_work")
		AvgPoolingNet.gpu_feedback=AvgPoolingNet.mod.get_function("avgpool_feedback")
		return True
	def put_title(self,dt_wt):
		BaseNet.put_title(self,dt_wt)
		dt_wt.putis([self.deep,self.inwidth,self.inheight,self.poolw,self.poolh])
	@staticmethod
	def get_title(dt_rd):
		d,iw,ih,w,h=dt_rd.getis(5)
		out= AvgPoolingNet(d,iw,ih,w,h)
		return out
	def __init__(self,deep,width,height,poolw,poolh):
		BaseNet.__init__(self)
		self.poolw=poolw
		self.poolh=poolh
		self.deep=deep
		self.inwidth=width
		self.inheight = height
		self.width=(width-poolw)/poolw+1
		self.height=(height-poolh)/poolh+1
		self.size=self.width*self.height*self.deep
		self.buildshape3d()
		self.sums=np.zeros(1)
		self.outs=np.array([0],dtype=GPU.float)
		self.revs=np.array([0],dtype=GPU.float)
		self.out_rvs=np.array([0],dtype=GPU.float)
	def work(self,ins):
		num=ins.shape[0]
		sums=self.sums
		if sums.shape!=(num,self.deep,self.height,self.width):
			sums=np.zeros([num,self.deep,self.height,self.width],dtype=GPU.float)
		if self.GPUOn():
			n=GPU.subnum(sums[0].size+ins[0].size,num,7)
			curr_id=0
			while curr_id<num:
				tnum,tsums,tins=GPU.subbatch(curr_id,n,num,sums,ins)
				GPU.cal(self.gpu_work,(
					GPU.Out( tsums.reshape(tsums.size) ),
					GPU.In( tins.reshape(tins.size) ),
					GPU.In( np.array( [self.poolh, self.poolw, self.height, self.width], dtype = np.int32 ) ),
					GPU.In( np.array( [tnum*self.deep, self.inheight, self.inwidth], dtype = np.int32 ) )
					), tnum * self.deep * self.height * self.width)
				curr_id+=tnum
		else:
			for i_h in xrange(self.height):
				pos_h=i_h*self.poolh
				for i_w in xrange(self.width):
					pos_w=i_w*self.poolw
					cut_in=ins[:,:,pos_h:pos_h+self.poolh,pos_w:pos_w+self.poolw]#.reshape(num*self.deep,self.poolh,self.poolw)
					#tmp=np.array([t.mean() for t in cut_in],dtype=GPU.float).reshape(num,self.deep)
					tmp = cut_in.mean(axis=(2,3))
					sums[:,:,i_h,i_w]=tmp
		self.outs=sums
	def learn_forward(self,ins,first=True):
		self.work(ins)
	def learn_reverse(self,ins,reverse,first=True,l2c=0.0):
		num=reverse.shape[0]
		if l2c!=0.0:
			l2c/=num
		if len(reverse.shape)!=4:
			reverse=reverse.reshape(num,self.deep,self.height,self.width)
		self.revs=reverse
		curr_rvs=np.zeros([num,self.deep,self.inheight,self.inwidth],dtype=GPU.float)
		if self.GPUOn():
			n=GPU.subnum(curr_rvs[0].size+ins[0].size+reverse[0].size,num,7)
			curr_id=0
			while curr_id<num:
				tnum,tcurr_rvs,tins,treverse=GPU.subbatch(curr_id,n,num,curr_rvs,ins,reverse)
				GPU.cal(self.gpu_feedback,(
					GPU.Out( tcurr_rvs.reshape(tcurr_rvs.size) ),
					GPU.In( tins.reshape(tins.size) ),
					GPU.In( treverse.reshape(treverse.size) ),
					GPU.In( np.array( [self.poolh, self.poolw, self.height, self.width], dtype = np.int32 ) ),
					GPU.In( np.array( [tnum*self.deep, self.inheight, self.inwidth], dtype = np.int32 ) )
					), tnum * self.deep * self.height * self.width)
				curr_id+=tnum
		else:
			inv=1.0/(self.poolh*self.poolw);
			for i_h in xrange(self.height):
				pos_h=i_h*self.poolh
				for i_w in xrange(self.width):
					pos_w=i_w*self.poolw
					curr_rvs[:,:,pos_h:pos_h+self.poolh,pos_w:pos_w+self.poolw]=inv*reverse[:,:,i_h,i_w].reshape(num,self.deep,1,1)
		return curr_rvs

		
class ConvNet(BaseNet):
	def typeupdate(self):
		self.filters=self.filters.astype(GPU.float)
		self.filters_feedback=self.filters_feedback.astype(GPU.float)
		self.bs=self.bs.astype(GPU.float)
		self.bs_feedback=self.bs_feedback.astype(GPU.float)
		self.outs=self.outs.astype(GPU.float)
		ConvNet.mod=None
	mod=None
	
	@staticmethod
	def GPUOn():
		if GPU.Load()==False:return False;
		if ConvNet.mod is not None:return True;
		ConvNet.workstr=GPU.floatstr+GPU.idstr+"""
		//thread_id : num  , ftnum, outheight, outwidth
		//outs   : num  , ftnum, outheight, outwidth
		//filters: ftnum, deep , fth      , ftw
		//bs     : ftnum
		//ins    : num  , deep , height   , width
		//ftsizes: ftnum, fth  , ftw      , type
		//sizes  : num  , deep , height   , width   , outh, outw
		#define _ftnum ftsizes[0]
		#define _ftheight ftsizes[1]
		#define _ftwidth ftsizes[2]
		#define _fttype ftsizes[3]
		#define _num sizes[0]
		#define _deep sizes[1]
		#define _height sizes[2]
		#define _width sizes[3]
		#define _outheight sizes[4]
		#define _outwidth sizes[5]
		#define _ftstp_h ftsizes[4]
		#define _ftstp_w ftsizes[5]
		__global__ void conv_work(Gfloat *outs, const Gfloat *filters, const Gfloat *bs, const Gfloat *ins, const int *ftsizes, const int *sizes){
			long id = idlong();
			long total_size = _num * _ftnum * _outheight * _outwidth;
			if (id >= total_size) return;
			int outw_id = id % _outwidth;
			id /= _outwidth;
			int outh_id = id % _outheight;
			id /= _outheight;
			int ftnum_id = id % _ftnum;
			id /= _ftnum;
			int num_id = id;
			filters = filters + ftnum_id * _deep * _ftheight * _ftwidth;
			ins = ins + num_id * _deep * _height * _width;
			outs = outs + (num_id * _ftnum + ftnum_id) * _outheight * _outwidth;
			//filters: deep, fh    , fw
			//ins    : deep, height, width
			//outs   : outheight, outwidth
			Gfloat tmp=0;
			if (_fttype == 0) {
				for (int ideep = 0; ideep < sizes[1]; ++ideep) {
					const Gfloat *tins = ins + ideep * _height * _width + outh_id * _ftstp_h * _width;
					const Gfloat *tfts = filters + ideep * _ftheight * _ftwidth;
					for (int ih = 0; ih < _ftheight; ++ih) {
						for (int iw = 0; iw < _ftwidth; ++iw){
							tmp += tfts[ih * _ftwidth + iw] * tins[ih * _width + outw_id * _ftstp_w +iw];
						}
					}
				}
			} else {
				//ft_num=ftsizes[0]
				//ft_height=ftsizes[1]
				//ft_width=ftsizes[2]
				//img_deep=sizes[1]
				//img_height=sizes[2]
				//img_width=sizes[3]
				//net_height=sizes[4]
				//net_width=sizes[5]
				//filters: img_deep x ft_height x ft_width
				//ins: img_deep x img_height x img_width
				//outs: net_height x net_width
				//unexam
				const int half_fth = _ftheight / 2;
				const int half_ftw = _ftwidth / 2;
				for (int ideep = 0; ideep < _deep; ++ideep) {
					const Gfloat *tins = ins + ideep * _height * _width;
					const Gfloat *tfts = filters + ideep * _ftheight * _ftwidth;
					for (int ih = 0; ih < _ftheight; ++ih) {
						int img_h = outh_id * _ftstp_h + ih - half_fth;
						if (img_h < 0 || img_h >= _height) {
							continue;
						}
						for (int iw = 0; iw < _ftwidth; ++iw) {
							int img_w = outw_id * _ftstp_w + iw - half_ftw;
							if (img_w < 0 || img_w >= _width) {
								continue;
							}
							tmp += tins[img_h * _width + img_w] * tfts[ih * _ftwidth + iw];
						}
					}
				}
			}
			outs[outh_id * _outwidth + outw_id]=tmp+bs[ftnum_id];
		}
		//single : tow kinds:
		//			1, single element in filters: ftnum*deep*fth*ftw
		//			2, single element in rvs    : num*deep*height*width
		//rvs    : num  , deep , height   , width
		//filters: ftnum, deep , fth      , ftw
		//bs_feedback     : ftnum
		//ins    : num  , deep , height   , width
		//reverse: num  , ftnum, outheight, outwidth
		//ftsizes: ftnum, fth  , ftw      , type
		//sizes  : num  , deep , height   , width   , outh, outw
		//chg_rds: chgrd, l2c
		#define _l2c chg_rds[1]
		__global__ void conv_feedback(Gfloat *rvs, Gfloat * filters_feedback, Gfloat *bs_feedback, 
			const Gfloat *reverse,
			const Gfloat *filters,
			const Gfloat *ins, 
			const int *ftsizes, const int *sizes,
			const Gfloat *chg_rds){
			long id = idlong();
			long total_ftsize = _ftnum * _deep * _ftheight * _ftwidth;
			long total_rvsize = _num * _deep * _height * _width;
			if (id >= (total_ftsize + total_rvsize)) return;
			if (id < total_ftsize) {
				const int ftw_id = id % _ftwidth;
				id /= _ftwidth;
				const int fth_id = id % _ftheight;
				id /= _ftheight;
				const int deep_id = id % _deep;
				id /= _deep;
				const int ftnum_id = id;
				Gfloat tmp = 0;
				const int half_fth = _ftheight / 2;
				const int half_ftw = _ftwidth / 2;
				for (int numi = 0; numi < _num; ++numi){
					const Gfloat *treverse = reverse + ( (numi * _ftnum + ftnum_id) * _outheight * _outwidth);
					//treverse: 
					const Gfloat *tins = ins + ( (numi * sizes[1] +deep_id) * _height * _width);
					if (_fttype == 0) {
						for (int hi = 0; hi < _outheight; ++hi) {
							for (int wi = 0; wi < _outwidth; ++wi) {
								tmp += treverse[hi * _outwidth + wi] * tins[ (hi * _ftstp_h + fth_id) * _width + wi * _ftstp_w + ftw_id];
							}
						}
					} else {
						//img_height=sizes[2]
						//img_width=sizes[3]
						//net_height=sizes[4]
						//net_width=sizes[5]
						//treverse: net_height x net_width
						//tins: img_height x img_width
						// unexam
						for (int hi = 0; hi < _outheight; ++hi) {
							int img_h = fth_id + hi * _ftstp_h - half_fth;
							if (img_h < 0 || img_h >= _height) {
								continue;
							}
							for (int wi = 0; wi < _outwidth; ++wi) {
								int img_w = ftw_id + wi * _ftstp_w - half_ftw;
								if (img_w < 0 || img_w >= _width) {
									continue;
								}
								tmp += treverse[hi* _outwidth + wi] * tins[img_h * _width +img_w];
							}
						}
					}
				}
				int ft_id = ( (ftnum_id * _deep + deep_id) * _ftheight + fth_id ) * _ftwidth + ftw_id;
				tmp += filters[ft_id] * _l2c;
				filters_feedback[ft_id] += tmp;
				if (deep_id == 0 && fth_id == 0 && ftw_id == 0) {
					tmp = 0;
					for (int numi = 0; numi < _num; ++numi) {
						const Gfloat *treverse = reverse + ( (numi * _ftnum + ftnum_id) * _outheight * _outwidth);
						for (int hi = 0; hi < _outheight; ++hi) {
							for (int wi = 0; wi < _outwidth; ++wi) {
								tmp += treverse[hi * _outwidth + wi];
							}
						}
					}
					bs_feedback[ftnum_id]+=tmp;
				}
			} else {
				id-=total_ftsize;
		//single : tow kinds:
		//			1, single element in filters: ftnum*deep*fth*ftw
		//			2, single element in rvs    : num*deep*height*width
		//rvs    : num  , deep , height   , width
		//filters: ftnum, deep , fth      , ftw
		//bs_feedback     : ftnum
		//ins    : num  , deep , height   , width
		//reverse: num  , ftnum, outheight, outwidth
		//ftsizes: ftnum, fth  , ftw      , type
		//sizes  : num  , deep , height   , width   , outh, outw
		//chg_rds: chgrd, l2c
				const int w_id = id % _width;
				id /= _width;
				const int h_id = id % _height;
				id /= _height;
				const int deep_id = id % _deep;
				id /= _deep;
				const int num_id = id;
				Gfloat tmp = 0;
				const int half_ftw = _ftwidth / 2;
				const int half_fth = _ftheight / 2;
				for (int ift = 0; ift < _ftnum; ++ift) {
					const Gfloat* treverse = reverse + (num_id * _ftnum + ift) * _outheight * _outwidth;
					const Gfloat *tfilter = filters + (ift * _deep + deep_id) * _ftheight * _ftwidth;
					if (_fttype == 0) {
						for (int ih = 0; ih < _ftheight; ++ih) {
							// int reverse_h = h_id + (_ftheight - ih - 1) - half_fth;
							//int reverse_h = h_id + (half_fth - ih - 1);
							//int reverse_h = h_id + (_ftheight -ih -1) - half_fth*2;
							int reverse_h = h_id -ih;
							if (reverse_h < 0 || reverse_h >= _outheight || reverse_h % _ftstp_h != 0) {
								continue;
							}
							reverse_h /= _ftstp_h;
							for (int iw =0; iw < _ftwidth; ++iw) {
								// int reverse_w = w_id + (_ftwidth - iw - 1) - half_ftw;
								//int reverse_w = w_id + (half_ftw - iw - 1);
								//int reverse_w = w_id + (_ftwidth - iw -1) - half_ftw*2;
								int reverse_w = w_id -iw;
								if (reverse_w < 0 || reverse_w >= _outwidth || reverse_w % _ftstp_w != 0) {
									continue;
								}
								reverse_w /= _ftstp_w;
								tmp += tfilter[ih * _ftwidth + iw] * treverse[reverse_h * _outwidth + reverse_w];
							}
						}
					} else {
						for (int ih = 0; ih < _ftheight; ++ih) {
							//int reverse_h = h_id + (half_fth - ih);
							int reverse_h = h_id + (_ftheight -ih -1) - half_fth;
							if (reverse_h < 0 || reverse_h >= _outheight || reverse_h % _ftstp_h != 0) {
								continue;
							}
							reverse_h /= _ftstp_h;
							for (int iw =0; iw < _ftwidth; ++iw) {
								//int reverse_w = w_id + (half_ftw - iw);
								int reverse_w = w_id + (_ftwidth - iw -1) - half_ftw;
								if (reverse_w < 0 || reverse_w >= _outwidth || reverse_w % _ftstp_w != 0) {
									continue;
								}
								reverse_w /= _ftstp_w;
								tmp += tfilter[ih * _ftwidth + iw] * treverse[reverse_h * _outwidth + reverse_w];
							}
							
						}
						// unexam
					}
				}
				rvs[( (num_id * _deep + deep_id) * _height + h_id) * _width + w_id]=tmp;
			}
		}
		"""
		ConvNet.mod=GPU.SourceModule(ConvNet.workstr)
		ConvNet.gpu_work=ConvNet.mod.get_function("conv_work")
		ConvNet.gpu_feedback=ConvNet.mod.get_function("conv_feedback")
		return True
	Valid=0
	Same=1
	Full=2
	def put_title(self,dt_wt):
		BaseNet.put_title(self,dt_wt)
		flter=self.filter
		dt_wt.putis([self.indeep,self.inheight,self.inwidth,flter.num,flter.w,flter.h,flter.type,flter.stp_h,flter.stp_w])
	def put_contents(self,dt_wt):
		fts=self.filters
		bs=self.bs
		dt_wt.putfs(bs.reshape(bs.size),bs.size)
		dt_wt.putfs(fts.reshape(fts.size),fts.size)
	@staticmethod
	def get_title(dt_rd):
		gts=dt_rd.getis(9)
		return ConvNet(*gts);

	def get_contents(self,dt_rd):
		fts=self.filters
		bs=self.bs
		dt_rd.getfs(bs.size,bs.reshape(bs.size))
		dt_rd.getfs(fts.size,fts.reshape(fts.size))
	
	def __init__(self,deep,width,height,num,ftw,fth,fttype=0,stp_h=1,stp_w=1):
		if fttype!=ConvNet.Valid and fttype!=ConvNet.Same:
			raise Exception("Error filter type: %d"%(fttype,))
		BaseNet.__init__(self)
		self.inwidth=width
		self.inheight=height 
		self.indeep=deep
		if fttype==ConvNet.Valid:
			self.step_width=width-ftw+1
			self.step_height=height-fth+1
		else:
			self.step_width=width #+ftw-(ftw%2==1)
			self.step_height=height #+fth-(ftw%2==1)
		self.step_width=(self.step_width+stp_w-1)/stp_w
		self.step_height=(self.step_height+stp_h-1)/stp_h
		self.width,self.height=self.step_width,self.step_height
		self.deep=num
		self.buildshape3d()
		self.size=self.width*self.height*self.deep
		self.filter=Demo()
		self.filter.num=num
		self.filter.w=ftw
		self.filter.h=fth
		self.filter.stp_h=stp_h
		self.filter.stp_w=stp_w
		self.filter.type=fttype
		fn=float(num)*float(self.width)*float(self.height)
		fn=np.sqrt(4.0/fn)
		self.fn=fn
		self.filters=xrands(fn,(num,deep,fth,ftw))
		self.bs=xrands(1.0,(num,))
		self.filters_feedback=np.zeros(self.filters.shape,dtype=GPU.float)
		self.bs_feedback=np.zeros(self.bs.shape,dtype=GPU.float)
		self.outs=np.array([0],dtype=GPU.float)
		self.out_rvs=np.array([0],dtype=GPU.float)
	def work(self,ins):
		num=ins.shape[0]
		filter=self.filter
		filters=self.filters
		bs=self.bs
		sums=np.zeros([num,filter.num,self.height,self.width], dtype = GPU.float)
		if self.GPUOn():
			n=GPU.subnum(sums[0].size+ins[0].size,num,10,filters.size+bs.size)
			curr_id=0
			while curr_id<num:
				tnum,tsums,tins=GPU.subbatch(curr_id,n,num,sums,ins)			
				GPU.cal(self.gpu_work,(
					GPU.Out(tsums.reshape(tsums.size)),
					GPU.In(filters.reshape(filters.size)),
					GPU.In(bs),
					GPU.In(tins.reshape(tins.size)),
					GPU.In(np.array([filter.num, filter.h, filter.w, filter.type,filter.stp_h,filter.stp_w], dtype = np.int32)),
					GPU.In(np.array([tnum, self.indeep, self.inheight, self.inwidth, self.height, self.width], dtype = np.int32))
				), tnum * filter.num * self.height * self.width)
				curr_id+=tnum
		else:
			#raise Exception("No complete ConvNet work in no GPU mod, Please use GPU mod")
			if filter.type==ConvNet.Valid:
				for stp_h in xrange(self.height):
					img_h = stp_h * filter.stp_h
					for stp_w in xrange(self.width):
						img_w = stp_w * filter.stp_w
						img = ins[:,:,img_h:img_h + filter.h, img_w:img_w+filter.w]
						imgshape=[img.shape[0],1]+list(img.shape[1:])
						mul = img.reshape(imgshape) * filters.reshape([1]+list(filters.shape))
						sums[:,:,stp_h,stp_w]=mul.sum(axis=(2,3,4))#.reshape(list(mul.shape[0:2])+[1,1])
			else:
				for stp_h in xrange(self.height):
					tflts=filters
					pos_h = stp_h * filter.stp_h - filter.h/2

					fbh = 0 
					fuh = filter.h
					if pos_h<0:
						fbh=filter.h + pos_h -1
						# tflts=tflts[:,:,
						# 	filter.h+pos_h-1:,:]
					if pos_h+filter.h>self.inheight:
						fuh=self.inheight-pos_h
						# tflts=tflts[:,:,
						# 	:pos_h+filter.h-self.inheight,:]
					tflts=tflts[:,:,fbh:fuh,:]
					#tph=max(pos_h,0)
					baseh=max(pos_h,0)
					uph=min(pos_h+filter.h,self.inheight)
					for stp_w in xrange(self.width):
						ttflts=tflts
						pos_w = stp_w * filter.stp_w - filter.w/2
						fbw = 0 
						fuw = filter.w
						if pos_w<0:
							fbw=filter.w+pos_w-1
						if pos_w+filter.w>self.inwidth:
							fuw=self.inwidth-pos_w
						ttflts=ttflts[:,:,:,fbw:fuw]

						# if pos_w<0:
						# 	ttflts=ttflts[:,:,:,filter.w+pos_w-1:]
						# elif pos_w+filter.w>self.inwidth:
						# 	ttflts=ttflts[:,:,:,:pos_w+filter.w-self.inwidth]
						#tpw=max(pos_w,0)
						basew=max(pos_w,0)
						upw=min(pos_w+filter.w,self.inwidth)
						img=ins[:,:,baseh:uph,basew:upw]
						imgshape=[img.shape[0],1]+list(img.shape[1:])
						mul=img.reshape(imgshape)*ttflts.reshape([1]+list(ttflts.shape))
						sums[:,:,stp_h,stp_w]=mul.sum(axis=(2,3,4))#.reshape(list(mul.shape[0:2])+[1,1])
		self.outs=sums
	def learn_forward(self,ins,first=True):
		self.work(ins)
	def learn_reverse(self,ins,reverse,first=True,l2c=0.0):
		chg_range=0.0
		reverse=self.reshape(reverse)
		num=ins.shape[0]
		if l2c!=0.0:
			l2c/=num
		filter=self.filter
		filters=self.filters
		filters_feedback=self.filters_feedback
		bs_feedback=self.bs_feedback
		if first:
			filters_feedback[:]=0
			bs_feedback[:]=0
		rvs=np.zeros(ins.shape,dtype=GPU.float)
		if self.GPUOn():
			n=GPU.subnum(rvs[0].size+ins[0].size+reverse[0].size,num,10,
				filters.size+bs_feedback.size+filters_feedback.size+2)
			curr_id=0
			while curr_id<num:
				tnum,trvs,tins,treverse=GPU.subbatch(curr_id,n,num,rvs,ins,reverse)
				GPU.cal(self.gpu_feedback,(
					GPU.Out(trvs.reshape(trvs.size)),
					GPU.InOut(filters_feedback.reshape(filters_feedback.size)),
					GPU.InOut(bs_feedback.reshape(bs_feedback.size)),
					GPU.In(treverse.reshape(treverse.size)),
					GPU.In(filters.reshape(filters.size)),
					GPU.In(tins.reshape(tins.size)),
					GPU.In(np.array([filter.num, filter.h, filter.w, filter.type,filter.stp_h,filter.stp_w], dtype = np.int32)),
					GPU.In(np.array([tnum, self.indeep, self.inheight, self.inwidth, self.height, self.width], dtype = np.int32)),
					GPU.In(np.array([chg_range, l2c], dtype = GPU.float))
				), filter.num * self.indeep * filter.h * filter.w
					+ tnum * self.indeep * self.inheight * self.inwidth)
				curr_id+=tnum
		else:
			#raise Exception("No complete ConvNet learn_reverse in no GPU mod, Please use GPU mod")
			if len(reverse.shape) != 4:
				reverse = reverse.reshape(num, filter.num, self.height, self.width)
			total_reverse=reverse.sum(axis=(0,2,3))
			bs_feedback+=total_reverse
			if filter.type==ConvNet.Valid:
				for stp_h in xrange(self.height):
					img_h = stp_h * filter.stp_h
					for stp_w in xrange(self.width):
						img_w = stp_w * filter.stp_w
						img=ins[:,:,img_h:img_h+filter.h,img_w:img_w+filter.w]
						rvt=reverse[:,:,stp_h,stp_w]
						imgshape=[img.shape[0],1]+list(img.shape[1:])
						filters_feedback+=(img.reshape(imgshape) * rvt.reshape(list(rvt.shape[0:2])+[1,1,1])).sum(axis=0)

						rvsi=rvs[:,:,img_h:img_h+filter.h,img_w:img_w+filter.w]
						#print "ft:",filters.shape 
						#print "rvsi:",rvsi.shape 
						#print "rvt:",rvt.shape 
						rvsi += (rvt.reshape(list(rvt.shape[0:2])+[1,1,1]) * filters.reshape([1]+list(filters.shape))).sum(axis=1)
			else:
				for stp_h in xrange(self.height):
					tflts=filters
					tflts_fb=filters_feedback
					pos_h = stp_h * filter.stp_h - filter.h/2
					fbh = 0 
					fuh = filter.h
					if pos_h<0:
						fbh=filter.h + pos_h -1
						# tflts=tflts[:,:,filter.h+pos_h-1:,:]
						# tflts_fb=tflts_fb[:,:,filter.h+pos_h-1:,:]
					if pos_h+filter.h>self.inheight:
						fuh=self.inheight-pos_h
						# tflts=tflts[:,:,:pos_h+filter.h-self.inheight,:]
						# tflts_fb=tflts_fb[:,:,:pos_h+filter.h-self.inheight,:]
					tflts=tflts[:,:,fbh:fuh,:]
					tflts_fb=tflts_fb[:,:,fbh:fuh,:]
					baseh=max(pos_h,0)
					uph=min(pos_h+filter.h,self.inheight)
					for stp_w in xrange(self.width):
						ttflts=tflts
						ttflts_fb=tflts_fb
						pos_w = stp_w * filter.stp_w - filter.w/2
						fbw = 0 
						fuw = filter.w
						if pos_w<0:
							fbw=filter.w+pos_w-1
						if pos_w+filter.w>self.inwidth:
							fuw=self.inwidth-pos_w
						ttflts=ttflts[:,:,:,fbw:fuw]
						ttflts_fb=ttflts_fb[:,:,:,fbw:fuw]
						basew=max(pos_w,0)
						upw=min(pos_w+filter.w,self.inwidth)
						img=ins[:,:,baseh:uph,basew:upw]
						rvt=reverse[:,:,stp_h,stp_w]
						imgshape=[img.shape[0],1]+list(img.shape[1:])
						#print "shape:",img.shape,ttflts.shape 
						ttflts_fb+=(img.reshape(imgshape) * rvt.reshape(list(rvt.shape[0:2])+[1,1,1])).sum(axis=0)

						rvsi=rvs[:,:,baseh:uph,basew:upw]
						rvsi += (rvt.reshape(list(rvt.shape[0:2])+[1,1,1]) * ttflts.reshape([1]+list(ttflts.shape))).sum(axis=1)
						#rvsi += rvt.reshape(list(rvt.shape[0:2])+[1,1,1]) * tflts
			if l2c!=0.0:
				filters_feedback+=self.filters*l2c
		return rvs
	def learn(self,alpha,inv_n,momentum=1.0):
		filters=self.filters
		feedbacks_filters=self.filters_feedback
		feedbacks_bs=self.bs_feedback
		inv_n*=-alpha;
		self.bs*=momentum
		self.filters*=momentum
		self.bs+=feedbacks_bs*inv_n;
		self.filters+=feedbacks_filters*inv_n

