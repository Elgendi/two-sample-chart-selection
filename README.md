# Choosing scientific visualizations through task-first optimization

**Version 5.0.1** · Mohamed Elgendi

A reproducible computational framework for comparing scientific charts according to the numerical information they need to communicate.

The workflow is simple: **define the task → render candidate charts → recover the target information → compare errors**. Candidates are scored under an explicit computational decoder, and selected charts are evaluated against strong fixed defaults under changed display conditions.

## Start here

| Your goal | Where to start |
|---|---|
| Read the paper | [Main manuscript](main.pdf) · [Supplementary information](supp.pdf) |
| Score your own data | [CSV formats and examples](QUICKSTART.md) |
| Reproduce the study | [Installation](#installation) and [Reproduction](#reproduction) below |
| Trace figures to results | [Results map](benchmark_release/RESULTS_MAP.md) |
| Check data sources and terms | [Data provenance](DATA_PROVENANCE.md) |

## What the framework evaluates

The benchmark covers six numerical tasks: median differences, spread differences, five-percentile differences, composition, ordered profiles, and association. It includes empirical data, synthetic stress tests, alternative decoders, and comparisons against strong defaults.

The paper uses simple worked examples and familiar charts to explain how task-specific selection works. **Higher scores indicate lower recovery error for the specified task and decoder.** Scores are not percentages of readers who understand a chart.

## Installation

Verified with **Python 3.12.14**. Use Python 3.12 and the pinned dependencies in `requirements.txt`. Run the following commands from the repository root.

**1. Create a virtual environment**

```bash
python -m venv .venv
```

**2. Activate it**

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Linux or macOS:

```bash
source .venv/bin/activate
```

**3. Install dependencies**

```bash
python -m pip install -r requirements.txt
```

## Try an example

Score the included spread-comparison example:

```bash
python benchmark_release/score_and_compare.py task_first/examples/spread.csv --task spread --output-dir example_spread
```

The output folder contains candidate scores, trial losses, the selected chart, and its comparison with the frozen default. For other tasks and your own CSV files, see [QUICKSTART.md](QUICKSTART.md).

## Reproduction

The numerical pipeline runs **offline using the bundled data** after dependency installation. A full numerical rebuild typically takes approximately **10–25 minutes**, depending on hardware.

| Action | Command |
|---|---|
| Rebuild the primary numerical results, tables, and figures | `python reproduce_benchmark.py --full` |
| Audit saved results | `python reproduce_benchmark.py --verify` |
| Check the four documented CSV examples | `python benchmark_release/check_examples.py` |
| Regenerate tables and figures and compile the PDFs | `python reproduce_benchmark.py --figures --pdf` |
| Rebuild the primary results and compile the PDFs | `python reproduce_benchmark.py --full --pdf` |

**PDF compilation additionally requires TeX Live and `latexmk`.** These are not needed to run the numerical benchmark.

Validation details are recorded in [REPRODUCIBILITY_REPORT.md](REPRODUCIBILITY_REPORT.md) and [GITHUB_PACKAGE_CHECK.md](GITHUB_PACKAGE_CHECK.md). The [results map](benchmark_release/RESULTS_MAP.md) connects manuscript figures and claims to their supporting outputs.

## Interpreting the results

- **What is measured:** recovery of specified numerical information from rendered chart pixels using explicit computational decoders.
- **How selection is evaluated:** comparison against strong defaults under changed display conditions, with sensitivity analyses for decoder choice and synthetic inputs.
- **What the evidence supports:** task- and decoder-specific comparisons; it does not establish a universal advantage for case-specific chart selection.
- **What remains untested:** human comprehension, reading speed, and reader preferences. The [reader-study protocol](READER_STUDY_PROTOCOL.md) describes planned work; no human-reader study was performed.

Genuine ties and candidate failures are retained. The worked scoring example uses a secondary tuning search, while the primary inference uses fixed configurations and strong defaults. Historical analyses are retained for provenance and are not additional independent validation.

## Repository structure

| Location | Contents |
|---|---|
| `benchmark_release/` | Current scoring interface, default comparisons, audits, reports, and result-to-figure map |
| `rendered_study/` | Chart rendering and pixel-recovery implementation |
| `validation_v3/`, `task_first/` | Primary benchmark implementations and task examples |
| `data/` | Bundled source data and prepared inputs |
| `main.tex`, `supp.tex`, `references.bib` | Manuscript and supplementary source files |
| `figures/`, `reader_figures/` | Manuscript figures and example galleries |
| `reader_study/` | Materials for the planned reader study |
| `archive/`, `validation_v2/`, `revision/`, `legacy_compression/` | Historical analyses and development provenance |

Use `benchmark_release/score_and_compare.py` for the current scoring comparison. Earlier interfaces, including `select_chart.py`, are retained for provenance.

## Data and code rights

Original datasets retain their source-specific terms and attribution requirements. See [DATA_PROVENANCE.md](DATA_PROVENANCE.md) for details and [LICENSE_NOTICE.md](LICENSE_NOTICE.md) for code rights. Public availability does not itself grant an open-source licence.

## Citation

Citation metadata are provided in [CITATION.cff](CITATION.cff). Please also cite the original datasets used in your analysis.
