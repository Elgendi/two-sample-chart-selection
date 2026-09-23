from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1];O=ROOT/'validation_v2/results';s=json.loads((O/'summary.json').read_text())
a=pd.read_csv(O/'configurations.csv',dtype={'setting':str});task=pd.read_csv(O/'task_configurations.csv',dtype={'setting':str});sim=pd.read_csv(O/'simulation_trials.csv',keep_default_na=False,na_values=['']);display=pd.read_csv(O/'display_transfer.csv')
assert s['primary_cases']==127 and s['resources']==9 and s['trials']==92456
assert len(sim)==5184 and sim.key.nunique()==72 and 'null' in set(sim.dataset)
assert len(task)==127*9*2*3
ref=a[(a.axis=='zero')&(a.H==256)];five=task[task.task=='five'];m=five.merge(ref,on=['key','family','setting','observer'],suffixes=('_task','_primary'))
assert len(m)==127*9*2;assert np.allclose(m.loss_task,m.loss_primary,equal_nan=True,atol=1e-12)
b=pd.read_csv(O/'robust_settings.csv',dtype={'setting':str});w=pd.read_csv(O/'robust_choices.csv',dtype={'setting':str});assert len(w)==127 and (w.n_env==6).all()
for _,r in w.iterrows():assert r.worst_regret<=b[b.key==r.key].worst_regret.min()+1e-12
assert len(display)==127*3*2
manifest=json.loads((O/'run_manifest.json').read_text());assert hashlib.sha256((ROOT/'validation_v2/protocol.json').read_bytes()).hexdigest()==manifest['protocol_sha256'];assert hashlib.sha256((ROOT/'data/derived/comparisons.json').read_bytes()).hexdigest()==manifest['data_sha256']
for name in ['run.py','observer.py']:assert hashlib.sha256((ROOT/'validation_v2'/name).read_bytes()).hexdigest()==manifest['source_sha256'][name]
assert len((ROOT/'reader_study/response_template.csv').read_text().splitlines())==1
checks=json.loads((O/'checks.json').read_text());assert checks['passed']==46
report=dict(primary_evaluations=92456,synthetic_evaluations=5184,synthetic_cases_including_null=72,task_aggregates=len(task),five_task_matches_primary=True,robust_choices_verified=127,new_display_aggregates=len(display),benchmark_source_hashes_match=True,input_hash_matches=True,protocol_hash_matches=True,decoder_fixture_checks=46,no_fabricated_reader_responses=True)
(O/'release_verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
