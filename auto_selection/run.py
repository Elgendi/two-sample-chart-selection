from pathlib import Path
import json
import numpy as np
import pandas as pd
from model import select,FAMILIES
P=Path(__file__).resolve().parents[1];R=P/'auto_selection/results';R.mkdir(exist_ok=True)
cases=json.loads((P/'data/derived/comparisons.json').read_text());rows=[];families=[];variants=[];details={}
for i,c in enumerate(cases):
 a=select(c['x'],c['y'],c['paired'],bootstrap=99,seed=9000+i);details[c['key']]=a
 base={k:c[k] for k in ['key','dataset','feature','unit','labels']};rows.append(dict(**base,**{k:v for k,v in a.items() if k not in ['families','variants','bootstrap_frequencies']}))
 families += [dict(key=c['key'],dataset=c['dataset'],feature=c['feature'],**r) for r in a['families']];variants += [dict(key=c['key'],**r) for r in a['variants']]
 if i%25==0:print('Analysed',i+1,'of',len(cases),flush=True)
d=pd.DataFrame(rows);d.to_csv(R/'automatic_selections.csv',index=False);pd.DataFrame(families).to_csv(R/'all_family_scores.csv',index=False);pd.DataFrame(variants).to_csv(R/'all_variant_scores.csv',index=False);(R/'details.json').write_text(json.dumps(details,indent=2))
summary=dict(comparisons=len(d),resources=d.dataset.nunique(),family_records=len(families),variant_records=len(variants),strata=d.stratum.value_counts().to_dict(),selected_sets=d.selected.value_counts().to_dict(),bootstrap_agreement_median=d.bootstrap_agreement.median(),bootstrap_agreement_below_080=int((d.bootstrap_agreement<.8).sum()),bootstrap_draws=99)
(R/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
