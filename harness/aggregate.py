"""Aggregation: per-condition N / SD / 95% CI, and paired differences (D4)."""
import numpy as np
import pandas as pd

from .stats import t_interval

META = ["condition", "arm", "scheduler", "ipc", "protocol", "utilization", "intensity", "tag"]


def summarize(result):
    """One row per condition. Never a bare mean: n, sd, ci_lo, ci_hi accompany every mean."""
    raw = result.raw
    rows = []
    for cid, g in raw.groupby("condition", sort=False):
        row = {k: g.iloc[0][k] for k in META}
        for metric in ("miss_rate", "max_lateness"):
            n, mean, sd, lo, hi = t_interval(g[metric].to_numpy())
            row.update({f"{metric}_n": n, f"{metric}_mean": mean, f"{metric}_sd": sd,
                        f"{metric}_ci_lo": lo, f"{metric}_ci_hi": hi})
        row.update(n_task_sets=len(g), jobs_total=int(g["jobs"].sum()),
                   deadlock_sets=int(g["deadlock"].sum()), overload_sets=int(g["overload"].sum()),
                   effective_u_mean=float(g["effective_u"].mean()),
                   dropped_messages=int(g["dropped_messages"].sum()))
        rows.append(row)
    out = pd.DataFrame(rows)
    blk = blocking_stats(result.blocking)
    return out.merge(blk, on="condition", how="left")


def blocking_stats(blocking):
    """Pooled per-job blocking-time statistics (shared-memory conditions only)."""
    rows = []
    for cid, g in blocking.groupby("condition", sort=False):
        b = g["blocking"].to_numpy()
        pos = b[b > 1e-9]
        rows.append(dict(condition=cid, blocking_jobs=len(b), blocking_frac_jobs=len(pos) / len(b),
                         blocking_mean_all=float(b.mean()),
                         blocking_mean_blocked=float(pos.mean()) if len(pos) else 0.0,
                         blocking_p95_all=float(np.percentile(b, 95)),
                         blocking_max=float(b.max())))
    return pd.DataFrame(rows, columns=["condition", "blocking_jobs", "blocking_frac_jobs",
                                       "blocking_mean_all", "blocking_mean_blocked",
                                       "blocking_p95_all", "blocking_max"])


def paired_differences(result):
    """For every cell (ipc, utilization, intensity, tag) and every comparison [A, B] in
    settings.comparisons: per-set differences d_i = miss_rate(A, set i) - miss_rate(B, set i),
    paired by task-set index (same UUniFast seeds across conditions).

    D4: winner = lower mean miss rate; 'tie' iff the 95% paired t-interval of d includes 0.
    Returns (summary DataFrame, per-set differences DataFrame)."""
    raw, comps = result.raw, result.settings.comparisons
    summ, diffs = [], []
    for (ipc, u, inten, tag), cell in raw.groupby(["ipc", "utilization", "intensity", "tag"], sort=True):
        arms = {}
        for arm, g in cell.groupby("arm"):
            if g["condition"].nunique() > 1:
                raise ValueError(f"arm {arm!r} is ambiguous in cell {(ipc, u, inten, tag)}")
            arms[arm] = g.sort_values("set_index").reset_index(drop=True)
        for a, b in comps:
            if a not in arms or b not in arms:
                continue
            ga, gb = arms[a], arms[b]
            if not (ga["set_index"].to_numpy() == gb["set_index"].to_numpy()).all():
                raise ValueError("arms are not paired on the same task-set indices")
            d = ga["miss_rate"].to_numpy() - gb["miss_rate"].to_numpy()
            n, mean, sd, lo, hi = t_interval(d)
            tie = bool(lo <= 0.0 <= hi) if n >= 2 else True
            mean_a, mean_b = float(ga["miss_rate"].mean()), float(gb["miss_rate"].mean())
            winner = "tie" if tie else (a if mean_a < mean_b else b)
            overload = bool(ga["overload"].any() or gb["overload"].any())
            summ.append(dict(ipc=ipc, utilization=u, intensity=inten, tag=tag, arm_a=a, arm_b=b,
                             cond_a=ga["condition"].iloc[0], cond_b=gb["condition"].iloc[0],
                             n=n, mean_a=mean_a, mean_b=mean_b, mean_diff=mean, sd_diff=sd,
                             ci_lo=lo, ci_hi=hi, tie=tie, winner="overload" if overload else winner,
                             overload=overload,
                             n_sets_differing=int((np.abs(d) > 1e-12).sum())))
            for si, di in zip(ga["set_index"], d):
                diffs.append(dict(ipc=ipc, utilization=u, intensity=inten, tag=tag,
                                  arm_a=a, arm_b=b, set_index=int(si), diff=float(di)))
    return pd.DataFrame(summ), pd.DataFrame(diffs)
