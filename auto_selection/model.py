"""Automatic numerical chart selection for two samples under one fixed objective.
Preserve the central empirical quantile contrast; never infer scientific intent.
"""
import numpy as np
from scipy.stats import gaussian_kde
from scipy.integrate import cumulative_trapezoid
FAMILIES=['Bar','Line','Scatter','Histogram','Box','Violin','Dot','Heatmap','Stacked bar','Pie / donut','Area','Bubble','Interval','Raincloud','Forest']
STRATA=['Mean summary sufficient','Quartile summary sufficient','Distribution detail required']
RANKS=np.array([0.,.25,.5,.75,1.])
def clean(x,y,paired):
 x=np.asarray(x,dtype=float);y=np.asarray(y,dtype=float)
 if x.ndim!=1 or y.ndim!=1:raise ValueError('Inputs must be one-dimensional samples.')
 if paired:
  if len(x)!=len(y):raise ValueError('Paired arrays require matching lengths.')
  v=np.isfinite(x)&np.isfinite(y);x=x[v];y=y[v]
 else:x=x[np.isfinite(x)];y=y[np.isfinite(y)]
 if min(len(x),len(y))<4:raise ValueError('At least four finite observations per sample are required.')
 return x,y

def scale(x,y):
 s=np.sqrt(((len(x)-1)*np.var(x,ddof=1)+(len(y)-1)*np.var(y,ddof=1))/(len(x)+len(y)-2))
 return float(s if s>0 else max(np.ptp(np.r_[x,y]),1.))

def grid(x,y,extra=()):
 base=np.r_[.05,.95,RANKS,np.arange(len(x))/(len(x)-1),np.arange(len(y))/(len(y)-1),np.asarray(extra).ravel()]
 base=np.r_[base,np.nextafter(base,0),np.nextafter(base,1)]
 return np.unique(base[(base>=.05)&(base<=.95)])

def profile(x,y,eta):
 p=grid(x,y);truth=np.quantile(y,p)-np.quantile(x,p);mean=y.mean()-x.mean()
 box=np.interp(p,RANKS,np.quantile(y,RANKS))-np.interp(p,RANKS,np.quantile(x,RANKS))
 eps=eta*scale(x,y);me=float(np.max(np.abs(truth-mean))/eps);be=float(np.max(np.abs(truth-box))/eps)
 k=0 if me<=1+1e-8 else (1 if be<=1+1e-8 else 2)
 return k,me,be

def sampling_resolution(x,y,paired,eta,B,seed):
 p=grid(x,y);observed=np.quantile(y,p)-np.quantile(x,p);rng=np.random.default_rng(seed);replicas=[];deviations=[]
 for _ in range(B):
  ix=rng.integers(len(x),size=len(x));iy=ix if paired else rng.integers(len(y),size=len(y));a=x[ix];b=y[iy]
  d=np.quantile(b,p)-np.quantile(a,p);m=b.mean()-a.mean();q=np.interp(p,RANKS,np.quantile(b,RANKS))-np.interp(p,RANKS,np.quantile(a,RANKS))
  deviations.append(np.max(np.abs(d-observed)));replicas.append((float(np.max(np.abs(d-m))),float(np.max(np.abs(d-q)))))
 uncertainty=float(np.quantile(deviations,.95)) if B else 0.;eps=max(eta*scale(x,y),uncertainty)
 counts=np.zeros(3,int)
 for me,be in replicas:counts[0 if me<=eps else (1 if be<=eps else 2)]+=1
 return eps,uncertainty,(counts/B).tolist() if B else None

def select(x,y,paired=False,eta=.1,bootstrap=99,seed=2026):
 if not isinstance(bootstrap,(int,np.integer)) or bootstrap<0:raise ValueError('bootstrap must be a non-negative integer.')
 if not np.isfinite(eta) or eta<=0:raise ValueError('eta must be finite and positive.')
 x,y=clean(x,y,paired);s=scale(x,y);eps,uncertainty,freq=sampling_resolution(x,y,paired,eta,bootstrap,seed);mean=y.mean()-x.mean();n=len(x)+len(y)
 candidates=[]
 def add(family,variant,N,qx,qy,breaks=()):candidates.append(dict(family=family,configuration=variant,N=N,qx=qx,qy=qy,breaks=breaks))
 for family,N,name in [('Bar',2,'Mean bars'),('Dot',2,'Mean dots'),('Interval',6,'Means with intervals'),('Forest',3,'Mean contrast with interval')]:
  add(family,name,N,lambda p:np.full(len(p),x.mean()),lambda p:np.full(len(p),y.mean()))
 bx=np.quantile(x,RANKS);by=np.quantile(y,RANKS)
 add('Box','Min-max box with mean markers',12,lambda p:np.interp(p,RANKS,bx),lambda p:np.interp(p,RANKS,by),RANKS)
 for family in ['Dot','Raincloud']+(['Scatter','Line'] if paired else []):
  add(family,'Individual observations'+(' with pairing' if paired and family in ['Scatter','Line'] else ''),n,lambda p:np.quantile(x,p),lambda p:np.quantile(y,p))
 lo=min(x.min(),y.min());hi=max(x.max(),y.max())
 if hi==lo:lo-=.5;hi+=.5
 for bins in [10,20,40]:
  edges=np.linspace(lo,hi,bins+1);fx=np.r_[0,np.cumsum(np.histogram(x,edges)[0])/len(x)];fy=np.r_[0,np.cumsum(np.histogram(y,edges)[0])/len(y)]
  for family in ['Histogram','Heatmap']:
   add(family,f'{bins} common bins',2*bins+2,lambda p,f=fx,e=edges:np.interp(p,f,e),lambda p,f=fy,e=edges:np.interp(p,f,e),np.r_[fx,fy])
 bw=max(np.std(x,ddof=1)*len(x)**(-.2),np.std(y,ddof=1)*len(y)**(-.2),.01*s)
 for points in [64,128,256]:
  z=np.linspace(lo-4*bw,hi+4*bw,points);cs=[]
  for v in [x,y]:
   f=gaussian_kde(v)(z) if np.std(v)>0 else np.exp(-.5*((z-v[0])/(.01*s))**2)
   cc=np.r_[0,cumulative_trapezoid(f,z)];cc=cc/cc[-1];cs.append(cc)
  cx,cy=cs
  add('Violin',f'{points}-point density per group',2*points+2,lambda p,c=cx,z=z:np.interp(p,c,z),lambda p,c=cy,z=z:np.interp(p,c,z),np.r_[cx,cy])
 p=grid(x,y,np.concatenate([np.asarray(c['breaks']).ravel() for c in candidates]));truth=np.quantile(y,p)-np.quantile(x,p)
 variant_rows=[]
 for c in candidates:
  err=float(np.max(np.abs(c['qy'](p)-c['qx'](p)-truth)));r=err/eps;ok=r<=1+1e-8
  variant_rows.append(dict(family=c['family'],configuration=c['configuration'],retained_values=c['N'],error=err,error_ratio=r,qualifies=ok,retention_cost=c['N']+min(r,1)/2 if ok else None))
 best=min(r['retention_cost'] for r in variant_rows if r['qualifies'])
 for r in variant_rows:r.update(score=1/r['retention_cost'] if r['qualifies'] else 0.,selected=r['qualifies'] and abs(r['retention_cost']-best)<=1e-9)
 family_rows=[]
 for f in FAMILIES:
  options=[r for r in variant_rows if r['family']==f]
  if options:
   chosen=sorted(options,key=lambda r:(not r['qualifies'],r['retention_cost'] if r['qualifies'] else r['error_ratio'],r['retained_values']))[0]
   family_rows.append(dict(**chosen,status='qualified' if chosen['qualifies'] else 'exceeds tolerance'))
  else:family_rows.append(dict(family=f,configuration='No configuration for this input schema',retained_values=None,error=None,error_ratio=None,qualifies=False,retention_cost=None,score=0.,selected=False,status='input mismatch'))
 family_rows.sort(key=lambda r:(-r['score'],r['family']))
 k,me,be=profile(x,y,eps/s)
 return dict(stratum=STRATA[k],mean_error_ratio=me,box_error_ratio=be,bootstrap_agreement=freq[k] if freq else None,bootstrap_frequencies=freq,n_x=len(x),n_y=len(y),paired=paired,scale=s,epsilon=eps,uncertainty_radius=uncertainty,resolution_floor=eta*s,eta=eta,mean_difference=float(mean),median_difference=float(np.median(y)-np.median(x)),iqr_difference=float(np.diff(np.quantile(y,[.25,.75]))[0]-np.diff(np.quantile(x,[.25,.75]))[0]),selected='; '.join(r['family'] for r in family_rows if r['selected']),score=1/best,families=family_rows,variants=variant_rows)
