# Version 3: scientific revision and submission readiness

The manuscript is now titled **Task-matched baselines reveal the limits of computational chart selection**.

This revision makes the scientific claim more defensible. It does not certify a top-1% paper, demonstrate improved human interpretation, or establish a universally superior chart selector. The strengthened experiments reveal a limitation of the original proposition: case-specific optimization does not consistently improve on a simple task-matched default. Concealing that finding or engineering different winners would weaken the paper.

## What changed in this revision

| Issue | Action completed | Evidence / status |
|---|---|---|
| Five-quantile task almost guarantees a direct quantile winner | Added six explicit quantile-based tasks and a 19-marker matched control | 20,320 image–decoder trials; 121,920 task losses. Dense control wins all 127 dense-task cases for one observer and 126 for the other. Dominance is disclosed, not artificially removed. |
| Apparent variety of winners could come from a weak control | Retained both five- and 19-marker configurations; report all tied memberships | Main Figure 2; complete per-case results. No claim of equal family tuning budgets in this extension. |
| Unclear incremental benefit of selection | Compare case-specific choices with resource-disjoint task defaults and fixed controls | Training at 256 pixels, frozen choices evaluated at 384 pixels and new placements. |
| Selection and evaluation on the same rendering | Separated the selection display from the transfer display | Every policy result verified against transfer records; all 108 resource/task/observer folds checked. |
| Treating correlated features as independent evidence | Average policy differences within resources, then use nine equally weighted resource summaries | Paired bootstrap intervals are explicitly descriptive and exploratory. No feature-level significance claims. |
| A high score can reflect a nearly zero target | Added a no-chart zero-target control for all six tasks | Marked as a post-run diagnostic in `validation_v3/analysis_addendum.json`; no primary result was altered to favor selection. |
| Confusing unavailable information with decoder error | Added an explicit identifiability condition and a constructive paired-change witness | Main Figure 1; marginal charts reject median within-person-change requests. This is an elementary criterion, not a claimed new theorem. |
| Conflating encoding loss with raster loss | Compute exact-marker and pixel-recovery losses for both direct controls | Main Figure 4; verify triangle bounds rather than falsely adding error magnitudes. |
| Figures repeatedly show the same winner | Replaced all four main figures with information eligibility, full multi-task counts, transferred policy benefit, and omitted-information/pixel-error diagnostics | Earlier baseline and robustness figures remain in the supplement. No favorable-case selection to manufacture diversity. |
| Case examples selected for a large gain | Use one fixed WDBC feature for all detailed reconstruction comparisons | Case rule specified before the new run; synthetic pairing example explicitly labeled. |
| Unsupported novelty and practical claims | Rewrote title, abstract, introduction and discussion around the actual limitation result | No claim of new quantile statistics, new minimax mathematics, human superiority or universal best charts. |
| Reproducibility gaps | Added complete protocol, raw recoveries, losses, fold choices, policies, error bounds, figures and verification | `reproduce_v3.py`; preserved v2 pipeline and exact parity for 2,286 fixed-setting five-task results. |
| Reader-study plan used the weaker comparator | Updated prospective protocol to compare frozen policies against task-matched defaults and the dense control | Protocol only: no invented recruitment, responses, approvals or power result. |

## What the new results support

The threshold observer shows a small positive transfer gain for tail asymmetry. That gain is uncertain under the alpha observer. The remaining five threshold-observer tasks have point estimates favoring the default; under the alpha observer, case-specific selection is worse for spread and upper-tail extent with descriptive intervals below zero. Exact values and intervals are generated in `validation_v3/results/findings.tex`, `paired_effects.csv`, and `policy_summary.csv`.

The earlier secondary experiment made ECDFs appear superior for 19 quantiles when the quantile competitor had only five markers. Once the directly matched 19-marker control is admitted, that advantage disappears. The revised paper makes this comparator issue a central finding.

These results favor a more limited contribution: an executable audit showing how task alignment, missing information and computational observer choices constrain claims for chart selection. They do not demonstrate the originally hoped-for broadly useful adaptive selector.

## Remaining evidence gaps — not solved by rewriting

1. **Human outcomes.** Neither decoder is calibrated against readers. Human estimation error, time, cognitive effort, confidence and accessibility have not been measured. The prospective protocol is prepared; the study is not performed.
2. **Untouched external validation.** All nine resources were available during development. Resource-disjoint selection and display transfer help diagnose generalization but are not an independent external population or laboratory replication.
3. **Breadth and novelty.** Six related quantile-based targets do not establish performance for means, associations, temporal trends, multimodality detection, uncertainty interpretation or pairing-dependent tasks. The mathematical ingredients are elementary or established. Strong journal positioning needs a compelling empirical or methodological contribution beyond this computational audit.
4. **Data limitations.** Previously disclosed CKD values, unresolved retinopathy participant linkage, small wrist sample and excluded Parkinsons identifier discrepancy remain documented. No missing identifiers or corrected source measurements were invented.
5. **Practical benefit.** The current evidence does not establish a meaningful advantage for case-specific chart selection over a task default. A future positive claim must survive the same strong controls and a prospectively defined useful-effect threshold.

A top-1% readiness claim would therefore be unsupported. The current package is suitable for critical scientific review and planning the decisive next study; it should not be submitted with claims that these remaining validations have already occurred.

## Files

- `main.pdf`, `main.tex`: current manuscript.
- `supp.pdf`, `supp.tex`: detailed contracts, earlier audit, new protocol and complete policy summaries.
- `validation_v3/figures/`: four vector PDF and high-resolution PNG figures.
- `validation_v3/results/verification.json`: numerical verification report.
- `validation_v3/results/decoded_trials.csv`: every recovered quantile vector and corresponding empirical evaluation target; targets are not decoder inputs.
- `validation_v3/results/folds.csv`: resource-disjoint training and chosen defaults.
- `validation_v3/results/policy_results.csv`: per-case frozen-policy transfer results.
- `validation_v3/results/quantile_error_decomposition.csv`: direct-control encoding and raster error records.
- `READER_STUDY_PROTOCOL.md`: revised prospective study, not performed.
- `archive/v2_manuscript/`: the preceding manuscript preserved for comparison.

The original code/data provenance and source limitations remain in `DATA_PROVENANCE.md`. `reproduce_v3.py` reproduces the new extension; `reproduce_strengthened.py` reproduces the preserved v2 audit. The current main document requires outputs from both, which are included. Nothing has been published or submitted to a journal or repository by this revision.
