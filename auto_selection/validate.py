from pathlib import Path
import json
import numpy as np
import pandas as pd
from model import select,profile,FAMILIES,STRATA
R=Path(__file__).resolve().parent/'results'
# Explicit matched empirical examples verify the hierarchy without sampling ambiguity.
x=np.linspace(-1,1,101)
a=select(x,x+.7,bootstrap=0);assert a['stratum']==STRATA[0] and 'Bar' in a['selected']
b=select(x,1.8*x,bootstrap=0);assert b['stratum']==STRATA[1] and 'Box' in b['selected']
c=select(x,np.sign(x)*np.abs(x)**.25,bootstrap=0);assert c['stratum']==STRATA[2]
# Same contrast reconstruction at every rank is the numerical objective.
y=np.sign(x)*np.abs(x)**.25
u=select(x,y);v=select(3*x+17,3*y+17)
assert u['selected']==v['selected'] and u['stratum']==v['stratum']
for r,t in zip(u['families'],v['families']):assert r['family']==t['family'] and np.isclose(r['score'],t['score'],atol=1e-5)
# Fixed development/test sampling protocol; no human performance is simulated.
rows=[];cases=[]
for mode in ['null','location','spread','shape']:
 for n in [40,160,640]:
  for rep in range(20):
   rng=np.random.default_rng(41000+10000*['null','location','spread','shape'].index(mode)+100*n+rep)
   x=rng.normal(size=n);y=rng.normal(size=n)
   if mode=='location':y+=.8
   if mode=='spread':y*=1.8
   if mode=='shape':y=(.6*y+rng.choice([-1.2,1.2],n))/np.sqrt(1.8)
   h=n//2;train=select(x[:h],y[:h],seed=100000+rep);test=select(x[h:],y[h:],seed=200000+rep);chosen=next(r for r in train['variants'] if r['selected'])
   candidates={'Automatic':next(r for r in test['variants'] if r['family']==chosen['family'] and r['configuration']==chosen['configuration']),'Always mean bars':next(r for r in test['variants'] if r['family']=='Bar'),'Always box':next(r for r in test['variants'] if r['family']=='Box'),'Raw dots':next(r for r in test['variants'] if r['family']=='Dot' and r['configuration']=='Individual observations')}
   for name,r in candidates.items():rows.append(dict(scenario=mode,n_per_group=n,replicate=rep,method=name,error_ratio=r['error_ratio'],passes=r['qualifies'],retained_values=r['retained_values'],train_stratum=train['stratum'],train_configuration=chosen['configuration']))
   cases.append(dict(scenario=mode,n=n,replicate=rep,stratum=train['stratum'],selected=train['selected']))
 print('Simulated',mode,flush=True)
d=pd.DataFrame(rows);d.to_csv(R/'simulation_holdout.csv',index=False);pd.DataFrame(cases).to_csv(R/'simulation_selections.csv',index=False)
s=d.groupby('method').agg(test_pass_rate=('passes','mean'),median_retained_values=('retained_values','median'),median_error_ratio=('error_ratio','median'));s.to_csv(R/'simulation_summary.csv')
# Check all real-case family scores, exact raw representations and truthful no-schema zeros.
f=pd.read_csv(R/'all_family_scores.csv');assert len(f)==149*15 and set(f.family)==set(FAMILIES)
assert f.score.notna().all() and np.isfinite(f.score).all() and f.score.between(0,1).all()
for key,g in f.groupby('key'):
 assert np.isclose(g[g.selected].score,g.score.max()).all() and (g[g.selected].qualifies).all();assert (g[~g.qualifies].score==0).all()
report={'status':'passed','real_comparisons':149,'family_records':len(f),'known_empirical_location_spread_shape_checks':True,'positive_affine_invariance_check':True,'simulation_datasets':240,'simulation_evaluations':len(d),'training_fraction':.5,'reader_performance_tested':False}
(R/'validation.json').write_text(json.dumps(report,indent=2));print(s.to_string());print(report)

previous=json.loads((R.parents[1]/'validation/previous_selected_sets.json').read_text()) if (R.parents[1]/'validation/previous_selected_sets.json').exists() else None
if previous:
 current=json.loads((R/'details.json').read_text())
 assert all(current[k]['selected']==v for k,v in previous.items())
 print('All 149 winning sets unchanged after removing winner normalization.')
assert np.allclose(f.loc[f.qualifies,'score'],1/f.loc[f.qualifies,'retention_cost'])
