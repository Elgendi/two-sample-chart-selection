"""Score a new two-column CSV using the current computational observer."""
from pathlib import Path
import argparse,sys
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parent/'rendered_study'))
from observer import prepare,render,decode,score,SETTINGS,P
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('csv');p.add_argument('--x',required=True);p.add_argument('--y',required=True)
p.add_argument('--resolution',type=int,choices=[128,256,512],default=256)
p.add_argument('--output',default='chart_scores.csv');a=p.parse_args()
d=pd.read_csv(a.csv);x=pd.to_numeric(d[a.x],errors='coerce').dropna().to_numpy();y=pd.to_numeric(d[a.y],errors='coerce').dropna().to_numpy()
if len(x)<4 or len(y)<4 or not np.isfinite(x).all() or not np.isfinite(y).all():p.error('Each group requires at least four finite numeric values.')
ctx=prepare(x,y);target=np.quantile(y,P)-np.quantile(x,P);rows=[]
for family,setting in SETTINGS:
 losses=[];error=''
 for i,phase in enumerate([0,.25,.5,.75]):
  im,spec=render(ctx,family,setting,a.resolution,phase,20260920+i)
  try:losses.append(score(target,decode(im,spec),ctx['scale'])[0])
  except ValueError as exc:error=str(exc)
 loss=np.mean(losses) if len(losses)==4 else np.nan
 rows.append(dict(family=family,setting=setting,loss=loss,score=100/(1+loss),decode_failure=error))
r=pd.DataFrame(rows).sort_values('score',ascending=False,na_position='last');r.to_csv(a.output,index=False)
print(r.to_string(index=False));print('Conditional computational scores; not validated human reading performance.')
