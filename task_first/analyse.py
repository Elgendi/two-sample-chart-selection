"""Compute task-wise winners, ties and frozen-choice transfer without changing outcomes."""
from pathlib import Path
import sys,json
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parent))
from benchmark import ROOT,OUT,FAMILIES,DEFAULT,truth,loss

def main():
 d=pd.read_csv(OUT/'trials.csv');cases={c['key']:c for c in json.loads((OUT/'inputs.json').read_text())}
 rows=[]
 for keys,q in d.groupby(['key','dataset','kind','task','family','H','observer'],sort=False):
  ll=float(q.loss.mean()) if q.loss.notna().all() and len(q)==4 else np.nan
  rows.append(dict(zip(['key','dataset','kind','task','family','H','observer'],keys),loss=ll,score=100/(1+ll),successful=int(q.loss.notna().sum())))
 c=pd.DataFrame(rows);mins=c.groupby(['key','H','observer']).loss.transform('min');c['winner']=np.isclose(c.loss,mins,atol=1e-12,rtol=0);c.to_csv(OUT/'configurations.csv',index=False)
 sums=[]
 for keys,q in c.groupby(['task','kind','observer','H','family']):
  sums.append(dict(zip(['task','kind','observer','H','family'],keys),cases=len(q),wins=int(q.winner.sum()),valid=int(q.loss.notna().sum()),median_score=float(q.score.median()),mean_loss=float(q.loss.mean())))
 pd.DataFrame(sums).to_csv(OUT/'summary.csv',index=False)
 transfers=[]
 for (key,obs),q in c.groupby(['key','observer']):
  ref=q[q.H==256].copy();task=q.iloc[0].task;ref['order']=ref.family.map({f:i for i,f in enumerate(FAMILIES[task])});ref=ref.sort_values(['loss','order']);best=ref.iloc[0];second=ref.iloc[1];test=q[q.H==384].set_index('family');default=DEFAULT[task]
  transfers.append(dict(key=key,task=task,dataset=q.iloc[0].dataset,kind=q.iloc[0].kind,observer=obs,selected=best.family,runner_up=second.family,reference_score=best.score,runner_reference_score=second.score,reference_margin=best.score-second.score,selected_test_score=test.loc[best.family,'score'],runner_test_score=test.loc[second.family,'score'],default=default,default_test_score=test.loc[default,'score'],default_test_loss=test.loc[default,'loss'],selected_test_loss=test.loc[best.family,'loss'],transfer_gain=test.loc[default,'loss']-test.loc[best.family,'loss'],reference_ties=int(ref.winner.sum()),selected_still_best=bool(test.loc[best.family,'winner'])))
 pd.DataFrame(transfers).to_csv(OUT/'transfer.csv',index=False)
 # Existing fixed seven-family median/spread/five results: reuse decoded arrays, not a new experiment.
 old=pd.read_csv(ROOT/'validation_v3/results/configurations.csv');old=old[~old.family.isin(['ECDF','Quantile plot']) & old.task.isin(['median','spread','five'])].copy();mins=old.groupby(['key','task','H','observer']).loss.transform('min');old['winner']=np.isclose(old.loss,mins,atol=1e-12,rtol=0);old['score']=100/(1+old.loss);old.to_csv(OUT/'legacy_task_scores.csv',index=False)
 oc=old[(old.H==256)&(old.observer=='threshold')];oc.groupby(['task','family']).agg(wins=('winner','sum'),median_score=('score','median'),valid=('loss','count')).reset_index().to_csv(OUT/'legacy_task_summary.csv',index=False)
 # Recompute every loss from decoded outputs and fresh target calculation.
 maximum=0.
 for _,z in d.iterrows():
  if pd.isna(z.loss):continue
  actual=loss(cases[z.key],np.array(json.loads(z.decoded)));maximum=max(maximum,abs(actual-z.loss));assert np.isclose(actual,z.loss,atol=1e-12,rtol=0)
 check=dict(trial_rows=len(d),valid_trial_rows=int(d.loss.notna().sum()),failed_trial_rows=int(d.loss.isna().sum()),maximum_loss_recomputation_error=maximum,case_counts=pd.DataFrame(list(cases.values())).groupby(['task','kind']).size().to_dict().__str__(),reference_selection_excludes_transfer=True,legacy_data_unchanged=True)
 (OUT/'verification.json').write_text(json.dumps(check,indent=2));print(json.dumps(check,indent=2));print(pd.DataFrame(sums).query("H==256 and observer=='hard'").to_string(index=False))
if __name__=='__main__':main()
