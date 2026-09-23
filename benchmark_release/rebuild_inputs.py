"""Rebuild wrist bin summaries from WFDB annotations and all prepared comparison arrays.
The original frozen CSV is preserved; equivalence is checked before using it.
WFDB format: https://wfdb.io/spec/annotation-files.html
"""
from pathlib import Path
import struct,json,subprocess,sys,hashlib
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'benchmark_release/results'

def beat_samples(path):
 raw=path.read_bytes();i=0;sample=0;beats=[]
 while i+1<len(raw):
  word=raw[i]+256*raw[i+1];i+=2;code=word>>10;delta=word&1023
  if word==0:break
  if code==59:
   if i+4>len(raw):raise ValueError('Truncated WFDB SKIP')
   q=raw[i:i+4];i+=4;sample+=struct.unpack('<i',q[2:4]+q[:2])[0]
  elif code==63:i+=delta+(delta%2)
  elif code in [60,61,62]:pass
  else:
   sample+=delta
   if code==1:beats.append(sample)
 return np.asarray(beats,dtype=float)

def main():
 rows=[]
 for p in sorted((ROOT/'data/raw/wrist').glob('*.atr')):
  fs=float(p.with_suffix('.hea').read_text().splitlines()[0].split()[2].split('/')[0]);t=beat_samples(p)/fs;rr=np.diff(t)
  if not (rr>0).all():raise ValueError('Non-increasing beat annotations')
  h=60/rr;bins=np.floor(t[1:]/5).astype(int)
  for ix in np.unique(bins):rows.append(dict(record=p.stem,participant=p.stem.split('_')[0],time_s=5*int(ix)+2.5,hr_5s=float(np.median(h[bins==ix]))))
 rebuilt=pd.DataFrame(rows);frozen=pd.read_csv(ROOT/'data/raw/wearable_5s_series.csv');keys=['record','participant','time_s'];z=frozen.merge(rebuilt,on=keys,suffixes=('_frozen','_rebuilt'),validate='one_to_one');assert len(z)==len(rebuilt)==len(frozen)==1364
 assert np.allclose(z.hr_5s_frozen,z.hr_5s_rebuilt,rtol=0,atol=1e-12)
 rebuilt.to_csv(OUT/'wrist_series_rebuilt.csv',index=False)
 before=json.loads((ROOT/'data/derived/comparisons.json').read_text())
 # Every packaged source copy must match the inherited acquisition manifest.
 raw_manifest=json.loads((ROOT/'data/raw_checksums.json').read_text())
 for item in raw_manifest:
  assert hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'],item['path']
 subprocess.run([sys.executable,str(ROOT/'code/prepare.py')],cwd=ROOT,check=True)
 after=json.loads((ROOT/'data/derived/comparisons.json').read_text());assert len(before)==len(after)
 for a,b in zip(before,after):
  assert a['key']==b['key']
  for g in ['x','y']:assert np.array_equal(a[g],b[g]),a['key']
 result=dict(status='passed',wrist_bins_rebuilt=len(z),wrist_records=frozen.record.nunique(),wrist_participants=frozen.participant.nunique(),max_wrist_difference=float(abs(z.hr_5s_frozen-z.hr_5s_rebuilt).max()),all_prepared_comparisons=len(after),primary_comparisons=sum(c['dataset']!='Parkinsons' for c in after),all_prepared_arrays_exactly_reproduced=True,raw_files_hash_verified=len(raw_manifest),note='Original frozen wrist CSV retained after independent raw-annotation equivalence check; no heart-rate filtering beyond valid positive beat intervals.')
 (OUT/'input_verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
