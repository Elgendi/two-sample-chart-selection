"""New synthetic cases; defaults frozen from empirical data before any synthetic outcome."""
from common import *
from concurrent.futures import ProcessPoolExecutor
V=loadmod('release_v3_benchmark','validation_v3/benchmark.py')
B=loadmod('release_task_benchmark','task_first/benchmark.py')
SEED=2026092201

def generate():
 rng=np.random.default_rng(SEED);m=[];e=[]
 for regime in ['null','location','scale','skew','mixture','heavy_tail']:
  for n in [30,150]:
   for rep in range(3):
    x=rng.normal(size=n)
    if regime=='null':y=rng.normal(size=n)
    elif regime=='location':y=rng.normal(.5,1,n)
    elif regime=='scale':y=rng.normal(0,1.8,n)
    elif regime=='skew':x=rng.lognormal(0,.5,n);y=rng.lognormal(0,1,n)
    elif regime=='mixture':y=rng.choice([-1.5,1.5],n)+rng.normal(0,.4,n)
    else:x=rng.standard_t(3,n);y=.3+1.3*rng.standard_t(3,n)
    m.append(dict(key=f'new_{regime}_{n}_{rep}',dataset=regime,regime=regime,x=x.tolist(),y=y.tolist()))
 for k in [2,3,5,8]:
  for alpha in [.3,1,5]:
   for rep in range(4):e.append(dict(key=f'new_comp_{k}_{alpha}_{rep}',dataset=f'k{k}',regime=f'k{k}_a{alpha}',kind='synthetic',task='composition',values=rng.dirichlet(np.full(k,alpha)).tolist()))
 x=np.linspace(0,1,12)
 for shape in ['ramp','wave','step']:
  for amp in [.01,.1,.4]:
   for rep in range(4):
    signal=x if shape=='ramp' else np.sin(2*np.pi*x) if shape=='wave' else (x>.5).astype(float)
    values=80*(1+amp*(signal+rng.normal(0,.1,12)))
    e.append(dict(key=f'new_profile_{shape}_{amp}_{rep}',dataset=shape,regime=f'{shape}_a{amp}',kind='synthetic',task='profile',values=values.tolist()))
 for rho in [-.8,0,.8]:
  for n in [16,64,256]:
   for rep in range(4):
    values=rng.multivariate_normal([0,0],[[1,rho],[rho,1]],n)
    e.append(dict(key=f'new_assoc_{rho}_{n}_{rep}',dataset=f'r{rho}',regime=f'r{rho}_n{n}',kind='synthetic',task='association',values=values.tolist()))
 return m,e

def run_marginal(c):
 rows,decoded=V.one(c)
 rows=[r for r in rows if r['task'] in TASKS[:3]]
 for r in rows:r['observer']={'threshold':'hard','alpha':'soft'}[r['observer']]
 return rows,decoded

def main():
 frozen=pd.read_csv(OUT/'frozen_empirical_defaults.csv').set_index(['task','observer']).candidate.to_dict()
 m,e=generate();(OUT/'new_synthetic_inputs.json').write_text(json.dumps(dict(seed=SEED,marginal=m,extension=e),indent=2))
 rows=[];dec=[]
 with ProcessPoolExecutor(max_workers=4) as pool:
  for i,(r,x) in enumerate(pool.map(run_marginal,m)):
   rows.extend(r);dec.extend(x)
   if i%6==0:print('Synthetic marginal',i+1,'/',len(m),flush=True)
 pd.DataFrame(dec).to_csv(OUT/'new_synthetic_marginal_decodes.csv',index=False)
 extra=[]
 for ci,c in enumerate(e):
  for H,phases in [(256,[0,.25,.5,.75]),(384,[.125,.375,.625,.875])]:
   for f in B.FAMILIES[c['task']]:
    for phase in phases:
     im,sp=B.render(c,f,H,phase)
     for ob in ['hard','soft']:
      val=np.nan;u=[];error=''
      try:u=B.decode(im,sp,ob);val=B.loss(c,u)
      except ValueError as ex:error=str(ex)
      z=dict(key=c['key'],dataset=c['dataset'],task=c['task'],candidate=f,family=f,H=H,phase=phase,observer=ob,loss=val,error=error)
      rows.append(z);extra.append(dict(**z,decoded=json.dumps(np.asarray(u).tolist()),target=json.dumps(B.truth(c)[0].tolist()),scale=B.truth(c)[1]))
  if ci%20==0:print('Synthetic extension',ci+1,'/',len(e),flush=True)
 pd.DataFrame(extra).to_csv(OUT/'new_synthetic_extension_decodes.csv',index=False)
 d=pd.DataFrame(rows);d.to_csv(OUT/'new_synthetic_trials.csv',index=False)
 a=d.groupby(['key','dataset','task','candidate','H','observer']).agg(loss=('loss','mean'),n=('loss','count')).reset_index();a.loc[a.n!=4,'loss']=np.nan;a.to_csv(OUT/'new_synthetic_configurations.csv',index=False)
 pairs=[]
 for (task,ob,key),q in a.groupby(['task','observer','key']):
  ref=q[q.H==256].set_index('candidate').loss;test=q[q.H==384].set_index('candidate').loss
  chosen=choose(ref,order_for(task));default=frozen[(task,ob)]
  pairs.append(dict(task=task,observer=ob,key=key,dataset=q.iloc[0].dataset,selected=chosen,default=default,default_loss=test[default],selected_loss=test[chosen],gain=test[default]-test[chosen]))
 p=pd.DataFrame(pairs);p.to_csv(OUT/'new_synthetic_policies.csv',index=False)
 summary=[]
 for (task,ob),q in p.groupby(['task','observer']):
  v=q.dropna(subset=['default_loss','selected_loss']);summary.append(dict(task=task,observer=ob,cases=len(q),paired_n=len(v),default_failures=q.default_loss.isna().sum(),selected_failures=q.selected_loss.isna().sum(),default_loss=v.default_loss.mean(),selected_loss=v.selected_loss.mean(),gain=v.gain.mean(),improved=(v.gain>TOL).sum(),worsened=(v.gain< -TOL).sum(),tied=(abs(v.gain)<=TOL).sum()))
 s=pd.DataFrame(summary);s.to_csv(OUT/'new_synthetic_summary.csv',index=False);print(s.to_string(index=False))
if __name__=='__main__':main()
