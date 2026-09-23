"""Development stress test; generated after method design, not preregistered."""
from pathlib import Path
import json
import numpy as np,pandas as pd
from scipy.stats import norm,t,lognorm,poisson
from scipy.optimize import brentq
from model import candidates,bootstrap_draws,choose,scale,RANKS
P=Path(__file__).resolve().parents[1];R=P/'revision/results'
MODES=['null','location','spread','bimodal','skew','heavy_tail','contamination','discrete','imbalance']
p=np.linspace(.05,.95,4001)
def population(mode):
 a=norm.ppf(p);b=a.copy();s=1.
 if mode=='location':b+=.8
 if mode=='spread':b*=1.8;s=np.sqrt((1+1.8**2)/2)
 if mode=='bimodal':b=np.array([brentq(lambda z:.5*norm.cdf((z+1.2)/.6)+.5*norm.cdf((z-1.2)/.6)-q,-5,5) for q in p])/np.sqrt(1.8)
 if mode=='skew':a=lognorm.ppf(p,s=.6);b=lognorm.ppf(p,s=1);s=np.sqrt(((np.exp(.36)-1)*np.exp(.36)+(np.exp(1)-1)*np.exp(1))/2)
 if mode=='heavy_tail':a=t.ppf(p,3)/np.sqrt(3);b=1.5*a;s=np.sqrt((1+2.25)/2)
 if mode=='contamination':b=np.array([brentq(lambda z:.95*norm.cdf(z)+.05*norm.cdf(z-6)-q,-7,13) for q in p]);s=np.sqrt((1+(1+.05*.95*36))/2)
 if mode=='discrete':a=poisson.ppf(p,2);b=poisson.ppf(p,3);s=np.sqrt(2.5)
 if mode=='imbalance':b*=1.8;s=np.sqrt((1+4*1.8**2)/5)
 return b-a,s
POP={m:population(m) for m in MODES}
def draw(rng,mode,n):
 ny=4*n if mode=='imbalance' else n
 x=rng.normal(size=n);y=rng.normal(size=ny)
 if mode=='location':y+=.8
 if mode in ['spread','imbalance']:y*=1.8
 if mode=='bimodal':y=(.6*y+rng.choice([-1.2,1.2],ny))/np.sqrt(1.8)
 if mode=='skew':x=np.exp(.6*x);y=np.exp(y)
 if mode=='heavy_tail':x=rng.standard_t(3,n)/np.sqrt(3);y=1.5*rng.standard_t(3,ny)/np.sqrt(3)
 if mode=='contamination':y+=6*(rng.random(ny)<.05)
 if mode=='discrete':x=rng.poisson(2,n).astype(float);y=rng.poisson(3,ny).astype(float)
 return x,y

def decode(x,y,config):
 if config=='means':return np.full(len(p),y.mean()-x.mean())
 if config=='five_number':return np.interp(p,RANKS,np.quantile(y,RANKS)-np.quantile(x,RANKS))
 if config=='raw':return np.quantile(y,p)-np.quantile(x,p)
 if config.startswith('bins_'):
  bins=int(config.split('_')[1]);lo=min(x.min(),y.min());hi=max(x.max(),y.max())
  if lo==hi:lo-=.5;hi+=.5
  edges=np.linspace(lo,hi,bins+1);cs=[np.r_[0,np.cumsum(np.histogram(v,edges)[0])/len(v)] for v in [x,y]]
  return np.interp(p,cs[1],edges)-np.interp(p,cs[0],edges)
 from scipy.stats import gaussian_kde
 from scipy.integrate import cumulative_trapezoid
 n=int(config.split('_')[1]);s=scale(x,y);lo=min(x.min(),y.min());hi=max(x.max(),y.max())
 if hi==lo:lo-=.5;hi+=.5
 bw=max(np.std(x,ddof=1)*len(x)**(-.2),np.std(y,ddof=1)*len(y)**(-.2),.01*s);z=np.linspace(lo-4*bw,hi+4*bw,n);cs=[]
 for v in [x,y]:
  logf=-.5*((z-v[0])/(.01*s))**2
  f=gaussian_kde(v)(z) if np.std(v)>0 else np.exp(logf-logf.max());cc=np.r_[0,cumulative_trapezoid(f,z)];cs.append(cc/cc[-1])
 return np.interp(p,cs[1],z)-np.interp(p,cs[0],z)
def main():
 rows=[]
 for j,mode in enumerate(MODES):
  for n in [20,80,320]:
   for rep in range(40):
    seed=9300000+j*100000+n*100+rep;rng=np.random.default_rng(seed);x,y=draw(rng,mode,n);a,b=draw(rng,mode,n)
    train=candidates(x,y);test=candidates(a,b);tb=bootstrap_draws(x,y,False,499,seed+1);vb=bootstrap_draws(a,b,False,499,seed+2)
    tau=max(.1*scale(x,y),np.quantile(tb[:,0],.95));tt=max(.1*scale(a,b),np.quantile(vb[:,0],.95));pop,s=POP[mode]
    config=choose(train,tau)['configuration'];fixed_config=choose(train,.2*s)['configuration']
    methods={'Adaptive':config,'Fixed-budget adaptive':fixed_config,'Means':'means','Five-number':'five_number','Raw':'raw','8-bin':'bins_8','8-grid density':'density_8'}
    for method,cf in methods.items():
     r=next(r for r in test if r['configuration']==cf);pop_error=np.max(abs(decode(a,b,cf)-pop))
     rows.append(dict(scenario=mode,n_A=n,n_B=len(y),replicate=rep,seed=seed,method=method,configuration=cf,N=r['N'],error=r['error'],train_tolerance=tau,test_tolerance=tt,passes_reestimated=r['error']<=tt,passes_frozen=r['error']<=tau,passes_fixed=r['error']<=.2*s,population_error=pop_error/s,population_pass=pop_error<=.2*s))
   print(mode,n,'done',flush=True)
 d=pd.DataFrame(rows);d.to_csv(R/'simulation_cases.csv',index=False)
 d.groupby('method').agg(cases=('seed','size'),reestimated=('passes_reestimated','mean'),frozen=('passes_frozen','mean'),fixed=('passes_fixed','mean'),population=('population_pass','mean'),median_N=('N','median'),median_population_error=('population_error','median')).to_csv(R/'simulation_summary.csv')
 d.groupby(['method','scenario','n_A']).agg(cases=('seed','size'),reestimated=('passes_reestimated','mean'),frozen=('passes_frozen','mean'),fixed=('passes_fixed','mean'),population=('population_pass','mean'),median_N=('N','median')).to_csv(R/'simulation_stratified.csv')
 print('DONE',len(d),flush=True)

if __name__=='__main__':main()
