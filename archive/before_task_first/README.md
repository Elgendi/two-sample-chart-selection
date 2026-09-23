# Choosing familiar charts by task-specific optimization

This archive contains the reader-focused revision of the version 3 manuscript and a complete offline computational reproduction package. It does not contain human-reader validation, an untouched external medical test cohort, or a claim of acceptance by a particular journal.

## Read first
- `main.pdf` and `main.tex`: revised manuscript.
- `supp.pdf` and `supp.tex`: exact contracts, full audit and supplementary analyses.
- `REVISION_REPORT.md`: changes, verified findings and remaining evidence gaps.
- `READER_STUDY_PROTOCOL.md`: prospective study, explicitly not performed.

## Start with the three main figures
- Figure 1: clearly different cell-nucleus area distributions; explicit scoring arithmetic and 60.17 → 97.70 for mean bars versus raw dots.
- Figure 2: eight successes spanning six resources and four winning families, with both charts, scores, gains and error reductions.
- Figure 3: the eight smallest valid gains over mean bars, including three unchanged winners and five small positive score gains.
- `reader_figures/Expanded_example_gallery.pdf`: worked scoring figure plus 16 enlarged example cards.

`reader_figures/READ_THE_FIGURES.md` explains all 17 examples, display crops and the retrospective selection rules. Supplementary Section S17 maps every panel to its feature, cohort size and exact setting. All reference losses remain unchanged.

```bash
python score_my_data.py reader_figures/example_input.csv --output-dir my_scores
python reader_figures/make_figures.py
python reader_figures/make_gallery.py
```

The example now uses WDBC mean area and reproduces all 21 Figure 1 configuration scores. Specialized controls remain optional (`--include-specialized`) and their results remain in the supplement. The three main figure sources, PDF/SVG/PNG exports, enlarged cards, full-precision values and verification records are under `reader_figures/`.

## Reproduce version 3
Use Python 3 with the pinned `requirements.txt`, then run:

```bash
python reproduce_v3.py
```

This runs 20,320 image–decoder trials across 127 cases, ten configurations, two observers, two display conditions and four placements. It computes six targets per trial, compares frozen policies, verifies all held-out folds and regenerated losses, and creates the four detailed diagnostic figures now in the supplement. No network is needed. The script retains the version 2 tables included in this archive as dependencies; rerun the earlier audit below if needed.

Current protocol, code, results and figures are under `validation_v3/`. The protocol was specified after v2 results were known. A later zero-target control is explicitly recorded in `analysis_addendum.json`. The principal finding is that case-specific chart selection does not consistently improve on a task default. This is a limitation study, not evidence of a universally superior selector.

## Reproduce version 2
Use Python 3 with `requirements.txt`, then run:

```bash
python reproduce_strengthened.py
```

The run checks both decoders, evaluates 23 settings across 127 prepared comparisons, runs 72 synthetic cases and source sensitivities, computes resource-disjoint and robustness analyses, transfers fixed choices to a new display resolution, and regenerates four figures and manuscript tables. A full run can take tens of minutes on a modest CPU. No network is needed when using the included data.

Compile `main.tex` and `supp.tex` separately using pdfLaTeX, BibTeX, then two further pdfLaTeX passes. The manuscript macros and result tables are generated from numerical CSVs, not hand-entered scores.

## Main analysis locations
- `validation_v2/observer.py`: original observer adapter, alternative alpha observer, ECDF and quantile baseline rendering.
- `validation_v2/protocol.json`: fixed numerical analysis specification, retrospectively developed.
- `validation_v2/display_protocol.json`: new display-condition transfer specification.
- `validation_v2/run.py`: primary, simulation and CKD omission runs.
- `validation_v2/analyse.py`: selection, margins, minimax regret, resource transfer, bootstrap and result tables.
- `validation_v2/display_transfer.py`: unchanged settings at 384 pixels and new placements.
- `validation_v2/checks.py`: executable numerical and pixel-dependence checks.
- `validation_v2/results/`: complete per-trial recovered values, aggregates and verification records.
- `validation_v2/figures/`: PDF and PNG figures.

## Interpret results correctly
Higher scores mean lower error for a specified computational task. They do not mean that more people read the chart correctly. Reference optima are selected using the empirical target for the same case; resource-disjoint evaluation instead selects a global setting without the omitted resource's outcomes. Neither is an untouched external clinical validation. Minimax guarantees apply only to the declared selection environments. New-resolution performance is reported separately.

The fixed quantile and ECDF baselines deliberately encode the requested distributional information. Strong performance does not make them universally best charts. Exact ties and small numerical margins are retained; excess-error budgets are not calibrated human-equivalence thresholds.

## Historical material
`rendered_study/` retains the earlier seven-family pixel benchmark for exact numerical parity checks. `archive/original_manuscript/` retains its manuscript sources and PDF. `auto_selection/` and `revision/` contain older compression-related analyses; they are not validation of the current score. `reproduce_revision.py` runs the older pixel pipeline; use `reproduce_v3.py` for the current extension and `reproduce_strengthened.py` for its preserved audit. Legacy report files are marked in the revision report.

## Data and licenses
See `DATA_PROVENANCE.md` and `LICENSE_NOTICE.md`. Source dataset licenses and attribution remain in force. Prepared observations have not been changed in the primary study. CKD omission results are separately labeled; retinopathy linkage and Parkinsons identifiers remain unresolved.

The project repository is https://github.com/Elgendi/two-sample-chart-selection. This task provides files to replace there; it does not assert that the remote repository has been updated.

## Apply the benchmark to your own two columns

```bash
python select_chart_v2.py data/example_paired.csv --x A --y B --output chart_result
python select_chart_v2.py data/example_paired.csv --x A --y B --robust --output robust_result
```

The selector exports all scores, the ranking, exact tied settings, the chosen raster and its calibration. The primary target is five marginal quantile differences. A raw scored raster is not automatically a publication-ready figure; retain readable axes and labels when presenting it. `select_chart.py` is the historical compression selector; use `select_chart_v2.py` for this paper.

The secondary `task_sensitivity.py` analysis holds charts fixed while requesting median-only, five-quantile or dense-19-quantile recovery. It was added retrospectively after observing the direct-quantile baseline's dominance; its protocol records that status.
