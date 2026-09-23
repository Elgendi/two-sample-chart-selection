from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd
from concurrent.futures import ProcessPoolExecutor
from observer import prepare,render,decode,P,FIXED
from task_decoders import decode_threshold_at,decode_alpha_at
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'validation_v2/results';DENSE=np.arange(1,20)/20
CASES=[c for c in json.loads((ROOT/'data/derived/comparisons.json').read_text()) if c['dataset']!='Parkinsons']
def ecdf_at(im,spec,obs,probs):
 a=np.asarray(im,float);out=[]
 for panel in spec['panels']:
  L,R,T,B=[panel[k] for k in ['L','R','T','B']];patch=a[int(T):int(B)+1,int(L):int(R)+1];col=np.array(panel['color'])
  alpha=np.clip(((255-patch)@(255-col))/np.sum((255-col)**2),0,1)
  ink=(np.linalg.norm(patch-col,axis=2)<80).astype(float) if obs=='threshold' else np.where(alpha>.05,alpha,0);qq=[]
  for p in probs:
   w=ink[:,round(p*(R-L))]
   if w.sum()==0:raise ValueError('Target mark not recovered')
   yy=np.average(np.arange(len(w))+T,weights=w);qq.append(spec['lo']+(B-yy)/(B-T)*(spec['hi']-spec['lo']))
  out.append(np.maximum.accumulate(qq))
 return np.array(out)
def one(c):
 ctx=prepare(c['x'],c['y']);rows=[];truth=np.array([np.quantile(c[g],DENSE) for g in ['x','y']]);target=truth[1]-truth[0]
 for f,s in FIXED:
  for j,phase in enumerate([0,.25,.5,.75]):
   im,spec=render(ctx,f,s,256,phase,20260920+j)
   for obs in ['threshold','alpha']:
    error='';q=np.full((2,19),np.nan)
    try:
     if f=='Quantile plot':q5=decode(im,spec,obs);q=np.array([np.interp(DENSE,P,v) for v in q5])
     elif f=='ECDF':q=ecdf_at(im,spec,obs,DENSE)
     else:q=(decode_threshold_at if obs=='threshold' else decode_alpha_at)(im,spec,DENSE)
    except ValueError as ex:error=str(ex)
    dense_error=error
    try:q5=decode(im,spec,obs);five_error=''
    except ValueError as ex:q5=np.full((2,5),np.nan);five_error=str(ex)
    true5=np.array([np.quantile(c[g],P) for g in ['x','y']]);target5=true5[1]-true5[0]
    for task in ['median','five','dense19']:
     if task=='dense19':loss=np.mean(abs(q[1]-q[0]-target))/ctx['scale'];err=dense_error
     elif task=='median':loss=abs(q5[1,2]-q5[0,2]-target5[2])/ctx['scale'];err=five_error
     else:loss=np.mean(abs(q5[1]-q5[0]-target5))/ctx['scale'];err=five_error
     rows.append(dict(key=c['key'],dataset=c['dataset'],family=f,setting=s,observer=obs,phase=phase,task=task,loss=loss,error=err))

 return rows
if __name__=='__main__':
 (OUT/'task_manifest.json').write_text(json.dumps({'protocol_sha256':hashlib.sha256((ROOT/'validation_v2/task_protocol.json').read_bytes()).hexdigest(),'source_sha256':{p:hashlib.sha256((ROOT/'validation_v2'/p).read_bytes()).hexdigest() for p in ['task_sensitivity.py','task_decoders.py']}},indent=2))
 # Original five-probability estimates must match the generalized decoder.
 c=CASES[0];ctx=prepare(c['x'],c['y'])
 for f,s in FIXED:
  im,sp=render(ctx,f,s,256,0,20260920)
  for ob in ['threshold','alpha']:
   if f not in ['Quantile plot','ECDF']:
    q=(decode_threshold_at if ob=='threshold' else decode_alpha_at)(im,sp,P);assert np.allclose(q,decode(im,sp,ob))
 rows=[]
 with ProcessPoolExecutor(max_workers=4) as pool:
  for i,r in enumerate(pool.map(one,CASES)):
   rows.extend(r)
   if (i+1)%30==0:print('Task sensitivity',i+1,flush=True)
 d=pd.DataFrame(rows);d.to_csv(OUT/'task_trials.csv',index=False)
 a=d.groupby(['key','dataset','family','setting','observer','task']).agg(loss=('loss','mean'),successful=('loss','count')).reset_index();a.loc[a.successful!=4,'loss']=np.nan;a.to_csv(OUT/'task_configurations.csv',index=False)
 w=a[a.loss.notna()].copy();minimum=w.groupby(['key','observer','task']).loss.transform('min');w=w[np.isclose(w.loss,minimum,atol=1e-12,rtol=0)].sort_values(['key','observer','task','family'])
 w.to_csv(OUT/'task_winners.csv',index=False)
 counts=w.groupby(['observer','task','family']).size().reset_index(name='wins');counts.to_csv(OUT/'task_summary.csv',index=False);print(counts.to_string(index=False))
 sets=w.groupby(['key','observer','task']).family.apply(lambda v:frozenset(v));records=[]
 for task in ['median','dense19']:
  for obs in ['threshold','alpha']:
   p=sets.xs((obs,'five'),level=('observer','task'));qq=sets.xs((obs,task),level=('observer','task')).reindex(p.index);records.append(dict(task=task,observer=obs,changed=sum(p.loc[k]!=qq.loc[k] for k in p.index),cases=len(p)))
 (OUT/'task_changes.json').write_text(json.dumps(records,indent=2))
 (OUT/'task_table.tex').write_text('\\begin{longtable}{lllr}\\toprule\nObserver & Task & Winning family & Cases\\\\\\midrule\\endhead\n'+''.join(f'{r.observer} & {r.task} & {r.family} & {r.wins}\\\\\n' for r in counts.itertuples())+'\\bottomrule\\end{longtable}\n')
 with (OUT/'task_numbers.tex').open('w') as f:
  for task,macro in [('median','MedianTaskChanges'),('dense19','DenseTaskChanges')]:
   v=next(r['changed'] for r in records if r['task']==task and r['observer']=='threshold');f.write('\\newcommand{\\'+macro+'}{'+str(v)+'}\n')
