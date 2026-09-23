# GitHub package verification

The packaged snapshot passed `python reproduce_benchmark.py --verify` (all three stages) and `python benchmark_release/check_examples.py` (all four CSV examples, 40 configuration losses; maximum difference approximately 1.01e-16).

The full 13-stage numerical rebuild was completed for the parent v5 release; see REPRODUCIBILITY_REPORT.md. This packaging update changes documentation and distribution housekeeping, not numerical methods. No remote repository update has been performed.
