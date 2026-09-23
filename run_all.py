"""Compatibility entry point: rebuild the final primary benchmark."""
from pathlib import Path
import subprocess,sys
subprocess.run([sys.executable,str(Path(__file__).resolve().parent/'reproduce_benchmark.py'),'--full'],check=True)
