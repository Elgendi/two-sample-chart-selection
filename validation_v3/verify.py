"""Checks tied to scientific risks: target definition, heldout leakage, transfer, identity."""
from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd
from benchmark import OUT,ROOT,PROBS,TASKS,CANDIDATES,targets,eligible,CASES,prepare,render19,decode19
A=pd.read_csv(OUT/'configurations.csv');D=pd.read_csv(OUT/'policy_results.csv');F=pd.read_csv(OUT/'folds.csv');X=pd.read_csv(OUT/'decoded_trials.csv')
assert len(A)==127*10*2*2*6 and len(X)==127*10*2*4*2
assert len(D)==127*2*6*7 and len(F)==9*2*6
assert not X.duplicated(['key','candidate','H','phase','observer']).any()
for r in F.itertuples():
 assert r.heldout_resource not in r.training_resources.split('|') and len(r.training_resources.split('|'))==8
 v=A[(A.observer==r.observer)&(A.task==r.task)&(A.H==256)&(A.dataset!=r.heldout_resource)]
 losses=v.groupby(['dataset','candidate']).loss.mean().groupby('candidate').mean();valid=v.groupby('candidate').loss.apply(lambda x:x.notna().all());losses=losses[valid]
 assert np.isclose(losses[r.candidate],losses.min(),atol=1e-12,rtol=0)
# Recompute all reported task losses from saved decoded pixels; never numerical metadata.
records=[]
for r in X.itertuples():
 q=np.array(json.loads(r.decoded_q));truth=np.array(json.loads(r.truth_q));t=targets(truth);u=targets(q)
 records.extend(dict(key=r.key,candidate=r.candidate,H=r.H,observer=r.observer,phase=r.phase,task=k,loss=np.mean(abs(u[k]-t[k]))/r.scale) for k in TASKS)
Y=pd.DataFrame(records);Y=Y.groupby(['key','candidate','H','observer','task']).agg(loss=('loss','mean'),n=('loss','count')).reset_index();Y.loc[Y.n!=4,'loss']=np.nan
Z=A.merge(Y,on=['key','candidate','H','observer','task'],suffixes=('_saved','_recomputed'),validate='one_to_one')
assert np.allclose(Z.loss_saved,Z.loss_recomputed,equal_nan=True)
# Transfer values must use the heldout display, not the in-sample minimum.
V=D.merge(A[A.H==384][['key','observer','task','candidate','loss']],on=['key','observer','task','candidate'],suffixes=('_policy','_source'),validate='many_to_one');assert np.allclose(V.loss_policy,V.loss_source,equal_nan=True)
assert D[D.rule!='zero_target'].excess_loss.min()>=-1e-12
assert len(V)==127*2*6*6
for r in D[D.rule=='zero_target'].itertuples():
 xx=X[X.key==r.key].iloc[0];expected=np.mean(abs(targets(np.array(json.loads(xx.truth_q)))[r.task]))/xx.scale;assert np.isclose(r.loss,expected)
# Pairing witness with exactly equal marginal multisets.
x=np.array([0.,1.,2.]);y0=x.copy();y1=np.array([1.,2.,0.]);assert np.array_equal(np.sort(y0),np.sort(y1));assert np.median(y0-x)==0 and np.median(y1-x)==1
# Original fixed-setting five-task parity, except no Q19 counterpart in v2.
v2=pd.read_csv(ROOT/'validation_v2/results/task_configurations.csv')
p=A[(A.H==256)&(A.task=='five')&(A.setting!='nineteen')].merge(v2[v2.task=='five'],on=['key','dataset','family','setting','observer','task'],suffixes=('_v3','_v2'),validate='one_to_one')
assert len(p)==127*9*2;assert np.allclose(p.loss_v3,p.loss_v2,atol=1e-12,rtol=0,equal_nan=True)
# Positive unit scaling and group exchange on the added control.
c=CASES[0];ctx=prepare(c['x'],c['y']);scaled=prepare(np.array(c['x'])*7,np.array(c['y'])*7);im,spec=render19(ctx,256,.25);im2,spec2=render19(scaled,256,.25)
assert np.array_equal(im,im2)
assert set(spec)=={'family','setting','H','W','lo','hi','panels'}
for ob in ['threshold','alpha']:assert np.allclose(decode19(im2,spec2,ob),7*decode19(im,spec,ob))
q=np.array([np.quantile(c[g],PROBS) for g in ['x','y']]);assert all(np.allclose(targets(q[::-1])[k],-targets(q)[k]) for k in TASKS)
# Encoding vs raster error on the two direct controls, with triangle bounds.
B=X[X.family=='Quantile plot'];encoding=[]
for r in B.itertuples():
 truth=np.array(json.loads(r.truth_q));q=np.array(json.loads(r.decoded_q));ideal=truth if r.setting=='nineteen' else np.array([np.interp(PROBS,PROBS[[1,4,9,14,17]],g[[1,4,9,14,17]]) for g in truth])
 t=targets(truth);i=targets(ideal);u=targets(q)
 for k in TASKS:
  total=np.mean(abs(u[k]-t[k]))/r.scale;enc=np.mean(abs(i[k]-t[k]))/r.scale;ras=np.mean(abs(u[k]-i[k]))/r.scale
  if np.isfinite(total):assert abs(enc-ras)-1e-12<=total<=enc+ras+1e-12
  encoding.append(dict(key=r.key,dataset=r.dataset,observer=r.observer,H=r.H,phase=r.phase,setting=r.setting,task=k,total=total,encoding=enc,raster=ras))
E=pd.DataFrame(encoding);E.to_csv(OUT/'quantile_error_decomposition.csv',index=False)
E.groupby(['observer','H','setting','task','dataset'])[['total','encoding','raster']].mean().groupby(['observer','H','setting','task']).mean().to_csv(OUT/'quantile_error_summary.csv')
result=dict(status='passed',configurations=len(A),decoded_trials=len(X),task_loss_recomputations=len(Y),original_five_task_matches=len(p),heldout_folds_verified=len(F),policy_transfer_values_verified=len(V),pairing_witness={'x':x.tolist(),'y_aligned':y0.tolist(),'y_permuted':y1.tolist(),'median_changes':[0,1]},unit_scaling_passed=True,metadata_check_passed=True,encoding_triangle_bounds_passed=True,source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'validation_v3').glob('*.py'))})
(OUT/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
