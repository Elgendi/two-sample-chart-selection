from pathlib import Path
import sys, importlib.util, json, re
import numpy as np, pandas as pd
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'benchmark_release/results'; OUT.mkdir(exist_ok=True)
TASKS=['median','spread','five','composition','profile','association']
LABELS={'median':'Median difference','spread':'Spread difference','five':'Five distributional gaps','composition':'Category shares','profile':'Ordered profile','association':'Correlation'}
TOL=1e-12

def loadmod(name,path):
 spec=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def choose(losses,order):
 s=losses.reindex(order).dropna()
 if not len(s):raise ValueError('No valid candidate')
 return s.index[np.flatnonzero(s.to_numpy()<=s.min()+TOL)[0]]

def patient(key):
 if 'bidmc_' in key:
  record=re.search(r'bidmc_\d+',key).group()
  txt=(ROOT/'data/raw/bidmc'/f'{record}_Fix.txt').read_text()
  return re.search(r'MIMIC II matched wdb ID: (\S+)',txt).group(1)
 return key

def all_configs():
 a=pd.read_csv(ROOT/'validation_v3/results/configurations.csv')
 a=a[a.task.isin(TASKS)].copy();a['kind']='empirical';a['observer']=a.observer.replace({'threshold':'hard','alpha':'soft'});a['cluster']=a.dataset
 b=pd.read_csv(ROOT/'task_first/results/configurations.csv');b['candidate']=b.family
 wrist=pd.read_csv(ROOT/'data/raw/wearable_5s_series.csv').groupby('record').participant.first().to_dict()
 b['cluster']=[patient(r.key) if r.dataset=='BIDMC' else str(wrist.get(r.key.removeprefix('profile_'),r.dataset)) if r.dataset=='Wrist' else r.dataset for r in b.itertuples()]
 cols=['key','dataset','kind','task','candidate','family','H','observer','loss','cluster']
 return pd.concat([a[cols],b[cols]],ignore_index=True)

def order_for(task):
 if task in TASKS[:3]:return ['Bar chart / means','Box plot / five','Interval plot / five','Dot plot / raw','Histogram / 16','Heatmap / 16','Violin plot / 64','ECDF / full','Quantile plot / five','Quantile plot / nineteen']
 return {'composition':['Bar chart','Pie chart','Donut chart','Stacked bar'],'profile':['Line chart','Area chart','Dot plot','Bar chart'],'association':['Scatter plot','Heatmap']}[task]

def balanced(d,column='loss'):
 return d.groupby(['dataset','cluster'])[column].mean().groupby('dataset').mean().mean()

def trained_default(train,order):
 valid=train.groupby('candidate').loss.apply(lambda s:s.notna().all())
 means=train.groupby(['candidate','dataset','cluster']).loss.mean().groupby(['candidate','dataset']).mean().groupby('candidate').mean()
 return choose(means.where(valid),order)
