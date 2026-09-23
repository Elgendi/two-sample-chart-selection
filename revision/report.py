from pathlib import Path
import json
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from model import frontier,choose
P=Path(__file__).resolve().parents[1];R=P/'revision/results';F=P/'revision/figures';F.mkdir(exist_ok=True)
a=pd.read_csv(R/'audit.csv');primary=a[a.primary];s=pd.read_csv(R/'simulation_cases.csv',keep_default_na=False);ss=pd.read_csv(R/'simulation_summary.csv',index_col=0)
cases=json.loads((P/'data/derived/comparisons.json').read_text());D=json.loads((R/'details.json').read_text())
colors={'Means':'#287a9e','Five-number':'#df9230','Binned':'#319786','Density':'#9d6cae','Observations':'#687782'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.titlesize':11,'axes.titleweight':'bold','axes.labelsize':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none','axes.grid':False,'savefig.facecolor':'white'})
def panel(ax,label,title):ax.set_title(f'{label}  {title}',loc='left',pad=13)
def save(fig,name):fig.savefig(F/f'{name}.pdf',bbox_inches='tight');fig.savefig(F/f'{name}.png',dpi=170,bbox_inches='tight');plt.close(fig)
def finish(fig,title):fig.suptitle(title,x=.07,ha='left',fontsize=15,fontweight='bold',y=.995)
# 1 actual data; no invented example values
c=next(c for c in cases if c['dataset']=='WDBC' and c['feature']=='mean radius');x=np.array(c['x']);y=np.array(c['y']);dd=D[c['key']];rr=dd['candidates'];tau=dd['tolerance'];scale=float(primary.set_index('key').loc[c['key'],'scale'])
fig,axs=plt.subplots(2,2,figsize=(10,7.3));fig.subplots_adjust(hspace=.52,wspace=.32,top=.89,bottom=.13)
ax=axs[0,0];rng=np.random.default_rng(7)
for i,v in enumerate([x,y]):ax.scatter(i+rng.uniform(-.13,.13,len(v)),v,s=5,alpha=.35,color=['#287a9e','#de7835'][i],rasterized=True)
ax.set_xticks([0,1],['Benign\nn=357','Malignant\nn=212']);ax.set_ylabel('Mean radius (source units)');panel(ax,'a','Start with the observations')
ax=axs[0,1];p=np.linspace(.05,.95,901);delta=np.quantile(y,p)-np.quantile(x,p);box=np.interp(p,[0,.25,.5,.75,1],np.quantile(y,[0,.25,.5,.75,1])-np.quantile(x,[0,.25,.5,.75,1]))
ax.plot(p,delta,color='#172f42',label='Empirical contrast',lw=2);ax.axhline(y.mean()-x.mean(),color=colors['Means'],label='Means',ls='--');ax.plot(p,box,color=colors['Five-number'],label='Five-number',ls=':');ax.set_xlabel('Quantile rank');ax.set_ylabel('Group B minus group A');ax.legend(frameon=False,fontsize=8);panel(ax,'b','Specify what must survive')
ax=axs[1,0]
for name in colors:
 subset=[r for r in rr if r['representation']==name];ax.scatter([r['N'] for r in subset],[r['error'] for r in subset],label=name,color=colors[name],s=35,zorder=3)
fr=frontier(rr);ax.scatter([r['N'] for r in fr],[r['error'] for r in fr],s=85,facecolors='none',edgecolors='#172f42',lw=1)
ax.axhline(tau,color='#d05b46',ls='--',label=f'Tolerance = {tau:.2f}');ax.set_xscale('log');ax.set_xlabel('Retained scalar values');ax.set_ylabel('Maximum contrast error');ax.legend(fontsize=7,frameon=False,ncol=2);panel(ax,'c','Inspect the error–size frontier')
ax=axs[1,1];ts=np.geomspace(.025,4,250);w=[choose(rr,t*scale) for t in ts];ax.step(ts,[r['N'] for r in w],where='post',color='#172f42')
for name in colors:
 ix=np.array([r['representation']==name for r in w]);ax.scatter(ts[ix],[r['N'] for i,r in enumerate(w) if ix[i]],s=5,color=colors[name])
ax.axvline(tau/scale,color='#d05b46',ls='--');ax.set_xscale('log');ax.set_yscale('log');ax.set_xlabel('Allowed error / pooled scale');ax.set_ylabel('Minimum qualifying size');panel(ax,'d','See when simplification is allowed')
fig.text(.07,.025,'Representation first. Encoding second. A histogram and a binned heatmap retain the same payload.',fontsize=10,color='#172f42');finish(fig,'How much detail does the comparison need?');save(fig,'Fig1')
#2 aggregate audit
fig,axs=plt.subplots(2,2,figsize=(10,8));fig.subplots_adjust(hspace=.67,wspace=.38,top=.90,bottom=.14)
ax=axs[0,0];tab=pd.crosstab(primary.dataset,primary.detail).reindex(columns=['Mean','Quartiles','Distribution'],fill_value=0);tab.plot.barh(stacked=True,ax=ax,color=[colors['Means'],colors['Five-number'],colors['Binned']],width=.75);ax.set_ylabel('');ax.set_xlabel('Feature comparisons');ax.legend(frameon=False,fontsize=7,ncol=3,loc='upper center',bbox_to_anchor=(.5,-.20));panel(ax,'a','127 comparisons · nine resources')
cv=pd.read_csv(R/'bootstrap_convergence.csv').query('primary').merge(primary[['key','configuration']],on='key',suffixes=('','_ref'));cv['changed']=cv.configuration!=cv.configuration_ref
ax=axs[0,1];vals=[cv.query('B==99 and stream=="nested"').changed.sum(),cv.query('B==499 and stream=="nested"').changed.sum(),cv.query('stream=="independent"').changed.sum()];bars=ax.bar(['99 draws','499 draws','999 draws\nnew stream'],vals,color='#287a9e',width=.55);ax.bar_label(bars,padding=3);ax.set_ylim(0,6);ax.set_ylabel('Changed configurations / 127');ax.yaxis.set_major_locator(MaxNLocator(integer=True));panel(ax,'b','Monte Carlo variability is modest')
se=pd.read_csv(R/'sensitivity.csv').query('primary').merge(primary[['key','configuration']],on='key',suffixes=('','_ref'));se['changed']=se.configuration!=se.configuration_ref
names=['percentile_0.8','percentile_0.9','percentile_0.99','band_0.01_0.99','band_0.1_0.9'];labels=['80th percentile','90th percentile','99th percentile','1st–99th ranks','10th–90th ranks'];vals=[se[se.setting==n].changed.sum() for n in names];ax=axs[1,0];bars=ax.barh(labels,vals,color='#319786');ax.bar_label(bars,padding=3);ax.set_xlim(0,48);ax.set_xlabel('Changed configurations / 127');ax.invert_yaxis();panel(ax,'c','Resolution choices matter more')
paths=pd.read_csv(R/'resolution_paths.csv').query('primary');pt=pd.crosstab(paths.resolution,paths.representation).reindex(columns=list(colors),fill_value=0);ax=axs[1,1];ax.stackplot(pt.index,*[pt[k] for k in colors],labels=list(colors),colors=list(colors.values()),alpha=.9);ax.set_xscale('log');ax.set_ylim(0,127);ax.set_xlabel('Fixed tolerance / pooled scale');ax.set_ylabel('Selected comparisons');ax.legend(frameon=False,fontsize=7,ncol=2,loc='upper center',bbox_to_anchor=(.5,-.27));panel(ax,'d','Report a path, not only one winner')
finish(fig,'Which assumptions change the answer?');save(fig,'Fig2')
#3 simulations
method_order=['Adaptive','Means','Five-number','8-bin','8-grid density','Raw'];mshort=['Adaptive','Means','Five-number','8-bin','8-grid density','Raw'];modes=['null','location','spread','bimodal','skew','heavy_tail','contamination','discrete','imbalance'];mlabel=['Null','Location','Spread','Bimodal','Skew','Heavy tail','Contamination','Discrete','Imbalance']
fig,axs=plt.subplots(2,2,figsize=(10.5,8.3));fig.subplots_adjust(hspace=.60,wspace=.42,top=.90,bottom=.13)
ax=axs[0,0];mat=s.groupby(['method','scenario']).passes_frozen.mean().unstack().loc[method_order,modes]*100;im=ax.imshow(mat,cmap='Blues',vmin=0,vmax=100,aspect='auto');ax.set_xticks(range(9),mlabel,rotation=55,ha='right',fontsize=7);ax.set_yticks(range(6),mshort,fontsize=8)
for i in range(6):
 for j in range(9):ax.text(j,i,f'{mat.iloc[i,j]:.0f}',ha='center',va='center',fontsize=7,color='white' if mat.iloc[i,j]>65 else '#172f42')
panel(ax,'a','Frozen empirical tolerance · pass %')
ax=axs[0,1];palette=['#172f42','#287a9e','#df9230','#319786','#9d6cae','#687782']
for method,col in zip(method_order,palette):
 g=s[s.method==method].groupby('n_A').population_pass.mean()*100;ax.plot(g.index,g.values,'o-',label=method,color=col,ms=4)
ax.set_xscale('log');ax.set_xticks([20,80,320],['20','80','320']);ax.set_ylim(0,100);ax.set_xlabel('Group-A sample size');ax.set_ylabel('Population pass (%)');ax.legend(fontsize=7,frameon=False,ncol=2,loc='upper left');panel(ax,'b','Known-population error · fixed budget')
ax=axs[1,0]
for method,col in zip(['Adaptive','Fixed-budget adaptive','Raw'],['#172f42','#d05b46','#687782']):
 g=s[s.method==method].groupby('n_A').N.median();ax.plot(g.index,g.values,'o-',label=method,color=col)
ax.set_xscale('log');ax.set_yscale('log');ax.set_xticks([20,80,320],['20','80','320']);ax.set_xlabel('Group-A sample size');ax.set_ylabel('Median retained values');ax.legend(frameon=False,fontsize=8);panel(ax,'c','Fidelity has a representation cost')
ax=axs[1,1];mat=s[s.method=='Adaptive'].groupby(['scenario','n_A']).passes_frozen.mean().unstack().loc[modes]*100;ax.imshow(mat,cmap='Blues',vmin=0,vmax=100,aspect='auto');ax.set_xticks(range(3),['20','80','320']);ax.set_yticks(range(9),mlabel,fontsize=8);ax.set_xlabel('Group-A sample size')
for i in range(9):
 for j in range(3):ax.text(j,i,f'{mat.iloc[i,j]:.0f}',ha='center',va='center',fontsize=8,color='white' if mat.iloc[i,j]>65 else '#172f42')
panel(ax,'d','Adaptive selector · frozen pass %');finish(fig,'Preserving the sample does not recover the population');save(fig,'Fig3')
#4 costs and source anomaly
fig,axs=plt.subplots(2,2,figsize=(10,7.5));fig.subplots_adjust(hspace=.56,wspace=.35,top=.90,bottom=.10)
co=pd.read_csv(R/'cost_contracts.csv').query('primary').merge(primary[['key','configuration']],on='key',suffixes=('','_ref'));co['changed']=co.configuration!=co.configuration_ref
ax=axs[0,0];vals=[co[co.contract==c].changed.sum() for c in ['legacy_box','free_parameters','equal']];bars=ax.barh(['Add box mean markers','Count free bin parameters','Remove compactness'],vals,color=['#df9230','#319786','#687782']);ax.bar_label(bars,padding=3);ax.set_xlim(0,150);ax.set_xlabel('Changed configurations / 127');ax.invert_yaxis();panel(ax,'a','Cost is a declared preference')
c=next(c for c in cases if c['dataset']=='CKD' and c['feature']=='pot');x=np.array(c['x']);y=np.array(c['y']);rng=np.random.default_rng(43)
for ax,yy,label,title in [(axs[0,1],y,'b','CKD potassium · as recorded'),(axs[1,0],y[~np.isin(y,[39,47])],'c','Sensitivity · two values excluded')]:
 for i,v in enumerate([x,yy]):ax.scatter(i+rng.uniform(-.15,.15,len(v)),v,s=7,alpha=.4,color=['#287a9e','#de7835'][i],rasterized=True)
 ax.set_xticks([0,1],[f'Non-CKD\nn={len(x)}',f'CKD\nn={len(yy)}']);ax.set_ylabel('Potassium (source units)');panel(ax,label,title);ax.text(.03,.96,'Selected: '+('32 bins' if len(yy)==167 else '4 bins')+'\nTolerance: 0.6',transform=ax.transAxes,va='top',fontsize=9)
ax=axs[1,1];u=np.arange(4.);v=u[::-1]
for i in range(4):ax.plot([0,1],[u[i],v[i]],'o-',color=plt.cm.viridis((i+.5)/4),lw=1.7)
ax.set_xticks([0,1],['Condition A','Condition B']);ax.set_ylabel('Constructed value');ax.set_ylim(-.4,4);ax.text(.03,.96,'Same marginals; different individuals',transform=ax.transAxes,va='top',fontsize=8);panel(ax,'d','Check the scientific question first');finish(fig,'A numerical pass has limits');save(fig,'Fig4')
# generated macros and tables
v=ss.loc['Adaptive'];mac={'FrozenPass':f'{100*v.frozen:.1f}','ReestimatedPass':f'{100*v.reestimated:.1f}','MedianN':f'{v.median_N:g}'};(R/'numbers.tex').write_text('\n'.join('\\newcommand{\\'+k+'}{'+str(val)+'}' for k,val in mac.items())+'\n')
lines=['\\begin{tabular}{lrrrrr}\\toprule Method & Re-est. & Frozen & Fixed & Population & Median $N$\\\\\\midrule']
for name in ['Adaptive','Fixed-budget adaptive','Means','Five-number','8-bin','8-grid density','Raw']:
 r=ss.loc[name];lines.append(f"{name} & {r.reestimated*100:.1f} & {r.frozen*100:.1f} & {r.fixed*100:.1f} & {r.population*100:.1f} & {r.median_N:g}"+r'\\')
lines.append(r'\bottomrule\end{tabular}');(R/'simulation_table.tex').write_text('\n'.join(lines))
def esc(x):return str(x).replace('_',r'\_').replace('%',r'\%').replace('&',r'\&')
lines=[]
for status,df in [('Primary audit',primary),('Excluded exploratory audit: Parkinsons',a[~a.primary])]:
 lines.extend([r'\subsection*{'+status+'}',r'\small',r'\begin{longtable}{p{1.95cm}p{4.25cm}rrp{1.7cm}p{2.1cm}rr}',r'\toprule Resource & Variable & $n_A$ & $n_B$ & Detail & Selected config. & $N$ & Agreement\\\midrule\endhead'])
 for _,r in df.iterrows():lines.append(' & '.join([esc(r.dataset),esc(r.feature),str(r.n_A),str(r.n_B),r.detail,esc(r.configuration),str(r.N),f'{r.agreement:.2f}'+('*' if r.provisional else '')])+r'\\')
 lines.extend([r'\bottomrule\end{longtable}',r'\normalsize'])
(R/'variables.tex').write_text('\n'.join(lines))
# Numerical ties are emitted explicitly; simulation uses deterministic catalogue order.
optimal=[]
for key,dd in D.items():
 w=choose(dd['candidates'],dd['tolerance']);ties=[r['configuration'] for r in dd['candidates'] if r['N']==w['N'] and np.isclose(r['error'],w['error'],rtol=0,atol=1e-10)];optimal.append(dict(key=key,configurations=';'.join(ties),count=len(ties)))
pd.DataFrame(optimal).to_csv(R/'optimal_sets.csv',index=False)
print(ss.to_string());print('Figures and tables complete')
