"""Reproduce the current pixel-observer manuscript, not legacy compression."""
from pathlib import Path
import subprocess,sys,os
root=Path(__file__).resolve().parent
env=os.environ.copy();env['OPENBLAS_NUM_THREADS']='1';env['OMP_NUM_THREADS']='1'
for script in ['checks.py','run_benchmark.py','report.py']:
    subprocess.run([sys.executable,str(root/'rendered_study'/script)],cwd=root,env=env,check=True)
print('Current computational-observer results and figures regenerated.')
