# Clarity revision, version 4.1

This revision improves presentation without changing the scientific dataset or numerical analyses. It does not claim acceptance at a particular journal or establish human comprehension.

- Figure 1 now places each actual chart beside a short explanation of the information it retains, with one directly reported error measure. The score transformation is left in the text rather than duplicating the same ranking in the figure.
- Figure 2 uses six aligned rows with plain-language task labels, a visible zero reference, directly labeled directions, explicit algorithm identities, and clearly disclosed separate numerical scales. Both algorithms and all descriptive intervals are retained.
- Figure 3 reports best-chart case counts in horizontal bars, defines ties, and states why counting all ties can exceed 24.
- Figure 4 shows the frequency of better, tied and worse outcomes on all new synthetic cases. Supplementary Figure S3 retains the full per-case error magnitudes and means, so the simpler display does not replace evidence about effect size.
- The main table retains exact primary losses and gains; uncertainty intervals remain in Figure 2 and the electronic summary.
- Supplementary Table S1 removes the all-zero failure column. Its note reports that all 1,060 empirical policy pairs decode successfully, distinguishes this from candidate-level failures, and defines the comparison and resampling units. A generation assertion prevents silently dropping a nonzero failure column in a later analysis.
- Supplementary Table S2 gives the synthetic error magnitudes.

Validation: publication figures and tables regenerated from saved numeric results; synthetic outcome counts checked against the saved summary; final PDFs compiled and visually inspected. The prior clean numerical rebuild remains documented in CLEAN_REBUILD_REPORT.md. No new numerical benchmark run was needed for these presentation changes.

Before submission: complete the author-specific items in SUBMISSION_NOTES.md and adapt the package to the selected journal.
