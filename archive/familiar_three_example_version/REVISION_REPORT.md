# Familiar-chart revision

The paper is now titled **Choosing familiar charts by task-specific optimization**.

- Main optimization: seven familiar families, 21 settings, one common five-gap task, 127 comparisons. No underlying observations or recovery losses were altered.
- Figure 1: worked score for raw dots, 98.36, with all seven optimized family scores and the explicit calculation.
- Figure 2: distinct actual winners: maximum heart rate selects a violin (85.67 → 98.01); blood enzyme concentration selects a histogram (85.41 → 97.49).
- Figure 3: mean bars remain optimal (95.35 → 95.35); full winner counts are heatmap 54, dots 39, histogram 18, violin 13, mean bars 3, box/interval 0.
- Abstract, introduction, results, discussion, tables, captions, quick-start code and example data now use the same restricted search scope. The family table includes a one-setting-per-family sensitivity control.
- ECDF and quantile-marker controls remain supplementary diagnostics. Their stronger performance is explicitly acknowledged in the main paper. Expanded transfer analyses are not relabeled as validation of the restricted selector.
- The CLI defaults to 21 familiar settings; `--include-specialized` enables 24 settings. The supplied example matches Figure 1 using the original five-gap decoder.
- Figures use the original scored rasters with external labels. Scores are computational, not measured reader accuracy. Example selection and the familiar-set restriction are retrospective.

## Remaining evidence limits

No claim of a top-1% journal outcome, human comprehension improvement, clinical utility or untouched external validation is made. Familiarity/popularity was not measured. Quantile-based targets favor direct-summary controls when admitted. Chart-specific decoders, unequal tuning budgets and rendering conditions influence rankings. Mean bars can win approximate contrast recovery without retaining distributional detail. Existing data-provenance limitations remain disclosed. These require evidence, not stronger wording.

## Verification

The worked example's 21 configuration losses are checked against stored reference results, and all three figures use computed winners. All 127 winner memberships, scores and source hashes are distributed. Manuscript and supplement are rebuilt with resolved references; figure PDFs and page layouts are inspected. Archive integrity and distributed SHA-256 checksums are verified.
