"""Rebuild the final computational benchmark offline from bundled source data.
--full regenerates inputs, empirical/synthetic trials, comparisons and figures.
--verify independently audits saved numerical results; --figures rebuilds tables/figures.
Add --pdf to compile main.tex and supp.tex using latexmk.
"""
from pathlib import Path
import argparse,subprocess,sys,os,time,json,shutil
ROOT=Path(__file__).resolve().parent

def main():
 p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True);g.add_argument('--full',action='store_true');g.add_argument('--verify',action='store_true');g.add_argument('--figures',action='store_true');p.add_argument('--pdf',action='store_true');args=p.parse_args()
 env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MPLBACKEND='Agg');logdir=ROOT/'benchmark_release/logs';logdir.mkdir(parents=True,exist_ok=True)
 if args.full:
  scripts=['benchmark_release/rebuild_inputs.py','validation_v3/benchmark.py','validation_v3/analyse.py','validation_v3/verify.py','task_first/checks.py','task_first/benchmark.py','task_first/analyse.py','benchmark_release/compare_defaults.py','benchmark_release/stress_test.py','benchmark_release/geometry_observer.py','benchmark_release/verify_release.py','benchmark_release/make_report.py','benchmark_release/make_figures.py']
 elif args.verify:scripts=['validation_v3/verify.py','benchmark_release/compare_defaults.py','benchmark_release/verify_release.py']
 else:scripts=['benchmark_release/make_report.py','benchmark_release/make_figures.py']
 runs=[]
 for script in scripts:
  start=time.monotonic();print('Running',script,flush=True)
  with (logdir/(script.replace('/','_')+'.log')).open('w') as f:subprocess.run([sys.executable,str(ROOT/script)],cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
  runs.append(dict(script=script,seconds=round(time.monotonic()-start,3),status='passed'));print('Passed in',runs[-1]['seconds'],'seconds',flush=True)
 if args.pdf:
  if not shutil.which('latexmk'):raise SystemExit('Install TeX Live/latexmk for PDFs; numerical results are already complete.')
  for name in ['main','supp']:
   with (logdir/f'build_{name}.log').open('w') as f:subprocess.run(['latexmk','-pdf','-g','-interaction=nonstopmode','-halt-on-error',name+'.tex'],cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
 report=dict(mode='full' if args.full else 'verify' if args.verify else 'figures',runs=runs,status='passed',network_used=False)
 (logdir/('pipeline_'+report['mode']+'.json')).write_text(json.dumps(report,indent=2));print('Completed. Read main.pdf and benchmark_release/results/verification.json.',flush=True)
if __name__=='__main__':main()
