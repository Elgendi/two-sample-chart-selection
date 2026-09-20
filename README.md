# Scoring rendered charts by recovery of two-sample differences

This is a computational development benchmark. It is not validated against human reading performance and is not a universal optimizer of all 15 chart families.

## Current deliverables

- [Read the manuscript](main.pdf) and [Supplement](supp.pdf).
- [Figure 2: when changing the chart helps](rendered_study/figures/Figure_2_Examples.pdf).
- [Figure 3: when changing the chart adds little](rendered_study/figures/Figure_3_Limits.pdf).
- `main.pdf` and `main.tex`: current manuscript.
- `supp.pdf` and `supp.tex`: full computational contract, all 15 catalogue families, all 127 primary reference-resolution winners.
- `rendered_study/figures/`: current three main figures and Supplementary Figure S1, PDF/SVG/PNG and combined main-figure PDF.
- `rendered_study/results/`: complete trial, setting, family, winner and verification results, including 22 excluded exploratory cases.

## Reproduce
Use the pinned `requirements.txt`. Run `python reproduce_revision.py` from this directory. This executes checks, 37,548 render/decode trials and figure generation. Four worker processes are used; allow roughly 20 minutes depending on hardware. Inputs are bundled; no download is required.

To regenerate figures from saved results only: `python rendered_study/report.py`.
Compile manuscript and supplement separately with pdfLaTeX, BibTeX, then pdfLaTeX twice. The minimal Overleaf ZIP includes all required typesetting files.

## New data
`python select_chart.py data/example_paired.csv --x A --y B --output chart_scores.csv`

The target is marginal even for paired data. The CSV may have missing entries to accommodate unequal group lengths; each group requires at least four finite observations. The output ranks all 21 implemented settings by actual score. It does not assert that a score difference predicts a human difference. Use `--resolution 128`, `256` or `512` (default 256).

## Objective
At five quantiles (10%, 25%, 50%, 75%, 90%), recover group differences from actual rendered pixels plus known axes. Score = 100 / (1 + mean absolute recovery error divided by pooled within-group SD), with loss averaged over four rendering realizations. No size penalty or artificial tie-breaking offset is used. Genuine ties remain ties; raw dots can legitimately win.

## Scope
The catalogue documents all 15 requested families. Seven have implemented contracts for the current task, contributing 21 settings. Other task families require separately specified targets and decoders. Rendering/decoder assumptions can favour particular charts. The main datasets were used in development. No reader study has been conducted.

## Historical files
`revision/`, `auto_selection/`, `legacy_compression/` and historical result folders preserve earlier compression analyses. They do NOT produce the current manuscript's pixel score and do not validate it. The authoritative current code is `rendered_study/`; the current entry point is `reproduce_revision.py`. Earlier simulations remain historical, not evidence for this new method.

Source attributions, unresolved identifiers and source-value concerns remain in `DATA_PROVENANCE.md`. Use a versioned repository release when citing or submitting this development benchmark.
