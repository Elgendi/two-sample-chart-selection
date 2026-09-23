# Choosing scientific visualizations through task-first optimization — v5.0.1

Read `main.pdf` and `supp.pdf`. The manuscript retains the worked-score example, eight familiar-chart examples and coverage overview, with full strong-default, decoder and synthetic comparisons in the main paper. `REVISION_REPORT.md` maps reviewer concerns to changes and remaining limits.

## Reproduce

Verified with Python 3.12.14. Use Python 3.12 with the pinned dependencies. From the repository root:

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Then run:

```bash
python reproduce_benchmark.py --full --pdf
```

The numerical run is offline and uses the bundled source data. PDF compilation requires TeX Live and latexmk. Use `--verify` to audit saved results or `--figures --pdf` to regenerate figures and documents. `python benchmark_release/check_examples.py` checks all four user-facing CSV examples. `QUICKSTART.md` describes those examples. Runtime depends on hardware; allow roughly 10–25 minutes for a full rebuild.

Main figures and claims map to their source data in `benchmark_release/RESULTS_MAP.md`. The scoring example uses a retained secondary tuning search; the full inference uses fixed configurations and strong defaults. Archived analyses are provenance, not independent validation.

This release contains the complete computational record, including `rendered_study/`, raw inputs, saved benchmark outputs, and verification reports. See `GITHUB_UPDATE.md` for instructions to synchronize an existing checkout. Preparing this package does not update the remote repository.

## Interpretation

Losses measure algorithmic recovery of specified numerical information. They do not measure human comprehension. Neither the main results nor the synthetic stress tests establish universal benefit from adaptive chart selection. Genuine ties and all candidate failures remain reported. The planned reader study is unperformed; see `READER_STUDY_PROTOCOL.md`.

Before journal submission, read `SUBMISSION_NOTES.md`. No top-percentile placement or acceptance is guaranteed. Dataset terms and inherited code rights are in `DATA_PROVENANCE.md` and `LICENSE_NOTICE.md`.

## Repository guide

- `benchmark_release/`: final comparisons, independent audits, scoring interface, and result-to-figure map.
- `rendered_study/`, `validation_v3/`, `task_first/`: rendering and primary benchmark implementations.
- `data/`: bundled inputs and dataset attribution; see `DATA_PROVENANCE.md`.
- `main.tex`, `supp.tex`, `figures/`, `reader_figures/`: manuscript and presentation sources.
- `archive/`, `validation_v2/`, `revision/`, `legacy_compression/`: historical analyses retained for provenance.
- `reader_study/`: planned reader-study materials; no completed human experiment is claimed.

Start with `QUICKSTART.md` to score your own CSV. `select_chart.py` is a historical interface; use `benchmark_release/score_and_compare.py` for the current comparison.
