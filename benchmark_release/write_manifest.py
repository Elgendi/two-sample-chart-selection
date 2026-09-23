"""Write or verify content hashes for the unpacked release, excluding transient files."""
from pathlib import Path
import hashlib,argparse
ROOT=Path(__file__).resolve().parents[1]
EXCLUDE={'.aux','.blg','.fdb_latexmk','.fls','.out','.synctex.gz','.pyc'}
def files():
 for p in sorted(ROOT.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts or p.name=='SHA256SUMS.txt':continue
  if p.suffix in EXCLUDE or (p.parent==ROOT and p.suffix=='.log'):continue
  yield p

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--verify',action='store_true');args=parser.parse_args();path=ROOT/'SHA256SUMS.txt'
 if args.verify:
  count=0
  for line in path.read_text().splitlines():
   expected,name=line.split('  ',1);p=ROOT/name
   if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected:raise SystemExit('Hash mismatch or missing file: '+name)
   count+=1
  print('Verified',count,'release file hashes. Regeneration may legitimately change PDF timestamps and run logs.')
 else:
  lines=[hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(ROOT).as_posix() for p in files()];path.write_text('\n'.join(lines)+'\n');print('Wrote',len(lines),'file hashes.')
if __name__=='__main__':main()
