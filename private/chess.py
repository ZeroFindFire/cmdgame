class Map(object):
	def __init__(self,*maps):
		if isinstance(maps,dict):
			self.maps=maps
		else:
			self.maps={}
			if len(maps)>0:
				names=maps[0]
				attrs=maps[1:]
				names=names.split(",")
				if len(attrs)!=len(names):
					raise Exception("Not pairs")
				for i in xrange(len(attrs)):
					self.maps[names[i]]=attrs[i]
		self.lnks={}
	def _rname(self,lnk):
		lnks=self.lnks
		while lnks.has_key(lnk):
			lnk=lnks[lnk]
		return lnk
	def __getattr__(self,name):
		if name=='m':
			name='maps'
		if name== "maps" or name== 'lnks':
			return object.__getattribute__(self,name)
		name=self._rname(name)
		return self.maps[name]
	def __setattr__(self,name,data):
		if name=='m':
			name='maps'
		if name== "maps" or name== 'lnks':
			return object.__setattr__(self,name,data)
		name=self._rname(name)
		self.maps[name]=data
	def __getitem__(self,name):
		name=self._rname(name)
		return self.maps[name]
	def __setitem__(self,name,data):
		name=self._rname(name)
		self.maps[name]=data
	def has_key(self,name):
		return self.maps.has_key(name)
	def _ln(self,name,lnk):
		rname=self._rname(name)
		if self.m.has_key(rname)==False:
			raise Exception("Not such attr: "+name+":"+rname)
		self.lnks[lnk]=name
		return self
	def ln(self,*attrs):
		l=len(attrs)
		if l%2!=0:
			raise Exception("Not pairs")
		for i in xrange(l/2):
			self._ln(attrs[i*2],attrs[i*2+1])
		return self
	def ls(self,lnk):
		return self._rname(lnk)
	def lns(self,str):
		return self.ln(*str.split(","))
import numpy as np
class Chess
	Empty=0
	Black=1
	White=2
def near(pos,add,size):
	rst=(pos[0]+add[0],pos[1]+add[1])
	for i in rst:
		if i<0 or i > size:
			return None
	return rst
def cnt_ept(chessboard):
	size=chessboard.shape[0]
	empty,white,black=0,0,0
	visited=np.zeros(chessboard.shape,dtype=np.bool)
	cals=((0,1),(1,0),(0,-1),(-1,0))
	for i in xrange(size):
		for j in xrange(size):
			if chessboard[i,j]==Chess.Empty and not visited[i,j]:
				tmp_cnt=0
				stk=[(i,j)]
				jg_bk,jg_wt=False,False
				while len(stk)>0:
					pos=stk.pop()
					tmp_cnt+=1
					visited[pos]=True
					for cal in cals:
						nxt=near(pos,cal,size)
						if nxt is None:continue;
						if chessboard[nxt]==Chess.Empty:
							if not visited[nxt] :
								stk.append(nxt)
						elif chessboard[nxt]==Chess.White:
							jg_wt=True
						else:
							jg_bk=True
				if jg_bk and jg_wt:
					empty+=tmp_cnt
				elif jg_bk:
					black+=tmp_cnt
				else:
					white+=tmp_cnt
	return black,white,empty



def situtation(chessboard):
	cnt=Map("black,white,empty",0,0,0).lns('black,bk,white,wt,empty,ept')
	cnt.bk+=(chessboard==Chess.Black).sum()
	cnt.wt+=(chessboard==Chess.White).sum()
	out=cnt_ept(chessboard)
	cnt.bk+=out[0]
	cnt.wt+=out[1]
	cnt.ept+=out[2]
	return cnt