# Expanded example revision

The main paper remains **Choosing familiar charts by task-specific optimization**.

## Completed changes

- Replaced the nearly identical ECG/pulse example in Figure 1 with visibly different benign/malignant cell-nucleus areas. Raw dots score 97.70 versus 60.17 for mean bars. The worked error, normalization and final score all use this new case.
- Expanded Figure 2 to eight before/after examples: two dot winners, two histograms, two violins and two heatmaps, spanning six resources. Gains are 12.09–49.29 score points and 79.1–98.3% lower computational recovery error.
- Expanded Figure 3 to eight cases with the smallest score gains over mean bars among the 122 valid mean-bar comparisons. Three gains are exactly zero; five are 1.13–2.46 points. Their relative error reductions are also reported, so small score gains are not falsely equated with no benefit.
- Added before and after renderings, both scores, score gain, error reduction, feature names, group labels and units to every example card. Heatmap intensities have an explicit key and retain their original colors.
- Added individual enlarged vector cards and a 17-page example gallery. Main Figures 2 and 3 each retain all eight panels.
- Updated manuscript results, captions, Supplementary Section S17, the input CSV, demonstration outputs, guide and README. Exact feature IDs, settings and sample counts are retained.
- Preserved the same data, 21 familiar settings and computational scoring objective. Specialized controls remain supplementary diagnostics; the restricted optimum is explicitly conditional on the familiar set.

## Verification and presentation details

All 21 Figure 1 configuration losses reproduce stored reference values. Each displayed optimum is checked against all seven optimized families, and each selected loss is recomputed from four placements' saved recovered gaps. The Figure 3 rule is checked against the complete valid-baseline set. No winners, source data or losses were changed to create diversity.

Scores apply to original 256-pixel square panels. Publication views crop unused histogram probability space and heatmap margins and enlarge the resulting pixels; measurement limits and colors are preserved. The changed layout is not assigned the original computational score as a new experiment. Figure captions and the supplement explain this distinction.

The main manuscript, supplement and enlarged cards are rendered and inspected. Archive integrity, source dependencies and distributed SHA-256 checksums are checked.

## Remaining evidence limits

The success examples are retrospective illustrations, not a representative estimate of average improvement. Multiple panels reuse cohorts. Figures demonstrate computational recovery, not human comprehension or clinical benefit. No claim of top-1% acceptance, untouched external validation, measured worldwide chart familiarity or universal optimality is made. Existing source-provenance and decoder limitations remain disclosed.
