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


pd.DataFrame(RECORDS).to_csv(OUT/'scoring_example_values.csv',index=False)
