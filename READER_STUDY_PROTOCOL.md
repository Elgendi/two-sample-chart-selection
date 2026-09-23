# Prospective reader validation — protocol draft, not performed

## Objective and claim
Test whether the frozen computational selector improves human numerical estimation relative to a strong task-matched default, and whether its pixel-recovery loss predicts human error beyond chart family. This document contains no recruited participants, ethical approval, registered protocol, power result or human observations. It must be finalized and registered before confirmatory data collection.

## Development, pilot and final test separation
Use different datasets for development, pilot and confirmatory testing. Split related participants/recordings together. The public inputs in this computational paper are development examples and must not become the untouched confirmatory set. Record case identities, transformations, numerical targets, source provenance and display parameters in a private truth manifest. Freeze the candidate set, computational algorithm, selected chart, defaults, exclusion rules and all analysis code before final testing. Do not select test cases to obtain a desired winner or favorable gain. Use a documented sampling scheme covering weak, strong and reversed predicted gains.

## Experimental conditions
For each task, compare the frozen selector with a strong task-matched default chosen only from development data. Include explicit percentile-marker controls for distributional questions. Use equal display area, matched axes, consistent labels/colors and fixed viewing conditions. Render each final stimulus once and retain its checksum. A default and selector may choose the same chart; retain that case and identify it, rather than forcing different stimuli.

Counterbalance chart assignment across participants and cases. Each participant should see a given dataset only once, while each dataset is evaluated in each applicable condition across different participants. Randomize trial order within task blocks and counterbalance block order. Keep practice examples separate. Log actual display size and timing, browser zoom, technical interruptions and accessibility accommodations. Participants receive scientific labels and a numerical question, without scores, winner labels or study hypotheses.

## Outcomes and scoring
Primary outcome: numerical estimation error, evaluated separately for each task using the frozen definitions below. These are human responses, not pixel-decoder outputs.

| Task | Requested response | Error |
|---|---|---|
| Median difference | Group B minus group A median | Absolute error / pooled within-group SD |
| Spread difference | Group B minus group A interquartile range | Absolute error / pooled within-group SD |
| Five distributional gaps | Five differences at 10, 25, 50, 75 and 90 percentiles | Mean absolute error / pooled within-group SD |
| Composition | Share of each displayed category | Half the sum of absolute share errors |
| Profile | Values at the twelve specified time positions | Mean absolute error / SD of true bin means |
| Association | Pearson correlation of displayed paired values | Absolute error / 2 |

Training must explain unfamiliar terms and check task comprehension without selecting participants according to favorable experimental responses. Exclude zero-scale or undefined-correlation cases before generating the frozen test set. Store each numerical response and its units. For composition, require nonnegative shares summing to 100% through a visible participant-facing rule; do not silently normalize invalid responses after collection.

Secondary outcomes: task completion time, confidence and confidence–accuracy calibration. Define timing as stimulus onset to final response submission; record interruptions separately. Missing answers and timeouts are outcomes with reasons, never zero-error responses. Freeze timeout duration and handling after the pilot. Report missingness by condition and conduct a prespecified sensitivity analysis.

## Analysis and uncertainty
Analyze each task separately. Estimate selector-minus-default human error using a prespecified repeated-measures model with participant and case effects; negative favors selection. Report raw task-scale differences and uncertainty, not only P values. Assess skew and model suitability on pilot data; freeze the final transformation/model and fallback before confirmatory collection. Account for all six primary task comparisons using Holm adjustment, unless one primary task is chosen before registration and the other five are explicitly secondary. No pooled task score is the primary endpoint.

Test incremental prediction by comparing a task/chart-family model against the same model plus frozen computational loss, with participant/case separation in predictive validation. Analyze novice versus experienced readers through prespecified interactions. Treat accuracy and time jointly in interpretation; a faster but less accurate response is not an unqualified improvement. Report identical-chart cases and technical failures explicitly.

## Sample size, ethics and release
Use a separate pilot to estimate participant and case variability and within-participant dependence. Choose a minimum meaningful human-error reduction with a substantive justification, then simulate the actual crossed allocation and planned multiplicity procedure to select participant and case counts for a prespecified power target. Do not substitute the computational error differences for human effect sizes. No sample size can be finalized from the current evidence alone.

Obtain institutional ethics review and informed consent before recruitment. Keep identifiers outside shared response files. Publish the registered protocol, frozen stimulus/truth manifests, analysis code and appropriately deidentified results subject to consent and data terms. Confirmatory outcomes must remain separate from this retrospective computational benchmark until collected and analyzed.
