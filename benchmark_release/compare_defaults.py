"""Frozen default comparison with source/patient grouping and explicit failure accounting."""
from common import *

def main():
 d=all_configs();rows=[];folds=[];frozen=[]
 for task in TASKS:
  order=order_for(task)
  for obs in ['hard','soft']:
   a=d[(d.task==task)&(d.observer==obs)&(d.kind=='empirical')];ref=a[a.H==256];test=a[a.H==384]
   final=trained_default(ref,order);frozen.append(dict(task=task,observer=obs,candidate=final))
   unit='cluster' if task=='association' else 'dataset'
   for held in sorted(ref[unit].unique()):
    train=ref[ref[unit]!=held];default=trained_default(train,order)
    folds.append(dict(task=task,observer=obs,heldout=held,unit=unit,default=default,training_units='|'.join(sorted(train[unit].unique()))))
    for key,q in ref[ref[unit]==held].groupby('key'):
     selected=choose(q.set_index('candidate').loss,order);t=test[test.key==key].set_index('candidate');oracle=choose(t.loss,order)
     dl=t.loc[default,'loss'];sl=t.loc[selected,'loss'];ol=t.loc[oracle,'loss'];source=q.iloc[0]
     rows.append(dict(task=task,observer=obs,key=key,dataset=source.dataset,cluster=source.cluster,default=default,selected=selected,oracle=oracle,default_loss=dl,selected_loss=sl,oracle_loss=ol,gain=dl-sl,regret=sl-ol,retained=bool(np.isfinite(sl) and sl<=ol+TOL)))
 r=pd.DataFrame(rows);r.to_csv(OUT/'strong_default_cases.csv',index=False);pd.DataFrame(folds).to_csv(OUT/'strong_default_folds.csv',index=False);pd.DataFrame(frozen).to_csv(OUT/'frozen_empirical_defaults.csv',index=False)
 rng=np.random.default_rng(2026092202);summary=[]
 for (task,obs),q in r.groupby(['task','observer']):
  p=q.dropna(subset=['default_loss','selected_loss']);units=p.groupby('cluster').gain.mean() if task=='association' else p.groupby(['dataset','cluster']).gain.mean().groupby('dataset').mean()
  lo=hi=np.nan
  if len(units)>=3:
   boot=units.to_numpy()[rng.integers(0,len(units),(5000,len(units)))].mean(1);lo,hi=np.quantile(boot,[.025,.975])
  summary.append(dict(task=task,observer=obs,cases=len(q),paired_n=len(p),clusters=len(units),default_failures=q.default_loss.isna().sum(),selected_failures=q.selected_loss.isna().sum(),default_loss=balanced(p,'default_loss'),selected_loss=balanced(p,'selected_loss'),gain=units.mean(),ci_low=lo,ci_high=hi,improved=(p.gain>TOL).sum(),worsened=(p.gain< -TOL).sum(),tied=(abs(p.gain)<=TOL).sum(),retained=q.retained.sum(),mean_regret=balanced(p,'regret')))
 s=pd.DataFrame(summary);s.to_csv(OUT/'strong_default_summary.csv',index=False)
 # Validate isolation and recompute transfer directly from candidate losses.
 for f in folds:assert f['heldout'] not in f['training_units'].split('|')
 for z in r.itertuples():
  t=d[(d.key==z.key)&(d.task==z.task)&(d.observer==z.observer)&(d.H==384)].set_index('candidate')
  assert np.isclose(z.selected_loss,t.loc[z.selected,'loss'],equal_nan=True)
  assert np.isclose(z.default_loss,t.loc[z.default,'loss'],equal_nan=True)
 (OUT/'default_checks.json').write_text(json.dumps(dict(status='passed',folds=len(folds),case_observer_pairs=len(r),no_heldout_units_in_training=True,transfer_values_verified=True),indent=2))
 print(s.to_string(index=False))
if __name__=='__main__':main()
