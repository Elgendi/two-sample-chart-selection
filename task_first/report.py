"""Create a single auditable task table, frozen-choice comparisons and manuscript numbers."""
from pathlib import Path
import json,numpy as np,pandas as pd
R=Path(__file__).resolve().parents[1];O=R/'task_first/results'
a=pd.read_csv(O/'configurations.csv');a['setting']=a.family.map({'Heatmap':'16x16','Scatter plot':'opaque 2px','Pie chart':'sectors','Donut chart':'52% hole','Stacked bar':'one strip','Bar chart':'values','Line chart':'2px','Area chart':'filled','Dot plot':'2px'})
b=pd.read_csv(O/'legacy_task_scores.csv');b['observer']=b.observer.map({'threshold':'hard','alpha':'soft'});b['kind']='empirical';b=b.drop(columns=['candidate']);c=pd.concat([a,b],ignore_index=True);c.to_csv(O/'all_task_scores.csv',index=False)
families=['Bar chart','Box plot','Interval plot','Dot plot','Histogram','Heatmap','Violin plot','Pie chart','Donut chart','Stacked bar','Line chart','Area chart','Scatter plot'];tasks=['median','spread','five','composition','profile','association']
q=c[(c.H==256)&(c.observer=='hard')&(c.kind=='empirical')]
mat=q.groupby(['family','task']).winner.sum().unstack().reindex(index=families,columns=tasks);mat.to_csv(O/'task_win_matrix.csv')
# Frozen selection in EACH task, keeping all exact ties and choosing declared deterministic order for summaries.
defaults={'median':'Box plot','spread':'Box plot','five':'Dot plot','composition':'Bar chart','profile':'Line chart','association':'Scatter plot'}
rows=[]
for (key,task,obs),z in c.groupby(['key','task','observer']):
 ref=z[z.H==256].copy();ref['order']=ref.family.map({f:i for i,f in enumerate(families)});ref=ref.sort_values(['loss','order']);best=ref.iloc[0];test=z[z.H==384].set_index('family');oracle=test.sort_values('loss').iloc[0];d=defaults[task]
 if not best.family in test.index:continue
 rows.append(dict(key=key,task=task,observer=obs,dataset=best.dataset,kind=best.kind,selected=best.family,reference_score=best.score,reference_ties=int(ref.winner.sum()),test_score=test.loc[best.family,'score'],test_best=oracle.name,test_best_score=oracle.score,regret=test.loc[best.family,'loss']-oracle.loss,score_gap=oracle.score-test.loc[best.family,'score'],still_best=bool(test.loc[best.family,'winner']),default=d,default_test_loss=test.loc[d,'loss'],selected_test_loss=test.loc[best.family,'loss'],gain=test.loc[d,'loss']-test.loc[best.family,'loss']))
t=pd.DataFrame(rows);t.to_csv(O/'all_transfer.csv',index=False)
summary=[]
for keys,z in t.groupby(['task','kind','observer']):
 paired=z.dropna(subset=['default_test_loss','selected_test_loss'])
 summary.append(dict(zip(['task','kind','observer'],keys),cases=len(z),retained=int(z.still_best.sum()),lost=int((~z.still_best).sum()),paired_n=len(paired),default_failures=int(z.default_test_loss.isna().sum()),selected_failures=int(z.selected_test_loss.isna().sum()),mean_default_loss=paired.default_test_loss.mean(),mean_selected_loss=paired.selected_test_loss.mean(),mean_gain=paired.gain.mean()))
pd.DataFrame(summary).to_csv(O/'all_transfer_summary.csv',index=False)
# Empirical task-wise table. Tasks have different units; no overall winner or pooled score.
labels={'median':'Median contrast','spread':'IQR contrast','five':'Five gaps','composition':'Category shares','profile':'Ordered profile','association':'Correlation'}
lines=[r'\begin{tabular}{lrrrr}\toprule',r'Task & Cases & Candidates & Retained & Changed\\\midrule']
for task in tasks:
 z=t[(t.task==task)&(t.observer=='hard')&(t.kind=='empirical')];nc=q[q.task==task].family.nunique();lines.append(f'{labels[task]} & {len(z)} & {nc} & {z.still_best.sum()} & {(~z.still_best).sum()}'+r'\\')
lines.append(r'\bottomrule\end{tabular}');(O/'transfer_table.tex').write_text('\n'.join(lines))
print(mat.to_string());print(pd.DataFrame(summary).query("kind=='empirical'").to_string(index=False))

# Exact source-level descriptive gains on paired valid cases; never treat features as independent trials.
t.dropna(subset=['gain']).groupby(['task','kind','observer','dataset']).agg(paired_n=('gain','size'),mean_gain=('gain','mean')).reset_index().to_csv(O/'resource_transfer_gains.csv',index=False)
