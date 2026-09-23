"""Separately implemented geometry-based composition decoder; not a model of people."""
from common import *
from PIL import Image
B=loadmod('release_composition_benchmark','task_first/benchmark.py')

def decode_geometry(image,calibration):
 a=np.asarray(image,float);pal=np.asarray(calibration['colors'],float);n=len(pal);H=calibration['H'];L,R,T,Bb=[calibration[k] for k in ['L','R','T','B']]
 def classify(pixels):
  dist=np.linalg.norm(pixels[:,None,:]-pal[None,:,:],axis=2);idx=dist.argmin(1);idx[dist.min(1)>=80]=-1;return idx
 family=calibration['family'];values=np.zeros(n)
 if family in ['Pie chart','Donut chart']:
  # Fixed angular lattice and public center. Phase is deliberately unavailable.
  angle=np.arange(4096)*2*np.pi/4096;rad=.76*(H-28)/2
  xx=np.clip(np.round(H/2+rad*np.cos(angle)).astype(int),0,H-1);yy=np.clip(np.round(H/2+rad*np.sin(angle)).astype(int),0,H-1)
  ids=classify(a[yy,xx]);values=np.bincount(ids[ids>=0],minlength=n).astype(float)
 elif family=='Stacked bar':
  ids=classify(a[round((T+Bb)/2),round(L):round(R)+1]);values=np.bincount(ids[ids>=0],minlength=n).astype(float)
 else:
  for i in range(n):
   x=round(L+(i+.5)*(R-L)/n);ids=classify(a[:,x]);hit=np.flatnonzero(ids==i)
   if len(hit):values[i]=max(0,(Bb-hit.min())/(Bb-T))
 if values.sum()<=0:raise ValueError('No composition recovered')
 return values/values.sum()

def main():
 cases=[c for c in json.loads((ROOT/'task_first/results/inputs.json').read_text()) if c['task']=='composition'];rows=[]
 for c in cases:
  for H,phases in [(256,[0,.25,.5,.75]),(384,[.125,.375,.625,.875])]:
   for f in B.FAMILIES['composition']:
    for phase in phases:
     im,sp=B.render(c,f,H,phase)
     try:u=decode_geometry(im,sp);ll=B.loss(c,u);error=''
     except ValueError as ex:u=np.full(len(c['values']),np.nan);ll=np.nan;error=str(ex)
     rows.append(dict(key=c['key'],kind=c['kind'],family=f,H=H,phase=phase,loss=ll,error=error,decoded=json.dumps(u.tolist())))
 d=pd.DataFrame(rows);d.to_csv(OUT/'geometry_trials.csv',index=False)
 a=d.groupby(['key','kind','family','H']).agg(loss=('loss','mean'),n=('loss','count')).reset_index();a.loc[a.n!=4,'loss']=np.nan
 a['winner']=a.loss<=a.groupby(['key','H']).loss.transform('min')+TOL;a.to_csv(OUT/'geometry_configurations.csv',index=False)
 a.groupby(['kind','H','family']).agg(wins=('winner','sum'),mean_loss=('loss','mean'),failures=('loss',lambda s:s.isna().sum())).reset_index().to_csv(OUT/'geometry_summary.csv',index=False)
 old=pd.read_csv(ROOT/'task_first/results/configurations.csv');old=old[(old.task=='composition')&(old.observer=='hard')]
 comparisons=[]
 for (key,H),q in a.groupby(['key','H']):
  prev=old[(old.key==key)&(old.H==H)];hard=set(prev.loc[prev.winner,'family']);geom=set(q.loc[q.winner,'family'])
  comparisons.append(dict(key=key,H=H,kind=q.iloc[0].kind,hard_winners='|'.join(sorted(hard)),geometry_winners='|'.join(sorted(geom)),any_shared=bool(hard&geom)))
 pd.DataFrame(comparisons).to_csv(OUT/'geometry_agreement.csv',index=False)
 for c in [dict(task='composition',values=[.25,.75])]:
  for family in B.FAMILIES['composition']:
   im,sp=B.render(c,family);u=decode_geometry(im,sp);assert abs(u-np.array(c['values'])).max()<.025
   try:decode_geometry(Image.new('RGB',im.size,'white'),sp)
   except ValueError:pass
   else:raise AssertionError('Blank image accepted')
 (OUT/'geometry_checks.json').write_text(json.dumps(dict(status='passed',contracts=4,blank_image_rejected=True,trial_count=len(d),failures=int(d.loss.isna().sum()),independent_implementation='Angles/endpoints/lengths; no calls to the area-counting decoder; same author and renderer'),indent=2))
 print(a.groupby(['kind','H','family']).winner.sum().to_string())
if __name__=='__main__':main()
