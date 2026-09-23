"""Score fixed chart configurations for a declared marginal two-sample task.
Example: python score_my_data.py reader_figures/example_input.csv --output-dir my_scores
This computes pixel-recovery accuracy; it does not predict human reading accuracy.
"""
from pathlib import Path
import argparse,json,sys,hashlib
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'validation_v3'))
from benchmark import prepare,render,render19,decode_all,targets,PROBS,CANDIDATES,TASKS,eligible

from observer import SETTINGS,decode

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('csv',type=Path,help='Numeric columns A and B by default; unequal lengths may be padded with blanks.')
 p.add_argument('--x-column',default='A');p.add_argument('--y-column',default='B')
 p.add_argument('--task',choices=TASKS,default='five')
 p.add_argument('--observer',choices=['threshold','alpha'],default='threshold')
 p.add_argument('--height',type=int,choices=[128,256,384,512],default=256)
 p.add_argument('--fixed-budget',action='store_true',help='One fixed setting per familiar family, matching the task-first audit.')
 p.add_argument('--include-specialized',action='store_true',help='Also evaluate ECDF and five/19-marker controls; changes the candidate set.')
 p.add_argument('--output-dir',type=Path,default=Path('chart_scores'))
 args=p.parse_args();eligible(args.task)
 d=pd.read_csv(args.csv);groups=[]
 for col in [args.x_column,args.y_column]:
  if col not in d:raise SystemExit(f'Missing column: {col}')
  v=pd.to_numeric(d[col],errors='raise').dropna().to_numpy(float)
  if len(v)<2 or not np.isfinite(v).all():raise SystemExit('Each group needs at least two finite numeric observations; blanks are omitted.')
  groups.append(v)
 x,y=groups;scale=np.sqrt(((len(x)-1)*np.var(x,ddof=1)+(len(y)-1)*np.var(y,ddof=1))/(len(x)+len(y)-2))
 if scale<=0:raise SystemExit('Pooled within-group SD is zero; this normalized score is undefined for these inputs.')
 ctx=prepare(x,y);truth=targets(np.array([np.quantile(v,PROBS) for v in groups]))[args.task];rows=[];trials=[]
 candidates=[(f,s) for f,s in SETTINGS if f not in ['ECDF','Quantile plot']]
 if args.fixed_budget:candidates=[(f,s) for f,s in CANDIDATES if f not in ['ECDF','Quantile plot']]
 if args.include_specialized:candidates += [('ECDF','full'),('Quantile plot','five'),('Quantile plot','nineteen')]
 for family,setting in candidates:
  losses=[];failures=[]
  for j,phase in enumerate([0,.25,.5,.75]):
   im,sp=render19(ctx,args.height,phase) if setting=='nineteen' else render(ctx,family,setting,args.height,phase,20260920+j)
   error='';estimate=np.full_like(truth,np.nan)
   try:
    if args.task=='five' and setting!='nineteen':
     recovered=decode(im,sp,args.observer);estimate=recovered[1]-recovered[0]
    else:estimate=targets(decode_all(im,sp,args.observer))[args.task]
    loss=float(np.mean(abs(estimate-truth))/scale)
   except ValueError as ex:error=str(ex);loss=np.nan;failures.append(error)
   losses.append(loss);trials.append(dict(family=family,setting=setting,phase=phase,loss=loss,error=error,recovered_target=json.dumps(estimate.tolist())))
  loss=np.mean(losses) if not failures else np.nan
  rows.append(dict(family=family,setting=setting,loss=loss,score=100/(1+loss) if np.isfinite(loss) else np.nan,failed_placements=len(failures)))
 r=pd.DataFrame(rows);valid=r.loss.notna()
 if not valid.any():raise SystemExit('No candidate decoded successfully at all four placements.')
 minimum=r.loc[valid,'loss'].min();r['tied_best']=np.isclose(r.loss,minimum,atol=1e-12,rtol=0)
 # First declared configuration among scientifically tied minima; no invented score offset.
 best=r[r.tied_best].iloc[0];args.output_dir.mkdir(parents=True,exist_ok=True)
 r.sort_values('loss',kind='stable').to_csv(args.output_dir/'scores.csv',index=False)
 pd.DataFrame(trials).to_csv(args.output_dir/'trials.csv',index=False)
 im,sp=render19(ctx,args.height,0) if best.setting=='nineteen' else render(ctx,best.family,best.setting,args.height,0,20260920)
 im.save(args.output_dir/'selected_scored_raster.png')
 (args.output_dir/'selected_calibration.json').write_text(json.dumps(sp,indent=2))
 summary=dict(candidate_scope="familiar plus specialized" if args.include_specialized else "seven familiar families",candidate_settings=len(candidates),task=args.task,target_description='Marginal group comparison; not within-person change.',observer=args.observer,height=args.height,n_A=len(x),n_B=len(y),pooled_sd=scale,true_target=truth.tolist(),selected_family=best.family,selected_setting=best.setting,score=float(best.score),all_tied_best=r[r.tied_best][['family','setting','score']].to_dict('records'),input_sha256=hashlib.sha256(args.csv.read_bytes()).hexdigest(),interpretation='Computational recovery only. Validate separately for readers and for another display condition.')
 (args.output_dir/'summary.json').write_text(json.dumps(summary,indent=2))
 print(r.sort_values('loss',kind='stable')[['family','setting','score','tied_best']].to_string(index=False,float_format=lambda v:f'{v:.2f}'))
 print(f'\nSaved results to {args.output_dir.resolve()}')
if __name__=='__main__':main()
