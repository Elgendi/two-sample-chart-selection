"""Figures with eight independently computed winning families and explicit task labels."""
from pathlib import Path
import sys,json,io,importlib.util
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import MaxNLocator
from matplotlib.transforms import Bbox
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'task_first'))
ns=importlib.util.spec_from_file_location('task_first_renderer',ROOT/'task_first/benchmark.py');nb=importlib.util.module_from_spec(ns);ns.loader.exec_module(nb);new_render=nb.render
spec=importlib.util.spec_from_file_location('legacy_task_benchmark',ROOT/'validation_v3/benchmark.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
OUT=ROOT/'reader_figures';FIG=OUT/'figures';PAN=FIG/'panels';PAN.mkdir(exist_ok=True)
# Remove superseded cards; these are generated files, preserved in the prior package.
for p in PAN.glob('*.pdf'):p.unlink()
C=pd.read_csv(ROOT/'task_first/results/all_task_scores.csv');C=C[C.observer=='hard'];TRANS=pd.read_csv(ROOT/'task_first/results/all_transfer.csv')
BASE={c['key']:c for c in json.loads((ROOT/'data/derived/comparisons.json').read_text())};NEW={c['key']:c for c in json.loads((ROOT/'task_first/results/inputs.json').read_text())}
NAVY='#183445';TEAL='#00877d';BLUE='#267ea5';ORANGE='#df7836';GREY='#647683';LIGHT='#f3f7f9';LINE='#d4dfe3';RED='#ad542f'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':NAVY,'axes.labelcolor':NAVY,'axes.edgecolor':LINE,'xtick.color':GREY,'ytick.color':GREY,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none'})
SHORT={'Bar chart':'Bars','Box plot':'Box plot','Interval plot':'Interval','Dot plot':'Dots','Histogram':'Histogram','Heatmap':'Heatmap','Violin plot':'Violin','Pie chart':'Pie','Donut chart':'Donut','Stacked bar':'Stacked bar','Line chart':'Line','Area chart':'Area','Scatter plot':'Scatter'}
TASK={'five':'How do five group gaps differ?','median':'How do the medians differ?','spread':'How do the spreads differ?','composition':'What share is in each category?','profile':'How does heart rate change over time?','association':'How are ECG and pulse rates related?'}
SUCCESS=[
 dict(key='WDBC__03',task='five',family='Dot plot',baseline='Bar chart',title='Cell-nucleus area',units='Area (source units)'),
 dict(key='Cleveland__00',task='five',family='Histogram',baseline='Bar chart',title='Age in the Cleveland cohort',units='Age (years)'),
 dict(key='Cleveland__04',task='five',family='Violin plot',baseline='Bar chart',title='Exercise-related ECG change',units='ST depression (source units)'),
 dict(key='HeartFailure__00',task='five',family='Heatmap',baseline='Bar chart',title='Age in the heart-failure cohort',units='Age (years)'),
 dict(key='WDBC__07',task='spread',family='Box plot',baseline='Bar chart',title='Cell-nucleus boundary shape',units='Concave points (source units)'),
 dict(key='cohort_HeartFailure',task='composition',family='Pie chart',baseline='Bar chart',title='Heart-failure cohort composition',units='Observed record shares; not population risk'),
 dict(key='profile_bidmc_04',task='profile',family='Line chart',baseline='Bar chart',title='Heart rate over one recording',units='12 successive time bins; beats/min'),
 dict(key='assoc_bidmc_22',task='association',family='Scatter plot',baseline='Heatmap',title='ECG-pulse association',units='Horizontal: ECG; vertical: pulse (beats/min)'),
]
TITLES={'WDBC__25':'Cell-nucleus compactness','HAR__17':'Acceleration-change variability','ILPD__04':'Liver enzyme ALT','HAR__09':'Gravity-signal variability','ILPD__05':'Liver enzyme AST','ILPD__01':'Total bilirubin','cohort_CKD':'Kidney-cohort composition','profile_bidmc_07':'Heart rate over one recording','assoc_bidmc_41':'ECG-pulse association'}
UNITS={'WDBC__25':'Compactness (source units)','HAR__17':'Normalized source units','ILPD__04':'Source units','HAR__09':'Normalized source units','ILPD__05':'Source units','ILPD__01':'Source units','cohort_CKD':'Observed record shares','profile_bidmc_07':'12 time bins; beats/min','assoc_bidmc_41':'Horizontal: ECG; vertical: pulse (beats/min)'}

def row(key,task,family,H=256):return C[(C.key==key)&(C.task==task)&(C.family==family)&(C.H==H)].iloc[0]
def txt(fig,x,y,s,**kw):fig.text(x,y,s,**kw)
def bg(fig,x,y,w,h):fig.add_artist(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.006,rounding_size=.008',transform=fig.transFigure,facecolor=LIGHT,edgecolor='none',zorder=-1))
def save(fig,name):
 for ext in ['pdf','svg','png']:
  buf=io.BytesIO();fig.savefig(buf,format=ext,dpi=240,bbox_inches='tight',facecolor='white');b=buf.getvalue()
  if ext=='pdf':assert b.rstrip().endswith(b'%%EOF')
  (FIG/(name+'.'+ext)).write_bytes(b)
 plt.close(fig)
def raster(key,task,family,H):
 phase=0 if H==256 else .125
 if key in NEW:return new_render(NEW[key],family,H,phase)
 b=BASE[key];ctx=old.prepare(b['x'],b['y']);s=str(row(key,task,family,H).setting);return old.render(ctx,family,s,H,phase,20260920)
def ticks(lo,hi):
 v=MaxNLocator(nbins=2,steps=[1,2,2.5,5,10]).tick_values(lo,hi);return v[(v>=lo)&(v<=hi)]
def fmt(x):return f'{x:g}'
def chart(fig,rect,key,task,family,H=256,fs=9):
 im,sp=raster(key,task,family,H);a=np.asarray(im);x,y,w,h=rect
 if key in NEW:
  ax=fig.add_axes(rect);ax.imshow(a,interpolation='none',aspect='auto');L,R,T,B=[sp[k] for k in ['L','R','T','B']]
  ax.set_xlim(0,H);ax.set_ylim(H,0);ax.tick_params(length=2,pad=2,labelsize=fs)
  if task=='composition':
   if family in ['Pie chart','Donut chart','Stacked bar']:
    ax.axis('off')
    if family in ['Pie chart','Donut chart']:ax.set_aspect('equal',adjustable='box')
   else:ax.set_xticks([]);ax.set_yticks([B,(B+T)/2,T]);ax.set_yticklabels(['0','50%','100%'])
  elif task=='profile':
   v=ticks(0,sp['hi']);ax.set_yticks(B-v/sp['hi']*(B-T));ax.set_yticklabels([fmt(z) for z in v]);ax.set_xticks([L+4,R-4]);ax.set_xticklabels(['Start','End'])
  else:
   vx=ticks(sp['xlo'],sp['xhi']);vy=ticks(sp['ylo'],sp['yhi']);ax.set_xticks(L+(vx-sp['xlo'])/(sp['xhi']-sp['xlo'])*(R-L));ax.set_xticklabels([fmt(z) for z in vx]);ax.set_yticks(B-(vy-sp['ylo'])/(sp['yhi']-sp['ylo'])*(B-T));ax.set_yticklabels([fmt(z) for z in vy])
  return
 lo,hi=sp['lo'],sp['hi'];vals=ticks(lo,hi);L=8;R=H-9;T=8;B=H-9
 if family=='Heatmap':
  for g in [0,1]:
   ax=fig.add_axes([x,y+(1-g)*h*.49,w,h*.31]);left=g*(H+16);patch=a[int(T+.35*(B-T)):int(T+.65*(B-T))+1,left+L:left+R+1];d=(hi-lo)/(R-L)
   ax.imshow(patch,interpolation='none',aspect='auto',extent=[lo-d/2,hi+d/2,0,1]);ax.set_xlim(lo,hi);ax.set_yticks([]);ax.set_xticks(vals if g==1 else []);ax.set_xticklabels([fmt(v) for v in vals] if g==1 else [],fontsize=fs);ax.tick_params(length=2,pad=2)
   for side in ax.spines:ax.spines[side].set_visible(False)
   ax.text(-.025,.5,str(g+1),transform=ax.transAxes,va='center',ha='right',fontsize=fs,color=[BLUE,ORANGE][g],weight='bold')
  return
 for g in [0,1]:
  ax=fig.add_axes([x+g*w*.55,y,w*.44,h]);ax.imshow(a[:,g*(H+16):g*(H+16)+H],interpolation='none',aspect='auto');ax.set_xlim(5,H-5);ax.set_ylim(H-5,5);ax.tick_params(length=2,pad=2,labelsize=fs)
  if family=='Histogram':
   ax.set_xticks(L+(vals-lo)/(hi-lo)*(R-L));ax.set_xticklabels([fmt(v) for v in vals],rotation=25);ax.set_yticks([B,T]);ax.set_yticklabels(['0','100%'] if g==0 else [])
  else:
   ax.set_yticks(B-(vals-lo)/(hi-lo)*(B-T));ax.set_yticklabels([fmt(v) for v in vals] if g==0 else []);ax.set_xticks([])
  ax.spines['left'].set_visible(g==0);ax.spines['bottom'].set_visible(family=='Histogram');ax.text(.5,1.035,str(g+1),transform=ax.transAxes,ha='center',fontsize=fs,color=[BLUE,ORANGE][g],weight='bold')
def labels(fig,x,y,key,task):
 if key in BASE:
  a,b=BASE[key]['labels'];a=a.replace('Non-CKD','No CKD');txt(fig,x,y,'1 '+a,fontsize=9,color=BLUE,weight='bold');txt(fig,x+.212,y,'2 '+b,fontsize=9,color=ORANGE,weight='bold')
 elif task=='composition':
  labs=NEW[key]['labels'];txt(fig,x,y,'1 '+labs[0],fontsize=9,color=BLUE,weight='bold');txt(fig,x+.212,y,'2 '+labs[1],fontsize=9,color=ORANGE,weight='bold')
 elif task=='profile':txt(fig,x,y,'BIDMC recording '+key.rsplit('_',1)[1],fontsize=9,color=GREY)
 else:txt(fig,x,y,'Paired observations from BIDMC '+key.rsplit('_',1)[1],fontsize=9,color=GREY)

records=[]
def make_grid(examples,number,transfer=False):
 fig=plt.figure(figsize=(11.4,13.9));txt(fig,.035,.974,('02 / EIGHT FAMILIAR-CHART EXAMPLES' if not transfer else 'S1 / FROZEN CHOICES AT A NEW DISPLAY'),fontsize=12,weight='bold',color=TEAL)
 txt(fig,.035,.939,'Different questions need different information.' if not transfer else 'Does the choice survive a new display size?',fontsize=24,weight='bold')
 txt(fig,.035,.910,'Illustrative familiar-chart comparisons. Strong defaults are tested separately in Figure 3.' if not transfer else 'Choices are frozen at 256 pixels. Both charts below are evaluated at 384 pixels.',fontsize=11.5,color=GREY)
 from matplotlib.colorbar import ColorbarBase
 from matplotlib.colors import LinearSegmentedColormap
 cb=fig.add_axes([.80,.881,.16,.008]);ColorbarBase(cb,cmap=LinearSegmentedColormap.from_list('probability',['white','blue']),orientation='horizontal',ticks=[0,.5,1]);cb.set_xticklabels(['0%','50%','100%'],fontsize=8.5);cb.tick_params(length=1,pad=1)
 txt(fig,.52,.881,'Heatmap: proportion per bin',fontsize=9.5,color=GREY)
 for i,e in enumerate(examples):
  x=.038+(i%2)*.495;y=.676-(i//2)*.207;key=e['key'];task=e['task'];fam=e['family'];H=384 if transfer else 256
  best=row(key,task,fam);assert best.winner;nc=len(C[(C.key==key)&(C.task==task)&(C.H==256)])
  second=e['test_best'] if transfer else fam;first=fam if transfer else e['baseline'];left=row(key,task,first,H);right=row(key,task,second,H);bg(fig,x-.006,y-.003,.451,.188)
  txt(fig,x,y+.167,f'{chr(97+i)}  {e["title"]}',fontsize=12.2,weight='bold')
  txt(fig,x,y+.148,TASK[task],fontsize=10.7,color=TEAL,weight='bold');labels(fig,x,y+.132,key,task)
  prec=3 if task in ['composition','association'] else 2
  txt(fig,x,y+.109,f'{SHORT[first]}  {left.score:.{prec}f}',fontsize=12,weight='bold',color=GREY if not transfer else TEAL)
  txt(fig,x+.238,y+.109,f'{SHORT[second]}  {right.score:.{prec}f}',fontsize=12,weight='bold',color=TEAL)
  chart(fig,[x+.032,y+.039,.145,.058],key,task,first,H);chart(fig,[x+.274,y+.039,.145,.058],key,task,second,H)
  txt(fig,x+.209,y+.063,'→',fontsize=19,ha='center',color=GREY);txt(fig,x,y+.017,e['units'],fontsize=9,color=GREY)
  if transfer:
   gap=right.score-left.score;message='Choice retained' if gap<1e-10 else f'Choice changes | gap {gap:.{prec}f} points'
   txt(fig,x,y-.001,message,fontsize=11.1,weight='bold',color=TEAL if gap<1e-10 else RED)
  else:
   gain=right.score-left.score;nt=int(C[(C.key==key)&(C.task==task)&(C.H==256)].winner.sum());assert nt==1, (key,task,'illustrated unique winner was tied')
   tag='best'
   txt(fig,x,y-.001,f'+{gain:.{prec}f} points | best of {nc} familiar charts',fontsize=11.1,weight='bold',color=TEAL)
  records.append(dict(figure=number,panel=chr(97+i),key=key,task=task,selected=fam,reference_score=float(best.score),left_family=first,right_family=second,left_score=float(left.score),right_score=float(right.score),H=H,eligible_count=nc,title=e['title'],displayed_gap=float(right.score-left.score)))
 txt(fig,.035,.035,'Scores compare charts within a question. Different questions use different losses; do not pool scores.',fontsize=10.5,color=GREY)
 txt(fig,.035,.017,'Computed examples, not human-reading results. A later-size optimum is a hindsight comparator.' if transfer else 'Starting charts are illustrative, often lossy baselines. These panels do not establish general benefit.',fontsize=10.5,color=GREY)
 for i,e in enumerate(examples):
  x=.038+(i%2)*.495;y=.676-(i//2)*.207;crop=Bbox.from_bounds(x-.019,y-.014,.477,.211).transformed(fig.transFigure).transformed(fig.dpi_scale_trans.inverted());buf=io.BytesIO();fig.savefig(buf,format='pdf',bbox_inches=crop,facecolor='white');(PAN/f'Figure_{number}{chr(97+i)}_{e["key"]}.pdf').write_bytes(buf.getvalue())
 save(fig,'Figure_2_When_optimization_helps' if number==2 else 'Figure_3_When_optimization_does_not_help')
make_grid(SUCCESS,2)
limits=[]
for e in SUCCESS:
 q=TRANS[(TRANS.task==e['task'])&(TRANS.selected==e['family'])&(TRANS.observer=='hard')&(TRANS.kind=='empirical')].sort_values(['score_gap','key'],ascending=[False,True]).iloc[0]
 limits.append(dict(key=q.key,task=q.task,family=q.selected,test_best=q.test_best,title=TITLES[q.key],units=UNITS[q.key]))
make_grid(limits,3,True)
assert len({e['family'] for e in SUCCESS})==8 and len({e['family'] for e in limits})==8
pd.DataFrame(records).to_csv(OUT/'task_example_values.csv',index=False);(OUT/'task_figure_checks.json').write_text(json.dumps(dict(examples=records,unique_reference_winning_families_per_figure=8,success_selection='Retrospective illustrative choice, one per eight genuinely winning families. Scores compared only within task.',transfer_selection='Largest 384-pixel score regret per selected family and task, empirical cases, hard observer; exact regret ties resolved by key. Not representative transfer frequency.',all_winner_assertions_passed=True),indent=2))
# Eligibility/result matrix: a dash means no implemented contract, not a score of zero.
mat=pd.read_csv(ROOT/'task_first/results/task_win_matrix.csv',index_col=0);tasks=['median','spread','five','composition','profile','association'];names=['Median\ngap','Spread\ngap','Five\ngaps','Category\nshares','Time\nprofile','Paired\nassociation'];ns=[127,127,127,24,72,53]
fig=plt.figure(figsize=(10.6,10.1));txt(fig,.04,.967,'04 / QUESTION FIRST, CHART SECOND',fontsize=11,color=TEAL,weight='bold');txt(fig,.04,.920,'No single chart answers every question.',fontsize=23,weight='bold')
txt(fig,.04,.880,'Winning-set memberships for each implemented task: all 13 familiar families are visible.',fontsize=11,color=GREY)
ax=fig.add_axes([.25,.20,.71,.61]);eligible=mat.notna().to_numpy();ax.imshow(np.where(eligible,1,0),cmap=matplotlib.colors.ListedColormap(['#f1f3f5','#e2f1ee']),vmin=0,vmax=1,aspect='auto');ax.set_xticks(range(6));ax.set_xticklabels([n+f'\n(n={k})' for n,k in zip(names,ns)],fontsize=10);ax.xaxis.tick_top();ax.tick_params(length=0,pad=8);ax.set_yticks(range(len(mat)));ax.set_yticklabels(mat.index,fontsize=12)
for i in range(len(mat)):
 for j in range(6):
  v=mat.iloc[i,j];ax.text(j,i,'—' if pd.isna(v) else str(int(v)),ha='center',va='center',fontsize=13,color=GREY if pd.isna(v) else TEAL,weight='normal' if pd.isna(v) or v==0 else 'bold')
for z in np.arange(-.5,len(mat),1):ax.axhline(z,color='white',lw=2)
for z in np.arange(-.5,6,1):ax.axvline(z,color='white',lw=2)
for sp in ax.spines.values():sp.set_visible(False)
txt(fig,.04,.129,'Number = cases in the winning set.  0 = tested, but no wins.  — = no implemented task contract.',fontsize=10.6,weight='bold')
txt(fig,.04,.083,'Ties are retained, so a column can sum above n. Counts depend on the decoder and setting.\nStrong specialized controls are included in Figure 3. Mean bars are lossy distributional controls.\nWinning under a decoder does not establish human preference.',fontsize=10.5,color=GREY,linespacing=1.65)
save(fig,'Figure_4_Question_first_chart_second')
print(pd.DataFrame(records)[['figure','key','task','selected','left_score','right_score']].to_string(index=False))
