from pathlib import Path
import json,pandas as pd
ROOT=Path(__file__).resolve().parents[1];O=ROOT/'validation_v2/results';s=json.loads((O/'summary.json').read_text());t=pd.read_csv(O/'task_summary.csv');dt=pd.read_csv(O/'display_transfer_summary.csv')
def wins(task,obs='threshold'):
 d=t[(t.task==task)&(t.observer==obs)].sort_values('wins',ascending=False);return '; '.join(f'{r.family}: {r.wins}' for r in d.itertuples())
text=f'''# Revision report: strengthened computational chart-selection study

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

- Primary comparisons: {s['primary_cases']} from {s['resources']} resources.
- Primary decoder evaluations: {s['trials']:,}; failed evaluations: {s['failed']:,}, retained explicitly.
- Original reference losses: all 2,667 old setting–comparison losses reproduced, including missing failures.
- Median best reference score: {s['median_best']:.3f}.
- Fixed five-quantile baseline beats the original seven-family optimum in {s['quantile_beats_legacy']}/127 comparisons.
- Median fixed-quantile score: {s['median_quantile']:.3f}; median ECDF score: {s['median_ecdf']:.3f}.
- Expanded reference-family wins: {s['wins']}.
- Winning-family changes between 128 and 512 pixels: {s['resolution_changes']}/127.
- More than one family within excess loss 0.01 pooled SD: {s['near_counts']['0.01']}/127.
- Resource-disjoint mean loss (equal resource weights): {s['transfer_mean_resource_loss']:.4f}.
- Exact reference tied cases: {s['tied_cases']}.

### Changing the requested task
Winning memberships under the threshold observer and one fixed setting per family (ties may make totals exceed 127):

- Median-only: {wins('median')}.
- Five quantiles: {wins('five')}.
- Nineteen quantiles: {wins('dense19')}.

These results materially change the interpretation of the earlier manuscript: a target-matched quantile display is a strong baseline, while a broader distributional task frequently favors an ECDF. Small score differences and observer-specific winners are retained rather than adjusted to support a preferred story.

### New display-condition transfer
Resource-balanced mean normalized loss at 384 pixels, with unchanged selected settings:

'''
text+='| Selection | Observer | Mean loss |\n|---|---|---:|\n'+''.join(f'| {r.choice} | {r.observer} | {r.loss:.5f} |\n' for r in dt.itertuples())
text+='''
## What is not claimed

This package does not claim improved human interpretation, speed, preference or clinical outcomes. No reader responses were generated or invented. The alpha decoder is a sensitivity analysis, not an independently human-validated observer. Neither the retrospective resource split nor the synthetic data create an untouched external clinical validation set. Minimax selection is a standard optimization construction, not a newly discovered theorem. The score is a monotone transformation of error, not a new information measure.

The revised manuscript is substantially stronger as a reproducible computational study, but these files do not justify certifying it as ready for a top-1% journal. Human-reader validation, independently assessed decoder performance or stronger external utility evidence would still be needed for broad claims about scientific chart recommendations.

## Author actions before submission

1. Verify the revised analyses, affiliation, correspondence details, funding statement and any journal-required disclosures.
2. Replace the repository contents with the supplied reproducibility archive and retain a versioned release/DOI if required by the chosen journal. This task supplies files and does not publish them.
3. Decide whether to submit the bounded computational study or first perform the prospective human-reader experiment. The protocol and blank templates are included; they are not completed validation.

## Reproduction and history

Use `python reproduce_strengthened.py` for this revision. Use `python select_chart_v2.py` for a new two-column input. The old selector and compression analyses are explicitly historical. Execution manifests record stage-time hashes; the final release checksum file identifies every distributed file. Minor report-generation fixes after numerical execution do not change generated observations, renderings or numerical recovery. The task-comparison reporting retains an absolute 1e-12 loss tolerance for genuine ties.
'''
(ROOT/'REVISION_REPORT.md').write_text(text)
print('Revision report saved.')
