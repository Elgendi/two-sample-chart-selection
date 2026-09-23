# Seventeen worked examples of familiar-chart optimization

## Figure 1: a visible difference and a worked score

The new example compares **cell-nucleus area in benign and malignant samples** (WDBC mean area, 357 and 212 records). The larger values and wider spread are visible in the selected raw-dot plot. Mean bars score **60.17**; raw dots score **97.70**.

The question is the same throughout all three figures: how does the difference between two groups change from low to high values? We check five positions in sorted data (10th, 25th, 50th, 75th and 90th percentiles). The 50th percentile is the middle value.

1. Calculate the true differences from the data.
2. Render all 21 familiar-chart settings and recover these differences from their pixels.
3. Average absolute errors across five positions and four placements.
4. Divide by pooled within-group standard deviation (data spread).
5. Calculate **score = 100 / (1 + normalized error)**.

For the selected raw dots, average absolute error is **5.85355**, data spread is **248.3973**, and normalized error is **0.023565**, giving **97.70**. Higher means more accurate computational recovery for this question. It is not a percentage of correct readers. The seven family scores in Figure 1 are each family's best valid setting; the code reports all 21 settings.

## Figure 2: eight successes, four different winning families

The eight examples span six source resources. They were chosen retrospectively for illustration: two winners per non-bar winning family, all with more than ten score points gained over mean bars. They are not a random sample or a population estimate of benefit.

| Panel | Input feature | Selected chart | Before | After | Gain |
|---|---|---|---:|---:|---:|
| 2a | WDBC__23: worst area | Dot plot / raw | 56.26 | 97.50 | +41.24 |
| 2b | CKD__03: bu | Dot plot / raw | 59.05 | 98.32 | +39.28 |
| 2c | HAR__29: tBodyGyroJerk-std()-Z | Histogram / 32 | 48.15 | 94.96 | +46.81 |
| 2d | HeartFailure__01: creatinine_phosphokinase | Histogram / 8 | 85.41 | 97.49 | +12.09 |
| 2e | Cleveland__04: oldpeak | Violin plot / 256 | 64.22 | 92.84 | +28.62 |
| 2f | Wrist__04: SD | Violin plot / 8 | 66.20 | 90.35 | +24.15 |
| 2g | HAR__36: tBodyGyroMag-mean() | Heatmap / 64 | 47.57 | 96.86 | +49.29 |
| 2h | CKD__02: bgr | Heatmap / 64 | 57.00 | 98.70 | +41.70 |

The score gains range from **12.09 to 49.29 points**, with **79.1–98.3% less computational recovery error**. Error reduction is 100 × (1 − selected loss / starting loss); it is not the score-point change or measured improvement in understanding.

## Figure 3: eight smallest score gains

These are the **eight smallest gains over mean bars among the 122 comparisons where mean bars decoded successfully**. Three keep mean bars. Five select another family and add 1.13–2.46 score points. Since starting errors are already small, those five gains still reduce recovery error by 19.9–57.0%. No human-equivalence threshold is claimed.

| Panel | Input feature | Selected chart | Before | After | Gain |
|---|---|---|---:|---:|---:|
| 3a | Wrist__00: mean | Bar chart / means | 95.35 | 95.35 | +0.00 |
| 3b | Wrist__01: median | Bar chart / means | 95.64 | 95.64 | +0.00 |
| 3c | Wrist__03: q90 | Bar chart / means | 95.48 | 95.48 | +0.00 |
| 3d | BIDMC__03: q90 | Dot plot / raw | 96.53 | 97.66 | +1.13 |
| 3e | Wrist__02: q10 | Violin plot / 16 | 93.57 | 94.78 | +1.22 |
| 3f | ILPD__06: total_protein | Dot plot / raw | 95.70 | 97.16 | +1.46 |
| 3g | WDBC__04: mean smoothness | Dot plot / raw | 95.84 | 98.11 | +2.27 |
| 3h | BIDMC__02: q10 | Histogram / 64 | 95.60 | 98.06 | +2.46 |

“Lower”, “middle” and “higher” heart rate name input summaries for each participant; the scoring task still compares the same five distributional gaps across participants. Several examples share source cohorts, so these are not independent clinical replications. Wrist examples contain eight participants. A mean-only chart can approximate contrasts without retaining the full distributions.

## How to read the charts

Group numbers 1 and 2 match the colored group labels. Bars, dots and violins use vertical measurement axes. Histograms use horizontal measurement axes and percentage heights. Heatmaps use horizontal measurement axes and darker blue for more observations per bin; the two strips are arranged as rows 1 and 2. CKD blood glucose is the source's random-glucose field. WDBC “largest nuclei” uses its worst-area feature, the mean of the three largest values for that sample.

The displayed charts contain original scored pixels, without contrast enhancement. Histogram views crop empty probability-axis space; heatmap views crop empty margins and stack strips. Scores are evaluated on the original 256-pixel square panels, **not on the resized publication composites**. Measurement limits and colors are unchanged. Only the first placement is displayed; errors average all four placements.

`Expanded_example_gallery.pdf` contains the worked scoring figure followed by enlarged copies of all 16 example cards. Individual vector cards are in `figures/panels/`. The main PDF/SVG/PNG figures remain eight-panel layouts. Exact values and source checks are in `figure_values.csv` and `figure_checks.json`; source features, group sizes and settings are also listed in Supplementary Section S17.

## Run the optimizer

From the full reproducibility archive:

```bash
pip install -r requirements.txt
python score_my_data.py reader_figures/example_input.csv --output-dir my_scores
python score_my_data.py my_data.csv --x-column control --y-column treatment --output-dir my_scores
```

The example CSV now reproduces Figure 1's **WDBC mean-area** results. Default columns are A and B; measure the same variable in the same units, padding unequal lengths with blanks. The default search evaluates seven families and 21 settings and retains all tied optima. Zero pooled SD is rejected.

```bash
python score_my_data.py my_data.csv --include-specialized --output-dir expanded_scores
python reader_figures/make_figures.py
python reader_figures/make_gallery.py
```

The optional specialized controls expand the candidate set and can change the winner. Their stronger results remain disclosed in the Supplement. Optional tasks (`--task median`, `spread`, `asymmetry`, `upper_tail`, `dense19`) change the question; none reconstructs pairing-dependent changes.

The full reference analysis still has 127 comparisons: heatmaps win 54, dots 39, histograms 18, violins 13 and mean bars three. Box and interval plots do not win this particular task. A best chart means best **within the declared candidate set, task and computational observer**, not universally best or proven easiest for people.
