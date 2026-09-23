"""Reproduce all revised numerical outputs and figures offline from bundled inputs."""
import os,subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent
if __name__=='__main__':
 env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
 for script in ['analyse.py','simulate.py','checks.py','check_selection_score.py','check_chart_catalogue.py','report.py','score_ranked_figures.py']:
  subprocess.run([sys.executable,str(P/'revision'/script)],cwd=P,env=env,check=True)
 print('Revision analysis complete. Compile main.tex and supp.tex with pdfLaTeX + BibTeX.')
