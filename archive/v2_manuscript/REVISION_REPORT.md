# Revision report: strengthened computational chart-selection study

## What has been completed

The manuscript and supplement have been rewritten around verified computational evidence. Four main figures, the complete analysis outputs, a reusable selector and a prospective human-reader protocol are included. The original manuscript is retained under `archive/original_manuscript/`.

| Prior issue | Completed action | Remaining limit |
|---|---|---|
| Weak mean-bar baseline | Added ECDF and direct five-quantile plots; evaluated 23 settings across nine families | Task-specific baselines are not universal visualization rankings |
| Unequal decoder capability | Compared threshold and alpha observers; retained every failed decode | Both are algorithmic observers with shared calibration assumptions; no human validation |
| Unequal tuning budgets | Compared full search with one prespecified setting per family | Chart design choices remain part of the contract |
| Fragile winners | Reported margins, exact tied sets, excess-error choice sets and six-environment minimax regret | Computational tolerances are not human equivalence thresholds |
| Same-condition optimization | Transferred unchanged settings to a new 384-pixel display and new placements | This is not an untouched medical population |
| Development-only datasets | Added retrospective leave-one-resource-out global-setting evaluation and 72 synthetic cases | Resources were previously available; external real-data validation remains outstanding |
| Error cancellation | Reported group-specific errors and skill over zero-contrast prediction; added a mathematical counterexample | Full-distribution fidelity is still broader than any selected target |
| Target favors a direct quantile plot | Added median-only and dense-19-quantile tasks with unchanged renderings | This secondary analysis is explicitly retrospective |
| Unresolved source issues | Recomputed CKD omission sensitivity; reported retinopathy exclusion; kept Parkinsons excluded | Source identity/measurement ambiguities themselves remain unresolved |
| Missing reproducibility assets | Included executable scripts, arrays, per-trial outputs, deterministic seeds and release hashes | The remote GitHub repository has not been changed by this task |

## Verified results

- Primary comparisons: 127 from 9 resources.
- Primary decoder evaluations: 92,456; failed evaluations: 217, retained explicitly.
- Original reference losses: all 2,667 old setting–comparison losses reproduced, including missing failures.
- Median best reference score: 99.172.
- Fixed five-quantile baseline beats the original seven-family optimum in 124/127 comparisons.
- Median fixed-quantile score: 99.167; median ECDF score: 97.826.
- Expanded reference-family wins: {'Quantile plot': 122, 'ECDF': 2, 'Heatmap': 2, 'Violin plot': 1}.
- Winning-family changes between 128 and 512 pixels: 13/127.
- More than one family within excess loss 0.01 pooled SD: 51/127.
- Resource-disjoint mean loss (equal resource weights): 0.0093.
- Exact reference tied cases: 0.

### Changing the requested task
Winning memberships under the threshold observer and one fixed setting per family (ties may make totals exceed 127):

- Median-only: Interval plot: 70; Quantile plot: 23; Box plot: 19; ECDF: 17; Violin plot: 12; Heatmap: 10; Histogram: 4; Dot plot: 2; Bar chart: 1.
- Five quantiles: Quantile plot: 123; ECDF: 2; Dot plot: 1; Heatmap: 1.
- Nineteen quantiles: ECDF: 114; Quantile plot: 7; Dot plot: 6.

These results materially change the interpretation of the earlier manuscript: a target-matched quantile display is a strong baseline, while a broader distributional task frequently favors an ECDF. Small score differences and observer-specific winners are retained rather than adjusted to support a preferred story.

### New display-condition transfer
Resource-balanced mean normalized loss at 384 pixels, with unchanged selected settings:

| Selection | Observer | Mean loss |
|---|---|---:|
| fixed quantile | alpha | 0.00339 |
| fixed quantile | threshold | 0.00638 |
| minimax optimum | alpha | 0.00351 |
| minimax optimum | threshold | 0.00655 |
| reference optimum | alpha | 0.00383 |
| reference optimum | threshold | 0.00646 |

## What is not claimed

This package does not claim improved human interpretation, speed, preference or clinical outcomes. No reader responses were generated or invented. The alpha decoder is a sensitivity analysis, not an independently human-validated observer. Neither the retrospective resource split nor the synthetic data create an untouched external clinical validation set. Minimax selection is a standard optimization construction, not a newly discovered theorem. The score is a monotone transformation of error, not a new information measure.

The revised manuscript is substantially stronger as a reproducible computational study, but these files do not justify certifying it as ready for a top-1% journal. Human-reader validation, independently assessed decoder performance or stronger external utility evidence would still be needed for broad claims about scientific chart recommendations.

## Author actions before submission

1. Verify the revised analyses, affiliation, correspondence details, funding statement and any journal-required disclosures.
2. Replace the repository contents with the supplied reproducibility archive and retain a versioned release/DOI if required by the chosen journal. This task supplies files and does not publish them.
3. Decide whether to submit the bounded computational study or first perform the prospective human-reader experiment. The protocol and blank templates are included; they are not completed validation.

## Reproduction and history

Use `python reproduce_strengthened.py` for this revision. Use `python select_chart_v2.py` for a new two-column input. The old selector and compression analyses are explicitly historical. Execution manifests record stage-time hashes; the final release checksum file identifies every distributed file. Minor report-generation fixes after numerical execution do not change generated observations, renderings or numerical recovery. The task-comparison reporting retains an absolute 1e-12 loss tolerance for genuine ties.
