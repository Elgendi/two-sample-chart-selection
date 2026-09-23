"""Combine the worked scoring figure and 16 enlarged example cards."""
from pathlib import Path
from pypdf import PdfWriter
r=Path(__file__).resolve().parent
w=PdfWriter()
w.append(str(r/'figures/Figure_1_How_scoring_works.pdf'),outline_item='Figure 1: worked score')
for p in sorted((r/'figures/panels').glob('*.pdf')):
 w.append(str(p),outline_item=p.stem.replace('_',' '))
w.write(str(r/'Expanded_example_gallery.pdf'))
