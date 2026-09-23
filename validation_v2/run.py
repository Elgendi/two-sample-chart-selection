from pathlib import Path
import sys,json,hashlib,time
import numpy as np,pandas as pd
from observer import prepare,render,decode,P,SETTINGS,FIXED
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'validation_v2/results';OUT.mkdir(exist_ok=True)
PHASES=[0,.25,.5,.75]
def evaluate(c,settings=SETTINGS,conditions=None):
    if conditions is None:conditions=[('zero',h) for h in [128,256,512]]+[('tight',256)]
    qtrue=np.array([np.quantile(c[g],P) for g in ['x','y']]);target=qtrue[1]-qtrue[0];records=[];contexts={}
    for axis,H in conditions:
        if axis not in contexts:contexts[axis]=prepare(c['x'],c['y'],axis)
        ctx=contexts[axis]
        for family,setting in settings:
            if axis=='tight' and family=='Bar chart':continue
            for pi,phase in enumerate(PHASES):
                im,spec=render(ctx,family,setting,H,phase,20260920+pi)
                for observer in ['threshold','alpha']:
                    loss=group_loss=float('nan');error='';q=np.full((2,5),np.nan)
                    try:
                        q=decode(im,spec,observer);loss=np.mean(abs(q[1]-q[0]-target))/ctx['scale'];group_loss=np.mean(abs(q-qtrue))/ctx['scale']
                    except ValueError as ex:error=str(ex)
                    r=dict(key=c['key'],dataset=c['dataset'],feature=c['feature'],family=family,setting=setting,axis=axis,H=H,phase=phase,observer=observer,loss=loss,group_loss=group_loss,zero_loss=np.mean(abs(target))/ctx['scale'],scale=ctx['scale'],decode_failure=error)
                    for g in range(2):
                        for k,p in enumerate(P):r[f'q{g}_{p}']=q[g,k]
                    records.append(r)
    return records

def simulation_cases():
    rng=np.random.default_rng(2026092017);cases=[]
    for regime in ['null','location','scale','skew','mixture','heavy_tail']:
        for n in [20,100,500]:
            for rep in range(4):
                x=rng.normal(size=n)
                if regime=='null':y=rng.normal(size=n)
                elif regime=='location':y=rng.normal(.5,1,n)
                elif regime=='scale':y=rng.normal(0,1.8,n)
                elif regime=='skew':x=rng.lognormal(0,.5,n);y=rng.lognormal(0,1,n)
                elif regime=='mixture':y=rng.normal(np.where(rng.random(n)<.5,-1.5,1.5),.4)
                else:x=rng.standard_t(3,n);y=.3+1.3*rng.standard_t(3,n)
                cases.append(dict(key=f'{regime}_{n}_{rep}',dataset=regime,feature=str(n),x=x.tolist(),y=y.tolist()))
    return cases

def simjob(c):return evaluate(c,FIXED,[('zero',256)])
if __name__=='__main__':
    from concurrent.futures import ProcessPoolExecutor
    stamp=dict(protocol_sha256=hashlib.sha256((ROOT/'validation_v2/protocol.json').read_bytes()).hexdigest(),data_sha256=hashlib.sha256((ROOT/'data/derived/comparisons.json').read_bytes()).hexdigest(),source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'validation_v2').glob('*.py')})
    (OUT/'run_manifest.json').write_text(json.dumps(stamp,indent=2)+'\n')
    cases=[c for c in json.loads((ROOT/'data/derived/comparisons.json').read_text()) if c['dataset']!='Parkinsons'];start=time.time();rows=[]
    with ProcessPoolExecutor(max_workers=4) as pool:
        for i,r in enumerate(pool.map(evaluate,cases)):
            rows.extend(r)
            pd.DataFrame(r).to_csv(OUT/('case_'+cases[i]['key']+'.csv'),index=False)
            if (i+1)%10==0:print(f'Primary {i+1}/{len(cases)}; {time.time()-start:.0f}s',flush=True)
    pd.DataFrame(rows).to_csv(OUT/'trials.csv',index=False)
    sim=simulation_cases();(OUT/'simulation_inputs.json').write_text(json.dumps(sim))
    rows=[]
    with ProcessPoolExecutor(max_workers=4) as pool:
        for i,r in enumerate(pool.map(simjob,sim)):
            rows.extend(r)
            if (i+1)%18==0:print(f'Simulation {i+1}/{len(sim)}',flush=True)
    pd.DataFrame(rows).to_csv(OUT/'simulation_trials.csv',index=False)
    c=next(c for c in cases if c['dataset']=='CKD' and c['feature']=='pot');c=dict(c)
    c['x']=[v for v in c['x'] if v not in [39,47]];c['y']=[v for v in c['y'] if v not in [39,47]]
    pd.DataFrame(evaluate(c,conditions=[('zero',256)])).to_csv(OUT/'ckd_omission_trials.csv',index=False)
    print('Completed',flush=True)
