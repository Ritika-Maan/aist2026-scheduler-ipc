"""Figures: regime map (two panels) and shared-memory blocking distributions."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                     # noqa: E402
import numpy as np                                  # noqa: E402
from matplotlib.patches import Patch                # noqa: E402

IPC_TITLES = {"shared_memory": "Shared memory (RMS+PIP vs EDF+SRP)",
              "message_passing": "Message passing = plain-scheduling control"}
COLORS = {"RMS": "#0072B2", "EDF": "#D55E00", "tie": "#E6E6E6", "overload": "#999999"}


def regime_map(paired, path, comparison=("RMS", "EDF"), tag="", intensities=("low", "high"),
               ipcs=("shared_memory", "message_passing")):
    """Winning scheduler (lower mean miss rate; 'tie' if the 95% paired t-interval includes 0)
    over utilization (x) x communication intensity (y), one panel per IPC mode.
    Cell text: mean paired difference (A - B) in percentage points of miss rate."""
    a, b = comparison
    d = paired[(paired.arm_a == a) & (paired.arm_b == b) & (paired.tag == tag)]
    us = sorted(d.utilization.unique())
    fig, axes = plt.subplots(1, len(ipcs), figsize=(4.4 * len(ipcs) + 0.8, 3.9), sharey=True,
                             constrained_layout=True)
    axes = np.atleast_1d(axes)
    for ax, ipc in zip(axes, ipcs):
        for yi, inten in enumerate(intensities):
            for xi, u in enumerate(us):
                row = d[(d.ipc == ipc) & (d.intensity == inten) & (d.utilization == u)]
                if row.empty:
                    continue
                r = row.iloc[0]
                color = COLORS[r.winner if r.winner in COLORS else "tie"]
                ax.add_patch(plt.Rectangle((xi - 0.5, yi - 0.5), 1, 1, facecolor=color,
                                           edgecolor="white", linewidth=2,
                                           hatch="//" if r.winner == "tie" else None))
                txt = "overload" if r.overload else f"{100 * r.mean_diff:+.1f}"
                ax.text(xi, yi, txt, ha="center", va="center", fontsize=9,
                        color="white" if r.winner in (a, b) else "black")
        ax.set_xlim(-0.5, len(us) - 0.5)
        ax.set_ylim(-0.5, len(intensities) - 0.5)
        ax.set_xticks(range(len(us)))
        ax.set_xticklabels([f"{u:g}" for u in us])
        ax.set_yticks(range(len(intensities)))
        ax.set_yticklabels(intensities)
        ax.set_xlabel("Target utilization U")
        ax.set_title(IPC_TITLES.get(ipc, ipc))
        for s in ax.spines.values():
            s.set_visible(False)
        ax.tick_params(length=0)
    axes[0].set_ylabel("Communication intensity")
    handles = [Patch(facecolor=COLORS[a], label=f"{a} lower miss rate"),
               Patch(facecolor=COLORS[b], label=f"{b} lower miss rate"),
               Patch(facecolor=COLORS["tie"], hatch="//", edgecolor="white",
                     label="tie (95% paired CI includes 0)")]
    fig.legend(handles=handles, loc="outside lower center", ncol=3, frameon=False, fontsize=8)
    fig.suptitle(f"Winning scheduler ({a} vs {b}); cell = mean paired miss-rate difference "
                 f"{a}-{b} (pp)\nMessage-passing overhead is inside WCET (baseline), so that panel equals plain "
                 f"{a}/{b} scheduling and is identical across intensities.", fontsize=8.5)
    fig.savefig(path, dpi=300)
    plt.close(fig)


def blocking_distributions(blocking, summary, path, intensities=("low", "high")):
    """Per-job blocking time (ms) of jobs that were blocked, shared-memory conditions only.
    Box = quartiles, whiskers 5-95%; label = share of jobs blocked."""
    s = summary[summary.ipc == "shared_memory"]
    arms = sorted(s.arm.unique())
    us = sorted(s.utilization.unique())
    colors = {"RMS": COLORS["RMS"], "EDF": COLORS["EDF"]}
    fig, axes = plt.subplots(1, len(intensities), figsize=(4.4 * len(intensities) + 0.4, 3.8),
                             sharey=True, constrained_layout=True)
    axes = np.atleast_1d(axes)
    width = 0.8 / max(len(arms), 1)
    for ax, inten in zip(axes, intensities):
        for ai, arm in enumerate(arms):
            for xi, u in enumerate(us):
                row = s[(s.arm == arm) & (s.utilization == u) & (s.intensity == inten) & (s.tag == "")]
                if row.empty:
                    continue
                r = row.iloc[0]
                v = blocking.loc[blocking.condition == r.condition, "blocking"].to_numpy()
                pos = v[v > 1e-9]
                x = xi + (ai - (len(arms) - 1) / 2) * width
                if len(pos) >= 2:
                    ax.bxp([dict(med=np.median(pos), q1=np.percentile(pos, 25), q3=np.percentile(pos, 75),
                                 whislo=np.percentile(pos, 5), whishi=np.percentile(pos, 95),
                                 fliers=[])], positions=[x], widths=width * 0.9, showfliers=False,
                           patch_artist=True,
                           boxprops=dict(facecolor=colors.get(arm, "gray"), alpha=0.8),
                           medianprops=dict(color="black"))
                ax.text(x, 1.01, f"{100 * r.blocking_frac_jobs:.0f}%", transform=ax.get_xaxis_transform(),
                        ha="center", va="bottom", fontsize=6.5, rotation=90)
        ax.set_yscale("log")
        ax.set_xticks(range(len(us)))
        ax.set_xticklabels([f"{u:g}" for u in us])
        ax.set_xlim(-0.6, len(us) - 0.4)
        ax.set_xlabel("Target utilization U")
        ax.set_title(f"{inten} intensity", pad=26)
    axes[0].set_ylabel("Blocking time of blocked jobs (ms, log)")
    handles = [Patch(facecolor=colors.get(a, "gray"), label=a) for a in arms]
    fig.legend(handles=handles, loc="outside lower center", ncol=len(arms), frameon=False, fontsize=8)
    fig.suptitle("Shared-memory blocking (labels above boxes: % of jobs blocked)", fontsize=9)
    fig.savefig(path, dpi=300)
    plt.close(fig)
