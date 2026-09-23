"""Verify task screening, exhaustive setting coverage, and honest encoding ties."""
from pathlib import Path
import json, math
import pandas as pd
from chart_catalogue import catalogue_rankings, CATALOGUE
P=Path(__file__).resolve().parents[1]
details=json.loads((P/'revision/results/details.json').read_text())
cases={c['key']:c for c in json.loads((P/'data/derived/comparisons.json').read_text())}
audit=pd.read_csv(P/'revision/results/audit.csv').set_index('key')
assert len(CATALOGUE)==15 and len({r[0] for r in CATALOGUE})==15
for key,d in details.items():
 c=cases[key];result=catalogue_rankings(d['candidates'],d['tolerance'],len(c['x'])+len(c['y']))
 f=result['families'];settings=result['settings'];lookup={r['chart_id']:r for r in f}
 assert len(f)==15 and len(settings)==21
 assert len({r['catalogue_id'] for r in f})==15
 assert [r['recommendation_order'] for r in f if r['applicable']]==list(range(1,8))
 assert sum(r['display_selected'] for r in f)==1
 assert f[0]['display_selected']
 assert sum(r['applicable'] for r in f)==7
 assert len({r['configuration'] for r in settings})==14
 for r in f:
  if not r['applicable']:assert r['score'] is None and r['rank'] is None and r['tested_settings']==0
  else:assert r['tested_settings']==sum(v['chart_id']==r['chart_id'] for v in settings)
 for a,b in [('histogram','heatmap'),('box','interval')]:
  assert all(lookup[a][v]==lookup[b][v] for v in ['score','N','error','rank','optimal'])
 assert f[0]['configuration']==audit.loc[key].configuration
 scores=[r['score'] for r in f if r['applicable'] and math.isfinite(r['score'])]
 assert scores==sorted(scores,reverse=True)
 # No hidden code path scores unsupported task types.
 assert all(not lookup[q]['applicable'] for q in ['line','scatter','pie','stacked_bar','area','bubble','treemap','choropleth'])
counts=audit[audit.primary].representation.value_counts().to_dict()
report=dict(cases=len(details),chart_families=15,applicable_families=7,not_applicable_families=8,encoding_settings_per_case=21,numerical_configurations_per_case=14,all_original_selections_preserved=True,equivalent_encodings_tied=True,unique_recommendation_order=True,one_display_selected=True,unique_catalogue_ids=True,primary_selection_counts=counts,scope='marginal two-sample contrast only; other tasks screened, not optimized')
(P/'revision/results/chart_catalogue_checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
