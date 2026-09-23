from pathlib import Path
import json,hashlib
from concurrent.futures import ProcessPoolExecutor
import numpy as np,pandas as pd
from observer import prepare,render,decode,P
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'validation_v2/results'
CASES={c['key']:c for c in json.loads((ROOT/'data/derived/comparisons.json').read_text())}
W=pd.read_csv(OUT/'winners.csv',dtype={'setting':str}).set_index('key');B=pd.read_csv(OUT/'robust_choices.csv',dtype={'setting':str}).set_index('key')
def one(key):
    c=CASES[key];ctx=prepare(c['x'],c['y']);target=np.quantile(c['y'],P)-np.quantile(c['x'],P);rows=[]
    for label,f,s in [('reference optimum',W.loc[key,'family'],W.loc[key,'setting']),('minimax optimum',B.loc[key,'family'],B.loc[key,'setting']),('fixed quantile','Quantile plot','five')]:
        for obs in ['threshold','alpha']:
            for i,phase in enumerate([.125,.375,.625,.875]):
                im,spec=render(ctx,f,s,384,phase,2026092070+i);loss=np.nan;error=''
                try:
                    q=decode(im,spec,obs);loss=np.mean(abs(q[1]-q[0]-target))/ctx['scale']
                except ValueError as e:error=str(e)
                rows.append(dict(key=key,dataset=c['dataset'],choice=label,family=f,setting=s,H=384,observer=obs,phase=phase,loss=loss,error=error))
    return rows
if __name__=='__main__':
    (OUT/'display_transfer_manifest.json').write_text(json.dumps({'protocol_sha256':hashlib.sha256((ROOT/'validation_v2/display_protocol.json').read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2))
    rows=[]
    with ProcessPoolExecutor(max_workers=4) as pool:
        for r in pool.map(one,list(W.index)):rows.extend(r)
    d=pd.DataFrame(rows);d.to_csv(OUT/'display_transfer_trials.csv',index=False)
    a=d.groupby(['key','dataset','choice','observer']).agg(loss=('loss','mean'),successful=('loss','count')).reset_index();a.loc[a.successful!=4,'loss']=np.nan
    a.to_csv(OUT/'display_transfer.csv',index=False)
    means=a.groupby(['dataset','choice','observer']).loss.mean().groupby(['choice','observer']).mean().reset_index()
    means.to_csv(OUT/'display_transfer_summary.csv',index=False);print(means.to_string(index=False))
    (OUT/'display_table.tex').write_text('\\begin{center}\\begin{tabular}{llrr}\\toprule\nSelection & Observer & Resource-balanced loss & Failed cases\\\\\\midrule\n'+''.join(f"{r.choice} & {r.observer} & {r.loss:.4f} & {int(a[(a.choice==r.choice)&(a.observer==r.observer)].loss.isna().sum())}\\\\\n" for r in means.itertuples())+'\\bottomrule\\end{tabular}\\end{center}\n')
