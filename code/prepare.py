from pathlib import Path
import zipfile,io,json,re,shutil,urllib.request
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];RAW=ROOT/'data/raw';DER=ROOT/'data/derived'
CASES=[];AUDIT=[]
def csv_zip(key,name,**kw):
 with zipfile.ZipFile(RAW/f'{key}.zip') as z:return pd.read_csv(io.BytesIO(z.read(name)),**kw)
def add(dataset,feature,x,y,paired=False,unit='source units',labels=('A','B'),rows=None):
 x=pd.to_numeric(pd.Series(x),errors='coerce').to_numpy(dtype=float);y=pd.to_numeric(pd.Series(y),errors='coerce').to_numpy(dtype=float)
 nx,ny=len(x),len(y)
 if paired:
  assert nx==ny;v=np.isfinite(x)&np.isfinite(y);x=x[v];y=y[v]
 else:x=x[np.isfinite(x)];y=y[np.isfinite(y)]
 assert min(len(x),len(y))>=4,(dataset,feature,len(x),len(y))
 key=f'{dataset}__{len([c for c in CASES if c["dataset"]==dataset]):02d}'
 CASES.append({'key':key,'dataset':dataset,'feature':feature,'paired':paired,'unit':unit,'labels':labels,'x':x.tolist(),'y':y.tolist()})
 AUDIT.append({'key':key,'dataset':dataset,'feature':feature,'paired':paired,'n_x':len(x),'n_y':len(y),'missing_x':nx-len(x),'missing_y':ny-len(y),'source_rows':rows})
def groups(ds,df,features,target,a,b,labels,units=None):
 for f in features:add(ds,f,df.loc[target==a,f],df.loc[target==b,f],labels=labels,rows=len(df),unit=(units or {}).get(f,'source units'))
def main():
 CASES.clear();AUDIT.clear();DER.mkdir(parents=True,exist_ok=True)
 # Raw source copies are bundled; fetch.py documents reproducible acquisition.
 df=pd.read_csv(RAW/'wdbc.csv');groups('WDBC',df,df.columns[:30],df.target,1,0,('Benign','Malignant'))
 cols=['age','sex','cp','trestbps','chol','fbs','restecg','thalach','exang','oldpeak','slope','ca','thal','num']
 df=csv_zip('heart','processed.cleveland.data',header=None,names=cols,na_values='?');groups('Cleveland',df,['age','trestbps','chol','thalach','oldpeak'],df.num.gt(0),False,True,('No disease','Disease'),{'age':'years','trestbps':'mmHg','chol':'mg/dL','thalach':'bpm'})
 df=csv_zip('failure','heart_failure_clinical_records_dataset.csv');groups('HeartFailure',df,['age','creatinine_phosphokinase','ejection_fraction','platelets','serum_creatinine','serum_sodium'],df.DEATH_EVENT,0,1,('Survived','Died'),{'age':'years','ejection_fraction':'%','serum_creatinine':'mg/dL','serum_sodium':'mEq/L'})
 p=RAW/'kidney.csv'
 if not p.exists():
  with urllib.request.urlopen('https://archive.ics.uci.edu/static/public/336/data.csv',timeout=40) as r:p.write_bytes(r.read())
 df=pd.read_csv(p).rename(columns={'wbcc':'wc','rbcc':'rc'});print('kidney columns',list(df.columns));target=df['class'].str.strip();groups('CKD',df,['age','bp','bgr','bu','sc','sod','pot','hemo','pcv','wc','rc'],target,'notckd','ckd',('Non-CKD','CKD'),{'age':'years','bp':'mmHg'})
 cols=['age','sex','total_bilirubin','direct_bilirubin','alkaline_phosphatase','ALT','AST','total_protein','albumin','albumin_globulin_ratio','class']
 df=csv_zip('liver','Indian Liver Patient Dataset (ILPD).csv',header=None,names=cols);groups('ILPD',df,[f for f in cols if f not in ['sex','class']],df['class'],2,1,('No liver disease','Liver disease'),{'age':'years'})
 df=csv_zip('parkinsons','parkinsons.data');features=[c for c in df if c not in ['name','status']];df['subject']=df.name.str.rsplit('_',n=1).str[0]
 assert (df.groupby('subject').status.nunique()==1).all();sub=df.groupby('subject')[features+['status']].median();groups('Parkinsons',sub,features,sub.status,0,1,('Healthy','Parkinson disease'));sub.to_csv(DER/'parkinsons_subjects.csv')
 with zipfile.ZipFile(RAW/'retina.zip') as z:raw=z.read('messidor_features.arff').decode().split('@data')[1]
 df=pd.read_csv(io.StringIO(raw),header=None);features=list(range(2,18));df=df.rename(columns={i:f'feature_{i}' for i in range(20)});groups('Retinopathy',df,[f'feature_{i}' for i in features],df.feature_19,0,1,('Class 0','Class 1'))
 with zipfile.ZipFile(RAW/'har.zip') as outer:
  with zipfile.ZipFile(io.BytesIO(outer.read('UCI HAR Dataset.zip'))) as z:
   prefix='UCI HAR Dataset/';names=[l.split(' ',1)[1] for l in z.read(prefix+'features.txt').decode().splitlines()]
   use=[i for i,n in enumerate(names) if n.startswith('t') and ('-mean()' in n or '-std()' in n)]
   pieces=[]
   for part in ['train','test']:
    x=np.loadtxt(io.BytesIO(z.read(prefix+f'{part}/X_{part}.txt')),usecols=use);y=np.loadtxt(io.BytesIO(z.read(prefix+f'{part}/y_{part}.txt')),dtype=int);subjects=np.loadtxt(io.BytesIO(z.read(prefix+f'{part}/subject_{part}.txt')),dtype=int)
    t=pd.DataFrame(x,columns=[names[i] for i in use]);t['activity']=y;t['subject']=subjects;pieces.append(t)
   df=pd.concat(pieces,ignore_index=True);sub=df.groupby(['subject','activity']).median();a=sub.xs(4,level='activity');b=sub.xs(1,level='activity');assert a.index.equals(b.index)
   for f in a:add('HAR',f,a[f],b[f],True,unit='normalized source units',labels=('Sitting','Walking'),rows=len(df))
   sub.to_csv(DER/'har_subject_activity.csv')
 functions={'mean':np.mean,'median':np.median,'q10':lambda z:np.quantile(z,.1),'q90':lambda z:np.quantile(z,.9),'SD':lambda z:np.std(z,ddof=1)}
 subjects={}
 for p in sorted((RAW/'bidmc').glob('*Numerics.csv')):
  df=pd.read_csv(p);df.columns=df.columns.str.strip();v=np.isfinite(df.HR)&np.isfinite(df.PULSE)&(df.HR>0)&(df.PULSE>0)
  identifier=re.search(r'MIMIC II matched wdb ID: (\S+)',p.with_name(p.name.replace('Numerics.csv','Fix.txt')).read_text()).group(1)
  subjects.setdefault(identifier,[]).append(df.loc[v,['HR','PULSE']].to_numpy())
 rows=[]
 for id,items in subjects.items():
  v=np.vstack(items)
  for f,fun in functions.items():rows.append({'subject':id,'statistic':f,'x':fun(v[:,0]),'y':fun(v[:,1]),'recordings':len(items)})
 df=pd.DataFrame(rows);df.to_csv(DER/'bidmc_subjects.csv',index=False)
 for f in functions:
  d=df[df.statistic==f];add('BIDMC',f,d.x,d.y,True,'bpm',('ECG HR','PPG pulse'),53)
 series=pd.read_csv(RAW/'wearable_5s_series.csv');rows=[]
 for record,s in series.groupby('record'):
  lo,hi=s.time_s.min(),s.time_s.max();a=s.loc[s.time_s<=lo+(hi-lo)/3,'hr_5s'];b=s.loc[s.time_s>=hi-(hi-lo)/3,'hr_5s'];assert min(len(a),len(b))>1
  for f,fun in functions.items():rows.append({'participant':s.participant.iloc[0],'record':record,'statistic':f,'x':fun(a),'y':fun(b)})
 df=pd.DataFrame(rows);df.to_csv(DER/'wrist_records.csv',index=False);sub=df.groupby(['participant','statistic'])[['x','y']].mean().reset_index();sub.to_csv(DER/'wrist_participants.csv',index=False)
 for f in functions:
  d=sub[sub.statistic==f];add('Wrist',f,d.x,d.y,True,'bpm',('Early third','Late third'),19)
 (DER/'comparisons.json').write_text(json.dumps(CASES,indent=2));pd.DataFrame(AUDIT).to_csv(DER/'comparison_audit.csv',index=False)
 print(pd.DataFrame(AUDIT).groupby('dataset').agg(comparisons=('key','count'),n_x_min=('n_x','min'),n_y_min=('n_y','min')))
 print('Total comparisons',len(CASES))
if __name__=='__main__':main()
