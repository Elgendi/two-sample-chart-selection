"""Task-scoped catalogue of 15 requested familiar chart families.

Only the marginal two-sample quantile-contrast task is implemented. Other
families are screened, not assigned invented scores or claimed optimized.
The list is user-specified, not an empirical worldwide popularity ranking.
"""
import math
from selection_score import score_candidates
CATALOGUE = [
 ('bar','Bar chart','Compare group means','Two group means','means'),
 ('line','Line chart','Show temporal or ordered trends','Requires an ordered-trend target; row order is not time',None),
 ('scatter','Scatter plot','Show bivariate association','Requires a joint-association target, not marginal contrast',None),
 ('pie','Pie chart','Show composition of a whole','Requires a declared part-to-whole target',None),
 ('histogram','Histogram','Compare frequency distributions','Common bins with group probabilities','bins'),
 ('box','Box plot','Compare median and spread','Five-number summary; min–max whiskers','five_number'),
 ('heatmap','Heatmap','Compare binned distributions using colour','Two-by-bin probability matrix with common bin boundaries','bins'),
 ('stacked_bar','Stacked bar chart','Compare totals and composition','Requires a declared component-composition target',None),
 ('area','Area chart','Show magnitude over an ordered domain','Requires an ordered-trend or accumulation target',None),
 ('bubble','Bubble chart','Show association with an additional magnitude','Requires a joint-association and size-variable target',None),
 ('dot','Dot plot','Compare group means or individual values','Mean dots or all raw dots; report the chosen setting','dot'),
 ('treemap','Treemap','Show hierarchical proportions','Requires a meaningful hierarchy and part-to-whole target',None),
 ('choropleth','Choropleth map','Compare values across regions','Requires geographic identifiers and a geographic target',None),
 ('violin','Violin plot','Compare distribution shapes','Sampled density on the declared grid','density'),
 ('interval','Error-bar / interval plot','Show centre and variability','Median dot, thick interquartile interval, thin min–max interval; not a confidence interval','five_number'),
]

def matches(mode,config):
    return mode is not None and (config==mode or (mode=='dot' and config in ['means','raw']) or (mode in ['bins','density'] and config.startswith(mode+'_')))

def catalogue_rankings(candidates,tolerance,n_raw):
    base=score_candidates(candidates,tolerance,n_raw)
    families=[];settings=[]
    for order,(ident,name,purpose,contract,mode) in enumerate(CATALOGUE):
        rows=[dict(r,chart_id=ident,chart=name,contract=contract,catalogue_order=order) for r in base if matches(mode,r['configuration'])]
        settings.extend(rows)
        if rows:
            best=rows[0]
            families.append(dict(best,applicable=True,applicability_reason='Implemented for the declared marginal comparison',tested_settings=len(rows)))
        else:
            families.append(dict(chart_id=ident,chart=name,contract=contract,catalogue_order=order,applicable=False,applicability_reason=contract,tested_settings=0,configuration=None,score=None,score_status='not_applicable',qualifies=None,N=None,error=None,discrepancy_ratio=None,n_raw=n_raw))
    def objective(r):
        if not r['applicable']:return (2,)
        if not math.isfinite(r['score']):return (1,)
        return (0,-r['score'],not r['qualifies'],r['N'] if r['qualifies'] else r['error'],r['error'] if r['qualifies'] else r['N'])
    families.sort(key=lambda r:(objective(r),r['catalogue_order']))
    best=objective(families[0]);last=None;rank=0
    for i,r in enumerate(families):
        key=objective(r)
        r['catalogue_id']=r['catalogue_order']+1
        r['recommendation_order']=i+1 if r['applicable'] else None
        r['display_selected']=i==0
        if r['applicable']:
            if key!=last:rank=i+1
            r['rank']=rank;r['optimal']=key==best;last=key
        else:r['rank']=None;r['optimal']=False
    return dict(task='marginal_two_sample_quantile_contrast',families=families,settings=settings,
                optimal_chart_families=[r['chart'] for r in families if r['optimal']],
                numerical_configurations=len(base),encoding_configurations=len(settings))
