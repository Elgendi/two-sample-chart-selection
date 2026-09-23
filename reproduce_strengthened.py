"""Reproduce v2 numerical validation and report. See README for original analyses."""
from pathlib import Path
import os,sys,subprocess
ROOT=Path(__file__).resolve().parent
env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
for script in ['checks.py','run.py','analyse.py','display_transfer.py','task_sensitivity.py','verify_release.py','revision_report.py','figures.py']:
    subprocess.run([sys.executable,str(ROOT/'validation_v2'/script)],cwd=ROOT,env=env,check=True)
print('Validated v2 tables and figures regenerated. Compile main.tex and supp.tex separately.')
