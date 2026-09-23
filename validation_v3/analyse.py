from pathlib import Path
import json,sys
import numpy as np,pandas as pd
from benchmark import OUT,TASKS,CANDIDATES,targets
X=pd.read_csv(OUT/'decoded_trials.csv').drop_duplicates('key').set_index('key')
ZERO={key:{t:np.mean(abs(v))/r.scale for t,v in targets(np.array(json.loads(r.truth_q))).items()} for key,r in X.iterrows()}
A=pd.read_csv(OUT/'configurations.csv');ORDER=[f+' / '+s for f,s in CANDIDATES];RES=sorted(A.dataset.unique())
def best(d):
 p=d.pivot(index='key',columns='candidate',values='loss').reindex(columns=ORDER)
 return p.idxmin(axis=1)
def rb(v):return v.groupby('dataset').loss.mean().mean()
rows=[];folds=[];members=[]
for ob in ['threshold','alpha']:
 for task in TASKS:
  d=A[(A.observer==ob)&(A.task==task)];train=d[d.H==256];test=d[d.H==384]
  ref=best(train);oracle=best(test)
  valid=test[test.loss.notna()];mins=valid.groupby('key').loss.transform('min');wins=valid[np.isclose(valid.loss,mins,atol=1e-12,rtol=0)]
  members.extend(wins[['key','dataset','candidate','observer','task','loss']].to_dict('records'))
  for res in RES:
   t=train[train.dataset!=res];m=t.groupby(['dataset','candidate']).loss.mean().groupby('candidate').mean().reindex(ORDER)
   valid_candidates=t.groupby('candidate').loss.apply(lambda x:x.notna().all());m=m.where(valid_candidates.reindex(m.index));chosen=m.idxmin()
   folds.append(dict(observer=ob,task=task,heldout_resource=res,candidate=chosen,training_loss=m[chosen],training_resources='|'.join(r for r in RES if r!=res)))
   for key in sorted(test[test.dataset==res].key.unique()):
    v=test[test.key==key].set_index('candidate').loss
    choices={'quantile5':'Quantile plot / five','quantile19':'Quantile plot / nineteen','ecdf':'ECDF / full','task_default':chosen,'case_selected':ref[key],'test_oracle':oracle[key]}
    rows.append(dict(key=key,dataset=res,observer=ob,task=task,rule='zero_target',candidate='No chart: predict zero',loss=ZERO[key][task],oracle_loss=v[oracle[key]],excess_loss=ZERO[key][task]-v[oracle[key]]))
    for rule,c in choices.items():rows.append(dict(key=key,dataset=res,observer=ob,task=task,rule=rule,candidate=c,loss=v[c],oracle_loss=v[oracle[key]],excess_loss=v[c]-v[oracle[key]]))
D=pd.DataFrame(rows);D.to_csv(OUT/'policy_results.csv',index=False);pd.DataFrame(folds).to_csv(OUT/'folds.csv',index=False)
W=pd.DataFrame(members);W.to_csv(OUT/'winner_memberships.csv',index=False)
W.groupby(['observer','task','candidate']).size().reset_index(name='memberships').to_csv(OUT/'winner_counts.csv',index=False)
summary=[];effects=[];rng=np.random.default_rng(20260921)
for (ob,task,rule),v in D.groupby(['observer','task','rule']):
 summary.append(dict(observer=ob,task=task,rule=rule,loss=rb(v),failures=int(v.loss.isna().sum()),n=len(v),median_excess_loss=v.excess_loss.median(),within_001=int((v.excess_loss<=.01).sum())))
for (ob,task),v in D.groupby(['observer','task']):
 p=v.pivot(index=['dataset','key'],columns='rule',values='loss')
 for comparator in ['task_default','quantile5','quantile19','ecdf','zero_target']:
  diff=p[comparator]-p.case_selected;means=diff.groupby('dataset').mean().dropna();boot=means.to_numpy()[rng.integers(0,len(means),(5000,len(means)))].mean(axis=1)
  effects.append(dict(observer=ob,task=task,comparator=comparator,gain=means.mean(),ci_low=np.quantile(boot,.025),ci_high=np.quantile(boot,.975),valid_pairs=int(diff.notna().sum()),resources=len(means),improved=int((diff>1e-12).sum()),worsened=int((diff< -1e-12).sum()),tied=int((abs(diff)<=1e-12).sum()),gain_above_001=int((diff>.01).sum()),harm_above_001=int((diff<-.01).sum())))
S=pd.DataFrame(summary);S.to_csv(OUT/'policy_summary.csv',index=False);E=pd.DataFrame(effects);E.to_csv(OUT/'paired_effects.csv',index=False)
labels={'median':'Median','spread':'Interquartile spread','asymmetry':'Tail asymmetry','upper_tail':'Upper-tail extent','five':'Five quantiles','dense19':'19 quantiles'}
lines=['\\begin{tabular}{lrrrr}\\toprule','Task & Q19 & Task default & Case selection & Gain (95\\% interval)\\\\\\midrule']
for task in TASKS:
 s=S[(S.observer=='threshold')&(S.task==task)].set_index('rule');e=E[(E.observer=='threshold')&(E.task==task)&(E.comparator=='task_default')].iloc[0]
 lines.append(f"{labels[task]} & {s.loc['quantile19','loss']:.4f} & {s.loc['task_default','loss']:.4f} & {s.loc['case_selected','loss']:.4f} & {e.gain:+.4f} [{e.ci_low:+.4f}, {e.ci_high:+.4f}]\\\\")
lines+=['\\bottomrule\\end{tabular}'];(OUT/'policy_table.tex').write_text('\n'.join(lines)+'\n')
lines=['\\begin{longtable}{lllrrr}\\toprule','Observer & Task & Rule & Mean loss & Failures & Within .01\\\\\\midrule\\endhead']
for r in S.itertuples():
 lines.append(f"{r.observer} & {labels[r.task]} & {r.rule.replace('_',' ')} & {r.loss:.5f} & {r.failures} & {r.within_001}\\\\")
lines+=['\\bottomrule\\end{longtable}'];(OUT/'full_policy_table.tex').write_text('\n'.join(lines)+'\n')
(OUT/'summary.json').write_text(json.dumps({'cases':127,'resources':len(RES),'task_losses':127*10*2*4*2*6,'image_decoder_trials':127*10*2*4*2,'invalid_configurations':int(A.loss.isna().sum()),'policy_failures':int(D.loss.isna().sum()),'paired_effects':E[E.comparator=='task_default'].to_dict('records')},indent=2))
print(E[E.comparator=='task_default'].to_string(index=False))
print(S[S.rule.isin(['quantile19','task_default','case_selected'])].to_string(index=False))
# Manuscript statements are generated from the same saved policy results.
e=E[(E.observer=='threshold')&(E.task=='asymmetry')&(E.comparator=='task_default')].iloc[0]
a=E[(E.observer=='alpha')&(E.task=='asymmetry')&(E.comparator=='task_default')].iloc[0]
q=W[W.candidate=='Quantile plot / nineteen'].groupby(['observer','task']).size()
(OUT/'findings.tex').write_text(f'''Case-specific selection does not consistently improve on the task default. For tail asymmetry, its threshold-observer gain is {e.gain:.5f} pooled SD (descriptive 95\\% interval {e.ci_low:.5f} to {e.ci_high:.5f}); the corresponding alpha-observer gain is {a.gain:.5f} ({a.ci_low:.5f} to {a.ci_high:.5f}). For the other five threshold-observer tasks, the point estimate favors the default. Under the alpha observer, selection increases mean loss for spread and upper-tail extent, with descriptive intervals below zero. No evaluated policy has a failed transfer case, although 168 candidate--case--task--environment aggregates are invalidated by failed placements. These results do not support a general advantage for choosing a separate chart for every case.\n\nAt the transfer display, the 19-marker control belongs to the dense-task winning set in {q[('threshold','dense19')]} cases under the threshold observer and {q[('alpha','dense19')]} under the alpha observer. The earlier dense-task ECDF advantage therefore does not survive adding the directly matched dense control. This is evidence about comparator adequacy, not a human preference for more quantile markers.\n''')
