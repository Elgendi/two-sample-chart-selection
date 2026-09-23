"""Reader-facing figures from frozen v3 results. No new outcomes or selection rules."""
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
ALL=pd.read_csv(ROOT/'validation_v3/results/configurations.csv');A=ALL[(ALL.observer=='threshold')&(ALL.task=='five')]
X=pd.read_csv(ROOT/'validation_v3/results/decoded_trials.csv');X=X[X.observer=='threshold']
D=pd.read_csv(ROOT/'validation_v3/results/policy_results.csv');D=D[(D.observer=='threshold')&(D.task=='five')]
CASES={c['key']:c for c in json.loads((ROOT/'data/derived/comparisons.json').read_text())}
NAVY='#183445';TEAL='#00877d';BLUE='#267ea5';ORANGE='#df7836';GREY='#6b7c87';LIGHT='#eef5f5';LINE='#d4dfe3';RED='#b55938'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'text.color':NAVY,'axes.labelcolor':NAVY,'axes.edgecolor':LINE,'xtick.color':GREY,'ytick.color':GREY,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none'})
C5='Quantile plot / five';C19='Quantile plot / nineteen';BAR='Bar chart / means'
SHORT={'Bar chart / means':'Mean bars','Box plot / five':'Box plot','Interval plot / five':'Interval plot','Dot plot / raw':'Raw dots','Histogram / 16':'Histogram','Heatmap / 16':'Heatmap','Violin plot / 64':'Violin plot','ECDF / full':'Cumulative curve (ECDF)',C5:'Quantiles: 5 markers',C19:'Quantiles: 19 markers'}
RECORDS=[]
def record(key,c,H=256,task='five'):
 r=ALL[(ALL.key==key)&(ALL.candidate==c)&(ALL.H==H)&(ALL.observer=='threshold')&(ALL.task==task)].iloc[0];return r

def score(key,c,H=256,task='five'):return 100/(1+record(key,c,H,task).loss)
def recovery(key,c,H=256):
 z=X[(X.key==key)&(X.candidate==c)&(X.H==H)]
 q=np.array([json.loads(v) for v in z.decoded_q]);t=np.array(json.loads(z.iloc[0].truth_q));scale=z.iloc[0].scale
 ix=[1,4,9,14,17];target=(t[1]-t[0])[ix];read=(q[:,1]-q[:,0])[:,ix];err=np.mean(abs(read-target),axis=0)
 assert np.isclose(err.mean()/scale,record(key,c,H).loss,atol=1e-12,rtol=0)
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
  if f=='Quantile plot':
   ax.set_xticks([8+p*(H-17) for p in [.1,.5,.9]]);ax.set_xticklabels(['10','50','90']);ax.set_xlabel('Percentile',fontsize=10,labelpad=3)
  else:ax.set_xticks([])
  labels=group_labels or CASES[key]['labels'];ax.set_title(labels[g],fontsize=11,color=[BLUE,ORANGE][g],pad=7,weight='bold')
  ax.spines['left'].set_visible(g==0);ax.spines['bottom'].set_visible(f=='Quantile plot')
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
# FIGURE 1. One actual case, all fixed choices, explicit arithmetic.
key='WDBC__00';best=score(key,C5);target,read,err,scale=recovery(key,C5)
fig=plt.figure(figsize=(9,10.4));header(fig,'01 / How the score works','Ask a question. Compare charts. Check the score.','Example: tumour radius in benign and malignant samples')
box(fig,[.055,.793,.89,.065]);txt(fig,.074,.835,'QUESTION',fontsize=10,weight='bold',color=TEAL);txt(fig,.074,.808,'How does the group difference change from low to high values?',fontsize=12)
label(fig,.055,.751,'a  Score every candidate');label(fig,.565,.751,'b  Inspect the selected chart')
rows=A[(A.key==key)&(A.H==256)].copy();order=[f+' / '+s for f,s in CANDIDATES];rows['order']=rows.candidate.map({c:i for i,c in enumerate(order)});rows=rows.sort_values(['loss','order']);rows['score']=100/(1+rows.loss)
ax=fig.add_axes([.26,.426,.23,.284]);ys=np.arange(len(rows));colors=[TEAL if c in [C5,C19] else '#aabcc6' for c in rows.candidate]
ax.barh(ys,rows.score,color=colors,height=.62);ax.set_yticks(ys);ax.set_yticklabels([SHORT[c] for c in rows.candidate],fontsize=10);ax.invert_yaxis();ax.set_xlim(0,112);ax.set_xticks([0,50,100]);ax.set_xlabel('Score (higher is better)',fontsize=10);ax.tick_params(length=0)
for y,v in zip(ys,rows.score):ax.text(v+1.3,y,f'{v:.2f}',va='center',fontsize=10,weight='bold' if v>99 else 'normal')
for sp in ['left','bottom']:ax.spines[sp].set_visible(False)
txt(fig,.57,.708,'Quantile plot',fontsize=12,color=TEAL,weight='bold');txt(fig,.94,.700,f'{best:.2f}',ha='right',fontsize=27,weight='bold',color=TEAL)
chart(fig,[.59,.470,.35,.183],key,C5,units='Radius (source units)')
txt(fig,.57,.402,'5 and 19 markers tie for best.\nEither is a valid numerical optimum.',fontsize=10,color=GREY,linespacing=1.55)
label(fig,.055,.351,'c  Read five gaps and turn the error into a score')
txt(fig,.055,.325,'Reading error = |gap recovered from chart − true gap|',fontsize=10,color=GREY)
ax=fig.add_axes([.055,.176,.89,.130]);ax.axis('off')
cell=[['True group gap']+[f'{v:.3f}' for v in target],['Mean absolute reading error']+[f'{v:.4f}' for v in err]]
tab=ax.table(cellText=cell,colLabels=['Percentile','10%\nLow','25%','50%\nMiddle','75%','90%\nHigh'],colWidths=[.35]+[.13]*5,cellLoc='center',bbox=[0,0,1,1]);tab.auto_set_font_size(False);tab.set_fontsize(11)
for (r,c),cell0 in tab.get_celld().items():
 cell0.set_edgecolor('white');cell0.set_linewidth(2);cell0.set_facecolor(LIGHT if r==0 else '#f7f9fa');cell0.set_text_props(color=NAVY,weight='bold' if r==0 or c==0 else 'normal')
box(fig,[.055,.055,.89,.094]);loss=err.mean()/scale
text1=f'Average error {err.mean():.5f} ÷ data spread {scale:.4f} = {loss:.6f}'
txt(fig,.076,.115,text1,fontsize=12)
txt(fig,.076,.077,rf'Score = 100 / (1 + {loss:.6f}) = ',fontsize=16,weight='bold');txt(fig,.915,.077,f'{best:.2f}',ha='right',fontsize=22,weight='bold',color=TEAL)
txt(fig,.055,.016,'100 means exact recovery of the five requested gaps. It is not a percentage of correct readers.',fontsize=10,color=GREY)
RECORDS.append(dict(figure=1,key=key,candidate=C5,H=256,loss=loss,score=best,mean_absolute_error=err.mean(),scale=scale))
save(fig,'Figure_1_How_scoring_works')
# FIGURE 2. Matched data/axes/resolution before and after, and the actual lost information.
key='HAR__29';b=score(key,BAR);after=score(key,C5);gain=after-b;t,rb,eb,s=recovery(key,BAR);_,ra,ea,_=recovery(key,C5)
fig=plt.figure(figsize=(9,9.4));header(fig,'02 / When optimization helps','Averages can hide where the groups differ.','Example: body-motion variability during sitting and walking')
label(fig,.065,.821,'BEFORE  |  Mean bars');label(fig,.545,.821,'AFTER  |  Quantile plot')
txt(fig,.065,.765,f'{b:.2f}',fontsize=34,color=GREY,weight='bold');txt(fig,.26,.767,'score',fontsize=11,color=GREY)
txt(fig,.545,.765,f'{after:.2f}',fontsize=34,color=TEAL,weight='bold');txt(fig,.77,.767,'score',fontsize=11,color=GREY)
chart(fig,[.08,.491,.39,.211],key,BAR,units='Motion variability\n(normalized source units)')
chart(fig,[.56,.491,.39,.211],key,C5,units='Motion variability\n(normalized source units)')
box(fig,[.065,.376,.88,.066]);txt(fig,.087,.415,f'+{gain:.2f} score points',fontsize=18,color=TEAL,weight='bold');txt(fig,.087,.390,'Same observations, panel size, axes and scoring rule.',fontsize=11)
label(fig,.065,.328,'What changed? The chart now preserves the changing gap.')
ax=fig.add_axes([.115,.124,.50,.160]);p=np.array([10,25,50,75,90]);ax.plot(p,t/s,'o-',color=NAVY,lw=2.5,ms=6,label='True gap in the data');ax.plot(p,rb/s,'s--',color=GREY,lw=2,ms=5,label='Read from mean bars');ax.plot(p,ra/s,'o',mfc='white',mec=TEAL,mew=2,ms=8,label='Read from selected chart');ax.set_xticks(p);ax.set_xticklabels(['10%\nLow','25%','50%\nMiddle','75%','90%\nHigh'],fontsize=10);ax.set_ylabel('Group gap / data spread',fontsize=11);ax.grid(axis='y',alpha=.16)
ax.legend(loc='upper left',bbox_to_anchor=(1.02,1),frameon=False,fontsize=10,labelspacing=1)
txt(fig,.665,.110,f'{100*(1-record(key,C5).loss/record(key,BAR).loss):.1f}% less\nrecovery error',fontsize=17,color=TEAL,weight='bold',linespacing=1.4)
txt(fig,.065,.035,'A large gain over mean bars does not imply a gain over a strong distributional default.',fontsize=10,color=GREY)
for c in [BAR,C5]:RECORDS.append(dict(figure=2,key=key,candidate=c,H=256,loss=record(key,c).loss,score=score(key,c)))
save(fig,'Figure_2_When_optimization_helps')
# FIGURE 3. No gain for an already aligned display; aggregate transfer evidence and reversal.
key='CKD__00';cbox='Box plot / five';s5=score(key,cbox,task='median');s19=s5
assert np.isclose(record(key,cbox,task='median').loss,ALL[(ALL.key==key)&(ALL.task=='median')&(ALL.H==256)&(ALL.observer=='threshold')].loss.min(),atol=1e-12,rtol=0)
fig=plt.figure(figsize=(9,10.0));header(fig,'03 / When optimization does not help','A good starting chart may need no replacement.','The same scoring rule must also reveal small gains, ties and losses.')
label(fig,.065,.818,'a  Question: compare the middle (median) age')
txt(fig,.08,.775,'START: box plot',fontsize=12,weight='bold');txt(fig,.55,.775,'AFTER SEARCH: keep the box plot',fontsize=12,weight='bold')
txt(fig,.08,.724,f'{s5:.2f}',fontsize=31,weight='bold',color=TEAL);txt(fig,.27,.727,'score',fontsize=11,color=GREY)
txt(fig,.55,.724,f'{s19:.2f}',fontsize=31,weight='bold',color=TEAL);txt(fig,.75,.727,'score',fontsize=11,color=GREY)
chart(fig,[.10,.497,.38,.167],key,cbox,units='Age',group_labels=['No chronic kidney\ndisease','Chronic kidney\ndisease']);chart(fig,[.57,.497,.38,.167],key,cbox,units='Age',group_labels=['No chronic kidney\ndisease','Chronic kidney\ndisease'])
box(fig,[.065,.383,.88,.060]);txt(fig,.086,.407,'0.00-point gain: the starting box plot is already best-scoring.',fontsize=13,weight='bold',color=TEAL)
label(fig,.065,.332,'b  Five-gap task: does a gain hold at another display size?')
p=D.pivot(index='key',columns='rule',values='loss');diff=p.task_default-p.case_selected
counts={'Higher score':int((diff>1e-12).sum()),'Same loss':int((abs(diff)<=1e-12).sum()),'Lower score':int((diff< -1e-12).sum())}
assert sum(counts.values())==127
ax=fig.add_axes([.065,.172,.39,.125]);ax.set_xlim(-.7,12.7);ax.set_ylim(-.7,9.7);ax.axis('off')
colors=[TEAL]*counts['Higher score']+['#bac8d0']*counts['Same loss']+[RED]*counts['Lower score']
for i,col in enumerate(colors):ax.scatter(i%13,9-i//13,s=32,color=col,edgecolor='none')
txt(fig,.065,.141,'127 comparisons • one dot per comparison',fontsize=10,color=GREY)
for y,(lab,col) in zip([.286,.249,.212],[('Higher score',TEAL),('Same loss',GREY),('Lower score',RED)]):
 txt(fig,.495,y,str(counts[lab]),fontsize=22,weight='bold',color=col);txt(fig,.635,y+.002,'Same score' if lab=='Same loss' else lab,fontsize=12,color=col)
k='HAR__10';qtrain=score(k,C5);dtrain=score(k,'Dot plot / raw');qtest=score(k,C5,384);dtest=score(k,'Dot plot / raw',384)
box(fig,[.065,.039,.88,.077],face='#faf2ed');txt(fig,.085,.088,'Example of reversal: five markers → selected raw dots',fontsize=11,weight='bold');txt(fig,.085,.055,f'At selection: {qtrain:.2f} → {dtrain:.2f}     At the new display: {qtest:.2f} → {dtest:.2f}',fontsize=12,color=RED)
txt(fig,.065,.009,'All 127 cases: optimized choice versus a task-matched default for five quantile gaps.',fontsize=10,color=GREY)
RECORDS.append(dict(figure=3,key=key,candidate=cbox,H=256,task='median',loss=record(key,cbox,task='median').loss,score=s5))
for c,H in [(C5,256),('Dot plot / raw',256),(C5,384),('Dot plot / raw',384)]:RECORDS.append(dict(figure=3,key=k,candidate=c,H=H,loss=record(k,c,H).loss,score=score(k,c,H)))
save(fig,'Figure_3_When_optimization_does_not_help')
for row in RECORDS:row.setdefault('task','five')
pd.DataFrame(RECORDS).to_csv(OUT/'figure_values.csv',index=False)
(OUT/'figure_checks.json').write_text(json.dumps({'status':'passed','counts':counts,'gain_score_points':gain,'error_reduction_percent':100*(1-record('HAR__29',C5).loss/record('HAR__29',BAR).loss),'worked_example_loss':loss,'worked_example_score':best,'no_gain_example':{'key':'CKD__00','task':'median','chart':'Box plot','score':s5},'reversal_selection':[qtrain,dtrain],'reversal_transfer':[qtest,dtest],'sources':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'validation_v3/results/configurations.csv',ROOT/'validation_v3/results/decoded_trials.csv',ROOT/'validation_v3/results/policy_results.csv',Path(__file__)]}},indent=2))
print(json.dumps({'worked_score':best,'improvement':[b,after],'transfer_counts':counts,'reversal':[qtrain,dtrain,qtest,dtest]},indent=2))
