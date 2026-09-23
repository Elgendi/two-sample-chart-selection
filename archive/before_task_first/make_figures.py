"""Reader-facing examples from frozen familiar-candidate reference results. No outcomes altered."""
from pathlib import Path
import sys,json,hashlib,io
from functools import lru_cache
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import MaxNLocator
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'validation_v3'))
from benchmark import prepare,render,render19,PROBS,CANDIDATES
OUT=ROOT/'reader_figures';FIG=OUT/'figures';FIG.mkdir(exist_ok=True)
ALL=pd.read_csv(ROOT/'validation_v2/results/families.csv')
A=ALL[~ALL.family.isin(['Quantile plot','ECDF'])].copy()
A['candidate']=A.family+' / '+A.setting
X=pd.read_csv(ROOT/'validation_v2/results/trials.csv')
X=X[(X.observer=='threshold')&(X.axis=='zero')&(X.H==256)]
CASES={c['key']:c for c in json.loads((ROOT/'data/derived/comparisons.json').read_text())}
NAVY='#183445';TEAL='#00877d';BLUE='#267ea5';ORANGE='#df7836';GREY='#6b7c87';LIGHT='#eef5f5';LINE='#d4dfe3';RED='#b55938'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'text.color':NAVY,'axes.labelcolor':NAVY,'axes.edgecolor':LINE,'xtick.color':GREY,'ytick.color':GREY,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none'})
C5='Quantile plot / five';C19='Quantile plot / nineteen';BAR='Bar chart / means'
SHORT={'Bar chart / means':'Mean bars','Box plot / five':'Box plot','Interval plot / five':'Interval plot','Dot plot / raw':'Raw dots','Histogram / 16':'Histogram','Heatmap / 16':'Heatmap','Violin plot / 64':'Violin plot','ECDF / full':'Cumulative curve (ECDF)',C5:'Quantiles: 5 markers',C19:'Quantiles: 19 markers'}
RECORDS=[]
def record(key,c,H=256,task='five'):
 f,setting=c.split(' / ')
 return A[(A.key==key)&(A.family==f)&(A.setting==setting)].iloc[0]
def score(key,c,H=256,task='five'):return float(record(key,c).score)
def recovery(key,c,H=256):
 f,setting=c.split(' / ');z=X[(X.key==key)&(X.family==f)&(X.setting==setting)]
 ps=[.1,.25,.5,.75,.9];cs=CASES[key];target=np.quantile(cs['y'],ps)-np.quantile(cs['x'],ps)
 read=z[[f'q1_{p}' for p in ps]].to_numpy()-z[[f'q0_{p}' for p in ps]].to_numpy()
 err=np.mean(abs(read-target),axis=0);scale=z.iloc[0].scale
 assert len(z)==4 and np.isclose(err.mean()/scale,record(key,c).loss,atol=1e-12,rtol=0)
 return target,read.mean(0),err,scale
@lru_cache(None)
def context(key):return prepare(CASES[key]['x'],CASES[key]['y'])
def chart(fig,rect,key,c,H=256,phase=0,units='Value',group_labels=None):
 ctx=context(key);f,s=c.split(' / ');im,sp=render19(ctx,H,phase) if s=='nineteen' else render(ctx,f,s,H,phase,20260920)
 a=np.asarray(im);x,y,w,h=rect
 for g in [0,1]:
  ax=fig.add_axes([x+g*w*.53,y,w*.43,h]);ax.imshow(a[:,g*(H+16):g*(H+16)+H],interpolation='none');ax.set_xlim(5,H-5);ax.set_ylim(H-5,5)
  vals=MaxNLocator(nbins=4,steps=[1,2,2.5,5,10]).tick_values(ctx['lo'],ctx['hi']);vals=vals[(vals>=ctx['lo'])&(vals<=ctx['hi'])];pos=H-9-(vals-ctx['lo'])/(ctx['hi']-ctx['lo'])*(H-17)
  ax.set_yticks(pos);ax.set_yticklabels([f'{v:g}' for v in vals] if g==0 else []);ax.tick_params(axis='both',length=3,labelsize=10,pad=3)
  if g==0:ax.set_ylabel(units,fontsize=11,labelpad=4)
  if f=='Histogram':
   ax.set_xticks(8+(vals-ctx['lo'])/(ctx['hi']-ctx['lo'])*(H-17));ax.set_xticklabels([f'{v:g}' for v in vals],rotation=30,fontsize=8)
   ax.set_yticks([H-9,H-9-.5*(H-17),8]);ax.set_yticklabels(['0','0.5','1'] if g==0 else [])
   if g==0:ax.set_ylabel('Proportion',fontsize=10)
   ax.set_xlabel(units,fontsize=9)
  else:ax.set_xticks([])
  labels=group_labels or CASES[key]['labels'];ax.set_title(labels[g],fontsize=10,color=[BLUE,ORANGE][g],pad=7,weight='bold')
  ax.spines['left'].set_visible(g==0);ax.spines['bottom'].set_visible(f=='Histogram')
 return sp

def txt(fig,x,y,text,**kw):fig.text(x,y,text,**kw)
def box(fig,rect,face=LIGHT):
 fig.add_artist(FancyBboxPatch((rect[0],rect[1]),rect[2],rect[3],boxstyle='round,pad=.009,rounding_size=.009',transform=fig.transFigure,facecolor=face,edgecolor='none',zorder=-1))
def header(fig,num,title,subtitle):
 txt(fig,.055,.958,num.upper(),fontsize=10,weight='bold',color=TEAL)
 txt(fig,.055,.918,title,fontsize=21,weight='bold')
 txt(fig,.055,.883,subtitle,fontsize=11,color=GREY)
def label(fig,x,y,t):txt(fig,x,y,t,fontsize=13,weight='bold')
def save(fig,name):
 for ext in ['pdf','svg','png']:
  buf=io.BytesIO();fig.savefig(buf,format=ext,dpi=240,bbox_inches='tight',facecolor='white');payload=buf.getvalue()
  if ext=='pdf':assert payload.rstrip().endswith(b'%%EOF')
  path=FIG/(name+'.'+ext);path.write_bytes(payload);assert path.read_bytes()==payload
 plt.close(fig)

def rank(fig,rect,key):
 rows=A[A.key==key].sort_values('loss');ax=fig.add_axes(rect);ys=np.arange(len(rows))
 ax.barh(ys,rows.score,color=[TEAL]+['#aabcc6']*6,height=.62);ax.invert_yaxis();ax.set_xlim(0,113);ax.set_xticks([0,50,100]);ax.set_yticks(ys);ax.set_yticklabels(rows.family,fontsize=10);ax.set_xlabel('Score (higher is better)',fontsize=10);ax.tick_params(length=0)
 for y,v in zip(ys,rows.score):ax.text(v+1,y,f'{v:.2f}',va='center',fontsize=10)
 for sp in ['left','bottom']:ax.spines[sp].set_visible(False)
 return rows.iloc[0]
# A worked example with a familiar raw-dot display.
key='WDBC__03';c='Dot plot / raw';best=score(key,c);target,read,err,scale=recovery(key,c)
fig=plt.figure(figsize=(9,10.4));header(fig,'01 / How the score works','Visible differences. A traceable score.','Example: cell-nucleus area in benign and malignant samples')
box(fig,[.055,.793,.89,.065]);txt(fig,.074,.835,'QUESTION',fontsize=10,weight='bold',color=TEAL);txt(fig,.074,.808,'How does the group difference change from low to high values?',fontsize=12)
label(fig,.055,.751,'a  Optimize each familiar family');label(fig,.565,.751,'b  Inspect the best chart')
rank(fig,[.23,.426,.26,.284],key)
txt(fig,.57,.708,'Raw dot plot',fontsize=12,color=TEAL,weight='bold');txt(fig,.94,.700,f'{best:.2f}',ha='right',fontsize=27,weight='bold',color=TEAL)
chart(fig,[.59,.458,.35,.221],key,c,units='Area (source units)')
txt(fig,.57,.402,f'Mean bars {score(key,BAR):.2f} → raw dots {best:.2f}\nThe larger values and spread are visible.',fontsize=10,color=GREY,linespacing=1.55)
label(fig,.055,.351,'c  Read five gaps and calculate the score')
txt(fig,.055,.325,'Reading error = |gap recovered from chart − true gap|',fontsize=10,color=GREY)
ax=fig.add_axes([.055,.176,.89,.130]);ax.axis('off')
cell=[['True group gap']+[f'{v:.3f}' for v in target],['Mean absolute reading error']+[f'{v:.4f}' for v in err]]
tab=ax.table(cellText=cell,colLabels=['Percentile','10%\nLow','25%','50%\nMiddle','75%','90%\nHigh'],colWidths=[.35]+[.13]*5,cellLoc='center',bbox=[0,0,1,1]);tab.auto_set_font_size(False);tab.set_fontsize(11)
for (rr,cc),ce in tab.get_celld().items():
 ce.set_edgecolor('white');ce.set_linewidth(2);ce.set_facecolor(LIGHT if rr==0 else '#f7f9fa');ce.set_text_props(color=NAVY,weight='bold' if rr==0 or cc==0 else 'normal')
box(fig,[.055,.055,.89,.094]);loss=err.mean()/scale
txt(fig,.076,.115,f'Average error {err.mean():.5f} ÷ data spread {scale:.4f} = {loss:.6f}',fontsize=12)
txt(fig,.076,.077,f'Score = 100 / (1 + {loss:.6f}) = ',fontsize=16,weight='bold');txt(fig,.915,.077,f'{best:.2f}',ha='right',fontsize=22,weight='bold',color=TEAL)
txt(fig,.055,.016,'100 means exact recovery of the requested gaps, not 100% correct readers.',fontsize=10,color=GREY)
RECORDS.append(dict(figure=1,key=key,candidate=c,score=best,before_score=score(key,BAR),gain=best-score(key,BAR),loss=loss,mean_absolute_error=err.mean(),scale=scale));save(fig,'Figure_1_How_scoring_works')

# Eight substantial-improvement examples; two winners per non-bar winning family.
SUCCESS=[
 dict(key='WDBC__23',title='Cell-nucleus area: largest nuclei',dataset='WDBC',units='Area (source units)',labels=['Benign','Malignant']),
 dict(key='CKD__03',title='Blood urea',dataset='Kidney disease',units='mg/dL',labels=['No CKD','CKD']),
 dict(key='HAR__29',title='Body-motion variability',dataset='Activity',units='Normalized source units',labels=['Sitting','Walking']),
 dict(key='HeartFailure__01',title='Blood enzyme concentration',dataset='Heart failure',units='Units/L',labels=['Survived','Died']),
 dict(key='Cleveland__04',title='Exercise-related ECG change',dataset='Cleveland',units='ST depression (source units)',labels=['No disease','Disease']),
 dict(key='Wrist__04',title='Within-session heart-rate variability',dataset='Wrist exercise',units='SD (beats/min)',labels=['Early third','Late third']),
 dict(key='HAR__36',title='Body-rotation magnitude',dataset='Activity',units='Normalized source units',labels=['Sitting','Walking']),
 dict(key='CKD__02',title='Blood glucose',dataset='Kidney disease',units='mg/dL',labels=['No CKD','CKD']),
]
# The eight smallest valid gains over mean bars among ALL 127 comparisons.
# This is a disclosed retrospective selection rule, not a threshold of human equivalence.
LIMITS=[
 dict(key='Wrist__00',title='Average heart rate',dataset='Wrist exercise',units='Beats/min',labels=['Early third','Late third']),
 dict(key='Wrist__01',title='Middle heart rate',dataset='Wrist exercise',units='Median (beats/min)',labels=['Early third','Late third']),
 dict(key='Wrist__03',title='Higher heart rate',dataset='Wrist exercise',units='90th percentile (beats/min)',labels=['Early third','Late third']),
 dict(key='BIDMC__03',title='Higher patient-level rate',dataset='BIDMC',units='90th percentile (beats/min)',labels=['ECG','Pulse sensor']),
 dict(key='Wrist__02',title='Lower heart rate',dataset='Wrist exercise',units='10th percentile (beats/min)',labels=['Early third','Late third']),
 dict(key='ILPD__06',title='Total blood protein',dataset='Liver disease',units='Protein (source units)',labels=['No liver disease','Liver disease']),
 dict(key='WDBC__04',title='Cell-nucleus smoothness',dataset='WDBC',units='Source units',labels=['Benign','Malignant']),
 dict(key='BIDMC__02',title='Lower patient-level rate',dataset='BIDMC',units='10th percentile (beats/min)',labels=['ECG','Pulse sensor']),
]
# Assert the displayed group order agrees with the stored source arrays.
# WDBC/CKD/Cleveland/HAR/BIDMC/Wrist order was checked against labels.
LABELS={'Bar chart':'Mean bars','Dot plot':'Raw dots','Histogram':'Histogram','Heatmap':'Heatmap','Violin plot':'Violin'}
def winner(key):return A[A.key==key].sort_values('loss').iloc[0]

def compact_chart(fig,rect,key,c,units,fs=10):
 """Display unchanged raster pixels. Crop empty probability space/heatmap margins only.
 Measurement limits, values, colors and score calculations are never altered.
 """
 ctx=context(key);f,setting=c.split(' / ');im,sp=render(ctx,f,setting,256,0,20260920);arr=np.asarray(im);x,y,w,h=rect
 vals=MaxNLocator(nbins=2,steps=[1,2,2.5,5,10]).tick_values(ctx['lo'],ctx['hi']);vals=vals[(vals>=ctx['lo'])&(vals<=ctx['hi'])]
 if len(vals)>3:vals=vals[::2]
 def fmt(v):
  if abs(v)>=10000:return f'{v/1000:g}k'
  return f'{v:g}'
 if f=='Heatmap':
  # Identical strip pixels, placed in two rows to share a measurement axis.
  for g in [0,1]:
   ax=fig.add_axes([x,y+(1-g)*h*.49,w,h*.31]);patch=arr[90:166,g*272+8:g*272+248]
   delta=(ctx['hi']-ctx['lo'])/239
   ax.imshow(patch,aspect='auto',interpolation='none',extent=[ctx['lo']-.5*delta,ctx['hi']+.5*delta,0,1]);ax.set_xlim(ctx['lo'],ctx['hi']);ax.set_yticks([])
   for side in ax.spines:ax.spines[side].set_visible(False)
   ax.set_xticks(vals if g==1 else []);ax.set_xticklabels([fmt(v) for v in vals] if g==1 else [],fontsize=fs)
   ax.tick_params(length=2,pad=2);ax.text(-.025,.5,str(g+1),transform=ax.transAxes,va='center',ha='right',fontsize=fs,color=[BLUE,ORANGE][g],weight='bold')
  return
 for g in [0,1]:
  ax=fig.add_axes([x+g*w*.55,y,w*.44,h]);ax.imshow(arr[:,g*272:g*272+256],interpolation='none',aspect='auto');ax.set_xlim(5,251)
  if f=='Histogram':
   # Enlarge nonempty probability space; score remains on the ORIGINAL full raster.
   maxp=max(max(v) for v in ctx['payload'][(f,setting)]);upper=min(1,max(.05,maxp*1.16))
   ax.set_ylim(249,247-upper*239);ax.set_xticks(8+(vals-ctx['lo'])/(ctx['hi']-ctx['lo'])*239);ax.set_xticklabels([fmt(v) for v in vals],fontsize=fs,rotation=25)
   pp=MaxNLocator(nbins=2).tick_values(0,upper);pp=pp[(pp>=0)&(pp<=upper)];ax.set_yticks(247-pp*239);ax.set_yticklabels([f'{100*v:g}%' for v in pp] if g==0 else [],fontsize=fs-1)
  else:
   ax.set_ylim(251,5);pos=247-(vals-ctx['lo'])/(ctx['hi']-ctx['lo'])*239;ax.set_yticks(pos);ax.set_yticklabels([fmt(v) for v in vals] if g==0 else [],fontsize=fs);ax.set_xticks([])
  ax.tick_params(length=2,pad=2);ax.spines['left'].set_visible(g==0);ax.spines['bottom'].set_visible(f=='Histogram')
  ax.text(.5,1.035,str(g+1),transform=ax.transAxes,ha='center',fontsize=fs,color=[BLUE,ORANGE][g],weight='bold')

def grid_figure(examples,number,title,subtitle,name):
 fig=plt.figure(figsize=(11.4,13.9));txt(fig,.035,.974,f'{number:02d} / EIGHT WORKED EXAMPLES',fontsize=12,weight='bold',color=TEAL)
 txt(fig,.035,.939,title,fontsize=25,weight='bold');txt(fig,.035,.911,subtitle,fontsize=12,color=GREY)
 if number==2:
  from matplotlib.colors import LinearSegmentedColormap
  from matplotlib.colorbar import ColorbarBase
  ax=fig.add_axes([.80,.881,.16,.009]);ColorbarBase(ax,cmap=LinearSegmentedColormap.from_list('probability',['white','blue']),orientation='horizontal',ticks=[0,.5,1])
  ax.set_xticklabels(['0%','50%','100%'],fontsize=9);ax.tick_params(length=1,pad=1)
  txt(fig,.50,.881,'Heatmap key: proportion per bin',fontsize=10,color=GREY)
 values=[]
 for i,e in enumerate(examples):
  x=.038+(i%2)*.495;y=.676-(i//2)*.207;w=.426;h=.188;key=e['key'];win=winner(key);c=win.candidate;b=score(key,BAR);after=win.score;gain=after-b
  err_reduction=100*(1-win.loss/record(key,BAR).loss)
  box(fig,[x-.006,y-.003,w+.025,h],face='#f5f8fa')
  txt(fig,x,y+.164,f'{chr(97+i)}  {e["title"]}',fontsize=12.3,weight='bold')
  txt(fig,x,y+.144,e['dataset'],fontsize=10,color=GREY)
  # Group mapping is explicit; marks are ordered 1 then 2 in each chart.
  txt(fig,x,y+.126,'1 '+e['labels'][0],fontsize=10.5,color=BLUE,weight='bold')
  txt(fig,x+.21,y+.126,'2 '+e['labels'][1],fontsize=10.5,color=ORANGE,weight='bold')
  txt(fig,x,y+.106,f'Mean bars  {b:.2f}',fontsize=13,weight='bold',color=GREY)
  txt(fig,x+.234,y+.106,f'{LABELS[win.family]}  {after:.2f}',fontsize=13,weight='bold',color=TEAL)
  compact_chart(fig,[x+.032,y+.035,.145,.059],key,BAR,e['units'])
  compact_chart(fig,[x+.274,y+.035,.145,.059],key,c,e['units'])
  txt(fig,x+.209,y+.061,'→',fontsize=20,color=GREY,ha='center')
  txt(fig,x,y+.014,e['units'],fontsize=9.5,color=GREY)
  detail='Keep the chart' if abs(gain)<1e-10 else f'{err_reduction:.1f}% less recovery error'
  txt(fig,x,y-.001,f'+{gain:.2f} points  |  {detail}',fontsize=11.3,color=TEAL,weight='bold')
  values.append(dict(figure=number,panel=chr(97+i),n_group1=len(CASES[key]['x']),n_group2=len(CASES[key]['y']),key=key,feature=CASES[key]['feature'],dataset=CASES[key]['dataset'],candidate=c,before_score=b,score=after,gain=gain,before_loss=float(record(key,BAR).loss),loss=float(win.loss),relative_error_reduction_percent=err_reduction))
 txt(fig,.035,.036,'Same five-gap question, 21 settings and original 256-pixel scoring panels in every example.',fontsize=11,color=GREY)
 if number==2:
  txt(fig,.035,.018,'Histograms: height = proportion. Heatmaps: darker = more per bin. Display crops enlarge marks.',fontsize=10.5,color=GREY)
 else:
  txt(fig,.035,.018,'Small score gains are not a tested threshold of human benefit. Different rows can share participants.',fontsize=10.5,color=GREY)
 # Export each original card as a vector PDF for enlarged inspection.
 from matplotlib.transforms import Bbox
 panels=FIG/'panels';panels.mkdir(exist_ok=True)
 for i,e in enumerate(examples):
  x=.038+(i%2)*.495;y=.676-(i//2)*.207
  crop=Bbox.from_bounds(x-.019,y-.014,.477,.211).transformed(fig.transFigure).transformed(fig.dpi_scale_trans.inverted())
  buf=io.BytesIO();fig.savefig(buf,format='pdf',bbox_inches=crop,facecolor='white');payload=buf.getvalue();assert payload.rstrip().endswith(b'%%EOF')
  (panels/f'Figure_{number}{chr(97+i)}_{e["key"]}.pdf').write_bytes(payload)
 save(fig,name);RECORDS.extend(values)
 return values

success=grid_figure(SUCCESS,2,'Different data. Different winning charts.','Eight improvements from the same starting chart; two examples per selected family.','Figure_2_When_optimization_helps')
limited=grid_figure(LIMITS,3,'When the starting chart is already close.','The eight smallest gains over mean bars: three unchanged charts and five modest gains.','Figure_3_When_optimization_does_not_help')
W=A.sort_values('loss').groupby('key').head(1).copy();B=A[A.family=='Bar chart'][['key','score']].rename(columns={'score':'before_score'});allg=W.merge(B,on='key');allg['gain']=allg.score-allg.before_score
assert set(allg.dropna(subset=['gain']).sort_values('gain').head(8).key)==set(e['key'] for e in LIMITS)
assert len(SUCCESS)==8 and len(LIMITS)==8 and len({e['candidate'].split(' / ')[0] for e in success})==4
assert all(r['gain']>10 for r in success) and all(0<=r['gain']<2.5 for r in limited)
for e in SUCCESS+LIMITS:
 z=winner(e['key']);target,recovered,err,sc=recovery(e['key'],z.candidate);assert np.isclose(100/(1+err.mean()/sc),z.score,atol=1e-10,rtol=0)
counts=W.family.value_counts().to_dict()
pd.DataFrame(RECORDS).to_csv(OUT/'figure_values.csv',index=False)
(OUT/'figure_checks.json').write_text(json.dumps(dict(candidate_families=7,settings=21,comparisons=127,winner_counts=counts,source_sha256=hashlib.sha256((ROOT/'validation_v2/results/families.csv').read_bytes()).hexdigest(),examples=RECORDS,success_selection='Retrospective illustrative selection: two winners per non-bar winning family, all gains >10 points; not a representative sample.',limited_selection='Eight smallest gains over mean bars among comparisons where bars decoded successfully; same task and candidate set.',display_policy='Original scored rasters. Histograms crop empty probability space; heatmap strips are cropped and stacked. Measurement limits and pixel colors are unchanged. Scores apply to original 256-pixel panels, not resized publication layouts.'),indent=2))
pd.DataFrame({'A':pd.Series(CASES['WDBC__03']['x']),'B':pd.Series(CASES['WDBC__03']['y'])}).to_csv(OUT/'example_input.csv',index=False)
# All-setting example scores and family settings are distributed alongside the figures.
print(pd.DataFrame(RECORDS)[['figure','key','candidate','score','before_score','gain']].to_string(index=False))

# Regenerate the exact panel-to-source mapping used in Supplementary Section S17.
def tex_escape(value):
 return str(value).replace('_',r'\_').replace('%',r'\%').replace('&',r'\&')
lines=[r'\begin{longtable}{lp{4.9cm}p{3.1cm}rrr}\toprule',r'Panel & Source feature & Selected setting & $n_1/n_2$ & Before & After\\\midrule\endhead']
for v in RECORDS:
 cs=CASES[v['key']];panel=str(v['figure'])+v.get('panel','')
 lines.append(f"{panel} & {tex_escape(v['key'])}: {tex_escape(cs['feature'])} & {tex_escape(v['candidate'])} & {len(cs['x'])}/{len(cs['y'])} & {v['before_score']:.2f} & {v['score']:.2f}"+r'\\')
lines.append(r'\bottomrule\end{longtable}');(OUT/'example_table.tex').write_text('\n'.join(lines))
