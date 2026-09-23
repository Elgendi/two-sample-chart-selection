"""Score two CSV columns using the manuscript's specified computational task.

Example: python select_chart_v2.py input.csv --x group_A --y group_B --output result
Outputs are computational recoverability, not validated human recommendations.
"""
from pathlib import Path
import argparse,json,sys
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parent/'validation_v2'))
from observer import prepare,render,decode,P,SETTINGS

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('csv');p.add_argument('--x',required=True);p.add_argument('--y',required=True);p.add_argument('--resolution',type=int,default=256);p.add_argument('--robust',action='store_true',help='Evaluate both observers at 128, 256 and 512 pixels and minimize worst regret');p.add_argument('--output',default='chart_result');a=p.parse_args()
 if a.resolution<64:raise ValueError('Use at least 64 pixels per panel')
 d=pd.read_csv(a.csv);x=pd.to_numeric(d[a.x],errors='raise').dropna().to_numpy();y=pd.to_numeric(d[a.y],errors='raise').dropna().to_numpy()
 if min(len(x),len(y))<2 or not np.isfinite(x).all() or not np.isfinite(y).all():raise ValueError('Both columns need at least two finite observations')
 ctx=prepare(x,y);target=np.quantile(y,P)-np.quantile(x,P);rows=[]
 environments=[(h,o) for h in [128,256,512] for o in ['threshold','alpha']] if a.robust else [(a.resolution,'threshold')]
 for f,s in SETTINGS:
  for H,obs in environments:
   losses=[];errors=[];group=[]
   for j,phase in enumerate([0,.25,.5,.75]):
    im,sp=render(ctx,f,s,H,phase,20260920+j)
    try:
     q=decode(im,sp,obs);losses.append(float(np.mean(abs(q[1]-q[0]-target))/ctx['scale']));group.append(float(np.mean(abs(q-np.array([np.quantile(x,P),np.quantile(y,P)])))/ctx['scale']))
    except ValueError as e:errors.append(str(e))
   loss=float(np.mean(losses)) if len(losses)==4 else np.nan
   rows.append(dict(family=f,setting=s,H=H,observer=obs,loss=loss,score=100/(1+loss),group_loss=float(np.mean(group)) if len(group)==4 else np.nan,valid_placements=len(losses),failures=';'.join(errors)))
 r=pd.DataFrame(rows);out=Path(a.output);out.mkdir(parents=True,exist_ok=True);r.to_csv(out/'all_settings.csv',index=False)
 if a.robust:
  r['regret']=r.loss-r.groupby(['H','observer']).loss.transform('min');b=r.groupby(['family','setting']).agg(objective=('regret','max'),valid=('loss','count')).reset_index();b=b[b.valid==6].sort_values(['objective','family','setting'])
 else:b=r[r.loss.notna()].rename(columns={'loss':'objective'}).sort_values(['objective','family','setting'])
 if len(b)==0:raise ValueError('No setting satisfies the declared validity conditions')
 b.to_csv(out/'ranking.csv',index=False);best=b.iloc[0];ties=b[np.isclose(b.objective,best.objective,atol=1e-12,rtol=0)]
 im,sp=render(ctx,best.family,best.setting,a.resolution,0,20260920);im.save(out/'selected_raster.png');(out/'selected_metadata.json').write_text(json.dumps(sp,indent=2))
 summary=dict(task='five empirical marginal quantile differences',x_column=a.x,y_column=a.y,n_x=len(x),n_y=len(y),selected_family=best.family,selected_setting=best.setting,selection='minimax regret over six declared environments' if a.robust else 'reference mean loss',objective=float(best.objective),tied_settings=ties[['family','setting']].to_dict('records'),scale=float(ctx['scale']),constant_scale_fallback=ctx['constant_scale_fallback'],warning='Not a validated measure of human readability; paired data are compared marginally; raw raster requires the supplied calibration')
 (out/'selection.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
