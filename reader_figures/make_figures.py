"""Regenerate all four main figures from the frozen, task-specific results."""
from pathlib import Path
import runpy
R=Path(__file__).resolve().parents[1]
runpy.run_path(str(R/'reader_figures/make_scoring_example.py'),run_name='__main__')
runpy.run_path(str(R/'task_first/figures.py'),run_name='__main__')
