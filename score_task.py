"""Task-first chart scoring. Choose the question BEFORE comparing charts.
CSV schemas: composition category,value; profile time,value; association x,y;
median/spread/five A,B (blank padding allowed). Scores describe pixels, not people.
"""
from pathlib import Path
import argparse,sys,json,subprocess
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'task_first'))
from benchmark import FAMILIES,render,decode,truth,loss

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('csv',type=Path);p.add_argument('--task',required=True,choices=['composition','profile','association','median','spread','five']);p.add_argument('--observer',choices=['hard','soft'],default='hard');p.add_argument('--output-dir',type=Path,default=Path('task_scores'));args=p.parse_args()
 if args.task in ['median','spread','five']:
  subprocess.run([sys.executable,str(ROOT/'score_my_data.py'),str(args.csv),'--task',args.task,'--fixed-budget','--observer',{'hard':'threshold','soft':'alpha'}[args.observer],'--output-dir',str(args.output_dir)],check=True);return
 d=pd.read_csv(args.csv);case=dict(key='user_input',task=args.task,kind='user',dataset='User')
 if args.task=='composition':
  if not {'category','value'}<=set(d.columns):raise SystemExit('Composition needs category,value columns with nonnegative counts or shares.')
  v=pd.to_numeric(d.value,errors='raise').to_numpy(float)
  if len(v)<2 or len(v)>8 or not np.isfinite(v).all() or np.any(v<0) or v.sum()<=0 or d.category.duplicated().any():raise SystemExit('Use 2–8 distinct categories, finite nonnegative values and a positive total.')
  case.update(values=(v/v.sum()).tolist(),labels=d.category.astype(str).tolist())
 elif args.task=='profile':
  if not {'time','value'}<=set(d.columns):raise SystemExit('Profile needs numeric time,value columns.')
  d=d.sort_values('time');t=d.time.to_numpy(float);y=d.value.to_numpy(float)
  if len(y)<12 or not np.isfinite(t).all() or not np.isfinite(y).all() or np.any(y<0) or np.ptp(t)==0:raise SystemExit('This profile implementation needs >=12 finite nonnegative values at varying times.')
  edges=np.linspace(t.min(),t.max()+max(1e-8,np.ptp(t)*1e-10),13);ix=np.clip(np.searchsorted(edges,t,side='right')-1,0,11)
  v=np.array([y[ix==i].mean() if np.any(ix==i) else np.nan for i in range(12)])
  if not np.isfinite(v).all() or np.std(v,ddof=1)==0:raise SystemExit('All 12 equal-duration bins must be populated and the bin means must have nonzero SD.')
  case.update(values=v.tolist(),derivation='12 equal-duration bin means')
 else:
  if not {'x','y'}<=set(d.columns):raise SystemExit('Association needs paired numeric x,y columns.')
  v=d[['x','y']].to_numpy(float)
  if len(v)<3 or not np.isfinite(v).all() or np.any(np.std(v,axis=0)==0):raise SystemExit('At least three finite pairs with variation in both variables are required.')
  v=v[np.linspace(0,len(v)-1,min(64,len(v))).round().astype(int)];case.update(values=v.tolist(),derivation='At most 64 systematically spaced pairs; target refers to this subset')
 rows=[];trials=[]
 for H,phases in [(256,[0,.25,.5,.75]),(384,[.125,.375,.625,.875])]:
  for family in FAMILIES[args.task]:
   ls=[]
   for phase in phases:
    im,sp=render(case,family,H,phase);err=''
    try:got=decode(im,sp,args.observer);ll=loss(case,got)
    except (ValueError,ZeroDivisionError) as ex:ll=np.nan;err=str(ex);got=[]
    ls.append(ll);trials.append(dict(H=H,family=family,phase=phase,loss=ll,error=err,recovered=json.dumps(np.asarray(got).tolist())))
   ll=np.mean(ls) if np.isfinite(ls).all() else np.nan;rows.append(dict(H=H,family=family,loss=ll,score=100/(1+ll)))
 r=pd.DataFrame(rows);ref=r[r.H==256];minimum=ref.loss.min()
 if not np.isfinite(minimum):raise SystemExit('All candidate decoders failed.')
 tied=ref[np.isclose(ref.loss,minimum,atol=1e-12,rtol=0)];best=tied.iloc[0];test=r[(r.H==384)&(r.family==best.family)].iloc[0]
 args.output_dir.mkdir(parents=True,exist_ok=True);r.to_csv(args.output_dir/'scores.csv',index=False);pd.DataFrame(trials).to_csv(args.output_dir/'trials.csv',index=False)
 im,sp=render(case,best.family);im.save(args.output_dir/'selected_scored_raster.png');(args.output_dir/'calibration.json').write_text(json.dumps(sp,indent=2))
 (args.output_dir/'summary.json').write_text(json.dumps(dict(task=args.task,case=case,selected=best.family,reference_score=best.score,transfer_score=test.score,all_tied_best=tied.family.tolist(),eligible_candidates=FAMILIES[args.task],interpretation='Computational task recovery. Do not compare scores across different questions or infer human comprehension.'),indent=2))
 print(r.to_string(index=False));print('Selected at 256 pixels:',best.family,'; transferred unchanged to 384 pixels.')
if __name__=='__main__':main()
