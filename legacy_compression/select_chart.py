"""Select numerical detail for two columns of a CSV; visual encoding remains explicit."""
import argparse,json,sys,math
from pathlib import Path
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parent/'revision'))
from model import select
from selection_score import score_candidates
from chart_catalogue import catalogue_rankings
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('csv');p.add_argument('--x',required=True);p.add_argument('--y',required=True);p.add_argument('--paired',action='store_true');p.add_argument('--bootstrap',type=int,default=999);p.add_argument('--seed',type=int,default=20260920);p.add_argument('--lower',type=float,default=.05);p.add_argument('--upper',type=float,default=.95);p.add_argument('--percentile',type=float,default=.95);args=p.parse_args()
 d=pd.read_csv(args.csv);result=select(d[args.x].to_numpy(),d[args.y].to_numpy(),args.paired,args.bootstrap,args.seed,(args.lower,args.upper),args.percentile)
 n_raw=next(r['N'] for r in result['candidates'] if r['configuration']=='raw')
 result['score_rankings']=score_candidates(result['candidates'],result['tolerance'],n_raw)
 result['chart_catalogue']=catalogue_rankings(result['candidates'],result['tolerance'],n_raw)
 result['score_definition']='100 * max(0, 1 - N / N_raw) when qualifying; zero if rejected; null if unavailable'
 def finite_json(value):
  if isinstance(value,dict):return {k:finite_json(v) for k,v in value.items()}
  if isinstance(value,list):return [finite_json(v) for v in value]
  if isinstance(value,float) and not math.isfinite(value):return None
  return value
 print(json.dumps(finite_json(result),indent=2,allow_nan=False))
