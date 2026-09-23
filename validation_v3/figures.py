from pathlib import Path
import json
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from benchmark import OUT,ROOT,PROBS,TASKS,CANDIDATES,CASES
FIG=ROOT/'validation_v3/figures';FIG.mkdir(exist_ok=True)
NAVY='#173649';TEAL='#00877d';BLUE='#267ea5';ORANGE='#df7836';GREY='#697b86'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':NAVY,'text.color':NAVY,'axes.edgecolor':GREY,'xtick.color':GREY,'ytick.color':GREY,'pdf.fonttype':42})
LABELS=['Median','IQR spread','Tail asymmetry','Upper-tail extent','Five quantiles','19 quantiles']
def save(fig,name):
 fig.savefig(FIG/(name+'.pdf'),bbox_inches='tight');fig.savefig(FIG/(name+'.png'),dpi=180,bbox_inches='tight');plt.close(fig)
def title(ax,t):ax.set_title(t,loc='left',fontweight='bold',pad=12,fontsize=12)
# A synthetic constructive example, never presented as patient data.
fig,axs=plt.subplots(1,3,figsize=(10.5,4.1),gridspec_kw={'wspace':.4});fig.suptitle('Same marginal distributions, different median changes',fontsize=16,weight='bold',y=1.05)
x=np.arange(3);cols=[BLUE,TEAL,ORANGE]
for ax,y,head,result in [(axs[0],x,'a  Aligned pairs','Changes: 0, 0, 0\nMedian change = 0'),(axs[1],np.array([1,2,0]),'b  Permuted pairs','Changes: +1, +1, −2\nMedian change = 1')]:
 for i,c in enumerate(cols):ax.plot([0,1],[x[i],y[i]],'o-',color=c,lw=2,ms=7)
 ax.set_xticks([0,1]);ax.set_xticklabels(['Before','After']);ax.set_yticks([0,1,2]);ax.set_xlim(-.15,1.15);ax.set_ylim(-.2,2.2);ax.set_ylabel('Value');title(ax,head);ax.text(.5,-.2,result,ha='center',va='top',transform=ax.transAxes,linespacing=1.7,weight='bold')
ax=axs[2]
for g,col in [(0,BLUE),(1,ORANGE)]:ax.scatter(np.full(3,g),x,s=80,color=col)
ax.set_xticks([0,1]);ax.set_xticklabels(['Before','After']);ax.set_yticks([0,1,2]);ax.set_xlim(-.3,1.3);ax.set_ylim(-.2,2.2);title(ax,'c  Identical marginals');ax.text(.5,-.2,'Pair identity omitted\nPaired-median task: ineligible',ha='center',va='top',transform=ax.transAxes,linespacing=1.7,weight='bold')
save(fig,'Figure_1_Eligibility')
# Configuration counts, including all ties.
W=pd.read_csv(OUT/'winner_counts.csv');names=['Mean bars','Box','Interval','Raw dots','Histogram (16)','Heatmap (16)','Violin (64)','ECDF','Quantiles (5)','Quantiles (19)'];order=[f+' / '+s for f,s in CANDIDATES]
fig,axs=plt.subplots(2,1,figsize=(9,10.5),gridspec_kw={'hspace':.43});fig.suptitle('Who wins after adding the task-matched control?',fontsize=16,weight='bold',y=1.01)
for ax,ob in zip(axs,['threshold','alpha']):
 p=W[W.observer==ob].pivot(index='candidate',columns='task',values='memberships').reindex(index=order,columns=TASKS).fillna(0)
 im=ax.imshow(p,cmap='YlGnBu',vmin=0,vmax=127,aspect='auto')
 for i in range(10):
  for j in range(6):ax.text(j,i,str(int(p.iloc[i,j])),ha='center',va='center',fontsize=12,color='white' if p.iloc[i,j]>90 else NAVY)
 ax.set_xticks(range(6));ax.set_xticklabels(LABELS,rotation=25,ha='right');ax.set_yticks(range(10));ax.set_yticklabels(names);title(ax,ob.capitalize()+' observer')
fig.subplots_adjust(bottom=.12,right=.88);cb=fig.add_axes([.91,.25,.022,.55]);fig.colorbar(im,cax=cb,label='Winning memberships / 127 cases')
fig.text(.12,.01,'384-pixel evaluation. Columns retain ties. Two quantile budgets are separate configurations.',fontsize=10,color=GREY)
save(fig,'Figure_2_Tasks')
# Out-of-display incremental value rather than winner novelty.
E=pd.read_csv(OUT/'paired_effects.csv');D=pd.read_csv(OUT/'policy_results.csv');fig,axs=plt.subplots(1,2,figsize=(9.5,5.7),sharey=True,gridspec_kw={'wspace':.12});fig.suptitle('Does choosing a chart per case beat a task default?',fontsize=16,weight='bold',y=1.01)
for ax,ob,co in zip(axs,['threshold','alpha'],[BLUE,TEAL]):
 e=E[(E.observer==ob)&(E.comparator=='task_default')].set_index('task').loc[TASKS]
 for i,task in enumerate(TASKS):
  p=D[(D.observer==ob)&(D.task==task)].pivot(index=['dataset','key'],columns='rule',values='loss');v=(p.task_default-p.case_selected).groupby('dataset').mean().to_numpy();ax.scatter(v,i+np.linspace(-.11,.11,len(v)),s=15,color=GREY,alpha=.35,zorder=1)
 ax.errorbar(e.gain,np.arange(6),xerr=np.array([e.gain-e.ci_low,e.ci_high-e.gain]),fmt='o',color=co,capsize=4,lw=2,zorder=3)
 ax.axvline(0,color=GREY,ls='--');ax.set_yticks(range(6));ax.set_yticklabels(LABELS);ax.invert_yaxis() if not ax.yaxis_inverted() else None;title(ax,ob.capitalize()+' observer');ax.set_xlabel('Task-default loss − case-selection loss\nPositive: case selection improves recovery');ax.grid(axis='x',alpha=.12);ax.set_xlim(-.0095,.0065);ax.set_xticks([-.008,-.004,0,.004])
fig.subplots_adjust(bottom=.2);fig.text(.12,.02,'Large points: resource-balanced gain. Lines: descriptive 95% intervals. Small points: nine resource means.',fontsize=10,color=GREY)
save(fig,'Figure_3_Policies')
# Same case throughout, exact summaries vs rendered recoveries.
X=pd.read_csv(OUT/'decoded_trials.csv');c=next(c for c in CASES if c['key']=='WDBC__00');z=X[(X.key==c['key'])&(X.H==384)&(X.observer=='threshold')];truth=np.array(json.loads(z.iloc[0].truth_q));scale=z.iloc[0].scale
ideal5=np.array([np.interp(PROBS,PROBS[[1,4,9,14,17]],g[[1,4,9,14,17]]) for g in truth]);q5=np.mean([json.loads(v) for v in z[(z.setting=='five')&(z.family=='Quantile plot')].decoded_q],axis=0);q19=np.mean([json.loads(v) for v in z[z.setting=='nineteen'].decoded_q],axis=0)
fig,axs=plt.subplots(2,2,figsize=(10,8),gridspec_kw={'hspace':.55,'wspace':.4});fig.suptitle('Separate what the chart omits from what pixels distort',fontsize=16,weight='bold',y=1.01)
ax=axs[0,0]
for g,col in enumerate([BLUE,ORANGE]):ax.plot(PROBS*100,truth[g],'.-',color=col,label=['A: '+str(c['labels'][0]),'B: '+str(c['labels'][1])][g],ms=5)
ax.set_xlabel('Percentile');ax.set_ylabel('Mean tumour radius (source units)');ax.legend(frameon=False,fontsize=10);title(ax,'a  One fixed example: WDBC, feature 00')
ax=axs[0,1]
for q,lab,col,ls in [(truth,'Empirical target',NAVY,'-'),(ideal5,'Exact five-marker interpolation',ORANGE,'--'),(q5,'Five-marker pixel recovery',BLUE,':'),(q19,'19-marker pixel recovery',TEAL,'--')]:ax.plot(PROBS*100,(q[1]-q[0])/scale,ls,color=col,label=lab,lw=1.6)
ax.set_xlabel('Percentile');ax.set_ylabel('B − A / pooled SD');ax.legend(frameon=False,fontsize=10);title(ax,'b  Target coverage and pixel recovery')
S=pd.read_csv(OUT/'quantile_error_summary.csv');S=S[(S.observer=='threshold')&(S.H==384)]
for ax,var,head in [(axs[1,0],'encoding','c  Information omitted by exact markers'),(axs[1,1],'raster','d  Error relative to exact plotted markers')]:
 for j,(setting,label,col) in enumerate([('five','Five markers',BLUE),('nineteen','19 markers',TEAL)]):
  vals=S[S.setting==setting].set_index('task').loc[TASKS,var];ax.bar(np.arange(6)+(j-.5)*.35,vals,width=.33,color=col,label=label)
 ax.set_xticks(range(6));ax.set_xticklabels(LABELS,rotation=35,ha='right');ax.set_ylabel('Resource-balanced mean loss');ax.legend(frameon=False,fontsize=10);title(ax,head)
fig.subplots_adjust(bottom=.18);fig.text(.1,.01,'Panels c–d: all 127 cases, nine equally weighted resources. Error magnitudes need not add because signs can cancel.',fontsize=9,color=GREY)
save(fig,'Figure_4_Encoding');print('Four v3 figures written.')
