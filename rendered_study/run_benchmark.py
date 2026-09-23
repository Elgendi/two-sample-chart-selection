"""Frozen development protocol: do not tune chart parameters against winners."""
from pathlib import Path
import sys,json,time,hashlib
import numpy as np,pandas as pd
from observer import prepare,render,decode,score,SETTINGS,P
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'rendered_study/results';OUT.mkdir(exist_ok=True)
CASES=json.loads((ROOT/'data/derived/comparisons.json').read_text())
RESOLUTIONS=[128,256,512];PHASES=[0.,.25,.5,.75]
def one_case(c):
    records=[];ctx=prepare(c['x'],c['y']);target=np.quantile(c['y'],P)-np.quantile(c['x'],P)
    for family,setting in SETTINGS:
        for H in RESOLUTIONS:
            for pi,phase in enumerate(PHASES):
                im,spec=render(ctx,family,setting,H,phase,20260920+pi)
                error='';loss=value=float('nan')
                try:q=decode(im,spec);loss,value=score(target,q,ctx['scale'])
                except ValueError as exc:error=str(exc)
                records.append(dict(key=c['key'],primary=c['dataset']!='Parkinsons',dataset=c['dataset'],feature=c['feature'],family=family,setting=setting,H=H,phase=phase,loss=loss,score=value,decode_failure=error,scale=ctx['scale'],constant_scale_fallback=ctx['constant_scale_fallback']))
    return records
if __name__=='__main__':
    from concurrent.futures import ProcessPoolExecutor
    records=[];start=time.time()
    with ProcessPoolExecutor(max_workers=4) as pool:
        for i,rr in enumerate(pool.map(one_case,CASES)):
            records.extend(rr)
            if (i+1)%5==0:
                pd.DataFrame(records).to_csv(OUT/'render_trials.partial.csv',index=False)
                print(f'{i+1}/{len(CASES)} cases; {time.time()-start:.1f}s',flush=True)
    df=pd.DataFrame(records);df.to_csv(OUT/'render_trials.csv',index=False)
    # Require successful recovery at every placement; never reward a failure.
    group=df.groupby(['key','primary','dataset','feature','family','setting','H'],sort=False)
    summaries=group.agg(loss=('loss','mean'),successful=('loss','count'),loss_min=('loss','min'),loss_max=('loss','max')).reset_index()
    summaries.loc[summaries.successful!=len(PHASES),'loss']=np.nan
    summaries['score']=100/(1+summaries.loss)
    summaries['placement_score_min']=100/(1+summaries.loss_max);summaries['placement_score_max']=100/(1+summaries.loss_min)
    summaries.to_csv(OUT/'configuration_scores.csv',index=False)
    rows=[]
    for (key,H),dd in summaries.groupby(['key','H'],sort=False):
        for family,ff in dd.groupby('family',sort=False):
            ff=ff.sort_values(['loss','setting'],na_position='last',kind='stable');rows.append(ff.iloc[0].to_dict())
    fam=pd.DataFrame(rows);fam.to_csv(OUT/'family_scores.csv',index=False)
    picks=[]
    for (key,H),dd in fam.groupby(['key','H'],sort=False):
        finite=dd[dd.loss.notna()];best=finite.loss.min();win=finite[np.isclose(finite.loss,best,atol=1e-12,rtol=0)]
        picks.append(dict(key=key,H=H,primary=bool(dd.primary.iloc[0]),best_score=100/(1+best),families=';'.join(win.family),n_tied=len(win)))
    pd.DataFrame(picks).to_csv(OUT/'winners.csv',index=False)
    print('Completed',len(df),'render/decode trials',flush=True)

    (OUT/'render_trials.partial.csv').unlink(missing_ok=True)
