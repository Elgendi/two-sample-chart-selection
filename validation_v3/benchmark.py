"""Six declared tasks; frozen selections transferred to a new display condition."""
from pathlib import Path
import sys,json,hashlib
import numpy as np,pandas as pd
from PIL import Image,ImageDraw,ImageFilter
from concurrent.futures import ProcessPoolExecutor
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'validation_v2'))
from observer import prepare,render,decode,FIXED,legacy,P
from task_decoders import decode_threshold_at,decode_alpha_at
from task_sensitivity import ecdf_at
OUT=ROOT/'validation_v3/results';PROBS=np.arange(1,20)/20
CANDIDATES=FIXED+[('Quantile plot','nineteen')]
TASKS=['median','spread','asymmetry','upper_tail','five','dense19']
CASES=[c for c in json.loads((ROOT/'data/derived/comparisons.json').read_text()) if c['dataset']!='Parkinsons']
def targets(q):
 d=np.asarray(q)[1]-np.asarray(q)[0]
 return dict(median=np.array([d[9]]),spread=np.array([d[14]-d[4]]),asymmetry=np.array([d[17]+d[1]-2*d[9]]),upper_tail=np.array([d[18]-d[9]]),five=d[[1,4,9,14,17]],dense19=d)
def render19(ctx,H,phase):
 S=4;W=2*H+16;im=Image.new('RGB',(W*S,H*S),'white');dr=ImageDraw.Draw(im)
 spec=dict(family='Quantile plot',setting='nineteen',H=H,W=W,lo=ctx['lo'],hi=ctx['hi'],panels=[])
 for g,v in enumerate(ctx['groups']):
  L=g*(H+16)+8;R=g*(H+16)+H-9;T=8.;B=H-9.;color=legacy.COLORS[g]
  spec['panels'].append(dict(L=L,R=R,T=T,B=B,color=color))
  for p,q in zip(PROBS,np.quantile(v,PROBS)):
   xx=L+p*(R-L);yy=B-(q-ctx['lo'])/(ctx['hi']-ctx['lo'])*(B-T)+phase
   dr.ellipse([round((xx-2)*S),round((yy-2)*S),round((xx+2)*S),round((yy+2)*S)],fill=color)
 return im.resize((W,H),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(.5)),spec
def decode19(im,spec,obs):
 a=np.asarray(im,float);out=[]
 for pan in spec['panels']:
  L,R,T,B=[pan[k] for k in ['L','R','T','B']];patch=a[int(T):int(B)+1,int(L):int(R)+1];col=np.array(pan['color'])
  alpha=np.clip(((255-patch)@(255-col))/np.sum((255-col)**2),0,1)
  ink=(np.linalg.norm(patch-col,axis=2)<80).astype(float) if obs=='threshold' else np.where(alpha>.05,alpha,0)
  qq=[]
  for p in PROBS:
   j=round(p*(R-L));weights=ink[:,max(0,j-2):j+3].sum(1)
   if weights.sum()==0:raise ValueError('Target mark not recovered')
   yy=np.average(np.arange(len(weights))+T,weights=weights);qq.append(spec['lo']+(B-yy)/(B-T)*(spec['hi']-spec['lo']))
  out.append(np.maximum.accumulate(qq))
 return np.array(out)
def decode_all(im,sp,obs):
 if sp['setting']=='nineteen':return decode19(im,sp,obs)
 if sp['family']=='Quantile plot':return np.array([np.interp(PROBS,P,v) for v in decode(im,sp,obs)])
 if sp['family']=='ECDF':return ecdf_at(im,sp,obs,PROBS)
 return (decode_threshold_at if obs=='threshold' else decode_alpha_at)(im,sp,PROBS)
def eligible(task,representation='marginal'):
 if task=='paired_median_change' and representation=='marginal':
  raise ValueError('Within-person change requires pair identity; marginal-only charts are ineligible.')
 if task not in TASKS:raise ValueError('Unsupported task; define and validate its recovery contract first.')
 return True
def one(case):
 ctx=prepare(case['x'],case['y']);truthq=np.array([np.quantile(case[g],PROBS) for g in ['x','y']]);truth=targets(truthq);rows=[];decoded=[]
 for H,phases in [(256,[0,.25,.5,.75]),(384,[.125,.375,.625,.875])]:
  for f,s in CANDIDATES:
   for j,ph in enumerate(phases):
    im,sp=render19(ctx,H,ph) if s=='nineteen' else render(ctx,f,s,H,ph,20260920+j)
    for obs in ['threshold','alpha']:
     err='';q=np.full((2,19),np.nan)
     try:q=decode_all(im,sp,obs)
     except ValueError as ex:err=str(ex)
     recovered=targets(q)
     base=dict(key=case['key'],dataset=case['dataset'],family=f,setting=s,candidate=f+' / '+s,H=H,phase=ph,observer=obs,error=err)
     decoded.append(dict(**base,scale=ctx['scale'],truth_q=json.dumps(truthq.tolist()),decoded_q=json.dumps(q.tolist())))
     for task in TASKS:
      rows.append(dict(**base,task=task,loss=float(np.mean(abs(recovered[task]-truth[task]))/ctx['scale'])))
 return rows,decoded
if __name__=='__main__':
 OUT.mkdir(exist_ok=True)
 manifest={'protocol_sha256':hashlib.sha256((ROOT/'validation_v3/protocol.json').read_bytes()).hexdigest(),'input_sha256':hashlib.sha256((ROOT/'data/derived/comparisons.json').read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
 (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
 # Numerical fixture independently verifies target indices and paired ineligibility.
 q=np.array([PROBS,2*PROBS]);t=targets(q)
 assert np.allclose([t[k][0] for k in TASKS[:4]],[.5,.5,0,.45])
 try:eligible('paired_median_change')
 except ValueError:pass
 else:raise AssertionError('Paired task was not rejected')
 ctx=prepare(CASES[0]['x'],CASES[0]['y']);im,sp=render19(ctx,256,0)
 for ob in ['threshold','alpha']:
  qq=decode19(im,sp,ob);assert np.isfinite(qq).all()
  try:decode19(Image.new('RGB',im.size,'white'),sp,ob)
  except ValueError:pass
  else:raise AssertionError('Blank image accepted')
 rows=[];decoded=[]
 with ProcessPoolExecutor(max_workers=4) as pool:
  for i,(r,d) in enumerate(pool.map(one,CASES)):
   rows.extend(r);decoded.extend(d)
   if (i+1)%10==0:print('Multi-task benchmark',i+1,'/',len(CASES),flush=True)
 pd.DataFrame(decoded).to_csv(OUT/'decoded_trials.csv',index=False)
 d=pd.DataFrame(rows);d.to_csv(OUT/'trials.csv',index=False)
 a=d.groupby(['key','dataset','candidate','family','setting','H','observer','task'],sort=False).agg(loss=('loss','mean'),successful=('loss','count')).reset_index()
 a.loc[a.successful!=4,'loss']=np.nan;a.to_csv(OUT/'configurations.csv',index=False)
 print('Finished',len(d),'task losses;',len(decoded),'image-decoder trials; invalid configurations',a.loss.isna().sum(),flush=True)
