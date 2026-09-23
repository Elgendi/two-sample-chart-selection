# Development record

This extension was developed retrospectively after the original 127-case results had been seen. It is not preregistered. The protocol defines the numerical comparisons before inspecting their aggregate outcomes.

During numerical fixture checks, the initial ECDF one-pixel stroke failed the strict color threshold after antialiasing and blur. The initial benchmark run was stopped before any aggregate results were computed; the stroke was changed to two target pixels. The change was motivated by a deterministic, known-input recovery failure, not a preferred winning chart. All final numerical results use the two-pixel stroke. The frozen protocol and source checksums are in results/run_manifest.json.

A heatmap pixel-dependence check uses erasure of half of the second group strip: vertical translation within a constant-color strip is correctly invariant and therefore is not a suitable dependence test for that encoding. Other displays use vertical displacement. Neither test measures human perception.
