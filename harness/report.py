"""Verdict, headline number and the human-readable summary."""
import math


def cell_table(paired, comparison=("RMS", "EDF"), tag=""):
    return paired[(paired.arm_a == comparison[0]) & (paired.arm_b == comparison[1]) & (paired.tag == tag)]


def flip_verdict(paired, comparison=("RMS", "EDF"), tag=""):
    """Strict flip: at some (U, intensity) both IPC modes have a non-tie winner and the winners
    differ. 'shifts' = cells where exactly one mode is a tie (significance changes, no reversal)."""
    d = cell_table(paired, comparison, tag)
    sm, mp = d[d.ipc == "shared_memory"], d[d.ipc == "message_passing"]
    m = sm.merge(mp, on=["utilization", "intensity"], suffixes=("_sm", "_mp"))
    m = m[~(m.overload_sm | m.overload_mp)]
    flips = m[(m.winner_sm != "tie") & (m.winner_mp != "tie") & (m.winner_sm != m.winner_mp)]
    shifts = m[(m.winner_sm == "tie") != (m.winner_mp == "tie")]
    return dict(n_cells=len(m), flips=flips, shifts=shifts,
                found=len(flips) > 0)


def headline(paired, comparison=("RMS", "EDF"), tag=""):
    """One sentence in the required form. Picks the (IPC mode, U, intensity) cell with a
    non-tie gap that differs most from the same cell under the other IPC mode (difference of
    mean paired gaps, descriptive). Gap = percentage points of miss rate."""
    d = cell_table(paired, comparison, tag)
    d = d[~d.overload]
    cands = []
    for _, r in d.iterrows():
        if r.tie:
            continue
        other = d[(d.ipc != r.ipc) & (d.utilization == r.utilization) & (d.intensity == r.intensity)]
        o = other.iloc[0] if len(other) else None
        o_gap = 0.0 if o is None or o.tie else o.mean_diff
        # larger contrast first; ties prefer shared memory (message passing is the control), then high intensity
        cands.append((-round(abs(r.mean_diff - o_gap), 12), r.ipc != "shared_memory",
                      r.intensity != "high", r.utilization, r, o))
    best = None
    if cands:
        c = min(cands, key=lambda x: x[:4])
        best = (None, c[4], c[5])
    if best is None:
        return ("No scheduler gap distinguishable from zero (95% paired t-interval includes 0) "
                "in any cell under either IPC mode.")
    _, r, o = best
    hi, lo = (r.arm_a, r.arm_b) if r.mean_diff > 0 else (r.arm_b, r.arm_a)
    hi_rate, lo_rate = (r.mean_a, r.mean_b) if r.mean_diff > 0 else (r.mean_b, r.mean_a)
    gap_pp = 100 * abs(r.mean_diff)
    same_dir = o is not None and not o.tie and (o.mean_diff > 0) == (r.mean_diff > 0)
    other_mode = "message passing" if r.ipc == "shared_memory" else "shared memory"
    this_mode = "shared memory" if r.ipc == "shared_memory" else "message passing"
    appear = "does" if same_dir else "doesn't"
    return (f"under {this_mode}, {hi}'s miss rate exceeds {lo}'s by {gap_pp:.2f} percentage points "
            f"({100 * hi_rate:.2f}% vs {100 * lo_rate:.2f}%, N={int(r.n)}, 95% paired CI "
            f"[{100 * r.ci_lo:+.2f}, {100 * r.ci_hi:+.2f}] pp on {comparison[0]}-{comparison[1]}) "
            f"at {r.utilization:g} utilization ({r.intensity} intensity), a gap that {appear} "
            f"appear under {other_mode}.")


def verdict_text(paired, comparison=("RMS", "EDF"), tag=""):
    v = flip_verdict(paired, comparison, tag)
    if v["found"]:
        cells = ", ".join(f"U={r.utilization:g}/{r.intensity}: {r.winner_sm} (shared) vs {r.winner_mp} (msg)"
                          for _, r in v["flips"].iterrows())
        return f"FLIP FOUND in {len(v['flips'])} of {v['n_cells']} cells: {cells}."
    msg = "No flip found: scheduler ranking is robust to IPC choice under these conditions."
    if len(v["shifts"]):
        msg += (f" ({len(v['shifts'])} of {v['n_cells']} cells differ only in whether the gap is "
                f"distinguishable from zero in one IPC mode but not the other; no reversal.)")
    return msg


def _fmt(x, pct=False, nd=2):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "n/a"
    return f"{100 * x:.{nd}f}" if pct else f"{x:.{nd}f}"


def write_summary(path, summary, paired, settings, rejected=None, comparison=("RMS", "EDF")):
    L = []
    L += ["# Baseline summary", "",
          f"Time unit: {settings.time_unit}. Task sets per condition: N = {settings.n_task_sets}; "
          f"{settings.n_tasks} tasks each; seed {settings.base_seed}.",
          "Miss rate is shown as mean % [95% t-interval] (SD, N). Max lateness is core's definition "
          "(max over jobs of finish - deadline; negative = all jobs had slack).", ""]
    if rejected:
        L += [f"Task sets rejected at generation (tiny WCET): {dict(rejected)}", ""]
    L += ["## How to read the message-passing results", "",
          "At baseline, message-passing overhead (m x baseline latency) is carved out of the generated "
          "total WCET C' (D2), so the message-passing schedule is identical to plain RMS/EDF scheduling "
          "and identical across low/high intensity. The message-passing rows (and the right regime-map "
          "panel) are therefore the **plain-scheduling control**, not a separate effect, and are flat "
          "across intensity by construction. The question the baseline answers is whether shared-memory "
          "blocking (RMS+PIP, EDF+SRP) changes that plain ranking. Message-latency effects appear only "
          "in the post-baseline sweep (baseline_latency convention, effective U reported).", "",
          "## Verdict", "", verdict_text(paired, comparison), "",
          "## Headline", "", headline(paired, comparison), "",
          "## Winner per cell", "",
          f"Paired by task-set index; diff = {comparison[0]} - {comparison[1]} miss rate in percentage points "
          "(positive = " + comparison[0] + " misses more). Tie = 95% paired t-interval includes 0.", "",
          "| IPC | U | intensity | N | " + comparison[0] + " mean % | " + comparison[1] +
          " mean % | mean diff (pp) | SD diff | 95% CI diff (pp) | sets differing | winner |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in cell_table(paired, comparison).iterrows():
        L.append(f"| {r.ipc} | {r.utilization:g} | {r.intensity} | {int(r.n)} | {_fmt(r.mean_a, True)} | "
                 f"{_fmt(r.mean_b, True)} | {_fmt(r.mean_diff, True)} | {_fmt(r.sd_diff, True)} | "
                 f"[{_fmt(r.ci_lo, True)}, {_fmt(r.ci_hi, True)}] | {int(r.n_sets_differing)}/{int(r.n)} | "
                 f"{r.winner} |")
    L += ["", "## Per-condition metrics", "",
          "| condition | N | miss rate % mean [95% CI] (SD) | max lateness mean [95% CI] (SD) | "
          "deadlock sets | blocked jobs % | blocking mean of blocked (ms) | blocking max (ms) |",
          "|---|---|---|---|---|---|---|---|"]
    for _, r in summary.iterrows():
        blk = ("n/a", "n/a", "n/a") if r.ipc != "shared_memory" else (
            _fmt(r.blocking_frac_jobs, True, 1), _fmt(r.blocking_mean_blocked, nd=3), _fmt(r.blocking_max, nd=3))
        L.append(f"| {r.condition} | {int(r.miss_rate_n)} | {_fmt(r.miss_rate_mean, True)} "
                 f"[{_fmt(r.miss_rate_ci_lo, True)}, {_fmt(r.miss_rate_ci_hi, True)}] "
                 f"({_fmt(r.miss_rate_sd, True)}) | {_fmt(r.max_lateness_mean, nd=2)} "
                 f"[{_fmt(r.max_lateness_ci_lo, nd=2)}, {_fmt(r.max_lateness_ci_hi, nd=2)}] "
                 f"({_fmt(r.max_lateness_sd, nd=2)}) | {int(r.deadlock_sets)} | {blk[0]} | {blk[1]} | {blk[2]} |")
    L += ["", "## Assumptions and placeholders", ""]
    for k, v in settings.notes.items():
        L.append(f"- **{k}**: {v}")
    with open(path, "w") as f:
        f.write("\n".join(L) + "\n")
