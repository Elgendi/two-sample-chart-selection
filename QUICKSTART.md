# Four examples in a few commands

Run these commands from the unpacked package root after installing `requirements.txt`.

```bash
python benchmark_release/score_and_compare.py task_first/examples/spread.csv --task spread --output-dir example_spread
python benchmark_release/score_and_compare.py task_first/examples/composition.csv --task composition --output-dir example_composition
python benchmark_release/score_and_compare.py task_first/examples/profile.csv --task profile --output-dir example_profile
python benchmark_release/score_and_compare.py task_first/examples/association.csv --task association --output-dir example_association
```

Each output folder contains:

- `input.json`: exact analyzed input, including any declared transformation.
- `trials.csv`: every placement loss and any failure.
- `scores.csv`: all candidate losses and scores at both displays.
- `summary.json`: reference choice, tied choices, empirical-trained default, and their test losses.

Read `gain` first: **default loss minus selected loss**. A positive value favors selection for this task and decoder; a negative value favors the fixed default. It says nothing about reading speed or human comprehension. A score near 100 means small error under the implemented task loss, not universal chart quality.

## CSV formats

| Task flag | Columns | Meaning |
|---|---|---|
| `median`, `spread`, `five` | `A,B` | Two groups; blank padding allowed; at least four finite values each |
| `composition` | `category,value` | 2–8 unique categories; nonnegative counts or shares with a positive total |
| `profile` | `time,value` | At least 12 nonnegative values; twelve equal-duration bins must be populated and have varying means |
| `association` | `x,y` | Finite paired values with nonzero variance; at most 64 systematically spaced pairs are displayed |

`--observer soft` evaluates the second color reader. Do not pool its results with the primary reader or choose the observer because it gives a favorable result.

The older `score_task.py` and `score_my_data.py` interfaces remain for provenance and familiar-only exploration. Use `benchmark_release/score_and_compare.py` for the final paper's expanded candidate comparison. The separate geometry reader is a sensitivity experiment for composition, not an additional primary selector.
