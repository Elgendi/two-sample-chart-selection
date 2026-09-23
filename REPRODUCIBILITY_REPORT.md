# Reproducibility check — 23 September 2026

A fresh offline `python reproduce_benchmark.py --full` run completed all 13 stages successfully. Recorded stage runtime totaled 935.4 seconds. This was a full primary numerical regeneration, not merely a manuscript compilation. Historical secondary sensitivities were retained, not claimed as independently rerun.

Verified results:
- All 156 raw source hashes checked; 149 prepared comparisons rebuilt exactly (127 primary plus 22 excluded exploratory comparisons).
- 30,480 marginal and 2,728 extension configuration results reproduced.
- 23,808 synthetic losses recomputed; maximum absolute discrepancy 2.22e-16.
- All 168 held-out-unit default folds and 1,060 empirical case–algorithm comparisons passed training-exclusion and test-display checks.
- All 1,114 applicable stability-bound checks passed.
- Geometry decoder: 2,304 evaluations, no failed trials, with blank-image rejection tested.
- Four documented CSV examples reproduced 40 configuration losses to approximately 1.1e-16.

Candidate-level synthetic failures remain in the release (360 task-loss rows). A passed verification does not mean every candidate decoded successfully. All deployed default/selection policies succeeded on their evaluated cases.

The main summary, synthetic summary and geometry summary match the fresh rebuild within 1e-12. Manuscript changes do not alter numerical-analysis code or results. Presentation sources were revised to retain the requested familiar-chart style, and figure writes now validate output before atomic replacement. Main and supplementary PDFs compile with resolved references and no overfull boxes; all pages were rendered and visually inspected.

Machine-readable evidence: `benchmark_release/logs/pipeline_full.json`, `benchmark_release/results/verification.json`, `benchmark_release/results/example_verification.json` and `REVISION_PROVENANCE.json`.

No human study or external clinical validation was performed. The public repository was inspected but not updated; this versioned archive is the complete computational record.
