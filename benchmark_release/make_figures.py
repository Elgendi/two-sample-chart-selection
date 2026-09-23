"""Publication figures generated from final result tables and unchanged scored rasters."""
from common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
V=loadmod('release_figure_v3','validation_v3/benchmark.py')
FIG=ROOT/'benchmark_release/figures';FIG.mkdir(exist_ok=True)
TEAL='#007E87';ORANGE='#C26226';NAVY='#203C4B';GRAY='#607580'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':NAVY,'text.color':NAVY,'xtick.color':GRAY,'ytick.color':GRAY,'pdf.fonttype':42,'ps.fonttype':42})
def save(fig,name):
 import io
 from PIL import Image
 for ext in ['pdf','png']:
  buf=io.BytesIO()
  fig.savefig(buf,format=ext,bbox_inches='tight',facecolor='white',dpi=180)
  data=buf.getvalue()
  if ext=='pdf':
   assert data.rstrip().endswith(b'%%EOF'),name
  else:
   Image.open(io.BytesIO(data)).verify()
  path=FIG/f'{name}.{ext}';tmp=path.with_suffix(path.suffix+'.tmp')
  tmp.write_bytes(data);tmp.replace(path)
 plt.close(fig)

PLAIN={'median':'Typical values','spread':'Spread','five':'Distribution shape','composition':'Category shares','profile':'Change over time','association':'Association'}
DETAIL={'median':'difference between medians','spread':'interquartile-range difference','five':'differences at five percentiles','composition':'proportion in each category','profile':'12 successive values','association':'correlation of paired values'}

def fig1():
 fig=plt.figure(figsize=(7.4,7.0))
 fig.text(.06,.96,'Start with the question, then test what the chart preserves',fontsize=13,weight='bold')
 fig.text(.06,.905,'Example: How do two groups differ across their distributions?',fontsize=11)
 fig.text(.06,.873,'Compare the 10th, 25th, 50th, 75th and 90th percentiles.',fontsize=10,color=GRAY)
 cases=json.loads((ROOT/'data/derived/comparisons.json').read_text());c=next(c for c in cases if c['key']=='WDBC__03');ctx=V.prepare(c['x'],c['y'])
 d=pd.read_csv(ROOT/'validation_v3/results/configurations.csv');d=d[(d.key==c['key'])&(d.task=='five')&(d.H==256)&(d.observer=='threshold')].set_index('candidate')
 rows=[('Bar chart','means','A  Group averages','Shows one average per group.','The five requested percentiles\nare not encoded.'),('Dot plot','raw','B  Individual observations','Shows the observed values.','A pixel-reading algorithm estimates\nthe five percentiles.'),('Quantile plot','five','C  Five percentile markers','Shows the five requested values.','A strong comparison chart: it directly\nencodes the information being tested.')]
 for i,(f,setting,title,line,body) in enumerate(rows):
  y=.635-i*.225
  ax=fig.add_axes([.085,y,.43,.165]);im,sp=V.render(ctx,f,setting,256,0,20260920);ax.imshow(im,interpolation='nearest');ax.set_xticks([128,400],['Benign','Malignant']);ax.tick_params(labelsize=9,pad=2)
  panel=sp['panels'][0];ax.set_yticks([panel['B']-(v-sp['lo'])/(sp['hi']-sp['lo'])*(panel['B']-panel['T']) for v in [0,1000,2000]],['0','1,000','2,000'])
  for spine in ax.spines.values():spine.set_visible(False)
  fig.text(.56,y+.142,title,fontsize=11,weight='bold');fig.text(.56,y+.105,line,fontsize=9.5);fig.text(.56,y+.062,body,fontsize=9.5,va='top',linespacing=1.4)
  loss=d.loc[f+' / '+setting,'loss'];fig.text(.56,y-.009,f'Recovery error: {loss:.4f}',fontsize=11,color=TEAL,weight='bold')
 fig.text(.018,.48,'Cell-nucleus area (source units)',rotation=90,ha='center',va='center',fontsize=9)
 fig.text(.06,.085,'Lower error means a more accurate numerical answer from the pixels.',fontsize=10,weight='bold')
 fig.text(.06,.045,'Next test: choose at one display size, freeze the choice, and compare it with\na strong default at a different display size. See Figure 3.',fontsize=10,linespacing=1.4,va='top')
 save(fig,'Figure_1_Question_to_test')

def fig2():
 d=pd.read_csv(OUT/'strong_default_summary.csv');fig=plt.figure(figsize=(7.4,7.6))
 fig.text(.04,.965,'Does choosing a chart for each case improve accuracy?',fontsize=13,weight='bold')
 fig.text(.04,.93,'Comparison: one strong default versus a chart chosen for each case.',fontsize=10)
 fig.text(.04,.901,'Both choices are fixed before testing at the changed display.',fontsize=10)
 fig.text(.37,.858,'Default has lower error',fontsize=9,color=ORANGE)
 fig.text(.72,.858,'Selection has lower error',fontsize=9,color=TEAL)
 for i,task in enumerate(TASKS):
  y=.75-i*.112;ax=fig.add_axes([.38,y,.56,.075]);q=d[d.task==task].set_index('observer')
  limit=max(abs(q[['ci_low','ci_high','gain']].to_numpy()[np.isfinite(q[['ci_low','ci_high','gain']].to_numpy())]))*1000*1.18
  ax.set_xlim(-limit,limit);ax.axvspan(-limit,0,color=ORANGE,alpha=.055);ax.axvspan(0,limit,color=TEAL,alpha=.055);ax.axvline(0,color=GRAY,lw=.8)
  for j,(ob,color,marker) in enumerate([('hard',NAVY,'o'),('soft',TEAL,'s')]):
   r=q.loc[ob];x=1000*r.gain
   if np.isfinite(r.ci_low):ax.errorbar(x,j,xerr=[[x-1000*r.ci_low],[1000*r.ci_high-x]],fmt=marker,color=color,capsize=3,ms=5)
   else:ax.plot(x,j,marker,color=color,ms=5)
  ax.set_ylim(1.6,-.6);ax.set_yticks([0,1],['Reader 1','Reader 2']);ax.tick_params(axis='both',labelsize=8);ax.set_xticks([-limit/1.18,0,limit/1.18]);ax.set_xticklabels([f'{-limit/1.18:.3g}','0',f'{limit/1.18:.3g}']);ax.spines['left'].set_visible(False)
  fig.text(.04,y+.047,f'{chr(65+i)}  '+PLAIN[task],fontsize=11,weight='bold');fig.text(.04,y+.022,DETAIL[task],fontsize=8.5,color=GRAY)
  r=q.iloc[0];unit='patients' if task=='association' else 'sources';fig.text(.04,y-.002,f'{int(r.cases)} cases; {int(r.clusters)} {unit}',fontsize=8.5,color=GRAY)
 fig.text(.38,.125,'Gain = default error minus selected-chart error',fontsize=9)
 fig.text(.04,.079,'Dots / squares: average gain. Lines: descriptive 95% intervals.',fontsize=9.5)
 fig.text(.04,.048,'Each row has its own scale (error units × 1,000). Reader 1: hard-color algorithm;\nReader 2: soft-color algorithm. Two profile sources: no interval estimated.',fontsize=9,linespacing=1.5,va='top')
 save(fig,'Figure_2_Strong_defaults')

def fig3():
 geom=pd.read_csv(OUT/'geometry_summary.csv');old=pd.read_csv(ROOT/'task_first/results/summary.csv');old=old[(old.task=='composition')&(old.kind=='empirical')&(old.H==256)&(old.observer=='hard')].set_index('family');geo=geom[(geom.kind=='empirical')&(geom.H==256)].set_index('family');families=['Bar chart','Pie chart','Donut chart','Stacked bar']
 fig=plt.figure(figsize=(7.4,5.5));fig.text(.05,.95,'The way pixels are read changes which chart ranks best',fontsize=13,weight='bold')
 fig.text(.05,.897,'Same 24 cases. Same chart images. Two image-reading algorithms.',fontsize=10)
 ax=fig.add_axes([.19,.27,.74,.49]);y=np.arange(4)
 for off,data,color,label in [(-.18,old,NAVY,'Count colored pixels'),(.18,geo,TEAL,'Measure angles and lengths')]:
  vals=[int(data.loc[f,'wins']) for f in families];ax.barh(y+off,vals,height=.3,color=color,label=label)
  for yy,v in zip(y+off,vals):ax.text(v+.25,yy,str(v),va='center',fontsize=10,weight='bold')
 ax.set_yticks(y,['Bars','Pie','Donut','Stacked bar']);ax.invert_yaxis();ax.set_xlim(0,24);ax.set_xticks([0,6,12,18,24]);ax.set_xlabel('Number of cases in which the chart is best (including ties)',fontsize=10);ax.legend(loc='lower left',bbox_to_anchor=(-.19,1.04),frameon=False,ncol=2,fontsize=10);ax.spines['left'].set_visible(False);ax.tick_params(axis='y',length=0);ax.grid(axis='x',alpha=.12);ax.set_axisbelow(True)
 fig.text(.05,.12,'Ties count for every chart tied for best, so totals can exceed 24.',fontsize=10)
 shared=int(pd.read_csv(OUT/'geometry_agreement.csv').query("kind == 'empirical' and H == 256").any_shared.sum())
 fig.text(.05,.065,f'Only {shared} of 24 cases share a best-ranked chart between the algorithms.\nThese algorithms test numerical recovery; neither measures human understanding.',fontsize=9.5,linespacing=1.5,va='top')
 save(fig,'Figure_3_Decoder_dependence')

def fig4():
 d=pd.read_csv(OUT/'new_synthetic_policies.csv');fig=plt.figure(figsize=(7.4,6.9))
 fig.text(.04,.96,'On new synthetic data, selection can help, tie or hurt',fontsize=13,weight='bold')
 fig.text(.04,.918,'How often does choosing a chart for each case beat the frozen default?',fontsize=10)
 colors=[ORANGE,'#E0E5E8',TEAL];labels=['Default better','Tied','Selection better']
 for i,(color,label) in enumerate(zip(colors,labels)):
  fig.add_artist(plt.Rectangle((.08+i*.31,.866),.022,.02,transform=fig.transFigure,color=color));fig.text(.111+i*.31,.867,label,fontsize=10)
 for i,task in enumerate(TASKS):
  y=.746-i*.103;ax=fig.add_axes([.4,y,.55,.080]);q=d[d.task==task]
  for j,ob in enumerate(['hard','soft']):
   vals=q[q.observer==ob].gain.to_numpy();assert np.isfinite(vals).all();counts=[int((vals < -1e-12).sum()),int((abs(vals)<=1e-12).sum()),int((vals>1e-12).sum())];left=0
   for count,color in zip(counts,colors):
    width=count/len(vals)*100;ax.barh(j,width,left=left,color=color,height=.78,edgecolor='white',linewidth=.5)
    if count:ax.text(left+width/2,j,str(count),ha='center',va='center',fontsize=9,color=NAVY if color==colors[1] else 'white',weight='bold')
    left+=width
  ax.set_xlim(0,100);ax.set_ylim(1.6,-.6);ax.set_yticks([0,1],['Reader 1','Reader 2']);ax.tick_params(axis='y',length=0,labelsize=8);ax.set_xticks([])
  for sp in ax.spines.values():sp.set_visible(False)
  fig.text(.04,y+.032,f'{chr(65+i)}  '+PLAIN[task],fontsize=11,weight='bold');fig.text(.04,y+.005,f'{len(q[q.observer=="hard"])} new cases',fontsize=9,color=GRAY)
 fig.text(.04,.125,'Numbers inside bars are case counts; each full bar represents all cases.',fontsize=10)
 fig.text(.04,.080,'Counts show frequency; Supplementary Figure S2 shows error magnitudes.',fontsize=9.5)
 fig.text(.04,.040,'Reader 1: hard-color algorithm. Reader 2: soft-color algorithm. Ties: |gain| ≤ 10⁻¹².',fontsize=9)
 save(fig,'Figure_4_Synthetic_transfer')
def synthetic_detail():
 d=pd.read_csv(OUT/'new_synthetic_policies.csv');fig,axs=plt.subplots(2,3,figsize=(7.3,6.3));fig.subplots_adjust(hspace=1.0,wspace=.48,top=.78,bottom=.18)
 rng=np.random.default_rng(22)
 for i,(task,ax) in enumerate(zip(TASKS,axs.flat)):
  ax.axvline(0,color='#A1AEB4',lw=1);q=d[d.task==task]
  for j,(ob,color) in enumerate([('hard',TEAL),('soft',ORANGE)]):
   vals=q[q.observer==ob].gain.dropna().to_numpy()*1000;ax.scatter(vals,j+rng.uniform(-.12,.12,len(vals)),s=9,alpha=.5,color=color);ax.plot(vals.mean(),j,'D',color=color,ms=6,mec='white',mew=.5)
  ax.set_yticks([0,1],['Hard','Soft']);ax.set_ylim(1.45,-.45);ax.set_title(f'{chr(97+i)}  '+{'median':'Median','spread':'Spread','five':'Five gaps','composition':'Composition','profile':'Profile','association':'Association'}[task],loc='left',fontsize=10,weight='bold',y=1.22);ax.set_xlabel(r'Gain ($10^{-3}$ loss units)',fontsize=8);ax.tick_params(axis='x',labelsize=8);ax.grid(axis='x',alpha=.1)
  ax.text(0,1.06,f'{len(q[q.observer=="hard"])} new synthetic cases',transform=ax.transAxes,fontsize=8,color=GRAY)
 fig.suptitle('New synthetic cases challenge frozen defaults',x=.125,ha='left',fontsize=13,weight='bold');fig.text(.125,.90,'One empirical-trained default per task; case selection at 256, testing at 384 pixels.',fontsize=9)
 fig.text(.125,.025,'Dots: individual paired gains. Diamonds: means. Positive favors case selection.\nScales differ by task. Simulation scenarios are stress tests, not population samples.',fontsize=8.5)
 save(fig,'Figure_S3_Synthetic_detail')
if __name__=='__main__':
 import subprocess
 # Regenerate the two labeled supplementary galleries from fresh trial results.
 for script in ['task_first/report.py','task_first/figures.py','reader_figures/make_scoring_example.py']:
  subprocess.run([sys.executable,str(ROOT/script)],cwd=ROOT,check=True)
 fig1();fig2();fig3();fig4();synthetic_detail()
