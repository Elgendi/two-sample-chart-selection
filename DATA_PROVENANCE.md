# Source attribution and transformations

The seven new UCI archives and CKD CSV were acquired for this revision on 19 September 2026. WDBC, BIDMC and wrist source copies were retained from the supplied earlier reproducibility package (its provenance records access on 13 September 2026). Every bundled raw file has a SHA-256 checksum in `data/raw_checksums.json`. URLs and acquisition hashes appear in `data/download_manifest.json` and `data/base_download_manifest.json`.

| Resource | Source and attribution | Analysed source |
|---|---|---|
| WDBC | Wolberg, Mangasarian and Street contributors; [UCI, DOI 10.24432/C5DW2B](https://doi.org/10.24432/C5DW2B) | 569 records; the supplied labelled scikit-learn representation, with feature values retained and source record IDs omitted. Target 0 malignant, 1 benign. A source-to-CSV acquisition fallback is included. |
| Cleveland | Janosi, Steinbrunn, Pfisterer and Detrano; [UCI, DOI 10.24432/C52P4X](https://doi.org/10.24432/C52P4X) | Only `processed.cleveland.data` from Heart Disease archive. Five numeric features. |
| Heart Failure | Chicco and Jurman; [UCI, DOI 10.24432/C5Z89R](https://doi.org/10.24432/C5Z89R) | `heart_failure_clinical_records_dataset.csv`; six numeric features, excluding follow-up time. |
| CKD | Rubini, Soundarapandian and Eswaran; [UCI, DOI 10.24432/C5G020](https://doi.org/10.24432/C5G020) | Official CSV: `https://archive.ics.uci.edu/static/public/336/data.csv`; 11 fields, complete observations separately by field. wbcc/rbcc renamed wc/rc. |
| ILPD | Ramana and Venkateswarlu; [UCI, DOI 10.24432/C5D02C](https://doi.org/10.24432/C5D02C) | Nine numeric fields; disease label 1 versus 2. Four missing albumin/globulin ratios retained as exclusions. |
| Parkinsons | Max Little; [UCI, DOI 10.24432/C59C74](https://doi.org/10.24432/C59C74) | Only `parkinsons.data`, not the telemonitoring file in the same archive. Medians of 22 features in 32 observed identifier groups. Documentation states 31 people: unresolved. |
| Retinopathy | Antal and Hajdu; [UCI, DOI 10.24432/C5XP4P](https://doi.org/10.24432/C5XP4P) | `messidor_features.arff`, nonbinary columns 2–17. No patient linkage supplied. |
| Smartphone HAR | Reyes-Ortiz, Anguita, Ghio, Oneto and Parra; [UCI, DOI 10.24432/C54S4K](https://doi.org/10.24432/C54S4K) | Nested `UCI HAR Dataset.zip`; 40 time-domain mean/std fields, subject/activity medians from train and test files. Sitting versus walking. |
| BIDMC | Pimentel, Johnson, Charlton and Clifton; [PhysioNet v1.0.0, DOI 10.13026/C2208R](https://physionet.org/content/bidmc/1.0.0/) | 53 Numerics CSV and Fix metadata files; 46 source patients; 25,361 paired-valid positive readings, excluding 132 other rows. Existing monitor outputs. |
| Wrist exercise | Alexander J. Casson; [PhysioNet v1.0.0, DOI 10.13026/C2PQ1X](https://physionet.org/content/wrist/1.0.0/) | 19 annotation/header pairs, eight participants. ECG reference R peaks only; 1,364 five-second median-HR bins. No PPG algorithm. |

UCI sources are distributed under Creative Commons Attribution 4.0 as specified on their repository pages. PhysioNet BIDMC and Wrist sources retain the Open Data Commons Attribution License v1.0: <https://opendatacommons.org/licenses/by/1-0/>. Original dataset files and source terms are not replaced by a blanket new package licence. Analysed subsets and derived tables are transformations of these attributed sources.

Relevant original physiological-data papers: Pimentel et al., *Towards a Robust Estimation of Respiratory Rate from Pulse Oximeters*, IEEE TBME 64, 1914–1923 (2017), DOI 10.1109/TBME.2016.2613124; Jarchi and Casson, *Description of a Database Containing Wrist PPG Signals Recorded during Physical Exercise with Both Accelerometer and Gyroscope Measures of Motion*, Data 2(1), 1 (2017), DOI 10.3390/data2010001. Platform attribution: Pollard et al., *PhysioNet as a global platform for biomedical research*, Nature Health (2026), DOI 10.1038/s44360-026-00096-z.

The source archives can contain additional resources and fields not analysed here. The ten resource count refers to the table above, not the number of individual files or columns. `prepare.py` is the authoritative transformation record. The original slide deck and Abela chart are not redistributed in this package; the new flowchart is independently drawn.


## Revised audit
The primary revision contains nine resources and 127 feature comparisons. Parkinsons (22 comparisons) is retained only as excluded exploratory material because 32 identifier prefixes cannot be reconciled with 31 documented people. `revision/results/parkinsons_identifier_audit.csv` lists every prefix.

CKD potassium values 39 and 47 occur at one-based data rows 62 and 129 of the original CSV. Their units/accuracy remain unverified. They are preserved in primary arrays; a separately labelled sensitivity analysis omits them without correction or rescaling. `revision/results/ckd_flagged_rows.csv` and `ckd_sensitivity.csv` record the audit.

The simulations in `revision/results/simulation_cases.csv` are newly generated synthetic data, not source-database observations or reader-study data. Figure 4d is an analytical paired-data counterexample. Original files and prepared arrays were not overwritten.

## Current pixel-observer revision
The rendered-chart study uses the same prepared arrays without changing observations. Historical compression simulations and source-omission results are archived and do not validate the current observer. Current results are under `rendered_study/results/`. Primary exclusion of 22 Parkinsons comparisons remains unchanged.

## Strengthened version 2
The 127 primary arrays remain unchanged. `validation_v2/results/` contains the new 23-setting, two-observer analyses. Its CKD potassium omission sensitivity removes the values 39 and 47 without correction; this is distinct from the archived compression sensitivity. Retinopathy omission removes its 16 feature comparisons from winner summaries without changing the other arrays. The 72 newly generated synthetic comparisons use the explicit regimes and seed in `validation_v2/protocol.json`; they are synthetic observations, not people or reader responses. Resource-disjoint tests are retrospective because the source resources were already available during development.


## Task-first extension
The 24 empirical compositions, 72 heart-rate profiles and 53 association inputs are derived from existing supplied resources, not newly recruited cohorts. Record shares do not estimate population prevalence. BIDMC repeated recordings retain their original source-patient dependence. All 48 synthetic compositions are explicitly labeled; Dirichlet seed 20260921. `task_first/results/inputs.json` and provenance hashes record the evaluated inputs. Original unresolved source issues and exclusions remain unchanged.

## Final strong-default benchmark (release 4.0)

Primary comparisons retain the same source observations. The final analysis weights resources equally and uses source-patient identifiers for repeated BIDMC recordings and wrist participant identifiers for profiles. New synthetic inputs use seed 2026092201 and are separately stored under `benchmark_release/results/new_synthetic_inputs.json`.

`benchmark_release/rebuild_inputs.py` independently reconstructs all 1,364 wrist five-second median-HR bins from the 19 supplied `.atr`/`.hea` pairs using the [WFDB annotation format](https://wfdb.io/spec/annotation-files.html). Normal-beat intervals determine `60/RR`; each interval is assigned to its ending beat's five-second bin. No physiological-range correction or threshold is applied. Reconstruction agrees with the inherited frozen CSV within 1e-12; the frozen CSV is preserved. All source files are checked against their inherited SHA-256 values and all prepared group arrays are rebuilt exactly.

The new geometry reader and synthetic trials introduce no new human participants. Existing source uncertainties and original terms remain in force. This package is the supplied final artifact; the remote repository has not been changed by this revision.
