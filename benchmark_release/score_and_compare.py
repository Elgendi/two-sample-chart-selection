"""Score a CSV and compare its frozen selection with an empirical-trained default.
Schemas: median/spread/five A,B; composition category,value; profile time,value;
association x,y. Targets and scores are computational, not human-performance measures.
"""
from common import *
import argparse
V=loadmod('release_cli_marginal','validation_v3/benchmark.py');B=loadmod('release_cli_extension','task_first/benchmark.py')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('csv',type=Path);p.add_argument('--task',choices=TASKS,required=True);p.add_argument('--observer',choices=['hard','soft'],default='hard');p.add_argument('--output-dir',type=Path,default=Path('benchmark_output'));args=p.parse_args();d=pd.read_csv(args.csv);rows=[];case=dict(key='user',dataset='User',kind='user',task=args.task)
 if args.task in TASKS[:3]:
  if not {'A','B'}<=set(d):raise SystemExit('Expected A,B columns. Blank padding is allowed.')
  for c,g in [('A','x'),('B','y')]:
   v=pd.to_numeric(d[c],errors='raise').dropna().to_numpy(float)
   if len(v)<4 or not np.isfinite(v).all():raise SystemExit('Each group needs at least four finite observations.')
   case[g]=v.tolist()
  rr,dd=V.one(case)
  for z in rr:
   if z['task']==args.task and z['observer']=={'hard':'threshold','soft':'alpha'}[args.observer]:rows.append(z)
 else:
  if args.task=='composition':
   if not {'category','value'}<=set(d):raise SystemExit('Expected category,value columns.')
   v=pd.to_numeric(d.value,errors='raise').to_numpy(float)
   if not 2<=len(v)<=8 or not np.isfinite(v).all() or (v<0).any() or v.sum()<=0 or d.category.duplicated().any():raise SystemExit('Use 2–8 unique categories with finite nonnegative values and a positive total.')
   case['values']=(v/v.sum()).tolist();case['labels']=d.category.astype(str).tolist()
  elif args.task=='profile':
   if not {'time','value'}<=set(d):raise SystemExit('Expected time,value columns.')
   d=d.sort_values('time');t=d.time.to_numpy(float);v=d.value.to_numpy(float)
   if len(t)<12 or not np.isfinite(t).all() or not np.isfinite(v).all() or (v<0).any() or np.ptp(t)==0:raise SystemExit('Need at least 12 finite nonnegative values across varying times.')
   edges=np.linspace(t.min(),t.max()+max(1e-8,np.ptp(t)*1e-10),13);ix=np.clip(np.searchsorted(edges,t,side='right')-1,0,11);vals=np.array([v[ix==i].mean() if (ix==i).any() else np.nan for i in range(12)])
   if not np.isfinite(vals).all() or np.std(vals,ddof=1)==0:raise SystemExit('All 12 bins must be populated and their means must vary.')
   case['values']=vals.tolist()
  else:
   if not {'x','y'}<=set(d):raise SystemExit('Expected x,y columns.')
   v=d[['x','y']].to_numpy(float)
   if len(v)<3 or not np.isfinite(v).all() or (np.std(v,axis=0)==0).any():raise SystemExit('Need at least three finite pairs with nonzero variance.')
   case['values']=v[np.linspace(0,len(v)-1,min(64,len(v))).round().astype(int)].tolist()
  for H,phases in [(256,[0,.25,.5,.75]),(384,[.125,.375,.625,.875])]:
   for family in B.FAMILIES[args.task]:
    for phase in phases:
     im,sp=B.render(case,family,H,phase);ll=np.nan;error=''
     try:u=B.decode(im,sp,args.observer);ll=B.loss(case,u)
     except ValueError as ex:error=str(ex)
     rows.append(dict(candidate=family,H=H,phase=phase,loss=ll,error=error))
 trials=pd.DataFrame(rows);scores=trials.groupby(['candidate','H']).agg(loss=('loss','mean'),n=('loss','count')).reset_index();scores.loc[scores.n!=4,'loss']=np.nan;scores['score']=100/(1+scores.loss)
 ref=scores[scores.H==256].set_index('candidate').loss;test=scores[scores.H==384].set_index('candidate').loss;selected=choose(ref,order_for(args.task));frozen=pd.read_csv(OUT/'frozen_empirical_defaults.csv');default=frozen[(frozen.task==args.task)&(frozen.observer==args.observer)].iloc[0].candidate
 summary=dict(task=args.task,observer=args.observer,selected=selected,all_reference_ties=ref.index[ref<=ref.min()+TOL].tolist(),default=default,default_test_loss=float(test[default]),selected_test_loss=float(test[selected]),gain=float(test[default]-test[selected]),interpretation='Positive gain favors selection for this computational task and decoder; no inference about human understanding. The default was trained on the bundled empirical benchmark.')
 args.output_dir.mkdir(parents=True,exist_ok=True);trials.to_csv(args.output_dir/'trials.csv',index=False);scores.to_csv(args.output_dir/'scores.csv',index=False);(args.output_dir/'summary.json').write_text(json.dumps(summary,indent=2));(args.output_dir/'input.json').write_text(json.dumps(case,indent=2));print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
