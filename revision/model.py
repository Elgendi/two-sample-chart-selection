"""Resolution-dependent representation selection. No perceptual score is computed."""
import numpy as np
from scipy.stats import gaussian_kde
from scipy.integrate import cumulative_trapezoid
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from legacy_model import clean,scale
STRATA=['Mean','Quartiles','Distribution']
RANKS=np.array([0,.25,.5,.75,1.])
def grid(x,y,band=(.05,.95),extra=()):
 p=np.r_[band,np.arange(len(x))/(len(x)-1),np.arange(len(y))/(len(y)-1),RANKS,np.asarray(extra).ravel()]
 p=np.r_[p,np.nextafter(p,0),np.nextafter(p,1)]
 return np.unique(p[(p>=band[0])&(p<=band[1])])
def bootstrap_draws(x,y,paired=False,B=999,seed=20260920,band=(.05,.95)):
 p=grid(x,y,band); target=np.quantile(y,p)-np.quantile(x,p)
 rng=np.random.default_rng(seed);out=[]
 for start in range(0,B,64):
  m=min(64,B-start);ix=rng.integers(len(x),size=(m,len(x)));iy=ix if paired else rng.integers(len(y),size=(m,len(y)))
  a=x[ix];b=y[iy];qa=np.quantile(a,p,axis=1).T;qb=np.quantile(b,p,axis=1).T;d=qb-qa
  aq=np.quantile(a,RANKS,axis=1).T;bq=np.quantile(b,RANKS,axis=1).T
  box=np.array([np.interp(p,RANKS,q) for q in bq-aq]);mean=b.mean(axis=1)-a.mean(axis=1)
  out.append(np.c_[np.max(abs(d-target),axis=1),np.max(abs(d-mean[:,None]),axis=1),np.max(abs(d-box),axis=1)])
 return np.vstack(out)
def candidates(x,y,band=(.05,.95),catalogue='balanced'):
 """Count scalar payloads under explicit decoders; counts are not reader effort."""
 x,y=clean(x,y,False);rows=[]
 def add(name,config,N,qx,qy,knots=()):
  p=grid(x,y,band,knots);err=np.max(abs(qy(p)-qx(p)-(np.quantile(y,p)-np.quantile(x,p))))
  rows.append(dict(representation=name,configuration=config,N=int(N),error=float(err)))
 add('Means','means',2,lambda p:np.full(len(p),x.mean()),lambda p:np.full(len(p),y.mean()))
 a=np.quantile(x,RANKS);b=np.quantile(y,RANKS)
 add('Five-number','five_number',10,lambda p:np.interp(p,RANKS,a),lambda p:np.interp(p,RANKS,b),RANKS)
 add('Observations','raw',len(x)+len(y),lambda p:np.quantile(x,p),lambda p:np.quantile(y,p))
 lo=min(x.min(),y.min());hi=max(x.max(),y.max())
 if hi==lo:lo-=.5;hi+=.5
 bins_list=[4,8,16,32,64] if catalogue=='balanced' else [10,20,40]
 for n in bins_list:
  edges=np.linspace(lo,hi,n+1);fx=np.r_[0,np.cumsum(np.histogram(x,edges)[0])/len(x)];fy=np.r_[0,np.cumsum(np.histogram(y,edges)[0])/len(y)]
  add('Binned',f'bins_{n}',2*n+2,lambda p,f=fx:np.interp(p,f,edges),lambda p,f=fy:np.interp(p,f,edges),np.r_[fx,fy])
 s=scale(x,y);bw=max(np.std(x,ddof=1)*len(x)**(-.2),np.std(y,ddof=1)*len(y)**(-.2),.01*s)
 ks=[gaussian_kde(v) if np.std(v)>0 else None for v in [x,y]]
 for n in ([8,16,32,64,128,256] if catalogue=='balanced' else [64,128,256]):
  z=np.linspace(lo-4*bw,hi+4*bw,n);cs=[]
  for v,k in zip([x,y],ks):
   logf=-.5*((z-v[0])/(.01*s))**2 if k is None else None
   f=k(z) if k is not None else np.exp(logf-logf.max())
   cc=np.r_[0,cumulative_trapezoid(f,z)];cs.append(cc/cc[-1])
  add('Density',f'density_{n}',2*n+2,lambda p:np.interp(p,cs[0],z),lambda p:np.interp(p,cs[1],z),np.r_[cs[0],cs[1]])
 return rows

def choose(rows,tau,cost_mode='payload'):
 feasible=[dict(r) for r in rows if r['error']<=tau*(1+1e-8)]
 def cost(r):
  if cost_mode=='equal':return 1
  if cost_mode=='legacy_box' and r['representation']=='Five-number':return 12
  if cost_mode=='free_parameters' and r['representation']=='Binned':return r['N']-2
  return r['N']
 win=min(feasible,key=lambda r:(cost(r),r['error']))
 return dict(win,error_ratio=win['error']/tau,cost=cost(win))
def frontier(rows):
 return [r for r in rows if not any(t['N']<=r['N'] and t['error']<=r['error'] and (t['N']<r['N'] or t['error']<r['error']) for t in rows)]
def detail(rows,tau):
 return STRATA[0] if rows[0]['error']<=tau else STRATA[1] if rows[1]['error']<=tau else STRATA[2]
def select(x,y,paired=False,B=999,seed=20260920,band=(.05,.95),percentile=.95,eta=.1):
 if not isinstance(B,(int,np.integer)) or B<1:raise ValueError('B must be a positive integer.')
 if not 0<band[0]<band[1]<1:raise ValueError('Probability interval must lie strictly inside (0, 1).')
 if not 0<percentile<1 or not np.isfinite(eta) or eta<=0:raise ValueError('Invalid percentile or resolution floor.')
 x,y=clean(x,y,paired);rows=candidates(x,y,band);draws=bootstrap_draws(x,y,paired,B,seed,band)
 tau=max(eta*scale(x,y),float(np.quantile(draws[:,0],percentile)))
 w=choose(rows,tau)
 optimal=[r for r in rows if r['N']==w['N'] and np.isclose(r['error'],w['error'],atol=1e-10,rtol=0)]
 return dict(selected=w,optimal_set=optimal,frontier=frontier(rows),detail=detail(rows,tau),tolerance=tau,scale=scale(x,y),candidates=rows)
