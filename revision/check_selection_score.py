"""Verify score/selector equivalence and the scientifically relevant boundaries."""
from pathlib import Path
import json, math
import pandas as pd
from selection_score import score_candidates
P=Path(__file__).resolve().parents[1]
details=json.loads((P/'revision/results/details.json').read_text())
cases={c['key']:c for c in json.loads((P/'data/derived/comparisons.json').read_text())}
audit=pd.read_csv(P/'revision/results/audit.csv').set_index('key')
finite=unavailable=0
for key,d in details.items():
    n=len(cases[key]['x'])+len(cases[key]['y'])
    rows=score_candidates(d['candidates'],d['tolerance'],n)
    assert len(rows)==14
    assert rows[0]['configuration']==audit.loc[key].configuration,key
    assert next(r for r in rows if r['configuration']=='raw')['score']==0
    nums=[r['score'] for r in rows if math.isfinite(r['score'])]
    assert nums==sorted(nums,reverse=True)
    assert all(0<=v<100 for v in nums)
    for r in rows:
        if math.isfinite(r['score']):
            finite+=1
            if not r['qualifies']:assert r['score']==0
        else:unavailable+=1

def r(name,n,e):return dict(configuration=name,N=n,error=e)
# Smaller but nonqualifying summaries never displace a qualifying larger one.
z=score_candidates([r('bad',2,1.01),r('good',10,.9),r('raw',100,0)],1,100)
assert z[0]['configuration']=='good' and z[0]['score']==90
# With no eligible reduction, raw is the zero-score fallback, not an invalid result.
z=score_candidates([r('bad',2,2),r('oversized',120,0),r('raw',100,0)],1,100)
assert [q['configuration'] for q in z]==['raw','oversized','bad']
# Equal payload uses discrepancy; exact objective ties remain equal scores.
z=score_candidates([r('a',10,.8),r('b',10,.2),r('c',10,.2),r('raw',100,0)],1,100)
assert [q['configuration'] for q in z[:3]]==['b','c','a']
assert z[0]['score']==z[1]['score']==z[2]['score']
# Preserve the existing feasibility allowance and unavailable status.
z=score_candidates([r('boundary',10,1+5e-9),r('outside',2,1+2e-8),r('missing',4,float('inf')),r('raw',100,0)],1,100)
assert z[0]['configuration']=='boundary' and not z[1]['configuration']=='missing'
assert z[-1]['score_status']=='numerically_unavailable'
# Exact zero-tolerance inputs do not divide by zero.
z=score_candidates([r('exact',2,0),r('raw',8,0)],0,8)
assert z[0]['score']==75 and z[0]['discrepancy_ratio']==0
result=dict(audit_cases=len(details),configurations=finite+unavailable,finite=finite,unavailable=unavailable,unchanged_selections=len(details),raw_baseline_zero=True,descending_scores=True,boundary_checks_passed=True)
(P/'revision/results/selection_score_checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
