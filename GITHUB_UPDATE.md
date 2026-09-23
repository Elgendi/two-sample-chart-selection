# Update the existing GitHub repository

This ZIP is a complete source snapshot, not a Git history or an automatic remote update.

1. Clone `https://github.com/Elgendi/two-sample-chart-selection` or open your existing checkout. Commit or back up any local work first.
2. Create a branch, for example `git switch -c release-v5.0.1`.
3. Copy the **contents** of the extracted `two-sample-chart-selection` folder into the checkout root, including `.gitignore`. Do not copy the enclosing folder as a nested directory. Keep the checkout's `.git` directory.
4. From the checkout root, install `requirements.txt` and run:

```bash
python reproduce_benchmark.py --verify
python benchmark_release/check_examples.py
```

For complete numerical regeneration, run `python reproduce_benchmark.py --full`. Add `--pdf` if TeX Live and latexmk are installed.

5. Review `git status` and `git diff --stat`. Confirm `rendered_study/`, `data/raw/har.zip`, and `benchmark_release/` are included. This snapshot preserves historical source folders; review files present only in your checkout separately rather than deleting them automatically.
6. Stage the reviewed files, commit, and push the branch:

```bash
git add .
git commit -m "Publish complete task-first chart-selection benchmark v5.0.1"
git push -u origin release-v5.0.1
```

7. Review and merge the branch on GitHub. Check a fresh clone with `python reproduce_benchmark.py --verify` before using the public repository as the submission's reproduction source.

Use Git or GitHub Desktop for the full snapshot; it contains many files. The ZIP itself can also be attached as a GitHub release asset. No remote changes were made while preparing this package.

`SHA256SUMS.txt` records snapshot file hashes before users regenerate outputs. Existing dataset terms and code rights remain as stated in `DATA_PROVENANCE.md` and `LICENSE_NOTICE.md`; this packaging update does not introduce a software licence.
