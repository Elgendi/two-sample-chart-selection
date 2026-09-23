from pathlib import Path
import sys,json,hashlib,zipfile,io
import numpy as np,pandas as pd
from model import candidates,bootstrap_draws,choose,detail,scale,frontier
P=Path(__file__).resolve().parents[1];R=P/'revision/results';R.mkdir(exist_ok=True)
cases=json.loads((P/'data/derived/comparisons.json').read_text())
rows=[];sens=[];all_candidates=[];convergence=[];costs=[];paths=[];details={}
for i,c in enumerate(cases):
 x=np.array(c['x']);y=np.array(c['y']);s=scale(x,y);seed=710000+i
 rr=candidates(x,y);bb=bootstrap_draws(x,y,c['paired'],999,seed);tau=max(.1*s,np.quantile(bb[:,0],.95));w=choose(rr,tau);d=detail(rr,tau)
 labels=np.where(bb[:,1]<=tau,'Mean',np.where(bb[:,2]<=tau,'Quartiles','Distribution'))
 agreement=np.mean(labels==d)
 base=dict(key=c['key'],dataset=c['dataset'],feature=c['feature'],primary=c['dataset']!='Parkinsons',n_A=len(x),n_B=len(y))
 rows.append(dict(**base,detail=d,representation=w['representation'],configuration=w['configuration'],N=w['N'],error=w['error'],error_ratio=w['error_ratio'],scale=s,tolerance=tau,agreement=agreement,provisional=agreement<.8))
 all_candidates.extend(dict(key=c['key'],**r) for r in rr)
 details[c['key']]=dict(tolerance=float(tau),candidates=rr,frontier=frontier(rr))
 for B in [99,499,999]:
  t=max(.1*s,np.quantile(bb[:B,0],.95));v=choose(rr,t);convergence.append(dict(**base,B=B,tolerance=t,configuration=v['configuration'],detail=detail(rr,t)))
 # independent Monte Carlo stream at the default count
 bc=bootstrap_draws(x,y,c['paired'],999,810000+i);tc=max(.1*s,np.quantile(bc[:,0],.95));vc=choose(rr,tc)
 convergence.append(dict(**base,B=1999,tolerance=tc,configuration=vc['configuration'],detail=detail(rr,tc))) # B=1999 is a stream label, not draw count; renamed below
 for q in [.80,.90,.95,.99]:
  t=max(.1*s,np.quantile(bb[:,0],q));v=choose(rr,t);sens.append(dict(**base,setting=f'percentile_{q}',configuration=v['configuration'],detail=detail(rr,t),tolerance=t))
 for band in [(.01,.99),(.1,.9)]:
  rr2=candidates(x,y,band);b2=bootstrap_draws(x,y,c['paired'],999,seed,band);t=max(.1*s,np.quantile(b2[:,0],.95));v=choose(rr2,t);sens.append(dict(**base,setting=f'band_{band[0]}_{band[1]}',configuration=v['configuration'],detail=detail(rr2,t),tolerance=t))
 for eta in [.05,.1,.2]:
  t=eta*s;v=choose(rr,t);sens.append(dict(**base,setting=f'fixed_{eta}',configuration=v['configuration'],detail=detail(rr,t),tolerance=t))
 for mode in ['payload','legacy_box','free_parameters','equal']:
  v=choose(rr,tau,mode);costs.append(dict(**base,contract=mode,configuration=v['configuration'],representation=v['representation'],N=v['N']))
 for eta in np.geomspace(.025,4,40):
  v=choose(rr,eta*s);paths.append(dict(**base,resolution=eta,representation=v['representation'],N=v['N']))
 if i%10==0:print('Audit',i+1,'/149',flush=True)
pd.DataFrame(rows).to_csv(R/'audit.csv',index=False);pd.DataFrame(sens).to_csv(R/'sensitivity.csv',index=False);pd.DataFrame(costs).to_csv(R/'cost_contracts.csv',index=False);pd.DataFrame(paths).to_csv(R/'resolution_paths.csv',index=False);pd.DataFrame(all_candidates).to_csv(R/'candidates.csv',index=False)
cv=pd.DataFrame(convergence);cv['stream']=np.where(cv.B==1999,'independent','nested');cv.loc[cv.B==1999,'B']=999;cv.to_csv(R/'bootstrap_convergence.csv',index=False)
(R/'details.json').write_text(json.dumps(details,indent=2))
# Source-level audit: no identity merges or silent correction.
with zipfile.ZipFile(P/'data/raw/parkinsons.zip') as z:pk=pd.read_csv(io.BytesIO(z.read('parkinsons.data')))
pk['parsed_group']=pk.name.str.rsplit('_',n=1).str[0];pk.groupby('parsed_group').agg(recordings=('name','size'),status=('status','first')).to_csv(R/'parkinsons_identifier_audit.csv')
k=pd.read_csv(P/'data/raw/kidney.csv');k['source_row_1based']=np.arange(1,len(k)+1);k.loc[pd.to_numeric(k.pot,errors='coerce')>10].to_csv(R/'ckd_flagged_rows.csv',index=False)
c=next(c for c in cases if c['dataset']=='CKD' and c['feature']=='pot');x=np.array(c['x']);y=np.array(c['y']);kr=[]
for name,a,b in [('as_recorded',x,y),('exclude_two_flagged_values',x,y[~np.isin(y,[39.,47.])])]:
 rr=candidates(a,b);bb=bootstrap_draws(a,b,False,999,710000+cases.index(c));t=max(.1*scale(a,b),np.quantile(bb[:,0],.95));kr.append(dict(analysis=name,n_A=len(a),n_B=len(b),tolerance=t,detail=detail(rr,t),**choose(rr,t)))
pd.DataFrame(kr).to_csv(R/'ckd_sensitivity.csv',index=False)
print(pd.DataFrame(rows).query('primary').groupby('detail').size(),flush=True)
