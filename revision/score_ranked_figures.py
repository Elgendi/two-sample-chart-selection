"""Three audience-friendly figures from unchanged public-database arrays/results."""
from pathlib import Path
import json,textwrap,io
from selection_score import score_candidates
from chart_catalogue import catalogue_rankings, CATALOGUE
from scipy.stats import gaussian_kde
from model import scale
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
from matplotlib.ticker import MaxNLocator
P=Path(__file__).resolve().parents[1];OUT=P/'revision/accessible_figures';OUT.mkdir(exist_ok=True)
CASES={c['key']:c for c in json.loads((P/'data/derived/comparisons.json').read_text())};DETAIL=json.loads((P/'revision/results/details.json').read_text());AUDIT=pd.read_csv(P/'revision/results/audit.csv').set_index('key')
BLUE='#267ea5';ORANGE='#df7836';INK='#183348';GREEN='#168376';MUTED='#62788b';RED='#b64c44';PALE='#eef5f8'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.labelsize':10,'axes.titlesize':11,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none','savefig.facecolor':'white'})
SOURCES={'WDBC':('UCI WDBC','10.24432/C5DW2B'),'HAR':('UCI Smartphone HAR','10.24432/C54S4K'),'CKD':('UCI Chronic Kidney Disease','10.24432/C5G020'),'BIDMC':('PhysioNet BIDMC','10.13026/C2208R')}
def data(key):
 c=CASES[key];d=DETAIL[key];a=AUDIT.loc[key];mean=d['candidates'][0]['error'];selected=next(r for r in d['candidates'] if r['configuration']==a.configuration)
 return c,np.array(c['x']),np.array(c['y']),d,a,selected,100*(1-selected['error']/mean) if mean>0 else 0.
def metric(key):
 c,x,y,d,a,w,g=data(key);return dict(key=key,dataset=c['dataset'],feature=c['feature'],n_A=len(x),n_B=len(y),configuration=a.configuration,mean_error=d['candidates'][0]['error'],selected_error=w['error'],tolerance=d['tolerance'],before_ratio=d['candidates'][0]['error']/d['tolerance'],after_ratio=w['error']/d['tolerance'],error_reduction_pct=round(g,10),agreement=a.agreement,source_doi=SOURCES[c['dataset']][1])
def save(fig,name):
 for ext in ['pdf','svg','png']:
  buffer=io.BytesIO();fig.savefig(buffer,format=ext,bbox_inches='tight',dpi=400);payload=buffer.getvalue();target=OUT/f'{name}.{ext}';temp=OUT/f'{name}.{ext}.tmp';temp.write_bytes(payload);temp.replace(target)
 plt.close(fig)
def arrow(fig,x0,y0,x1,y1,color=GREEN):fig.add_artist(FancyArrowPatch((x0,y0),(x1,y1),transform=fig.transFigure,arrowstyle='-|>',mutation_scale=20,lw=2,color=color))
def plot(ax,x,y,config,labels,limits,unit):
 if config=='means':ax.bar([0,1],[x.mean(),y.mean()],color=[BLUE,ORANGE],width=.48);ax.set_xticks([0,1],labels)
 elif config=='raw':
  rng=np.random.default_rng(20260920)
  for j,v,col in [(0,x,BLUE),(1,y,ORANGE)]:
   ax.scatter(j+rng.uniform(-.18,.18,len(v)),v,s=9,alpha=.5,color=col,edgecolors='none',rasterized=False)
  ax.set_xticks([0,1],labels);ax.set_xlim(-.5,1.5)
 elif config=='five_number':
  b=ax.boxplot([x,y],positions=[0,1],widths=.45,whis=(0,100),patch_artist=True,showfliers=False,medianprops={'color':INK,'linewidth':1.5})
  for patch,col in zip(b['boxes'],[BLUE,ORANGE]):patch.set_facecolor(col);patch.set_alpha(.8)
  ax.set_xticks([0,1],labels)
 elif config.startswith('bins_'):
  n=int(config.split('_')[1]);edges=np.linspace(min(x.min(),y.min()),max(x.max(),y.max()),n+1)
  for v,col in [(x,BLUE),(y,ORANGE)]:
   ax.bar(edges[:-1],100*np.histogram(v,edges)[0]/len(v),width=np.diff(edges),align='edge',color=col,alpha=.55,edgecolor=col,linewidth=.55)
  ax.set_xlabel('Measurement value',fontsize=10);ax.set_ylabel('Observations (%)',fontsize=10);ax.set_xlim(limits);ax.set_ylim(bottom=0)
  ax.tick_params(labelsize=10);ax.xaxis.set_major_locator(MaxNLocator(4));ax.yaxis.set_major_locator(MaxNLocator(4));ax.spines['left'].set_color(MUTED);ax.spines['bottom'].set_color(MUTED)
  return
 elif config.startswith('density_'):
  n=int(config.split('_')[1]);lo=min(x.min(),y.min());hi=max(x.max(),y.max());sc=scale(x,y)
  if hi==lo:lo-=.5;hi+=.5
  bw=max(np.std(x,ddof=1)*len(x)**(-.2),np.std(y,ddof=1)*len(y)**(-.2),.01*sc)
  z=np.linspace(lo-4*bw,hi+4*bw,n)
  for j,v,col in [(0,x,BLUE),(1,y,ORANGE)]:
   if np.std(v)>0:dens=gaussian_kde(v)(z)
   else:
    ld=-.5*((z-v[0])/(.01*sc))**2;dens=np.exp(ld-ld.max())
   width=.28*dens/dens.max();ax.fill_betweenx(z,j-width,j+width,color=col,alpha=.75,lw=.8,edgecolor=col)
  ax.set_xticks([0,1],labels);ax.set_xlim(-.5,1.5)
 else:raise ValueError(config)
 ax.set_ylim(limits);ax.set_ylabel(unit,fontsize=12);ax.tick_params(labelsize=11);ax.yaxis.set_major_locator(MaxNLocator(5));ax.spines['left'].set_color(MUTED);ax.spines['bottom'].set_color(MUTED)

def ranked(key):
 c=CASES[key];d=DETAIL[key]
 rows=score_candidates(d['candidates'],d['tolerance'],len(c['x'])+len(c['y']))
 assert rows[0]['configuration']==AUDIT.loc[key].configuration
 return rows
def label(config):
 if config=='means':return 'Mean bars'
 if config=='five_number':return 'Box plots'
 if config=='raw':return 'Raw dots'
 n=config.split('_')[1]
 return f'Histogram / {n} bins' if config.startswith('bins') else f'Violin / {n} grid points'
def chart_rows(key):
 c=CASES[key];d=DETAIL[key]
 return catalogue_rankings(d['candidates'],d['tolerance'],len(c['x'])+len(c['y']))
def family_label(r):
 name=r['chart'];config=r['configuration']
 if not r['applicable']:return name
 if config.startswith('bins_'):return name+' / '+config.split('_')[1]+' bins'
 if config.startswith('density_'):return name+' / '+config.split('_')[1]+' grid'
 if r['chart_id']=='dot':return name+(' / means' if config=='means' else ' / raw')
 if r['chart_id']=='interval':return 'Interval plot / five-number'
 return name
def detailed_ranking(fig,rect,key):
 ax=fig.add_axes(rect);ax.set_xlim(0,1);ax.set_ylim(8.3,-1.5);ax.axis('off')
 ax.text(.005,-1.02,'ORDER / ELIGIBLE CHART',fontsize=9.5,color=MUTED,weight='bold')
 ax.text(.685,-1.02,'E / τ',fontsize=10,color=MUTED,weight='bold',ha='right')
 ax.text(.86,-1.02,'SCORE',fontsize=10,color=MUTED,weight='bold',ha='right');ax.text(.98,-1.02,'SIZE',fontsize=10,color=MUTED,weight='bold',ha='right')
 for i,r in enumerate(q for q in chart_rows(key)['families'] if q['applicable']):
  col=GREEN if r['display_selected'] else (BLUE if r['qualifies'] else '#89939c')
  if r['display_selected']:ax.add_patch(FancyBboxPatch((0,i-.43),1,.86,boxstyle='round,pad=0.002,rounding_size=.04',facecolor='#e6f2ee',edgecolor='none'))
  ax.text(.012,i,str(r['recommendation_order']),fontsize=10.5,color=col,va='center')
  ax.text(.072,i,family_label(r),fontsize=10,color=INK,va='center',weight='bold' if r['display_selected'] else 'normal')
  ax.text(.685,i,f"{r['discrepancy_ratio']:.3f}",fontsize=10,color=MUTED,va='center',ha='right')
  ax.text(.86,i,f"{r['score']:.1f}"+('' if r['qualifies'] else '*'),fontsize=10.5,color=col,va='center',ha='right',weight='bold' if r['display_selected'] else 'normal')
  ax.text(.98,i,str(r['N']),fontsize=10,color=MUTED,ha='right',va='center')
 ax.text(.012,7.0,'Green: displayed choice. E / τ ≤ 1 meets tolerance.',fontsize=8.7,color=MUTED)
 ax.text(.012,7.65,'Exact numerical ties use declared catalogue order.',fontsize=8.7,color=MUTED)
 return ax

SUCCESS=[('WDBC__10','Breast tumour data','Radius standard error',['Benign','Malignant'],'Source units','Histogram · 8 bins','Distribution detail retained'),('HAR__29','Smartphone activity data','Gyroscope-jerk variability, z axis',['Sitting','Walking'],'Normalized source units','Box plots · min–max whiskers','Variation across people retained'),('WDBC__22','Breast tumour data','Worst perimeter',['Benign','Malignant'],'Source units','Violin · 8 grid points','Sampled-density representation')]

LIMITS=[('BIDMC__00','Physiological monitor data','Mean heart rate',['ECG HR','PPG pulse'],'Heart rate (bpm)','Mean bars · unchanged','The original summary already suffices.\nNo chart change is needed.'),('CKD__09','Kidney disease data','White blood cell count',['Non-CKD','CKD'],'Source units','Histogram · 4 bins','A long upper tail stretches the axis.\nThe gain is modest.'),('CKD__06','Kidney disease data','Serum potassium',['Non-CKD','CKD'],'Source units','Histogram · 32 bins','Extreme source values compress the centre.\nTheir accuracy and units remain unresolved.')]

allrows=[];rankingrows=[]
def comparisons(examples,name,title,subtitle,limitations=False,detailed=False):
 f=plt.figure(figsize=(10.2,13.4))
 f.text(.035,.962,title,fontsize=21,weight='bold',color=INK)
 f.text(.035,.93,subtitle,fontsize=11.5,color=MUTED)
 for panel,(key,dataset,feature,labels,unit,selected,explain) in enumerate(examples):
  top=.881-panel*.278
  c,x,y,d,a,w,g=data(key);scores={r['configuration']:r for r in ranked(key)};before=scores['means']['score'];after=scores[a.configuration]['score']
  row=dict(figure=name,panel='abc'[panel],**metric(key),mean_selection_score=before,selected_selection_score=after,selection_gain_points=after-before)
  if not detailed:allrows.append(row)
  if not detailed:rankingrows.extend(dict(key=key,figure=name,**r) for r in ranked(key))
  if panel:f.add_artist(plt.Line2D([.035,.97],[top+.012,top+.012],transform=f.transFigure,color='#d7e1e6',lw=.8))
  f.text(.035,top,'abc'[panel],fontsize=17,weight='bold',color=INK)
  f.text(.063,top,dataset+' / '+feature,fontsize=13,weight='bold',color=INK)
  f.text(.055,top-.024,f'A: {labels[0]} (n={len(x)})',fontsize=10,color=BLUE)
  f.text(.248,top-.024,f'B: {labels[1]} (n={len(y)})',fontsize=10,color=ORANGE)
  f.text(.055,top-.064,f'{before:.1f}'+('' if scores['means']['qualifies'] else '*'),fontsize=23,weight='bold',color=MUTED)
  f.text(.166,top-.061,'→',fontsize=19,color=MUTED)
  f.text(.219,top-.064,f'{after:.1f}',fontsize=23,weight='bold',color=GREEN)
  f.text(.346,top-.058,f'+{after-before:.1f}',fontsize=16,weight='bold',color=GREEN)
  f.text(.346,top-.075,'score points',fontsize=9.5,color=MUTED)
  f.text(.055,top-.083,'Mean bars',fontsize=10,color=MUTED)
  f.text(.219,top-.083,'Selected / 100',fontsize=10,weight='bold',color=GREEN)
  lo=min(0,x.min(),y.min());hi=max(0,x.max(),y.max());pad=.04*(hi-lo);limits=(lo-pad if lo<0 else 0,hi+pad)
  if a.configuration.startswith('density_'):
   sc=scale(x,y);bw=max(np.std(x,ddof=1)*len(x)**(-.2),np.std(y,ddof=1)*len(y)**(-.2),.01*sc)
   limits=(min(0,x.min()-4*bw,y.min()-4*bw),max(x.max(),y.max())+4*bw)
  ax1=f.add_axes([.082,top-.202,.108,.106]);ax2=f.add_axes([.286,top-.202,.163,.106])
  plot(ax1,x,y,'means',labels,limits,unit);plot(ax2,x,y,a.configuration,labels,limits,unit)
  if not a.configuration.startswith('bins_'):ax2.set_ylabel('')
  for ax in [ax1,ax2]:ax.tick_params(labelsize=9);ax.yaxis.label.set_size(9);ax.xaxis.label.set_size(9)
  ax1.set_xticks([0,1],['A','B']);ax2.set_xticks([0,1],['A','B']) if (a.configuration in ['means','five_number'] or a.configuration.startswith('density_')) else None
  detailed_ranking(f,[.505,top-.257,.465,.242],key)
  notes={
   'WDBC__10':'Histogram shown; heatmap has equal numerical merit.',
   'CKD__08':'8-bin histogram: 18 of 329 values; within tolerance.',
   'HAR__29':'Box shown; five-number interval has equal merit.',
   'WDBC__22':'Violin selected; provisional bootstrap agreement 0.71.',
   'BIDMC__00':'Mean bars shown; no change in detail is needed.',
   'CKD__09':'The long tail remains; a high score is not data quality.',
   'CKD__06':'66 of 312 values needed; source extremes remain.'}
  f.text(.055,top-.241,notes[key],fontsize=9.7,color=INK)
  f.text(.055,top-.257,SOURCES[c['dataset']][0]+' / '+SOURCES[c['dataset']][1],fontsize=8.8,color=MUTED)
 f.text(.035,.039,'Score: percentage reduction in retained values, credited only when the comparison stays within tolerance.',fontsize=10,color=INK)
 f.text(.035,.023,'Raw dots = 0 (no reduction). 0* = does not qualify. Equal positive scores: smaller discrepancy ranks first.',fontsize=10,color=MUTED)
 f.text(.035,.007,'All 15 families are documented in Table S3. Eight other-task families are excluded from these scored tables.',fontsize=9.5,color=MUTED)
 save(f,name)

comparisons(SUCCESS,'Figure_2_Improvement','Preserve the comparison with less detail','15 families screened / Seven eligible choices / One displayed recommendation')
comparisons(LIMITS,'Figure_3_Limits','Simplification has limits','No change may be needed / Long tails remain / Source extremes can require more detail',True)
# Figure 1 illustrates the original constrained compactness objective.
f=plt.figure(figsize=(13.5,6.8))
f.text(.035,.95,'How much detail does the comparison need?',fontsize=21,weight='bold',color=INK)
f.text(.035,.895,'Two raw-data columns → test preservation and compactness → select the smallest qualifying representation',fontsize=12,color=MUTED)
for left,width in [(.035,.245),(.335,.325),(.715,.25)]:
 f.add_artist(FancyBboxPatch((left,.23),width,.57,boxstyle='round,pad=.008,rounding_size=.014',transform=f.transFigure,facecolor=PALE,edgecolor='none',zorder=-2))
c,x,y,d,a,w,g=data('WDBC__10')
f.text(.05,.75,'01  RAW VALUES',fontsize=13,weight='bold',color=INK)
f.text(.065,.694,'Benign',color=BLUE,fontsize=12,weight='bold');f.text(.17,.694,'Malignant',color=ORANGE,fontsize=12,weight='bold')
for i in range(6):
 for xx,val,col in [(.065,x[i],BLUE),(.17,y[i],ORANGE)]:f.text(xx,.639-.05*i,f'{val:.4f}',color=col,fontfamily='DejaVu Sans Mono',fontsize=12)
f.text(.05,.275,'Six rows shown; all 569 values used.',fontsize=10,color=MUTED)
arrow(f,.285,.5,.325,.5)
f.text(.35,.75,'02  SCREEN 15 CHART FAMILIES',fontsize=13,weight='bold',color=INK)
f.text(.35,.655,'Match chart purpose to the question.',fontsize=12,color=INK)
f.text(.35,.605,'7 eligible families → 21 display settings',fontsize=11.5,color=INK)
f.text(.35,.555,'Exclude 8 families for other tasks',fontsize=11.5,color=INK)
f.text(.35,.452,'Preserve the comparison: E ≤ tolerance',fontsize=12,weight='bold',color=GREEN)
f.text(.35,.37,'Score = reduction in values (%)',fontsize=12,color=INK)
f.text(.35,.31,'Floor at 0; reject with 0*. Highest score first.',fontsize=10.5,color=MUTED)
arrow(f,.669,.5,.705,.5)
f.text(.73,.75,'03  ONE DISPLAYED CHOICE',fontsize=11.5,weight='bold',color=INK)
ax=f.add_axes([.765,.39,.17,.29]);plot(ax,x,y,'bins_8',['Benign','Malignant'],(0,3.1),'Radius standard error');ax.tick_params(labelsize=9);ax.yaxis.label.set_size(9)
f.text(.74,.29,'Histogram / 96.8',fontsize=23,weight='bold',color=GREEN)
f.text(.035,.15,'Here, a histogram is displayed: 18 of 569 values retained. A binned heatmap has equal numerical merit.',fontsize=11.5,color=INK)
f.text(.035,.095,'Primary audit: 61 mean, 29 five-number, 33 binned and 4 density selections across 127 comparisons.',fontsize=11.5,color=MUTED)
f.text(.035,.04,'The score describes eligible numerical simplification, not reader accuracy. Source: UCI WDBC / 10.24432/C5DW2B.',fontsize=10,color=MUTED)
save(f,'Figure_1_Workflow')
pd.DataFrame([dict(key=key,**r) for key in DETAIL for r in ranked(key)]).to_csv(OUT/'all_149_cases_descending_scores.csv',index=False)
pd.DataFrame(rankingrows).to_csv(OUT/'illustrated_descending_scores.csv',index=False)
def diagnostics(examples,name):
 f,axes=plt.subplots(3,1,figsize=(10.2,13.4))
 f.subplots_adjust(top=.93,bottom=.055,hspace=.23)
 f.suptitle('Every score has a preservation check',x=.055,ha='left',fontsize=21,weight='bold',color=INK)
 for panel,(ax,example) in enumerate(zip(axes,examples)):
  key,dataset,feature,*_=example
  ax.axis('off');ax.set_xlim(0,1);ax.set_ylim(14.5,-2.8)
  ax.text(0,-2.15,'abc'[panel]+'  '+dataset+' / '+feature,fontsize=12,weight='bold',color=INK)
  for xpos,txt in [(0,'CONFIGURATION'),(.49,'SCORE'),(.63,'SIZE'),(.78,'E / tolerance'),(.96,'STATUS')]:
   ax.text(xpos,-.85,txt,fontsize=10,color=MUTED,ha='left' if xpos==0 else 'right',weight='bold')
  for i,r in enumerate(ranked(key)):
   col=GREEN if i==0 else (BLUE if r['qualifies'] else MUTED)
   if i==0:ax.axhspan(i-.43,i+.43,color='#e6f2ee',zorder=-1)
   ax.text(0,i,f'{i+1:02d}  '+label(r['configuration']),fontsize=10,color=col,va='center')
   for xpos,txt in [(.49,f"{r['score']:.1f}"),(.63,str(r['N'])),(.78,f"{r['discrepancy_ratio']:.3f}"),(.96,'Qualifies' if r['qualifies'] else 'Does not qualify')]:
    ax.text(xpos,i,txt,fontsize=10,color=col,ha='right',va='center')
 f.text(.055,.029,'E / tolerance ≤ 1 qualifies. Score credits retained-value reduction only after this preservation check passes.',fontsize=10,color=INK)
 f.text(.055,.013,'Raw observations retain every value and score 0. Scores are conditional on the declared target, tolerance and size contract.',fontsize=9.5,color=MUTED)
 save(f,name)
diagnostics(SUCCESS,'Figure_S5_DetailedScores')
diagnostics(LIMITS,'Figure_S6_DetailedScores')
from pypdf import PdfWriter
writer=PdfWriter()
for name in ['Figure_1_Workflow','Figure_2_Improvement','Figure_3_Limits']:writer.append(OUT/(name+'.pdf'))
writer.write(OUT/'Three_Figure_Story.pdf')

pd.DataFrame(allrows).to_csv(OUT/"figure_values_and_sources.csv",index=False)
pd.DataFrame(rankingrows).to_csv(OUT/"all_configuration_scores_and_order.csv",index=False)

family_rows=[];encoding_rows=[]
for key in DETAIL:
 result=chart_rows(key)
 family_rows.extend(dict(key=key,**r) for r in result['families'])
 encoding_rows.extend(dict(key=key,**r) for r in result['settings'])
pd.DataFrame(family_rows).to_csv(OUT/'all_149_cases_15_chart_families.csv',index=False)
pd.DataFrame(encoding_rows).to_csv(OUT/'all_149_cases_21_encoding_settings.csv',index=False)
pd.DataFrame([dict(catalogue_id=i+1,chart_id=a,chart=b,purpose=c,contract=d,numerical_mode=e) for i,(a,b,c,d,e) in enumerate(CATALOGUE)]).to_csv(OUT/'chart_catalogue_15.csv',index=False)

# A shared-data atlas makes the new encoding contracts inspectable.
key='WDBC__10';c,x,y,d,a,w,g=data(key)
family_map={r['chart_id']:r for r in chart_rows(key)['families']}
f,axs=plt.subplots(2,4,figsize=(14,8));f.subplots_adjust(left=.065,right=.965,top=.84,bottom=.12,wspace=.44,hspace=.65)
f.suptitle('Seven eligible chart families, one declared comparison',x=.045,ha='left',fontsize=21,weight='bold',color=INK)
f.text(.045,.9,'Same WDBC radius-standard-error observations / Best setting within each family / Equivalent numerical optima remain tied',fontsize=11,color=MUTED)
for idx,ident in enumerate(['bar','histogram','box','heatmap','dot','violin','interval']):
 ax=axs.flat[idx];r=family_map[ident];config=r['configuration']
 if ident=='heatmap':
  n=int(config.split('_')[1]);edges=np.linspace(min(x.min(),y.min()),max(x.max(),y.max()),n+1)
  vals=np.array([100*np.histogram(v,edges)[0]/len(v) for v in [x,y]])
  im=ax.imshow(vals,aspect='auto',extent=[edges[0],edges[-1],1.5,-.5],cmap='Blues',vmin=0,vmax=100,interpolation='nearest')
  ax.set_yticks([0,1],['A','B']);ax.set_xlabel('Measurement value');f.colorbar(im,ax=ax,fraction=.06,pad=.04,label='Group (%)')
 elif ident=='interval':
  for j,v,col in [(0,x,BLUE),(1,y,ORANGE)]:
   q=np.quantile(v,[0,.25,.5,.75,1]);ax.vlines(j,q[0],q[4],color=col,lw=1.2);ax.vlines(j,q[1],q[3],color=col,lw=5);ax.plot(j,q[2],'o',color=INK,ms=4)
  ax.set_xticks([0,1],['A','B']);ax.set_xlim(-.5,1.5);ax.set_ylim(0,3.1);ax.set_ylabel('Measurement value')
 else:
  atlas_limits=(0,3.1)
  if config.startswith('density_'):
   sc=scale(x,y);bw=max(np.std(x,ddof=1)*len(x)**(-.2),np.std(y,ddof=1)*len(y)**(-.2),.01*sc)
   atlas_limits=(min(0,x.min()-4*bw,y.min()-4*bw),max(x.max(),y.max())+4*bw)
  plot(ax,x,y,config,['A','B'],atlas_limits,'Measurement value')
 ax.set_title('abcdefg'[idx]+'  '+r['chart'],loc='left',fontsize=12,weight='bold',color=GREEN if r['display_selected'] else INK,pad=22)
 setting={'means':'2 group means','five_number':'5 quantiles/group','raw':'all observations'}.get(config,config.replace('bins_','bins: ').replace('density_','grid points: '))
 ax.text(0,1.025,f"Score {r['score']:.1f}"+('' if r['qualifies'] else '*')+' / '+setting,transform=ax.transAxes,fontsize=8.5,color=MUTED)
 ax.tick_params(labelsize=9);ax.xaxis.label.set_size(9);ax.yaxis.label.set_size(9)
ax=axs.flat[7];ax.axis('off');ax.text(0,1.15,'h  Other tasks: excluded',fontsize=12,weight='bold',color=INK,transform=ax.transAxes)
ax.text(0,.96,'Line • Area\nScatter • Bubble\nPie • Stacked bar\nTreemap • Choropleth',va='top',fontsize=11,linespacing=1.7,color=MUTED,transform=ax.transAxes)
ax.text(0,.15,'No scores assigned.\nSee task contracts in Table S3.',va='top',fontsize=10,color=MUTED,transform=ax.transAxes)
f.text(.045,.045,'A: benign (n=357). B: malignant (n=212). * Does not preserve the contrast within tolerance. Intervals show variability, not confidence.',fontsize=10,color=MUTED)
f.text(.045,.017,'Source: UCI WDBC / 10.24432/C5DW2B. Encoding ties are numerical equivalence, not evidence of equal human reading performance.',fontsize=10,color=MUTED)
save(f,'Figure_S7_ChartEncodings')
