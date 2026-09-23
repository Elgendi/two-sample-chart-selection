from pathlib import Path
import json
import numpy as np,pandas as pd
from observer import SETTINGS,FIXED
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'validation_v2/results'
D=pd.read_csv(OUT/'trials.csv',dtype={'setting':str})
KEY=['key','dataset','feature','family','setting','axis','H','observer']
def aggregate(d):
    a=d.groupby(KEY,sort=False).agg(loss=('loss','mean'),group_loss=('group_loss','mean'),zero_loss=('zero_loss','first'),successful=('loss','count'),low=('loss','min'),high=('loss','max'),scale=('scale','first')).reset_index()
    a.loc[a.successful!=4,['loss','group_loss']]=np.nan
    a['score']=100/(1+a.loss);return a
A=aggregate(D);A.to_csv(OUT/'configurations.csv',index=False)
R=A[(A.axis=='zero')&(A.H==256)&(A.observer=='threshold')].copy()
def best(d,by=['key']):
    finite=d[d.loss.notna()].copy();m=finite.groupby(by).loss.transform('min');ties=finite[np.isclose(finite.loss,m,atol=1e-12,rtol=0)]
    return ties.sort_values(['family','setting'],kind='stable').groupby(by,sort=False).head(1)
F=best(R,['key','family']);W=best(R);F.to_csv(OUT/'families.csv',index=False);W.to_csv(OUT/'winners.csv',index=False)
old=pd.read_csv(ROOT/'rendered_study/results/configuration_scores.csv',dtype={'setting':str});old=old[(old.primary)&(old.H==256)]
pair=R.merge(old,on=['key','family','setting'],suffixes=('_new','_old'))
assert len(pair)==127*21
assert np.allclose(pair.loss_new,pair.loss_old,atol=1e-12,equal_nan=True)
# Oracle family comparisons vs fixed settings: oracle results are explicitly in-sample.
fixedkeys=set(FIXED);fixed=R[R.apply(lambda r:(r.family,r.setting) in fixedkeys,axis=1)]
fixedwinner=best(fixed);fixedwinner.to_csv(OUT/'fixed_budget_winners.csv',index=False)
# All six specified observer x resolution environments; complete settings only.
E=A[A.axis=='zero'].copy();E['best_env']=E.groupby(['key','H','observer']).loss.transform('min');E['regret']=E.loss-E.best_env
B=E.groupby(['key','dataset','family','setting']).agg(worst_regret=('regret','max'),max_loss=('loss','max'),n_env=('loss','count')).reset_index()
B=B[B.n_env==6];BW=B.sort_values(['worst_regret','family','setting']).groupby('key',sort=False).head(1)
B.to_csv(OUT/'robust_settings.csv',index=False);BW.to_csv(OUT/'robust_choices.csv',index=False)
selected=E.merge(W[['key','family','setting']],on=['key','family','setting'])
selectedrisk=selected.groupby('key').agg(worst_regret=('regret','max'),n_env=('loss','count')).reset_index()
# Winner margins and near-optimal families under prespecified error budgets.
rows=[]
for key,f in F.groupby('key'):
    f=f.sort_values('loss');w=f.iloc[0];r=dict(key=key,dataset=w.dataset,winner=w.family,score=w.score,loss=w.loss,runner_up=f.iloc[1].family,gap_loss=f.iloc[1].loss-w.loss,gap_score=w.score-f.iloc[1].score)
    for eps in [.001,.005,.01,.025]:r['near_'+str(eps)]=int((f.loss<=w.loss+eps).sum())
    rows.append(r)
M=pd.DataFrame(rows);M.to_csv(OUT/'margins.csv',index=False)
# Paired comparisons, averaged within resource first; resource bootstrap, not feature IID.
rng=np.random.default_rng(2026092021);comparisons=[]
for f in sorted(F.family.unique()):
    d=F[F.family==f][['key','dataset','loss']].merge(F[F.family=='Quantile plot'][['key','loss']],on='key',suffixes=('_family','_quantile'))
    d['difference']=d.loss_family-d.loss_quantile;means=d.groupby('dataset').difference.mean().dropna().to_numpy()
    boot=np.mean(rng.choice(means,(5000,len(means)),replace=True),axis=1)
    comparisons.append(dict(family=f,valid_cases=int(d.difference.notna().sum()),resources=len(means),mean_resource_loss_difference=float(means.mean()),lower=float(np.quantile(boot,.025)),upper=float(np.quantile(boot,.975))))
pd.DataFrame(comparisons).to_csv(OUT/'resource_bootstrap.csv',index=False)
# One configuration selected on the other resources, each resource weighted equally.
transfer=[]
for dataset in sorted(R.dataset.unique()):
    training=R[R.dataset!=dataset];held=R[R.dataset==dataset]
    cnt=training.groupby(['family','setting']).loss.count();eligible=cnt[cnt==training.key.nunique()].index
    means=training.groupby(['dataset','family','setting']).loss.mean().groupby(['family','setting']).mean()
    pick=means.loc[eligible].sort_values(kind='stable').index[0]
    d=held[(held.family==pick[0])&(held.setting==pick[1])]
    q=held[held.family=='Quantile plot'].set_index('key')
    for _,r in d.iterrows():transfer.append(dict(key=r.key,dataset=dataset,selected_family=pick[0],selected_setting=pick[1],loss=r.loss,quantile_loss=q.loc[r.key,'loss'],score=r.score))
T=pd.DataFrame(transfer);T.to_csv(OUT/'resource_transfer.csv',index=False)
# Observer, resolution, and axes compare both adaptive winners and unchanged configurations.
ref=W.set_index('key');changes=[]
for axis,H,obs in [('zero',128,'threshold'),('zero',512,'threshold'),('zero',256,'alpha'),('tight',256,'threshold')]:
    e=A[(A.axis==axis)&(A.H==H)&(A.observer==obs)]
    commonref=best(R[R.family!='Bar chart']) if axis=='tight' else W
    w=best(e).merge(commonref[['key','family']],on='key',suffixes=('_new','_ref'))
    changes.append(dict(axis=axis,H=H,observer=obs,changed_families=int((w.family_new!=w.family_ref).sum()),cases=len(w)))
pd.DataFrame(changes).to_csv(OUT/'sensitivity.csv',index=False)
# All candidate zero-estimate skill and group-specific error are retained.
G=F.copy();G['skill_vs_zero']=np.where(G.zero_loss>0,1-G.loss/G.zero_loss,np.nan)
G['contrast_to_group_ratio']=np.where(G.group_loss>0,G.loss/(2*G.group_loss),np.nan)
G.to_csv(OUT/'group_error_and_zero_baseline.csv',index=False)
# Synthetic cases generated only after fixed protocol; they are not external human data.
SA=aggregate(pd.read_csv(OUT/'simulation_trials.csv',dtype={'setting':str},keep_default_na=False,na_values=['']));SA.to_csv(OUT/'simulation_configurations.csv',index=False)
SW=best(SA,['key','observer']);SW.to_csv(OUT/'simulation_winners.csv',index=False)
# Flagged CKD values omitted as sensitivity, never silently corrected.
CA=aggregate(pd.read_csv(OUT/'ckd_omission_trials.csv',dtype={'setting':str}));CA.to_csv(OUT/'ckd_omission_configurations.csv',index=False)
CW=best(CA,['key','observer']);CW.to_csv(OUT/'ckd_omission_winners.csv',index=False)
# Descriptive counts only; exact tie tolerance applied to loss.
small=best(A[(A.axis=='zero')&(A.H==128)&(A.observer=='threshold')]).set_index('key')
large=best(A[(A.axis=='zero')&(A.H==512)&(A.observer=='threshold')]).set_index('key')
wm=W.merge(G[['key','family','group_loss','skill_vs_zero']],on=['key','family'],suffixes=('','_audit'))
legacybest=best(R[~R.family.isin(['ECDF','Quantile plot'])]).set_index('key')
q=R[R.family=='Quantile plot'].set_index('key');ec=R[R.family=='ECDF'].set_index('key')
reg=selectedrisk.merge(BW[['key','worst_regret']],on='key',suffixes=('_ref','_robust'))
summary=dict(primary_cases=127,resources=9,trials=len(D),failed=int(D.loss.isna().sum()),legacy_reference_parity=True,wins=W.family.value_counts().to_dict(),fixed_budget_wins=fixedwinner.family.value_counts().to_dict(),median_best=float(W.score.median()),median_quantile=float(q.score.median()),median_ecdf=float(ec.score.median()),median_old_best=float(legacybest.score.median()),quantile_beats_legacy=int((q.loss<legacybest.loss.reindex(q.index)-1e-12).sum()),ecdf_beats_legacy=int((ec.loss<legacybest.loss.reindex(ec.index)-1e-12).sum()),median_margin_score=float(M.gap_score.median()),margins_below_point_one=int((M.gap_score<.1).sum()),median_margin_loss=float(M.gap_loss.median()),near_counts={str(e):int((M['near_'+str(e)]>1).sum()) for e in [.001,.005,.01,.025]},resolution_changes=int((small.family!=large.family.reindex(small.index)).sum()),sensitivity=changes,robust_wins=BW.family.value_counts().to_dict(),median_reference_worst_regret=float(reg[reg.n_env==6].worst_regret_ref.median()),median_robust_worst_regret=float(reg[reg.n_env==6].worst_regret_robust.median()),reference_incomplete_settings=int((selectedrisk.n_env<6).sum()),transfer_selected=T.groupby('dataset').selected_family.first().to_dict(),transfer_mean_resource_loss=float(T.groupby('dataset').loss.mean().mean()),transfer_failures=int(T.loss.isna().sum()),simulation_cases=SA.key.nunique(),simulation_threshold_wins=SW[SW.observer=='threshold'].family.value_counts().to_dict(),simulation_alpha_wins=SW[SW.observer=='alpha'].family.value_counts().to_dict(),ckd_omission_winners=CW[['observer','family','setting','score']].to_dict('records'),wins_without_retinopathy=W[W.dataset!='Retinopathy'].family.value_counts().to_dict())
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
# Manuscript table generated from current results.
lines=[]
for family,dd in F.groupby('family'):
    count=int((W.family==family).sum());fw=int((fixedwinner.family==family).sum())
    lines.append((count,family,dd.score.median(),dd.group_loss.median(),dd.loss.notna().sum(),fw))
lines.sort(reverse=True)
(OUT/'family_table.tex').write_text('\\begin{tabular}{lrrrrr}\\toprule\nFamily & Wins & Fixed wins & Median $S$ & Median $G$ & Valid\\\\\\midrule\n'+''.join(f'{f} & {n} & {fw} & {s:.2f} & {g:.3f} & {v}\\\\\n' for n,f,s,g,v,fw in lines)+'\\bottomrule\\end{tabular}\n')
# Explicit tied sets accompany deterministic representative rows.
tied=F[F.loss.notna()].copy();tied['minimum']=tied.groupby('key').loss.transform('min');tied=tied[np.isclose(tied.loss,tied.minimum,atol=1e-12,rtol=0)];tied.to_csv(OUT/'winning_sets.csv',index=False)
summary['tied_cases']=int((tied.groupby('key').size()>1).sum())
assert np.all(A.loc[A.loss.notna(),'loss']<=2*A.loc[A.loss.notna(),'group_loss']+1e-10)
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
mac={'BestMedian':f"{summary['median_best']:.3f}",'QuantileMedian':f"{summary['median_quantile']:.3f}",'ECDFMedian':f"{summary['median_ecdf']:.3f}",'LegacyMedian':f"{summary['median_old_best']:.3f}",'QuantileBetter':summary['quantile_beats_legacy'],'ECDFBetter':summary['ecdf_beats_legacy'],'ResolutionChanged':summary['resolution_changes'],'NearCount':summary['near_counts']['0.01'],'MarginMedian':f"{summary['median_margin_score']:.3f}",'SmallMargins':summary['margins_below_point_one'],'ObserverChanged':next(r['changed_families'] for r in changes if r['observer']=='alpha'),'TransferLoss':f"{summary['transfer_mean_resource_loss']:.4f}"}
(OUT/'numbers.tex').write_text(''.join('\\newcommand{\\'+k+'}{'+str(v)+'}\n' for k,v in mac.items()))
def esc(s):return str(s).replace('_',r'\_').replace('&',r'\&')
# Complete reference audit with group fidelity and excess-error choice counts.
audit=W.merge(M[['key','gap_score','near_0.01']],on='key').sort_values(['dataset','key'])
head='\\begin{longtable}{llrrrr}\\toprule\nComparison & Selected family & $S$ & $G$ & Margin & Near\\\\\\midrule\\endhead\n'
(OUT/'audit.tex').write_text(head+''.join(f"{esc(r.key)} & {esc(r.family)} & {r.score:.2f} & {r.group_loss:.3f} & {r.gap_score:.3f} & {int(r['near_0.01'])}\\\\\n" for _,r in audit.iterrows())+'\\bottomrule\\end{longtable}\n')
boot=pd.read_csv(OUT/'resource_bootstrap.csv')
(OUT/'bootstrap.tex').write_text('\\begin{tabular}{lrrrr}\\toprule\nFamily & Cases & Mean difference & Lower & Upper\\\\\\midrule\n'+''.join(f'{r.family} & {r.valid_cases} & {r.mean_resource_loss_difference:.4f} & {r.lower:.4f} & {r.upper:.4f}\\\\\n' for r in boot.itertuples())+'\\bottomrule\\end{tabular}\n')
tr=T.groupby('dataset').agg(family=('selected_family','first'),setting=('selected_setting','first'),n=('key','size'),valid=('loss','count'),loss=('loss','mean')).reset_index()
(OUT/'transfer.tex').write_text('\\begin{tabular}{llrrrr}\\toprule\nOmitted resource & Selected family & Setting & Cases & Valid & Mean loss\\\\\\midrule\n'+''.join(f'{r.dataset} & {r.family} & {r.setting} & {r.n} & {r.valid} & {r.loss:.4f}\\\\\n' for r in tr.itertuples())+'\\bottomrule\\end{tabular}\n')
# Failure denominators retained; multiple settings and observers differ in difficulty.
fa=D.groupby(['family','observer']).agg(trials=('key','size'),failures=('loss',lambda x:x.isna().sum())).reset_index()
(OUT/'failures.tex').write_text('\\begin{longtable}{llrr}\\toprule\nFamily & Observer & Trials & Failures\\\\\\midrule\\endhead\n'+''.join(f'{r.family} & {r.observer} & {r.trials} & {r.failures}\\\\\n' for r in fa.itertuples())+'\\bottomrule\\end{longtable}\n')
# Explicit CKD before/after records for the sensitivity table.
ckdkey=CA.key.iloc[0];cb=W[W.key==ckdkey].iloc[0];new=CW[CW.observer=='threshold'].iloc[0]
(OUT/'ckd.tex').write_text('\\begin{tabular}{llrr}\\toprule\nCondition & Winner & Setting & Score\\\\\\midrule\n'+f'Original & {cb.family} & {cb.setting} & {cb.score:.3f}\\\\\nOmit flagged values & {new.family} & {new.setting} & {new.score:.3f}\\\\\n'+'\\bottomrule\\end{tabular}\n')
print('Manuscript tables and macros generated; tied cases:',summary['tied_cases'])
source_rows=[]
for label,ww in [('All resources',W),('Exclude retinopathy',W[W.dataset!='Retinopathy'])]:
    for f,n in ww.family.value_counts().items():source_rows.append((label,f,n))
(OUT/'source_sensitivity.tex').write_text('\\begin{center}\\begin{tabular}{llr}\\toprule\nSource set & Winning family & Cases\\\\\\midrule\n'+''.join(f'{l} & {f} & {n}\\\\\n' for l,f,n in source_rows)+'\\bottomrule\\end{tabular}\\end{center}\n')
