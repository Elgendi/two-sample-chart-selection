# Revision history

## Rendered-chart benchmark update

- Replace the default compression selector with the pixel-recovery benchmark.
- Score five two-sample quantile differences on a positive 0–100 scale; score order determines selection.
- Include all 37,548 trials, 21 settings and seven implemented families, with a documented 15-family catalogue.
- Separate 127 primary comparisons from 22 excluded exploratory comparisons.
- Include the revised manuscript and Figures 2–3 showing large versus limited numerical gains; retain resolution sensitivity as Supplementary Figure S1.
- Provide the updated CLI, pinned dependencies, software checks and reproducibility entry point.
- Preserve earlier compression analyses as explicitly historical material.

This is a computational development benchmark. Human-reading performance is unvalidated; 77 of 127 winning family sets change between the smallest and largest resolutions.
