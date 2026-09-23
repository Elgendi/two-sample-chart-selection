"""Task-first extension. Pixel decoders receive images and public calibration only."""
from pathlib import Path
import json,hashlib,sys
import numpy as np,pandas as pd
from PIL import Image,ImageDraw,ImageFilter
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'task_first/results'
PALETTE=[(38,126,165),(223,120,54),(55,153,110),(152,104,184),(201,153,42),(185,70,110),(80,89,103),(66,173,181)]
FAMILIES={'composition':['Bar chart','Pie chart','Donut chart','Stacked bar'],'profile':['Line chart','Area chart','Dot plot','Bar chart'],'association':['Scatter plot','Heatmap']}
DEFAULT={'composition':'Bar chart','profile':'Line chart','association':'Scatter plot'}
def make_cases():
 cases=[];base=json.loads((ROOT/'data/derived/comparisons.json').read_text());base=[c for c in base if c['dataset']!='Parkinsons'];first={}
 for c in sorted(base,key=lambda c:c['key']):first.setdefault(c['dataset'],c)
 for ds,c in first.items():
  edges=np.r_[-np.inf,np.quantile(c['x']+c['y'],[.25,.5,.75]),np.inf]
  for g in range(2):
   p=np.histogram(c[['x','y'][g]],edges)[0].astype(float);p/=p.sum()
   cases.append(dict(key=f'comp_{ds}_{g}',dataset=ds,task='composition',kind='empirical',title=ds+' / '+c['labels'][g],source_key=c['key'],derivation='Group counts in four pooled-quartile categories; fixed ordered categories',labels=['Q1','Q2','Q3','Q4'],values=p.tolist()))
  if ds not in ['HAR','BIDMC','Wrist']:
   p=np.array([len(c['x']),len(c['y'])],float);p/=p.sum()
   cases.append(dict(key=f'cohort_{ds}',dataset=ds,task='composition',kind='empirical',title=ds+' / group composition',source_key=c['key'],derivation='Group proportions among records valid for the first source feature; not population prevalence',labels=c['labels'],values=p.tolist()))
 rng=np.random.default_rng(20260921)
 for k in [2,3,5,8]:
  for a in [.3,1,5]:
   for rep in range(4):
    p=rng.dirichlet(np.repeat(a,k));cases.append(dict(key=f'synthetic_{k}_{a}_{rep}',dataset='Synthetic',task='composition',kind='synthetic',title=f'{k} categories / concentration {a}',derivation='Dirichlet probability vector, not participants',labels=[f'C{i+1}' for i in range(k)],values=p.tolist()))
 rejected=[]
 def profile(key,ds,t,y,title):
  t=np.asarray(t,float);y=np.asarray(y,float);good=np.isfinite(t)&np.isfinite(y)&(y>0);t=t[good];y=y[good]
  if len(y)<12:rejected.append(dict(key=key,reason='fewer than 12 valid measurements'));return
  edges=np.linspace(t.min(),t.max()+1e-8,13);ix=np.clip(np.searchsorted(edges,t,side='right')-1,0,11)
  v=np.array([y[ix==i].mean() if np.any(ix==i) else np.nan for i in range(12)])
  if not np.isfinite(v).all() or np.std(v,ddof=1)==0:rejected.append(dict(key=key,reason='empty bin or zero profile SD'));return
  cases.append(dict(key=key,dataset=ds,task='profile',kind='empirical',title=title,values=v.tolist(),time_start=float(t.min()),time_end=float(t.max()),derivation='12 equal-duration bin means of positive HR; recording-level, not independent patients'))
 d=pd.read_csv(ROOT/'data/raw/wearable_5s_series.csv')
 for record,q in d.groupby('record',sort=True):profile('profile_'+record,'Wrist',q.time_s,q.hr_5s,record)
 for path in sorted((ROOT/'data/raw/bidmc').glob('*_Numerics.csv')):
  d=pd.read_csv(path);d.columns=d.columns.str.strip();key=path.stem.replace('_Numerics','')
  profile('profile_'+key,'BIDMC',d['Time [s]'],d.HR,key+' heart rate')
  d=d[np.isfinite(d.HR)&np.isfinite(d.PULSE)&(d.HR>0)&(d.PULSE>0)]
  take=np.linspace(0,len(d)-1,min(64,len(d))).round().astype(int) if len(d) else []
  xy=d.iloc[take][['HR','PULSE']].to_numpy(float)
  if len(xy)<3 or np.any(np.std(xy,axis=0)==0):rejected.append(dict(key='assoc_'+key,reason='correlation undefined'));continue
  cases.append(dict(key='assoc_'+key,dataset='BIDMC',task='association',kind='empirical',title=key+' ECG versus pulse',values=xy.tolist(),derivation='At most 64 systematically spaced valid HR/PULSE paired rows; repeated recordings may share patients'))
 return cases,rejected

def truth(case):
 v=np.asarray(case['values'],float);t=case['task']
 if t=='composition':return v,1.
 if t=='profile':return v,float(np.std(v,ddof=1))
 return np.array([np.corrcoef(v.T)[0,1]]),2.
def loss(case,decoded):
 target,scale=truth(case)
 if case['task']=='composition':return float(np.sum(abs(decoded-target))/2)
 return float(np.mean(abs(decoded-target))/scale)

def render(case,family,H=256,phase=0):
 task=case['task'];v=np.asarray(case['values'],float);S=4
 im=Image.new('RGB',(H*S,H*S),'white');dr=ImageDraw.Draw(im);L=12.;R=H-13.;T=12.;B=H-13.;color=PALETTE[0]
 sp=dict(task=task,family=family,H=H,L=L,R=R,T=T,B=B,n=len(v))
 def xy(x,y):return (round(x*S),round(y*S))
 def rect(x0,y0,x1,y1,fill):dr.rectangle([*xy(x0,y0),*xy(x1,y1)],fill=fill)
 if task=='composition':
  sp['colors']=PALETTE[:len(v)]
  if family in ['Pie chart','Donut chart']:
   cx=H/2+phase;cy=H/2+phase;r=(H-28)/2;angle=-90
   for value,col in zip(v,sp['colors']):
    end=angle+360*value
    if value>0:dr.pieslice([*xy(cx-r,cy-r),*xy(cx+r,cy+r)],start=float(angle),end=float(end),fill=col)
    angle=end
   if family=='Donut chart':dr.ellipse([*xy(cx-r*.52,cy-r*.52),*xy(cx+r*.52,cy+r*.52)],fill='white')
  elif family=='Bar chart':
   step=(R-L)/len(v)
   for i,(value,col) in enumerate(zip(v,sp['colors'])):
    if value>0:rect(L+(i+.15)*step+phase,B-value*(B-T)+phase,L+(i+.85)*step+phase,B+phase,col)
  else:
   start=L+phase
   for value,col in zip(v,sp['colors']):
    end=start+value*(R-L)
    if value>0:rect(start,T+.35*(B-T)+phase,end,T+.65*(B-T)+phase,col)
    start=end
 elif task=='profile':
  sp.update(lo=0.,hi=float(max(v)*1.05),color=color)
  xx=np.linspace(L+4,R-4,len(v));yy=B-v/sp['hi']*(B-T)
  pts=[xy(x+phase,y+phase) for x,y in zip(xx,yy)]
  if family=='Line chart':dr.line(pts,fill=color,width=2*S)
  elif family=='Area chart':dr.polygon([xy(xx[0]+phase,B+phase)]+pts+[xy(xx[-1]+phase,B+phase)],fill=color)
  elif family=='Dot plot':
   for x,y in zip(xx,yy):dr.ellipse([*xy(x-2+phase,y-2+phase),*xy(x+2+phase,y+2+phase)],fill=color)
  else:
   w=(xx[1]-xx[0])*.7
   for x,y in zip(xx,yy):rect(x-w/2+phase,y+phase,x+w/2+phase,B+phase,color)
 else:
  lo=v.min(0);hi=v.max(0);span=hi-lo;lo=lo-.05*span;hi=hi+.05*span;sp.update(xlo=float(lo[0]),xhi=float(hi[0]),ylo=float(lo[1]),yhi=float(hi[1]),color=color,bins=16)
  if family=='Scatter plot':
   xx=L+(v[:,0]-lo[0])/(hi[0]-lo[0])*(R-L);yy=B-(v[:,1]-lo[1])/(hi[1]-lo[1])*(B-T)
   for x,y in zip(xx,yy):dr.ellipse([*xy(x-2+phase,y-2+phase),*xy(x+2+phase,y+2+phase)],fill=color)
  else:
   counts=np.histogram2d(v[:,0],v[:,1],bins=16,range=[[lo[0],hi[0]],[lo[1],hi[1]]])[0];counts/=len(v)
   for i in range(16):
    for j in range(16):
     tone=int(round(255*(1-counts[i,j])));rect(L+i*(R-L)/16+phase,B-(j+1)*(B-T)/16+phase,L+(i+1)*(R-L)/16+phase,B-j*(B-T)/16+phase,(tone,tone,255))
 return im.resize((H,H),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(.5)),sp

def single_ink(arr,col,observer):
 a=np.asarray(arr,float);c=np.asarray(col,float)
 if observer=='hard':return (np.linalg.norm(a-c,axis=-1)<80).astype(float)
 alpha=np.clip(np.sum((255-a)*(255-c),axis=-1)/np.sum((255-c)**2),0,1)
 return np.where(alpha>.05,alpha,0)
def weighted_r(x,y,w):
 w=np.asarray(w,float);w/=w.sum();x=np.asarray(x);y=np.asarray(y);dx=x-np.sum(w*x);dy=y-np.sum(w*y);den=np.sqrt(np.sum(w*dx**2)*np.sum(w*dy**2))
 if den<=0:raise ValueError('No recovered variance')
 return float(np.sum(w*dx*dy)/den)
def decode(im,sp,observer='hard'):
 a=np.asarray(im,float);t=sp['task'];H=sp['H'];L,R,T,B=[sp[k] for k in ['L','R','T','B']]
 if t=='composition':
  pixels=a.reshape(-1,3);pixels=pixels[np.min(pixels,axis=1)<250];pal=np.array(sp['colors'],float)
  dist=np.sum((pixels[:,None,:]-pal[None,:,:])**2,axis=2);which=np.argmin(dist,axis=1)
  if observer=='hard':weights=(np.min(dist,axis=1)<80**2).astype(float)
  else:
   direction=255-pal[which];weights=np.clip(np.sum((255-pixels)*direction,axis=1)/np.sum(direction**2,axis=1),0,1);weights[weights<.05]=0
  masses=np.bincount(which,weights=weights,minlength=sp['n'])
  if masses.sum()==0:raise ValueError('No category colors recovered')
  return masses/masses.sum()
 if t=='profile':
  ink=single_ink(a,sp['color'],observer);xx=np.linspace(L+4,R-4,sp['n']);out=[]
  for x in xx:
   col=ink[:,max(0,round(x)-1):round(x)+2].sum(1);hit=np.flatnonzero(col>(.15 if observer=='soft' else 0))
   if not len(hit):raise ValueError('No value recovered')
   yy=float(hit.min()) if sp['family'] in ['Area chart','Bar chart'] else float(np.average(np.arange(H),weights=col))
   out.append(sp['lo']+(B-yy)/(B-T)*(sp['hi']-sp['lo']))
  return np.asarray(out)
 if sp['family']=='Scatter plot':
  ink=single_ink(a,sp['color'],observer);y,x=np.nonzero(ink)
  if len(x)<3:raise ValueError('No joint observations recovered')
  return np.array([weighted_r(x,-y,ink[y,x])])
 masses=[];xx=[];yy=[]
 for i in range(16):
  for j in range(16):
   x=round(L+(i+.5)*(R-L)/16);y=round(B-(j+.5)*(B-T)/16)
   patch=a[y:y+1,x:x+1] if observer=='hard' else a[y-1:y+2,x-1:x+2]
   masses.append(max(0,1-patch[:,:,0].mean()/255));xx.append(i+.5);yy.append(j+.5)
 return np.array([weighted_r(xx,yy,np.array(masses))])

def run():
 OUT.mkdir(exist_ok=True);cases,rejected=make_cases();(OUT/'inputs.json').write_text(json.dumps(cases,indent=2));(OUT/'excluded.json').write_text(json.dumps(rejected,indent=2));rows=[]
 for ci,c in enumerate(cases):
  target,scale=truth(c)
  for H,phases in [(256,[0,.25,.5,.75]),(384,[.125,.375,.625,.875])]:
   for family in FAMILIES[c['task']]:
    for phase in phases:
     im,sp=render(c,family,H,phase)
     for obs in ['hard','soft']:
      err='';decoded=np.full_like(target,np.nan);ll=np.nan
      try:decoded=decode(im,sp,obs);ll=loss(c,decoded)
      except (ValueError,ZeroDivisionError) as ex:err=str(ex)
      rows.append(dict(key=c['key'],dataset=c['dataset'],kind=c['kind'],task=c['task'],family=family,H=H,phase=phase,observer=obs,loss=ll,error=err,decoded=json.dumps(decoded.tolist()),target=json.dumps(target.tolist()),scale=scale))
  if ci%25==0:print(f'{ci+1}/{len(cases)} cases',flush=True)
 pd.DataFrame(rows).to_csv(OUT/'trials.csv',index=False)
 (OUT/'provenance.json').write_text(json.dumps(dict(cases=len(cases),trial_rows=len(rows),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),protocol_sha256=hashlib.sha256((ROOT/'task_first/protocol.json').read_bytes()).hexdigest(),inputs_sha256=hashlib.sha256((OUT/'inputs.json').read_bytes()).hexdigest(),scope='Retrospective computational extension; no new participants or human-reader responses.'),indent=2))
if __name__=='__main__':run()
