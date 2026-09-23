"""Independently recompute losses, audit fixed-selection isolation and empirical parity."""
from common import *
import hashlib, platform, importlib.metadata

def main():
 check={};root=ROOT
 check['input_verification']=json.loads((OUT/'input_verification.json').read_text())
 assert check['input_verification']['status']=='passed'
 old=pd.read_csv(ROOT/'benchmark_release/reference_checks/original_v3_configurations.csv');new=pd.read_csv(ROOT/'validation_v3/results/configurations.csv')
 keys=['key','candidate','H','observer','task'];z=old.merge(new,on=keys,suffixes=('_old','_new'),validate='one_to_one')
 assert len(z)==len(old)==len(new);assert np.allclose(z.loss_old,z.loss_new,atol=1e-12,rtol=0,equal_nan=True);check['original_marginal_configurations_reproduced']=len(z)
 old=pd.read_csv(ROOT/'benchmark_release/reference_checks/original_extension_configurations.csv');new=pd.read_csv(ROOT/'task_first/results/configurations.csv');keys=['key','family','H','observer'];z=old.merge(new,on=keys,suffixes=('_old','_new'),validate='one_to_one')
 assert len(z)==len(old)==len(new);assert np.allclose(z.loss_old,z.loss_new,atol=1e-12,rtol=0,equal_nan=True);check['original_extension_configurations_reproduced']=len(z)
 # Recompute the new synthetic marginal truth from saved source arrays, independently of benchmark.targets.
 cases=json.loads((OUT/'new_synthetic_inputs.json').read_text());m={c['key']:c for c in cases['marginal']};e={c['key']:c for c in cases['extension']};records=[]
 for r in pd.read_csv(OUT/'new_synthetic_marginal_decodes.csv').itertuples():
  c=m[r.key];x=np.array(c['x']);y=np.array(c['y']);scale=np.sqrt(((len(x)-1)*np.var(x,ddof=1)+(len(y)-1)*np.var(y,ddof=1))/(len(x)+len(y)-2));u=np.asarray(json.loads(r.decoded_q));v=np.array([np.quantile(x,np.arange(1,20)/20),np.quantile(y,np.arange(1,20)/20)])
  delta=u[1]-u[0];truth=v[1]-v[0]
  losses={'median':abs(delta[9]-truth[9])/scale,'spread':abs((delta[14]-delta[4])-(truth[14]-truth[4]))/scale,'five':np.mean(abs(delta[[1,4,9,14,17]]-truth[[1,4,9,14,17]]))/scale}
  for task,value in losses.items():records.append(dict(key=r.key,candidate=r.candidate,H=r.H,phase=r.phase,observer={'threshold':'hard','alpha':'soft'}[r.observer],task=task,loss=value))
 for r in pd.read_csv(OUT/'new_synthetic_extension_decodes.csv').itertuples():
  v=np.asarray(e[r.key]['values']);u=np.array(json.loads(r.decoded));value=np.nan
  if np.isfinite(r.loss):
   value=np.sum(abs(u-v))/2 if r.task=='composition' else np.mean(abs(u-v))/np.std(v,ddof=1) if r.task=='profile' else abs(u[0]-np.corrcoef(v.T)[0,1])/2
  records.append(dict(key=r.key,candidate=r.candidate,H=r.H,phase=r.phase,observer=r.observer,task=r.task,loss=value))
 rec=pd.DataFrame(records);saved=pd.read_csv(OUT/'new_synthetic_trials.csv');keys=['key','candidate','H','phase','observer','task'];z=rec.merge(saved,on=keys,suffixes=('_recomputed','_saved'),validate='one_to_one');assert len(z)==len(saved);assert np.allclose(z.loss_recomputed,z.loss_saved,atol=1e-12,rtol=0,equal_nan=True)
 check['new_synthetic_losses_recomputed']=len(z);check['max_loss_difference']=float(abs(z.loss_recomputed-z.loss_saved).max());check['failed_synthetic_trials']=int(saved.loss.isna().sum())
 # Elementary stability bound; valid for a fixed candidate set valid in both environments.
 configs=all_configs();bounds=[]
 for keys,q in configs.groupby(['key','task','observer','kind']):
  p=q.pivot(index='candidate',columns='H',values='loss')
  if p.isna().any().any():continue
  chosen=choose(p[256],order_for(keys[1]));eps=float(abs(p[384]-p[256]).max());reg=float(p.loc[chosen,384]-p[384].min());assert reg<=2*eps+TOL+1e-12
  bounds.append(dict(key=keys[0],task=keys[1],observer=keys[2],kind=keys[3],epsilon=eps,regret=reg,bound=2*eps+TOL))
 pd.DataFrame(bounds).to_csv(OUT/'stability_bounds.csv',index=False);check['stability_bounds_verified']=len(bounds)
 check['default_checks']=json.loads((OUT/'default_checks.json').read_text());check['geometry_checks']=json.loads((OUT/'geometry_checks.json').read_text());check['status']='passed';check['python']=platform.python_version();check['dependencies']={p:importlib.metadata.version(p) for p in ['numpy','pandas','scipy','matplotlib','Pillow','pypdf']}
 check['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'benchmark_release').glob('*.py'))};(OUT/'verification.json').write_text(json.dumps(check,indent=2));print(json.dumps(check,indent=2))
if __name__=='__main__':main()
