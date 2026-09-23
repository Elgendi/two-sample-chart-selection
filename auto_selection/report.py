from pathlib import Path
import json
import pandas as pd
from dataset_sources import SOURCES
P=Path(__file__).resolve().parents[1];R=P/'auto_selection/results';d=pd.read_csv(R/'automatic_selections.csv');f=pd.read_csv(R/'all_family_scores.csv')
def esc(x):return str(x).replace('_',r'\_').replace('%',r'\%').replace('&',r'\&').replace('#',r'\#')
def label(s):return {'Mean summary sufficient':'Mean sufficient','Quartile summary sufficient':'Quartiles sufficient','Distribution detail required':'Distribution detail'}[s]
lines=[r'\small\setlength{\tabcolsep}{4pt}\setlength{\LTcapwidth}{\linewidth}',r'\begin{longtable}{>{\raggedright\arraybackslash}p{2.5cm}>{\raggedright\arraybackslash}p{4.5cm}rr>{\raggedright\arraybackslash}p{3.0cm}>{\raggedright\arraybackslash}p{4.0cm}rp{2.0cm}}','\\caption{Every variable and its automatic selection. Higher scores are better under the stated numerical objective; ties are retained. Dataset sources: WDBC\\cite{wdbc}; Cleveland\\cite{heart}; HeartFailure\\cite{failure}; CKD\\cite{kidney}; ILPD\\cite{liver}; Parkinsons\\cite{parkinsons}; Retinopathy\\cite{retina}; HAR\\cite{har}; BIDMC\\cite{bidmc}; Wrist\\cite{wrist}.}\\\\', r'\toprule Dataset & Variable & $n_A$ & $n_B$ & Detected requirement & Optimal common charts & Score & Stability flag\\\midrule\endhead']
for _,r in d.iterrows():
 lines.append(' & '.join([esc(r.dataset)+r'\cite{'+SOURCES[r.dataset][0]+'}',esc(r.feature),str(r.n_x),str(r.n_y),label(r.stratum),r.selected.replace('; ',' / '),f'{r.score:.4f}','Provisional' if r.bootstrap_agreement<.8 else 'No flag'])+r'\\')
lines.append(r'\bottomrule\end{longtable}');(R/'all_variables.tex').write_text('\n'.join(lines))
lines=[r'\begin{tabular}{lrrrr}\toprule Resource & Variables & Mean sufficient & Quartiles sufficient & Distribution detail\\\midrule']
for ds,g in d.groupby('dataset',sort=False):lines.append(' & '.join([ds,str(len(g)),str(sum(g.stratum=='Mean summary sufficient')),str(sum(g.stratum=='Quartile summary sufficient')),str(sum(g.stratum=='Distribution detail required'))])+r'\\')
lines.append(r'\bottomrule\end{tabular}');(R/'resource_summary.tex').write_text('\n'.join(lines))
sim=pd.read_csv(R/'simulation_holdout.csv');lines=[r'\begin{tabular}{lrrr}\toprule Selection rule & Test cases within tolerance & Median retained values & Median error / tolerance\\\midrule']
for method,g in sim.groupby('method'):lines.append(f'{method} & {g.passes.sum()}/240 ({100*g.passes.mean():.1f}\\%) & {g.retained_values.median():.0f} & {g.error_ratio.median():.3f}'+r'\\')
lines.append(r'\bottomrule\end{tabular}');(R/'simulation.tex').write_text('\n'.join(lines))
# Complete numerical matrix: all families have a score for each variable.
wide=f.pivot(index='key',columns='family',values='score');complete=d.merge(wide,on='key');complete['dataset_doi']=complete.dataset.map(lambda x:SOURCES[x][1]);complete['dataset_source_url']='https://doi.org/'+complete.dataset_doi;complete.to_csv(R/'complete_variable_scores.csv',index=False)
# Sensitivity using all previously measured variant errors, no chart-specific retuning.
v=pd.read_csv(R/'all_variant_scores.csv');sensitivity=[]
for multiplier in [.5,1,2]:
 for key,g in v.groupby('key'):
  row=d[d.key==key].iloc[0];eps=max(multiplier*row.resolution_floor,row.uncertainty_radius);ok=g[g.error<=eps*(1+1e-8)].copy();ok['cost']=ok.retained_values+.5*ok.error/eps;best=ok.cost.min();win='; '.join(sorted(ok.loc[(ok.cost-best).abs()<1e-9,'family'].unique()));sensitivity.append(dict(key=key,floor_multiplier=multiplier,selected=win,changed=win!=row.selected))
s=pd.DataFrame(sensitivity);s.to_csv(R/'sensitivity.csv',index=False);print('Floor sensitivity:',s.groupby('floor_multiplier').changed.sum().to_dict())
# Strict-resolution ablation: no sampling allowance; same candidate configurations.
a=[]
for key,g in v.groupby('key'):
 row=d[d.key==key].iloc[0];eps=row.resolution_floor;ok=g[g.error<=eps*(1+1e-8)].copy();ok['cost']=ok.retained_values+.5*ok.error/eps;best=ok.cost.min();a.append(dict(key=key,selected='; '.join(sorted(ok.loc[(ok.cost-best).abs()<1e-9,'family'].unique())),stratum='Mean sufficient' if row.mean_error_ratio*row.epsilon<=eps else ('Quartiles sufficient' if row.box_error_ratio*row.epsilon<=eps else 'Distribution detail')))
pd.DataFrame(a).to_csv(R/'no_sampling_allowance.csv',index=False)
print('Tables generated.')

example_keys=['WDBC__00','Cleveland__04','HeartFailure__00','CKD__06','ILPD__01','Parkinsons__08','Retinopathy__00','HAR__05','BIDMC__00','Wrist__00']
ex=d.set_index('key').loc[example_keys].reset_index()
lines=[r'\begin{tabular}{p{2.4cm}p{3.0cm}p{3.8cm}rp{2.2cm}}\toprule Resource & Example variable & Most suitable chart set & Score & Stability flag\\\midrule']
for _,r in ex.iterrows():lines.append(' & '.join([esc(r.dataset)+r'\cite{'+SOURCES[r.dataset][0]+'}',esc(r.feature),r.selected.replace('; ',' / '),f'{r.score:.4f}','Provisional' if r.bootstrap_agreement<.8 else 'No flag'])+r'\\')
lines.append(r'\bottomrule\end{tabular}');(R/'example_recommendations.tex').write_text('\n'.join(lines))
ex.to_csv(R/'example_recommendations.csv',index=False)
