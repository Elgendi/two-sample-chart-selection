from pathlib import Path
import json
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from observer import prepare,render,decode,P
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'validation_v2/results';FIG=ROOT/'validation_v2/figures';FIG.mkdir(exist_ok=True)
S=json.loads((OUT/'summary.json').read_text());F=pd.read_csv(OUT/'families.csv',dtype={'setting':str});W=pd.read_csv(OUT/'winners.csv',dtype={'setting':str});M=pd.read_csv(OUT/'margins.csv');A=pd.read_csv(OUT/'configurations.csv',dtype={'setting':str});B=pd.read_csv(OUT/'robust_choices.csv',dtype={'setting':str})
CASES={c['key']:c for c in json.loads((ROOT/'data/derived/comparisons.json').read_text())}
NAVY='#173649';TEAL='#00877d';BLUE='#267ea5';ORANGE='#df7836';GREY='#697b86';LIGHT='#e9f2f3'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':NAVY,'text.color':NAVY,'axes.edgecolor':GREY,'xtick.color':GREY,'ytick.color':GREY,'pdf.fonttype':42,'svg.fonttype':'none'})
def save(fig,name):
    fig.savefig(FIG/(name+'.pdf'),bbox_inches='tight');fig.savefig(FIG/(name+'.png'),dpi=180,bbox_inches='tight');plt.close(fig)
def label(ax,title):ax.set_title(title,loc='left',weight='bold',fontsize=11,pad=12)
def rank(ax,key):
    d=F[F.key==key].sort_values('loss');ax.axis('off')
    ax.text(0,1,'FAMILY',weight='bold',fontsize=9);ax.text(1,1,'SCORE',ha='right',weight='bold',fontsize=9)
    for i,(_,r) in enumerate(d.iterrows()):
        yy=.90-i*.092;co=TEAL if i==0 else NAVY
        ax.text(0,yy,f'{i+1}. {r.family}',color=co,weight='bold' if i==0 else 'normal')
        ax.text(1,yy,f'{r.score:.3f}' if np.isfinite(r.score) else 'Failed',ha='right',color=co)
    ax.text(0,-.02,'Ranks are conditional on the decoder.',fontsize=10,color=GREY)
def raster(ax,key,f,s,H=256):
    c=CASES[key];ctx=prepare(c['x'],c['y']);im,spec=render(ctx,f,s,H,0,20260920)
    ax.imshow(im,interpolation='none');ax.set_xlim(0,2*H+16);ax.set_ylim(H,0)
    ax.set_xticks([H/2,1.5*H+16]);ax.set_xticklabels(['A','B']);ax.tick_params(length=0)
    if f not in ['Histogram','Heatmap']:
        vals=np.linspace(ctx['lo'],ctx['hi'],3);ax.set_yticks(H-9-(vals-ctx['lo'])/(ctx['hi']-ctx['lo'])*(H-17));ax.set_yticklabels([f'{v:.2g}' for v in vals]);ax.set_ylabel('Measurement')
        if f in ['Quantile plot','ECDF']:
            ticks=[];labs=[]
            for g in [0,1]:
                for p in [.1,.5,.9]:ticks.append(g*(H+16)+8+p*(H-17));labs.append(str(int(p*100)))
            ax.set_xticks(ticks);ax.set_xticklabels(labs,fontsize=9);ax.set_xlabel('Percentile (A | B)',fontsize=10)
    else:
        ax.set_yticks([H-9,(H-1)/2,8] if f=='Histogram' else []);ax.set_yticklabels(['0','.5','1'] if f=='Histogram' else []);ax.set_ylabel('Bin probability' if f=='Histogram' else '')
        vals=[ctx['lo'],ctx['hi']]*2;ax.set_xticks([8,H-9,H+24,2*H+7]);ax.set_xticklabels([f'{v:.2g}' for v in vals],fontsize=9);ax.set_xlabel('Measurement (A | B)',fontsize=10)
    for sp in ax.spines.values():sp.set_visible(False)
    return ctx
# Figure 1: compact mathematical workflow + actual example and full ranking.
fig=plt.figure(figsize=(10.5,7.1));fig.text(.05,.97,'A chart score needs a task and a robustness check',fontsize=17,weight='bold')
boxes=[('DECLARE','Five quantile differences\nCommon units and axes'),('RECOVER','Rendered pixels + calibration\nTwo computational observers'),('AUDIT','Contrast + group error\nStrong baselines and failures')]
for i,(head,body) in enumerate(boxes):
    ax=fig.add_axes([.05+i*.32,.73,.28,.17]);ax.axis('off');ax.add_patch(FancyBboxPatch((.01,.01),.98,.95,boxstyle='round,pad=.01',facecolor=LIGHT,edgecolor='#c6d8dd'));ax.text(.06,.73,head,weight='bold',fontsize=11);ax.text(.06,.28,body,fontsize=9,linespacing=1.5)
fig.text(.05,.65,r'$S_c=100/(1+L_c)$',fontsize=17,color=TEAL);fig.text(.37,.65,r'$R_c=\max_e\{L_{c,e}-\min_j L_{j,e}\}$',fontsize=17,color=TEAL)
fig.text(.05,.60,'Reference score: lower recovery error',fontsize=9);fig.text(.48,.60,'Robust choice: lower worst-environment regret',fontsize=9)
key='WDBC__10';w=W[W.key==key].iloc[0];ax=fig.add_axes([.07,.13,.50,.34]);raster(ax,key,w.family,w.setting);label(ax,'Example: tumour radius standard error')
ax=fig.add_axes([.68,.13,.27,.39]);rank(ax,key)
fig.text(.05,.02,'A high score means accurate computational recovery of this task; it does not establish human readability.',fontsize=9,color=GREY)
save(fig,'Figure_1_Contract')
# Figure 2: strong baselines, equal-budget results, and synthetic stress tests.
fig,axs=plt.subplots(2,2,figsize=(11,8.3),gridspec_kw={'hspace':.52,'wspace':.38});fig.suptitle('Strong baselines test what chart optimization adds',fontsize=17,weight='bold',y=1.01)
order=F.groupby('family').score.median().sort_values().index.tolist();ax=axs[0,0]
for i,f in enumerate(order):
    a=F[F.family==f].score.dropna();ax.plot(np.quantile(a,[.1,.9]),[i,i],color=GREY,lw=2);ax.scatter(a.median(),i,color=TEAL if f in ['Quantile plot','ECDF'] else BLUE,s=35,zorder=3)
ax.set_yticks(range(len(order)));ax.set_yticklabels(order);ax.set_xlabel('Median score; lines: 10th–90th percentiles');ax.set_xlim(0,101);label(ax,'a  All 127 comparisons')
ax=axs[0,1];q=F[F.family=='Quantile plot'].set_index('key');old=F[~F.family.isin(['Quantile plot','ECDF'])].sort_values('loss').groupby('key').head(1).set_index('key')
ax.scatter(old.score,q.loc[old.index,'score'],s=18,color=TEAL,alpha=.65);ax.plot([60,100],[60,100],ls='--',color=GREY);ax.set_xlim(60,100);ax.set_ylim(60,100);ax.set_xlabel('Best of original seven families');ax.set_ylabel('Fixed five-quantile plot');label(ax,'b  A task-matched baseline')
ax=axs[1,0];families=sorted(F.family.unique());xx=np.arange(len(families));ax.barh(xx-.18,[S['wins'].get(f,0) for f in families],height=.34,color=BLUE,label='All settings');ax.barh(xx+.18,[S['fixed_budget_wins'].get(f,0) for f in families],height=.34,color=TEAL,label='One setting / family');ax.set_yticks(xx);ax.set_yticklabels(families);ax.set_xlabel('Winning comparisons');ax.legend(frameon=False,fontsize=10,loc='lower right');label(ax,'c  Control the tuning budget')
ax=axs[1,1];ts=pd.read_csv(OUT/'task_summary.csv');ts=ts[ts.observer=='threshold'];cols=['median','five','dense19'];rows=sorted(F.family.unique());pivot=ts.pivot(index='family',columns='task',values='wins').reindex(index=rows,columns=cols).fillna(0);im=ax.imshow(pivot,cmap='YlGnBu',aspect='auto',vmin=0,vmax=127)
for i,r in enumerate(rows):
 for j,c in enumerate(cols):
    v=pivot.loc[r,c];ax.text(j,i,str(int(v)),ha='center',va='center',fontsize=10,color='white' if v>65 else NAVY)
ax.set_xticks(range(3));ax.set_xticklabels(['Median','Five quantiles','19 quantiles'],rotation=15,ha='right');ax.set_yticks(range(len(rows)));ax.set_yticklabels(rows,fontsize=10);label(ax,'d  Change the task, keep the charts');fig.colorbar(im,ax=ax,fraction=.045,pad=.03,label='Winning comparisons')
save(fig,'Figure_2_Baselines')
# Figure 3: robustness and numerical precision; an unseen display test is reported.
fig,axs=plt.subplots(2,2,figsize=(10.5,7.8),gridspec_kw={'hspace':.5,'wspace':.4});fig.suptitle('A numerical winner can be fragile',fontsize=17,weight='bold',y=1.01)
ax=axs[0,0];sens=pd.read_csv(OUT/'sensitivity.csv');labels=['128 px','512 px','Alternative decoder','Tight axes'];ax.barh(labels,sens.changed_families,color=[BLUE,BLUE,ORANGE,TEAL]);ax.set_xlim(0,127);ax.set_xlabel('Family changes from reference / 127');label(ax,'a  Change one condition')
ax=axs[0,1];ax.hist(M.gap_score,bins=20,color=BLUE,edgecolor='white');ax.axvline(.1,color=ORANGE,ls='--');ax.set_xlabel('Best minus second-best family score');ax.set_ylabel('Comparisons');label(ax,'b  Report the winning margin')
ax=axs[1,0];eps=[.001,.005,.01,.025];ax.plot(eps,[S['near_counts'][str(e)] for e in eps],'-o',color=TEAL);ax.set_xlabel('Allowed excess error (pooled SD)');ax.set_ylabel('Cases with multiple eligible families');ax.set_ylim(0,130);label(ax,'c  Error budgets produce choice sets')
ax=axs[1,1];dt=pd.read_csv(OUT/'display_transfer_summary.csv');labels2=['reference optimum','minimax optimum','fixed quantile'];xx=np.arange(3)
for j,obs in enumerate(['threshold','alpha']):
 vals=dt[dt.observer==obs].set_index('choice').loc[labels2,'loss'];ax.bar(xx+(j-.5)*.34,vals,width=.32,color=[BLUE,TEAL][j],label=obs)
ax.set_xticks(xx);ax.set_xticklabels(['Reference\noptimum','Minimax\noptimum','Fixed\nquantiles']);ax.set_ylabel('Resource-balanced mean loss');ax.set_ylim(0,.0085);ax.legend(frameon=False,fontsize=10);label(ax,'d  Transfer unchanged settings to 384 px')
fig.text(.06,-.015,'Error budgets and display perturbations are computational checks, not confidence intervals or human-equivalence thresholds.',fontsize=10,color=GREY)
save(fig,'Figure_3_Robustness')
# Figure 4: preserve original large/low gain story, update every candidate and score.
fig=plt.figure(figsize=(11,12.5));fig.text(.04,.98,'What the selected chart recovers—and what it adds',fontsize=17,weight='bold')
for i,(key,title) in enumerate([('WDBC__29','Breast tumour: worst fractal dimension'),('HAR__29','Activity: gyroscope-jerk variability'),('Wrist__00','Wrist exercise: mean heart rate')]):
 top=.90-i*.29;c=CASES[key];w=W[W.key==key].iloc[0];bar=F[(F.key==key)&(F.family=='Bar chart')].iloc[0]
 fig.text(.045,top,f'{chr(97+i)}  {title}',weight='bold',fontsize=12);fig.text(.045,top-.027,f'Mean bars {bar.score:.2f}  →  {w.family} {w.score:.2f}     Gain {w.score-bar.score:.2f} points',fontsize=10,color=TEAL)
 ax=fig.add_axes([.06,top-.145,.245,.09]);raster(ax,key,'Bar chart','means');ax.tick_params(labelsize=9);ax.set_ylabel('Value',fontsize=10)
 ax=fig.add_axes([.37,top-.145,.245,.09]);ctx=raster(ax,key,w.family,w.setting);ax.tick_params(labelsize=9);ax.set_ylabel('Value',fontsize=10)
 ax=fig.add_axes([.06,top-.25,.56,.055]);true=(np.quantile(c['y'],P)-np.quantile(c['x'],P))/ctx['scale'];ax.plot(P*100,true,'o-',color=NAVY,label='True difference',ms=3)
 for f,s,co,ls,lbl in [('Bar chart','means',GREY,'--','Mean-bar recovery'),(w.family,w.setting,TEAL,'-','Selected recovery')]:
    qq=[]
    for j,phase in enumerate([0,.25,.5,.75]):
        im,sp=render(ctx,f,s,256,phase,20260920+j);q=decode(im,sp);qq.append((q[1]-q[0])/ctx['scale'])
    ax.plot(P*100,np.mean(qq,axis=0),ls,color=co,label=lbl,lw=1.5)
 ax.set_ylabel('B − A / SD',fontsize=10);ax.set_xticks(P*100);ax.tick_params(labelsize=9);ax.set_xlabel('Percentile' if i==2 else '',fontsize=10);ax.grid(axis='y',alpha=.2)
 if i==0:fig.legend(*ax.get_legend_handles_labels(),loc='upper left',bbox_to_anchor=(.045,.96),ncol=3,fontsize=10,frameon=False)
 ax=fig.add_axes([.72,top-.25,.24,.22]);rank(ax,key)
fig.text(.04,.008,'Examples are retained from the earlier revision, not selected afresh for the largest gains. No reader benefit is inferred.',fontsize=10,color=GREY)
save(fig,'Figure_4_Examples')
print('Four revised figures saved.')
