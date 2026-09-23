"""Readable illustrative figures; no alteration of scored pixels or rankings."""
import numpy as np,pandas as pd
from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from observer import prepare,render,decode,P
GOOD_KEYS=['WDBC__29','HAR__29','Cleveland__04']
LIMIT_KEYS=['Wrist__00','BIDMC__00']
TITLES={'WDBC__29':'Breast tumour / Fractal dimension (worst)','HAR__29':'Smartphone activity / Gyroscope-jerk variability','Cleveland__04':'Heart disease / ST depression (oldpeak)','Wrist__00':'Wrist exercise / Mean heart rate','BIDMC__00':'Bedside monitoring / Mean heart rate'}
INSIGHTS={'WDBC__29':'Larger differences emerge toward the upper tail.','HAR__29':'Walking has a much wider spread.','Cleveland__04':'Differences increase from the lower to the upper end.','Wrist__00':'The best choice is unchanged: keep the mean bars.','BIDMC__00':'A more detailed chart adds only 2.64 score points.'}
NAVY='#183749';TEAL='#008479';BLUE='#267ea5';ORANGE='#df7836';GREY='#77838b';FAINT='#e5ecef'
def make_story(cases,fam,out,keys,limited=False):
 W=10;H=1.6+3.85*len(keys);fig=plt.figure(figsize=(W,H))
 def ax_at(x,y,w,h):return fig.add_axes([x/W,y/H,w/W,h/H])
 def txt(x,y,s,**kw):return fig.text(x/W,y/H,s,**kw)
 def ranks(key):return fam[(fam.key==key)&(fam.H==256)].sort_values(['score','family'],ascending=[False,True],kind='stable')
 def setting(r):
  if r.family in ['Histogram','Heatmap']:return r.setting+' bins'
  if r.family=='Violin plot':return r.setting+' grid points'
  return {'means':'means','raw':'raw observations','five':'five-number'}[r.setting]
 title='When changing the chart helps' if not limited else 'When changing the chart adds little'
 txt(.35,H-.34,title,fontsize=18,fontweight='bold',color=NAVY)
 txt(.35,H-.62,'Large numerical gains over mean bars' if not limited else 'A high-scoring baseline leaves little room for improvement',fontsize=11,color=GREY)
 handles=[Line2D([],[],color=NAVY,marker='o',ms=3,lw=1.4),Line2D([],[],color=GREY,ls='--',lw=1.4),Line2D([],[],color=TEAL,marker='s',ms=3,lw=1.4)]
 fig.legend(handles,['True difference','Recovered from mean bars','Recovered from selected chart'],loc='center left',bbox_to_anchor=(.035,(H-.89)/H),frameon=False,ncol=3,fontsize=8.5,handlelength=2,columnspacing=1.4)
 audit=[]
 for i,key in enumerate(keys):
  c=cases[key];d=ranks(key);best=d.iloc[0];base=d[d.family=='Bar chart'].iloc[0];ctx=prepare(c['x'],c['y']);top=H-1.25-i*3.85
  txt(.35,top,chr(97+i)+'  '+TITLES[key],fontsize=12.5,fontweight='bold',color=NAVY)
  txt(.50,top-.25,f"A: {c['labels'][0]} (n={len(c['x'])})",fontsize=9,color=BLUE)
  txt(3.30,top-.25,f"B: {c['labels'][1]} (n={len(c['y'])})",fontsize=9,color=ORANGE)
  txt(.52,top-.62,f'Mean bars  {base.score:.2f}',fontsize=12,fontweight='bold',color=GREY)
  txt(2.93,top-.62,'→',fontsize=18,color=GREY)
  txt(3.35,top-.62,f'{best.family}  {best.score:.2f}',fontsize=12,fontweight='bold',color=TEAL)
  gain=best.score-base.score
  txt(6.42,top-.56,f'+{gain:.2f}',fontsize=20,fontweight='bold',color=TEAL if not limited else NAVY)
  txt(8.08,top-.56,'score points',fontsize=10,color=GREY)
  for x,r in [(.65,base),(3.45,best)]:
   im,spec=render(ctx,r.family,r.setting,256,0,20260920)
   ax=ax_at(x,top-2.04,2.30,1.10);ax.imshow(im,interpolation='none');ax.set_xlim(0,528);ax.set_ylim(256,0);ax.tick_params(length=0,pad=3,labelsize=8)
   for sp in ax.spines.values():sp.set_visible(False)
   if r.family in ['Histogram','Heatmap']:
    vals=[ctx['lo'],(ctx['lo']+ctx['hi'])/2,ctx['hi']]*2
    ax.set_xticks([8,127.5,247,280,399.5,519]);ax.set_xticklabels([f'{v:.2g}' for v in vals],fontsize=7)
    for j,l in enumerate(ax.get_xticklabels()):l.set_ha('left' if j in [0,3] else ('right' if j in [2,5] else 'center'))
    ax.text(.24,1.03,'A',transform=ax.transAxes,ha='center',fontsize=9,color=BLUE);ax.text(.76,1.03,'B',transform=ax.transAxes,ha='center',fontsize=9,color=ORANGE)
    ax.set_xlabel('Measurement value',fontsize=8,labelpad=3)
    if r.family=='Histogram':ax.set_yticks([247,127.5,8]);ax.set_yticklabels(['0','0.5','1']);ax.set_ylabel('Bin probability',fontsize=8)
    else:ax.set_yticks([])
   else:
    vals=plt.MaxNLocator(3).tick_values(ctx['lo'],ctx['hi']);vals=vals[(vals>=ctx['lo'])&(vals<=ctx['hi'])];ys=247-(vals-ctx['lo'])/(ctx['hi']-ctx['lo'])*239
    ax.set_yticks(ys);ax.set_yticklabels([f'{v:.3g}' for v in vals]);ax.set_ylabel('Measurement',fontsize=8,labelpad=4)
    ax.set_xticks([128,400]);ax.set_xticklabels(['A','B'],fontsize=9)
  # Recovery plots use exact empirical targets and averages of all four scored realizations.
  target=np.quantile(c['y'],P)-np.quantile(c['x'],P);decoded=[]
  for r in [base,best]:
   deltas=[]
   for pi,phase in enumerate([0,.25,.5,.75]):
    im,spec=render(ctx,r.family,r.setting,256,phase,20260920+pi);q=decode(im,spec);deltas.append(q[1]-q[0])
   deltas=np.array(deltas);actual=100/(1+np.mean(abs(deltas-target))/ctx['scale']);assert np.isclose(actual,r.score,atol=1e-10)
   decoded.append(deltas.mean(axis=0)/ctx['scale'])
  ax=ax_at(1.03,top-3.04,4.72,.64)
  ax.plot(P*100,target/ctx['scale'],'o-',color=NAVY,lw=1.4,ms=3,zorder=3)
  ax.plot(P*100,decoded[0],'--',color=GREY,lw=1.5,zorder=4)
  ax.plot(P*100,decoded[1],'s-',color=TEAL,lw=1.25,ms=3,markerfacecolor='white',zorder=5)
  ax.set_xticks([10,25,50,75,90]);ax.tick_params(labelsize=8,pad=2,length=2);ax.set_xlabel('Percentile: lower end → upper end',fontsize=8,labelpad=2)
  if limited:ax.set_ylim(-.25,.25)
  ax.set_ylabel('B − A\n(pooled SD)',fontsize=8,labelpad=3);ax.spines[['top','right']].set_visible(False);ax.yaxis.set_major_locator(plt.MaxNLocator(3));ax.grid(axis='y',color=FAINT,lw=.6)
  # Complete family ranking, fixed 0–100 bar scale, unrounded ordering.
  ax=ax_at(6.3,top-3.10,3.34,2.28);ax.set_xlim(0,1);ax.set_ylim(-.4,7.55);ax.axis('off')
  ax.text(0,7.22,'RANK / CHART',fontsize=9,color=GREY,fontweight='bold');ax.text(1,7.22,'SCORE / 100',ha='right',fontsize=9,color=GREY,fontweight='bold')
  for j,(_,r) in enumerate(d.iterrows()):
   y=6.55-j;optimal=np.isclose(r.loss,d.loss.min(),atol=1e-12,rtol=0)
   if optimal:ax.axhspan(y-.44,y+.44,color='#e4f1ed')
   color=TEAL if optimal else NAVY
   ax.text(.015,y,str(j+1) if np.isfinite(r.score) else '–',va='center',fontsize=10,color=color)
   ax.text(.11,y+.20,r.family,va='center',fontsize=10.5,color=color,fontweight='bold' if optimal else 'normal')
   ax.text(.11,y-.31,setting(r),va='center',fontsize=7.5,color=GREY)
   if np.isfinite(r.score):
    ax.plot([.66,.66+.115*r.score/100],[y,y],lw=3,color=TEAL if optimal else '#9ab0bc',solid_capstyle='round');ax.text(.99,y,f'{r.score:.3f}',ha='right',va='center',fontsize=10,color=color)
   else:ax.text(.99,y,'Failed',ha='right',va='center',fontsize=9,color=GREY)
  txt(.67,top-2.31,INSIGHTS[key],fontsize=9.2,color=NAVY)
  fig.add_artist(Line2D([.035,.965],[(top-3.55)/H]*2,transform=fig.transFigure,color=FAINT,lw=.8))
  audit.append(dict(figure=3 if limited else 2,panel=chr(97+i),key=key,selected_family=best.family,selected_setting=best.setting,baseline_score=base.score,best_score=best.score,gain=gain))
 txt(.35,.12,'Scores describe this computational observer; numerical gain is not demonstrated human-reading benefit.',fontsize=8.5,color=GREY)
 stem='Figure_3_Limits' if limited else 'Figure_2_Examples'
 for ext in ['pdf','svg','png']:
  buffer=BytesIO();fig.savefig(buffer,format=ext,bbox_inches='tight',dpi=300)
  target=out/(stem+'.'+ext);temporary=target.with_suffix('.'+ext+'.tmp');temporary.write_bytes(buffer.getvalue());temporary.replace(target)
 plt.close(fig);return audit
