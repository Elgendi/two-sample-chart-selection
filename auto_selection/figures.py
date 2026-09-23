from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
P=Path(__file__).resolve().parents[1];F=P/'figures';R=P/'auto_selection/results';F.mkdir(exist_ok=True)
cases={c['key']:c for c in json.loads((P/'data/derived/comparisons.json').read_text())};results=json.loads((R/'details.json').read_text())
BLUE='#287DA8';ORANGE='#DE7135';INK='#17354B';TEAL='#177D68';MUTED='#627585';COLORS=[BLUE,ORANGE]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'text.color':INK,'axes.labelcolor':INK,'axes.titlecolor':INK,'svg.fonttype':'none','pdf.fonttype':42})
def save(fig,name):
 for ext in ['pdf','svg','png']:fig.savefig(F/(name+'.'+ext),dpi=210,facecolor='white')
 plt.close(fig)
def raw(ax,c):
 rng=np.random.default_rng(33)
 for i,k in enumerate(['x','y']):
  v=np.array(c[k]);ax.scatter(i+rng.uniform(-.15,.15,len(v)),v,s=5,color=COLORS[i],alpha=.3,edgecolors='none')
 ax.set_xticks([0,1],['A','B']);ax.set_xlim(-.5,1.5)
def render(ax,c,result,family=None):
 family=family or ('Bar' if 'Bar' in result['selected'] else 'Box' if 'Box' in result['selected'] else 'Histogram' if 'Histogram' in result['selected'] else 'Dot')
 x=np.array(c['x']);y=np.array(c['y']);chosen=next(r for r in result['families'] if r['family']==family)
 if family=='Bar':
  means=[x.mean(),y.mean()];ax.bar([0,1],means,color=COLORS,width=.55);ax.set_xticks([0,1],['A','B'])
  for i,m in enumerate(means):ax.annotate(f'{m:.2f}',(i,m),xytext=(0,4),textcoords='offset points',ha='center',fontsize=10)
  ax.margins(y=.2)
 elif family=='Box':
  b=ax.boxplot([x,y],positions=[0,1],patch_artist=True,widths=.45,whis=(0,100),showmeans=True,meanprops={'marker':'o','markerfacecolor':'white','markeredgecolor':INK,'markersize':4},medianprops={'color':INK,'linewidth':1.2})
  for v,col in zip(b['boxes'],COLORS):v.set_facecolor(col)
  ax.set_xticks([0,1],['A','B'])
 elif family=='Histogram':
  bins=int(chosen['configuration'].split()[0]);edges=np.linspace(min(x.min(),y.min()),max(x.max(),y.max()),bins+1)
  for v,col in zip([x,y],COLORS):ax.hist(v,bins=edges,weights=np.ones(len(v))/len(v),histtype='step',color=col,lw=1.8)
  ax.set_ylabel('Bin probability',fontsize=10);ax.set_xlabel('Measurement',fontsize=10)
 else:raw(ax,c)
 return family

def ranking(fig,result,left,top,width,step,fontsize=11):
 for j,r in enumerate(result['families']):
  yy=top-j*step;win=r['selected'];color=TEAL if win else (INK if r['score']>0 else MUTED)
  if win:fig.add_artist(FancyBboxPatch((left-.004,yy-.005),width+.012,step*.90,boxstyle='round,pad=0.002',transform=fig.transFigure,facecolor='#DDF0E8',edgecolor='none',zorder=-1))
  name={'Interval':'Error-bar / interval','Pie / donut':'Pie / donut'}.get(r['family'],r['family'])
  val=f"{r['score']:.4f}" if r['score']>0 else ('0 E' if r['status']=='exceeds tolerance' else '0 T')
  fig.text(left,yy,name,fontsize=fontsize,color=color,weight='bold' if win else 'normal');fig.text(left+width,yy,val,ha='right',fontsize=fontsize,color=color,weight='bold' if win else 'normal')

def arrow(fig,a,b):fig.add_artist(FancyArrowPatch(a,b,transform=fig.transFigure,arrowstyle='-|>',mutation_scale=24,linewidth=2,color=TEAL))
# Full four-stage workflow, fixed default objective (no mean/quartile question entered).
c=cases['WDBC__00'];r=results['WDBC__00'];fig=plt.figure(figsize=(17,8.2))
fig.text(.03,.947,'Let the data determine how much detail the chart must retain',fontsize=22,weight='bold')
fig.text(.03,.899,'DEFAULT AIM   Preserve the observed difference between two distributions at the estimated sampling resolution.',fontsize=12.5)
for left,width in [(.025,.17),(.235,.18),(.455,.25),(.755,.22)]:fig.add_artist(FancyBboxPatch((left,.235),width,.595,boxstyle='round,pad=.009',transform=fig.transFigure,facecolor='#F7FAFC',edgecolor='#DAE4EA',zorder=-4))
fig.text(.04,.784,'1  RAW SAMPLES',fontsize=12,weight='bold');fig.text(.04,.745,'No mean / quartile choice',fontsize=10.5,color=MUTED)
ax=fig.add_axes([.063,.39,.114,.28]);raw(ax,c);ax.set_ylabel('Mean radius (source units)',fontsize=10)
fig.text(.04,.292,'A: benign (357)\nB: malignant (212)',fontsize=11,linespacing=1.5)
fig.text(.25,.784,'2  DETECT REQUIRED DETAIL',fontsize=11.5,weight='bold')
fig.text(.25,.712,'Mean summary\nFails reconstruction tolerance',fontsize=11,linespacing=1.5)
fig.text(.25,.599,'Quartile summary\nFails reconstruction tolerance',fontsize=11,linespacing=1.5)
fig.text(.25,.454,'Distribution detail\nREQUIRED AT THIS RESOLUTION',fontsize=10.7,weight='bold',color=TEAL,linespacing=1.6)
fig.text(.25,.29,f'Data-derived tolerance: {r["epsilon"]:.2f}\nsource units',fontsize=10,color=MUTED)
fig.text(.47,.784,'3  SCORE ALL 15 COMMON CHARTS',fontsize=11.5,weight='bold');fig.text(.47,.746,'HIGHER SCORE IS BETTER',fontsize=11,color=TEAL)
ranking(fig,r,.474,.698,.21,.0284,10.5)
fig.text(.47,.252,'0 E: excess error · 0 T: input mismatch',fontsize=9,color=MUTED)
fig.text(.77,.784,'4  SELECTED OPTION',fontsize=12,weight='bold');fig.text(.77,.742,f'Histogram · score {r["score"]:.4f}',fontsize=13,weight='bold',color=TEAL)
ax=fig.add_axes([.80,.402,.155,.26]);render(ax,c,r)
fig.text(.77,.295,f'10 bins selected automatically.\nHeatmap ties at {r["score"]:.4f}.',fontsize=11,linespacing=1.5)
for a,b in [((.203,.54),(.226,.54)),((.427,.54),(.446,.54)),((.718,.54),(.745,.54))]:arrow(fig,a,b)
fig.text(.03,.171,'ONE SCORE   Higher = more compact after meeting tolerance. Zero = does not qualify. Keep all ties.',fontsize=13,weight='bold',color=TEAL)
fig.text(.03,.115,r'$Q(c)=\frac{1}{N_c+e_c/2}$,  where $e_c=\max_p|\widehat{\Delta}_c(p)-\Delta(p)|/\tau$.  Qualifying charts satisfy $e_c\leq1$.',fontsize=13)
fig.text(.03,.055,'Same observations and colours throughout. The method detects numerical detail requirements; it does not infer clinical importance or prove reader accuracy.',fontsize=10.5,color=MUTED)
save(fig,'Fig1_automatic_workflow')
# Three complete vertical workflows. All 15 scores shown in every example.
keys=['HeartFailure__00','HAR__05','WDBC__00'];fig=plt.figure(figsize=(16,10));fig.text(.035,.955,'Raw data → detected requirement → ranked charts → selected display',fontsize=20,weight='bold')
fig.text(.035,.918,'No question about means or quartiles is supplied. The same equation and resolution rule are applied to every pair.',fontsize=11.5,color=MUTED)
titles=['a  Heart failure · age','b  Smartphone HAR · acceleration SD','c  WDBC · mean radius']
for idx,(key,left) in enumerate(zip(keys,[.04,.37,.70])):
 c=cases[key];r=results[key];fig.text(left,.868,titles[idx],fontsize=13,weight='bold')
 ax=fig.add_axes([left+.055,.724,.20,.103]);raw(ax,c);ax.tick_params(labelsize=9);ax.set_ylabel('Raw values',fontsize=10)
 text={'Mean summary sufficient':'MEAN SUMMARY SUFFICIENT','Quartile summary sufficient':'QUARTILE SUMMARY SUFFICIENT','Distribution detail required':'DISTRIBUTION DETAIL REQUIRED'}[r['stratum']]
 fig.text(left,.680,text,fontsize=11.5,weight='bold',color=TEAL)
 fig.text(left,.648,'Rank all charts · higher is better',fontsize=10.5,color=MUTED)
 ranking(fig,r,left+.008,.613,.265,.0215,10.5)
 fig.text(left,.270,'0 E: excess error · 0 T: input mismatch',fontsize=8.5,color=MUTED)
 ax=fig.add_axes([left+.055,.083,.20,.125]);family=render(ax,c,r);ax.tick_params(labelsize=9)
 fig.text(left,.236,f'SELECTED: {family} · score {r["score"]:.4f}',fontsize=12,weight='bold',color=TEAL)
 # Exact selected sets remain visible in the ranking; no unique-winner invention.
fig.text(.035,.024,'A / B: survived / died; sitting / walking; benign / malignant. Scores measure numerical efficiency, not percentages of visual accuracy.',fontsize=10.5,color=MUTED)
save(fig,'Fig2_raw_to_chart_examples')
print('Automatic workflow figures generated.')
# Successful in-sample examples and separate limits/transfer-failure examples.
# Success is numerical: initial bars fail, selected chart passes, stratum agreement >= .8.
import pandas as pd
from model import select
AUDIT=[]

def score_row(result,family):return next(v for v in result['families'] if v['family']==family)
def after_plot(ax,c,r,family):
 x=np.asarray(c['x']);y=np.asarray(c['y']);z=score_row(r,family)
 if family=='Histogram':
  bins=int(z['configuration'].split()[0]);edges=np.linspace(min(x.min(),y.min()),max(x.max(),y.max()),bins+1)
  for v,col in zip([x,y],COLORS):ax.hist(v,bins=edges,weights=np.ones(len(v))/len(v),orientation='horizontal',histtype='step',color=col,lw=1.6)
  ax.set_xlabel('Bin probability',fontsize=9)
 else:render(ax,c,r,family)

def example_figure(specs,title,subtitle,name,footer):
 count=len(specs);fig=plt.figure(figsize=(10,3*count));fig.text(.04,.965,title,fontsize=16,weight='bold')
 fig.text(.04,.934,subtitle,fontsize=10.5,color=MUTED)
 fig.text(.065,.906,'BEFORE: mean bars',fontsize=12,weight='bold');fig.text(.365,.906,'SELECTION / CHECK',fontsize=11,weight='bold');fig.text(.72,.906,'AFTER: chart evaluated',fontsize=11.5,weight='bold')
 spacing=.82/count;h=spacing*.52
 for i,spec in enumerate(specs):
  key=spec['key'];c=cases[key];r=results[key];family=spec['family'];head=.872-spacing*i;bottom=head-spacing*.73
  before=score_row(r,'Bar');after=score_row(r,family);col=TEAL if after['qualifies'] else '#A45325'
  fig.text(.04,head,chr(97+i)+'  '+spec['title'],fontsize=12.5,weight='bold')
  ax=fig.add_axes([.075,bottom,.18,h]);render(ax,c,r,'Bar');ax.tick_params(labelsize=9);ax.set_ylabel(c['unit'],fontsize=9)
  x=np.asarray(c['x']);y=np.asarray(c['y']);lo=min(0,x.min(),y.min());hi=max(0,x.max(),y.max());pad=.08*max(hi-lo,1);ylim=(lo-pad if lo<0 else 0,hi+pad);ax.set_ylim(ylim)
  fig.text(.065,head-spacing*.16,f'Score {before["score"]:.4f}'+(' | fails' if not before['qualifies'] else ''),fontsize=12,weight='bold',color=TEAL if before['qualifies'] else MUTED)
  compatible=[v for v in r['families'] if v['status']!='input mismatch'][:3]
  for j,z in enumerate(compatible):
   yy=head-spacing*(.32+j*.12);cc=TEAL if z['selected'] else MUTED
   fig.text(.365,yy,z['family'],fontsize=11,weight='bold' if z['selected'] else 'normal',color=cc);fig.text(.615,yy,f'{z["score"]:.4f}',fontsize=11,ha='right',color=cc)
  fig.text(.365,head-spacing*.70,spec['note'],fontsize=9.5,color=col)
  tied=r['selected'].replace('; ',' / ');fig.text(.365,head-spacing*.79,('Tied best: ' if ';' in r['selected'] else 'Best: ')+tied,fontsize=9.2,color=col)
  ax=fig.add_axes([.745,bottom,.19,h]);after_plot(ax,c,r,family);ax.set_ylim(ylim);ax.tick_params(labelsize=9)
  fig.text(.72,head-spacing*.16,f'{family} | score {after["score"]:.4f}',fontsize=11.5,weight='bold',color=col)
  arrow(fig,(.28,bottom+h/2),(.34,bottom+h/2));arrow(fig,(.64,bottom+h/2),(.71,bottom+h/2))
  labels=c['labels'];fig.text(.07,bottom-spacing*.16,f'A: {labels[0]} (n={len(x)})   B: {labels[1]} (n={len(y)})',fontsize=8.7,color=MUTED)
  AUDIT.append(dict(figure=name,key=key,dataset=c['dataset'],feature=c['feature'],category=spec['category'],before='Bar',before_score=before['score'],before_error_ratio=before['error_ratio'],after=family,after_score=after['score'],after_error_ratio=after['error_ratio'],after_qualifies=after['qualifies'],selected_set=r['selected'],bootstrap_agreement=r['bootstrap_agreement'],ymin=ylim[0],ymax=ylim[1],same_displayed_samples=True,same_measurement_scale=True))
 fig.text(.04,.035,r'$Q=1/(N+e/2)$ if tolerance is met; otherwise $Q=0$. Higher is better within a comparison.',fontsize=10.5)
 fig.text(.04,.012,footer,fontsize=9.5,color=MUTED)
 save(fig,name)

success=[dict(key='WDBC__07',family='Box',title='WDBC | mean concave points',note='Summary detail recovered.',category='numerical_success'),dict(key='CKD__08',family='Histogram',title='Chronic kidney disease | packed cell volume',note='Distribution detail retained.',category='numerical_success'),dict(key='HAR__29',family='Box',title='Smartphone HAR | gyroscope-jerk SD, z axis',note='Between-participant spread retained.',category='numerical_success')]
for s in success:
 r=results[s['key']];assert not score_row(r,'Bar')['qualifies'] and score_row(r,s['family'])['selected'] and r['bootstrap_agreement']>=.8
example_figure(success,'Numerical success: the selected chart meets the requirement','Same observations, colours and measurement scale before and after. All 15 scores are in the data table.','Fig3_before_after','Selected illustrations of reconstruction improvement; human visual benefit has not been measured.')

limits=[dict(key='ILPD__01',family='Histogram',title='Liver bilirubin | NUMERICAL PASS, COMPRESSED DISPLAY',note='Visual advantage remains untested.',category='visual_benefit_unmeasured'),dict(key='Parkinsons__08',family='Box',title='Voice shimmer | PROVISIONAL RECOMMENDATION',note=f'Stratum agreement: {results["Parkinsons__08"]["bootstrap_agreement"]:.2f}.',category='provisional'),dict(key='BIDMC__00',family='Bar',title='BIDMC heart rate | NO CHANGE REQUIRED',note='Initial bars already qualify.',category='unchanged'),dict(key='CKD__06',family='Dot',title='Kidney potassium | EXTREMES COMPRESS THE DISPLAY',note='Central cloud remains compressed.',category='extremes_compress_display')]
example_figure(limits,'Limits of numerical selection in real database examples','All four rows use database observations. Same samples, colours and measurement limits within each row.','Fig4_limits_and_failure','Numerical qualification does not establish visual benefit; these examples do not claim transfer failure.')
pd.DataFrame(AUDIT).to_csv(R/'before_after_examples.csv',index=False)
from dataset_sources import SOURCES
mapping=[('Figure 1','main','WDBC__00'),('Figure 2','a','HeartFailure__00'),('Figure 2','b','HAR__05'),('Figure 2','c','WDBC__00')]+[('Figure 3',chr(97+i),z['key']) for i,z in enumerate(success)]+[('Figure 4',chr(97+i),z['key']) for i,z in enumerate(limits)]
source_rows=[]
for figure,panel,key in mapping:
 c=cases[key];bib,doi=SOURCES[c['dataset']]
 source_rows.append(dict(figure=figure,panel=panel,key=key,dataset=c['dataset'],feature=c['feature'],n_A=len(c['x']),n_B=len(c['y']),citation_key=bib,doi=doi,source_url='https://doi.org/'+doi,source_kind='public_database',simulated=False))
pd.DataFrame(source_rows).to_csv(R/'figure_data_sources.csv',index=False)
assert len(source_rows)==11 and all(z['key'] in cases and not z['simulated'] for z in source_rows)
print('All four figures use database observations; all 11 panels have source citations.')
