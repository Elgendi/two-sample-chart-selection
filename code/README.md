# Source preparation

`prepare.py` rebuilds the complete comparison arrays from bundled sources. The final pipeline first verifies raw hashes and independently reconstructs the frozen wrist summary from WFDB annotations in `benchmark_release/rebuild_inputs.py`.

`fetch.py` documents the original network acquisition route. It is not invoked by offline reproduction. The final study is run using `python reproduce_benchmark.py --full` from the package root. Historical compression and selection scripts are not the current primary analysis.
