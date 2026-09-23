"""Rebuild the task-first extension. Original frozen quantile results must be present."""
from pathlib import Path
import subprocess,sys
R=Path(__file__).resolve().parent
for script in ['task_first/checks.py','task_first/benchmark.py','task_first/analyse.py','task_first/report.py','reader_figures/make_figures.py','reader_figures/make_gallery.py']:
 subprocess.run([sys.executable,str(R/script)],cwd=R,check=True)
