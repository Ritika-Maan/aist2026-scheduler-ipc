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
    ap.add_argument("--extended", action="store_true",
                    help="also write controls / sweeps outputs (needs the extended config)")
    ap.add_argument("--baseline-csv", default=None,
                    help="with --extended: committed baseline.csv to regression-check the 40 baseline conditions")
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
    if a.extended:
        write_extended(a, p, settings, result, summary, paired)
    print(verdict_text(paired))
    print(headline(paired))


def write_extended(a, p, settings, result, summary, paired):
    import pandas as pd
    from .plotting import regime_map
    from .sweeps import (control_flips, control_table, cs_sweep, cs_sweep_plot, ipc_effect,
                         latency_sweep, latency_sweep_plot, protocol_effect, write_extended_summary)
    raw = result.raw
    ok, note = True, "no baseline.csv given; regression check skipped"
    if a.baseline_csv:
        ref = pd.read_csv(a.baseline_csv)
        cur = summary.set_index("condition").loc[ref["condition"]]
        cols = [c for c in ("miss_rate_mean", "miss_rate_sd", "max_lateness_mean", "blocking_frac_jobs",
                            "blocking_max") if c in ref]
        ref = ref.set_index("condition")
        bad = [(cid, c) for cid in ref.index for c in cols
               if not (abs(float(cur.loc[cid, c]) - float(ref.loc[cid, c])) <= 1e-12
                       or (pd.isna(cur.loc[cid, c]) and pd.isna(ref.loc[cid, c])))]
        ok = not bad
        note = (f"all {len(ref)} baseline conditions reproduce {a.baseline_csv} exactly "
                f"({', '.join(cols)})." if ok else f"MISMATCH in {bad[:5]} ...")
        if not ok:
            print("!!! REGRESSION FAILURE: " + note)
    ctrl, flips = control_table(summary, paired, 0.9), control_flips(paired)
    proto, effect = protocol_effect(paired, 0.9), ipc_effect(raw)
    cs, lat = cs_sweep(raw, summary, paired), latency_sweep(raw, summary, paired)
    pre = a.prefix
    ctrl.to_csv(p(f"{pre}_control_summary_U0.9.csv"), index=False)
    flips.to_csv(p(f"{pre}_control_flips.csv"), index=False)
    effect.to_csv(p(f"{pre}_ipc_effect.csv"), index=False)
    cs.to_csv(p(f"{pre}_cs_sweep.csv"), index=False)
    lat.to_csv(p(f"{pre}_latency_sweep.csv"), index=False)
    cs_sweep_plot(cs, p("cs_fraction_sweep.png"))
    latency_sweep_plot(lat, p("latency_sweep.png"))
    regime_map(paired, p("regime_map_extended.png"))
    write_extended_summary(p(f"{pre}_controls_and_sweeps.md"), summary, paired, raw, settings, ok, note,
                           ctrl, flips, proto, effect, cs, lat)
    print(f"regression check: {'PASS' if ok else 'FAIL'} - {note}")
    print(f"control flips: {int(flips['flip'].sum())} of {len(flips)} control cells")


if __name__ == "__main__":
    main()
