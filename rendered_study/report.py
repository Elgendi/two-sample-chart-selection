from pathlib import Path
import sys,json
from io import BytesIO
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.backends.backend_pdf import PdfPages
from observer import prepare,render,decode,P
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'rendered_study/results';FIG=ROOT/'rendered_study/figures';FIG.mkdir(exist_ok=True)
CASES={c['key']:c for c in json.loads((ROOT/'data/derived/comparisons.json').read_text())}
fam=pd.read_csv(OUT/'family_scores.csv',dtype={'setting':str});win=pd.read_csv(OUT/'winners.csv');tr=pd.read_csv(OUT/'render_trials.csv')
pri=fam[fam.primary];w=win[(win.primary)&(win.H==256)];ref=pri[pri.H==256]
wsmall=win[win.primary & (win.H==128)].set_index('key');wlarge=win[win.primary & (win.H==512)].set_index('key')
changes=sum(set(wsmall.loc[k,'families'].split(';'))!=set(wlarge.loc[k,'families'].split(';')) for k in wsmall.index)
summary=dict(primary_comparisons=127,exploratory_comparisons=22,trials=len(tr),primary_trials=int(tr.primary.sum()),unique_winners=int((w.n_tied==1).sum()),tied_winners=int((w.n_tied>1).sum()),median_best=float(w.best_score.median()),min_best=float(w.best_score.min()),max_best=float(w.best_score.max()),resolution_changes=changes,failed_primary_trials=int(tr[tr.primary].loss.isna().sum()),failed_exploratory_trials=int(tr[~tr.primary].loss.isna().sum()),constant_scale_cases=int(tr[tr.constant_scale_fallback]['key'].nunique()))
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
macros={'UniqueWinners':summary['unique_winners'],'TiedWinners':summary['tied_winners'],'MedianBest':f"{summary['median_best']:.3f}",'MinBest':f"{summary['min_best']:.3f}",'MaxBest':f"{summary['max_best']:.3f}",'ResolutionChanges':changes,'FailedTrials':summary['failed_primary_trials']}
(OUT/'numbers.tex').write_text(''.join('\\newcommand{\\'+k+'}{'+str(v)+'}\n' for k,v in macros.items()))
rows=[]
for f,d in ref.groupby('family'):
 count=sum(f in a.split(';') for a in w.families);rows.append((f,count,d.score.median(),int(d.score.notna().sum())))
rows.sort(key=lambda x:(-x[1],x[0]))
(OUT/'winner_table.tex').write_text('\\begin{tabular}{lrrr}\\toprule\nFamily & Winning memberships & Median score & Valid cases\\\\\\midrule\n'+''.join(f'{f} & {n} & {s:.3f} & {v}\\\\\n' for f,n,s,v in rows)+'\\bottomrule\\end{tabular}\n')
failure=tr[tr.primary].assign(failed=lambda d:d.loss.isna()).groupby(['family','H']).failed.sum().unstack().fillna(0).astype(int)
(OUT/'failure_table.tex').write_text('\\begin{tabular}{lrrr}\\toprule\nFamily & 128 pixels & 256 pixels & 512 pixels\\\\\\midrule\n'+''.join(f'{f} & {r[128]} & {r[256]} & {r[512]}'+r'\\'+'\n' for f,r in failure.iterrows())+'\\bottomrule\\end{tabular}\n')
NAVY='#173649';TEAL='#07867d';BLUE='#267ea5';ORANGE='#df7836';GREY='#6b7d89'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':NAVY,'text.color':NAVY,'axes.edgecolor':GREY,'xtick.color':GREY,'ytick.color':GREY,'pdf.fonttype':42,'svg.fonttype':'none'})
def escape(s):return str(s).replace('_',r'\_').replace('&',r'\&').replace('%',r'\%')
def name(c):
 return {'WDBC__29':'Breast tumour / Fractal dimension (worst)','Cleveland__04':'Heart disease / ST depression (oldpeak)','Wrist__00':'Wrist exercise / Mean heart rate','BIDMC__00':'Bedside monitoring / Mean heart rate','WDBC__10':'Breast tumour / Radius standard error','WDBC__22':'Breast tumour / Worst perimeter','HAR__29':'Smartphone activity / Gyroscope-jerk variability','HAR__09':'Activity / Gravity variability, x axis','CKD__06':'Kidney disease / Potassium'}.get(c['key'],c['dataset']+' / '+c['feature'])
def ranked(key,H=256):return fam[(fam.key==key)&(fam.H==H)].sort_values(['score','family'],ascending=[False,True],kind='stable')
def setting_label(row):
 s=row.setting
 if row.family in ['Histogram','Heatmap']:return s+' bins'
 if row.family=='Violin plot':return s+' grid points'
 return {'five':'five-number','means':'means','raw':'raw observations'}[s]
def plot_raster(ax,c,row,title):
 ctx=prepare(c['x'],c['y']);im,spec=render(ctx,row.family,row.setting,256,0,20260920)
 ax.imshow(im,interpolation='none');ax.set_title(title,fontsize=9,loc='left',pad=24,fontweight='bold');ax.set_xlim(0,528);ax.set_ylim(256,0)
 ax.set_xticks([128,400]);ax.set_xticklabels(['A','B']);ax.tick_params(length=0,labelsize=8)
 if row.family not in ['Histogram','Heatmap']:
  vals=np.linspace(ctx['lo'],ctx['hi'],3);ys=247-(vals-ctx['lo'])/(ctx['hi']-ctx['lo'])*239
  ax.set_yticks(ys);ax.set_yticklabels([f'{v:.3g}' for v in vals],fontsize=7);ax.set_ylabel('Measurement',fontsize=8)
 elif row.family=='Histogram':
  ax.set_yticks([247,127.5,8]);ax.set_yticklabels(['0','0.5','1'],fontsize=7);ax.set_ylabel('Probability per bin',fontsize=8)
  ax.text(.5,-.20,'Measurement value',transform=ax.transAxes,ha='center',fontsize=7)
 else:
  ax.set_yticks([]);ax.text(.5,-.20,'Value • White → blue: bin probability 0 → 1',transform=ax.transAxes,ha='center',fontsize=6.5)
 if row.family in ['Histogram','Heatmap']:
  ticks=[8,127.5,247,280,399.5,519];vals=[ctx['lo'],(ctx['lo']+ctx['hi'])/2,ctx['hi']]*2
  ax.set_xticks(ticks);ax.set_xticklabels([f'{v:.2g}' for v in vals],fontsize=6)
  for j,label in enumerate(ax.get_xticklabels()):label.set_ha('left' if j in [0,3] else ('right' if j in [2,5] else 'center'))
  ax.text(.24,1.02,'A',transform=ax.transAxes,ha='center',fontsize=8,color=BLUE)
  ax.text(.76,1.02,'B',transform=ax.transAxes,ha='center',fontsize=8,color=ORANGE)
 for spine in ax.spines.values():spine.set_visible(False)
 return ctx

def rank_table(ax,key,H=256):
 d=ranked(key,H);best=d.loss.min();ax.set_xlim(0,1);ax.set_ylim(-.65,7.5);ax.axis('off')
 ax.text(0,7.2,'RANK / CHART AND SETTING',fontsize=8,color=GREY,fontweight='bold');ax.text(1,7.2,'SCORE / 100',ha='right',fontsize=8,color=GREY,fontweight='bold')
 for i,(_,r) in enumerate(d.iterrows()):
  y=6.5-i;optimal=np.isclose(r.loss,best,atol=1e-12,rtol=0);color=TEAL if optimal else NAVY
  if optimal:ax.axhspan(y-.43,y+.43,color='#e4f1ed',zorder=-1)
  ax.text(.01,y,str(i+1) if np.isfinite(r.score) else '–',va='center',color=color,fontsize=9)
  ax.text(.085,y+.20,r.family,va='center',color=color,fontsize=9,fontweight='bold' if optimal else 'normal')
  ax.text(.085,y-.30,setting_label(r),va='center',color=GREY,fontsize=6.8)
  if np.isfinite(r.score):
   ax.plot([.60,.60+.19*r.score/100],[y,y],lw=4,color=TEAL if optimal else BLUE,solid_capstyle='round')
   ax.text(.99,y,f'{r.score:.3f}',ha='right',va='center',color=color,fontsize=9)
  else:ax.text(.99,y,'Decode failed',ha='right',va='center',fontsize=7)
 ax.text(0,-.4,'Higher is better • Green: computational optimum',fontsize=7,color=GREY)

def save(fig,n):
 for ext in ['pdf','png','svg']:
  buffer=BytesIO();fig.savefig(buffer,format=ext,bbox_inches='tight',dpi=240)
  target=FIG/(n+'.'+ext);temporary=target.with_suffix('.'+ext+'.tmp');temporary.write_bytes(buffer.getvalue());temporary.replace(target)
 plt.close(fig)
# Figure 1: real values, concise workflow, actual ranking.
c=CASES['WDBC__10'];d=ranked(c['key']);best=d.iloc[0]
fig=plt.figure(figsize=(10,6.4));fig.text(.03,.955,'From two columns to a testable chart choice',fontsize=18,fontweight='bold');fig.text(.03,.913,'Same task. Actual pixels. One score that determines the ranking.',fontsize=10,color=GREY)
ax=fig.add_axes([.035,.55,.20,.30]);ax.axis('off');ax.text(0,1,'1  RAW OBSERVATIONS',weight='bold',fontsize=10)
ax.text(0,.86,'A: benign',color=BLUE);ax.text(.53,.86,'B: malignant',color=ORANGE)
for i in range(5):ax.text(.05,.69-i*.12,f"{c['x'][i]:.4f}",fontsize=10);ax.text(.58,.69-i*.12,f"{c['y'][i]:.4f}",fontsize=10)
ax.text(0,-.02,f"All {len(c['x'])} + {len(c['y'])} records analysed",fontsize=8,color=GREY)
ax=fig.add_axes([.30,.55,.38,.30]);ax.axis('off');ax.add_patch(FancyBboxPatch((0,.03),1,.94,boxstyle='round,pad=.02',facecolor='#eaf2f5',edgecolor='#b3cad5'))
ax.text(.05,.81,'2  RENDER AND RECOVER',weight='bold',fontsize=11)
ax.text(.05,.59,'21 settings • 7 eligible chart families',fontsize=10)
ax.text(.05,.40,'Pixels + calibrated axes → five differences',fontsize=9)
ax.text(.05,.20,r'$S=100/(1+\mathrm{normalized\ recovery\ loss})$',fontsize=10)
fig.text(.25,.70,'→',fontsize=25);fig.text(.705,.70,'→',fontsize=25)
ax=fig.add_axes([.77,.57,.20,.27]);ax.axis('off');ax.text(0,1,'3  SELECT',weight='bold',fontsize=11);ax.text(0,.67,best.family,fontsize=14,weight='bold',color=TEAL);ax.text(0,.40,f'{best.score:.3f} / 100',fontsize=17,color=TEAL,weight='bold');ax.text(0,.13,'Best under this protocol',fontsize=8)
ax=fig.add_axes([.04,.12,.39,.27]);plot_raster(ax,c,best,'Actual selected raster • reference resolution')
ax=fig.add_axes([.53,.10,.44,.34]);rank_table(ax,c['key'])
fig.text(.03,.015,'15-family catalogue screened; seven implemented for this task. Scores are computational, not human accuracy.',fontsize=8,color=GREY)
save(fig,'Figure_1_Workflow')
from story_figures import make_story,GOOD_KEYS,LIMIT_KEYS,TITLES
keys=GOOD_KEYS
figure_audit=make_story(CASES,fam,FIG,GOOD_KEYS)
figure_audit+=make_story(CASES,fam,FIG,LIMIT_KEYS,limited=True)
pd.DataFrame(figure_audit).to_csv(OUT/'illustrative_gain_cases.csv',index=False)
# Actual worst case; never manufacture a low score.
worst=w.sort_values('best_score').iloc[0];key=worst.key;c=CASES[key];summary['lowest_case']=key
fig=plt.figure(figsize=(10,7.5));fig.text(.03,.96,'A best score has limits',fontsize=18,fontweight='bold');fig.text(.03,.92,'Resolution sensitivity and the lowest-scoring primary optimum',fontsize=10,color=GREY)
ax=fig.add_axes([.08,.55,.32,.29]);ax.scatter(wsmall.best_score,wlarge.loc[wsmall.index].best_score,s=16,alpha=.7,color=BLUE)
lim=[min(wsmall.best_score.min(),wlarge.best_score.min())-2,100];ax.plot(lim,lim,color=GREY,lw=.8,ls='--');ax.set_xlim(lim);ax.set_ylim(lim);ax.set_xlabel('Best score at 128 pixels');ax.set_ylabel('Best score at 512 pixels');ax.set_title('a  Changing display resolution',loc='left',weight='bold',pad=15);ax.text(.04,.92,f'{changes}/127 winner sets change',transform=ax.transAxes,fontsize=8)
ax=fig.add_axes([.54,.53,.43,.31]);rank_table(ax,key);ax.set_title('b  Lowest reference optimum',loc='left',fontweight='bold',pad=10)
fig.text(.54,.485,name(c),fontsize=9,weight='bold');fig.text(.54,.454,f'Best score: {worst.best_score:.3f} / 100',fontsize=11,color=TEAL,weight='bold')
ax=fig.add_axes([.08,.12,.37,.28]);dd=pri[pri.key==key]
for f,g in dd.groupby('family'):ax.plot(g.H,g.score,'o-',lw=1,ms=3,label=f)
ax.set_xticks([128,256,512]);ax.set_xlabel('Panel resolution (pixels)');ax.set_ylabel('Best family score');ax.set_title('c  Settings reselected at each resolution',loc='left',weight='bold',fontsize=10,pad=12);ax.legend(fontsize=6.5,ncol=2,loc='lower right')
best=ranked(key).iloc[0];plot_raster(fig.add_axes([.56,.17,.39,.19]),c,best,'Actual best raster at 256 pixels')
fig.text(.56,.10,f"A: {c['labels'][0]} (n={len(c['x'])})   B: {c['labels'][1]} (n={len(c['y'])})",fontsize=8,color=GREY)
fig.text(.03,.024,'A lower score can reflect summary loss, rendering or decoder limitations. It does not diagnose poor source data.',fontsize=8,color=GREY)
save(fig,'Figure_S1_Resolution')
# Inspectable target-to-pixel arithmetic for the three illustrated optima.
recovery=[];latex=[]
for key in keys+LIMIT_KEYS:
 c=CASES[key];ctx=prepare(c['x'],c['y']);r=ranked(key).iloc[0]
 target=np.quantile(c['y'],P)-np.quantile(c['x'],P);estimates=[]
 for pi,phase in enumerate([0,.25,.5,.75]):
  im,spec=render(ctx,r.family,r.setting,256,phase,20260920+pi)
  q=decode(im,spec);delta=q[1]-q[0];estimates.append(delta)
  for k,p in enumerate(P):recovery.append(dict(key=key,family=r.family,setting=r.setting,phase=phase,p=p,target=target[k],recovered=delta[k],normalized_absolute_error=abs(delta[k]-target[k])/ctx['scale']))
 estimates=np.array(estimates);err=np.mean(abs(estimates-target),axis=0)/ctx['scale']
 assert np.isclose(100/(1+err.mean()),r.score,atol=1e-10)
 latex.append('\\begin{minipage}{\\linewidth}\\textbf{'+escape(name(c))+'}: '+escape(r.family)+'; score '+f'{r.score:.3f}'+'.\n\\begin{center}\\begin{tabular}{rrrr}\\toprule\nQuantile & Target difference & Mean recovered & Mean normalized error\\\\\\midrule\n')
 for k,p in enumerate(P):latex.append(f'{p:.2f} & {target[k]:.5g} & {estimates[:,k].mean():.5g} & {err[k]:.5f}'+r'\\'+'\n')
 latex.append('\\bottomrule\\end{tabular}\\end{center}\\end{minipage}\\par\\medskip\n')
pd.DataFrame(recovery).to_csv(OUT/'example_quantile_recovery.csv',index=False)
(OUT/'example_recovery.tex').write_text(''.join(latex))

# Full audit tables in supplement and CSV, plus all settings machine readable.
lines=['\\begin{longtable}{p{2.7cm}p{5.5cm}p{3.4cm}r}\\toprule\nKey & Feature & Winning family set & Score\\\\\\midrule\\endhead\n']
for _,r in w.sort_values('key').iterrows():lines.append(f"{escape(r.key)} & {escape(CASES[r.key]['feature'])} & {escape(r.families.replace(';',', '))} & {r.best_score:.3f}\\\\\n")
lines.append('\\bottomrule\\end{longtable}\n');(OUT/'audit_table.tex').write_text(''.join(lines))
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
from pypdf import PdfWriter
pdf=PdfWriter()
for n in ['Figure_1_Workflow','Figure_2_Examples','Figure_3_Limits']:pdf.append(FIG/(n+'.pdf'))
with (FIG/'Three_Figure_Story.pdf').open('wb') as f:pdf.write(f)
print(json.dumps(summary,indent=2))
