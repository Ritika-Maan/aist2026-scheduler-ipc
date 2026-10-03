"""python -m harness.cli --config harness/configs/baseline.json --out results [--n-sets N]"""
import argparse
import os

from .aggregate import paired_differences, summarize
from .conditions import load_config, required_min_wcet
from .plotting import blocking_distributions, regime_map
from .report import headline, verdict_text, write_summary
from .runner import run_matrix
from .taskgen import generate_task_sets


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="harness/configs/baseline.json")
    ap.add_argument("--out", default="results")
    ap.add_argument("--n-sets", type=int, default=None, help="override settings.n_task_sets")
    ap.add_argument("--prefix", default="baseline")
    a = ap.parse_args(argv)

    settings, conditions = load_config(a.config)
    if a.n_sets:
        settings.n_task_sets = a.n_sets
    os.makedirs(a.out, exist_ok=True)
    us = sorted({c.utilization for c in conditions})
    bank = generate_task_sets(us, settings.n_task_sets, settings.n_tasks, settings.period_grid,
                              settings.base_seed, min_wcet=required_min_wcet(settings, conditions))
    result = run_matrix(conditions, bank, settings, progress=True)
    summary = summarize(result)
    paired, diffs = paired_differences(result)

    p = lambda name: os.path.join(a.out, name)          # noqa: E731
    result.raw.to_csv(p(f"{a.prefix}_raw.csv"), index=False)
    summary.to_csv(p(f"{a.prefix}.csv"), index=False)
    paired.to_csv(p(f"{a.prefix}_paired.csv"), index=False)
    diffs.to_csv(p(f"{a.prefix}_paired_diffs.csv"), index=False)
    result.blocking.to_csv(p(f"{a.prefix}_blocking_samples.csv.gz"), index=False)
    write_summary(p(f"{a.prefix}_summary.md"), summary, paired, settings, bank.rejected)
    regime_map(paired, p("regime_map.png"))
    blocking_distributions(result.blocking, summary, p("blocking_distributions.png"))
    print(verdict_text(paired))
    print(headline(paired))


if __name__ == "__main__":
    main()
