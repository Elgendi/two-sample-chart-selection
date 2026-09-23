"""Reproduce current multi-task extension; v2 output tables are retained dependencies."""
from pathlib import Path
import os,sys,subprocess
ROOT=Path(__file__).resolve().parent
env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
for script in ['benchmark.py','analyse.py','figures.py','verify.py']:
 subprocess.run([sys.executable,str(ROOT/'validation_v3'/script)],cwd=ROOT,env=env,check=True)
print('Version 3 results and figures regenerated. Compile main.tex and supp.tex with pdfLaTeX/BibTeX.')
