# Different data, different optimal familiar charts

The main figures search seven familiar families across 21 settings. The best choice means the smallest computational recovery error **within that declared set**, for the stated question and rendering conditions. No winner is assigned in advance.

## Figure 1: calculate a score

The question is: how does the difference between two groups change from low to high values? We evaluate five positions in sorted data (10th, 25th, 50th, 75th and 90th percentiles). The 50th percentile is the middle value.

1. Calculate the true differences from the data.
2. Render every candidate and recover these differences from its pixels.
3. Average absolute errors across five positions and four placements.
4. Divide by the pooled within-group standard deviation (data spread).
5. Calculate score = 100 / (1 + normalized error).

For patient-level median ECG and pulse rates, the selected raw-dot plot has average absolute error 0.2056746661 beats/min and data spread 12.3416932106 beats/min. The normalized error is 0.0166650283 and the score is **98.36**. The figure compares each family's best setting; the software reports every setting. This is not 98.36% correct readers.

## Figure 2: different datasets select different families

For maximum heart rate, a violin improves the score from **85.67 to 98.01**. For blood enzyme concentration, a histogram improves it from **85.41 to 97.49**. Both use the same question and search settings. Larger scores mean lower computational recovery error. These examples were chosen for explanation; they do not estimate the average benefit.

## Figure 3: keep an already optimal chart

For early versus late exercise heart rate, mean bars already score **95.35**, higher than the tested alternatives. Optimization keeps the chart: improvement **0.00 points**. This uses the same question as Figures 1–2. A mean-only chart can approximate this sample's contrasts without preserving distributions in general.

Across all 127 comparisons, the winning families are heatmap 54, dot plot 39, histogram 18, violin 13 and mean bars 3. Box and interval plots have zero wins for this task. Different datasets *can* have different optima; the method does not require that every dataset or every family have a different winner.

## Run the optimizer

From the full reproducibility archive:

```bash
pip install -r requirements.txt
python score_my_data.py reader_figures/example_input.csv --output-dir my_scores
python score_my_data.py my_data.csv --x-column control --y-column treatment --output-dir my_scores
```

Default CSV columns are A and B. Both must measure the same variable in the same units; unequal lengths can be padded with blanks. Default search: seven families, 21 settings. Outputs include every setting's score, per-placement errors, all tied optima, a selected raster and calibration metadata. Zero pooled SD is rejected.

Specialized ECDF and direct-marker controls remain available explicitly:

```bash
python score_my_data.py my_data.csv --include-specialized --output-dir expanded_scores
```

This expands the search to 24 settings and can change the winner. Supplementary specialized controls often outperform the familiar set; they have not been discarded as evidence. The main claim is restricted optimization, not universal superiority of familiar charts. Optional tasks (`--task median`, `spread`, `asymmetry`, `upper_tail`, `dense19`) change the question; none recovers pairing-dependent changes.

To regenerate figures, run `python reader_figures/make_figures.py`. PDF/SVG exports contain vector labels and exact scored rasters; PNG copies are supplied. CSVs and JSON checks retain scores, winner counts and provenance. The figure pack requires the full code/data archive to regenerate figures.
