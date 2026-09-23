from pathlib import Path
import urllib.request,zipfile,io,json,hashlib
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[1]
SOURCES={
 'heart':(45,'heart+disease'),
 'failure':(519,'heart+failure+clinical+records'),
 'kidney':(336,'chronic+kidney+disease'),
 'liver':(225,'ilpd+indian+liver+patient+dataset'),
 'parkinsons':(174,'parkinsons'),
 'retina':(329,'diabetic+retinopathy+debrecen'),
 'har':(240,'human+activity+recognition+using+smartphones')}
def get(item):
 key,(number,slug)=item;url=f'https://archive.ics.uci.edu/static/public/{number}/{slug}.zip';p=ROOT/'data/raw'/f'{key}.zip'
 if not p.exists():
  for attempt in range(3):
   try:
    with urllib.request.urlopen(url,timeout=90) as r:raw=r.read()
    with zipfile.ZipFile(io.BytesIO(raw)) as z: assert z.namelist()
    p.write_bytes(raw);break
   except Exception:
    if attempt==2:raise
 return {'key':key,'url':url,'file':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
 with ThreadPoolExecutor(max_workers=7) as pool: manifests=list(pool.map(get,SOURCES.items()))
 (ROOT/'data/download_manifest.json').write_text(json.dumps(manifests,indent=2))
 for m in manifests:
  with zipfile.ZipFile(ROOT/m['file']) as z:print(m['key'],z.namelist()[:12])
if __name__=='__main__':main()
