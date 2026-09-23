# Current revision: pixel-based chart recovery

The manuscript and all three main figures have been rebuilt around actual rendered-chart recovery. The previous compression score was removed from the current manuscript, along with Size, E/t and qualification thresholds. Scores now determine descending order directly. Genuine numerical ties are retained; no log transform or chart offset fabricates separation. Raw dots are not forced to the bottom.

The package screens a catalogue of 15 families and evaluates 21 settings from seven implemented families for one marginal two-group task. It does not claim all 15 are numerically optimized. Every evaluated setting is disclosed in CSV; main examples show every implemented family.

The new experiment is a development benchmark with a specified computational observer, not a validated model of human reading. Human improvement, universal optimality, clinical impact and submission to a top-percentile journal are not established by this analysis. No held-out observer validation or completed reader study is included.

Software checks test access restrictions, pixel dependence and numerical consistency. Rendering sensitivity uses three resolutions and four realizations; it does not estimate sampling uncertainty. See `rendered_study/results/summary.json` for measured results and `checks.json` for executed checks.

Before submission: freeze and deposit the release, confirm author statements and source permissions, independently evaluate the observer on held-out data, and conduct the planned human-reader validation if the paper is to claim perceptual benefit. Historical compression simulations cannot serve as validation of the new pixel score.

## Figure clarity revision
Figure 2 now uses WDBC worst fractal dimension, HAR gyroscope-jerk variability and Cleveland oldpeak, selected after inspection for clear renderings and substantial computed gains. Figure 3 now uses Wrist mean HR and BIDMC mean HR to show zero and small incremental gains over already-high-scoring mean bars. Lower contrast plots make the score's target recovery visible. Raw scored pixels, benchmark settings and numerical results are unchanged. The former Figure 3 robustness analysis is retained as Supplementary Figure S1. These selections are illustrative, not an unbiased estimate of reader benefit.
