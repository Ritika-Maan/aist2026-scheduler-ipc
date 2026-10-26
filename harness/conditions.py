"""Data-driven experiment configuration (JSON).

A condition is a dict; extra conditions (RMS+SRP control, ICPP control, critical-section
fraction sweep, message-latency sweep) are just more dict entries in the JSON -- no .py edits.

Condition keys
  scheduler   "RMS" | "EDF"                         (required)
  ipc         "shared_memory" | "message_passing"   (required)
  protocol    "PIP" | "ICPP" | "SRP" | null          (null for message_passing)
  utilization float, must be a key of the task-set bank
  intensity   name of an entry in settings.intensity ("low" | "high" | ...)
  arm         label compared in `comparisons` (default = scheduler)
  tag         sweep label; conditions are only compared within the same tag (default "")
  id          optional; auto-generated if absent
  overrides   optional dict overriding intensity values / latency:
              n_resources, cs_per_job, cs_fraction, msgs_per_job,
              msg_latency, baseline_latency, msg_capacity
"""
import json
from dataclasses import dataclass, field

SCHEDULERS = ("RMS", "EDF")
IPC_MODES = ("shared_memory", "message_passing")
OVERRIDE_KEYS = {"n_resources", "cs_per_job", "cs_fraction", "msgs_per_job",
                 "msg_latency", "baseline_latency", "msg_capacity"}


@dataclass
class Settings:
    time_unit: str
    base_seed: int
    n_task_sets: int
    n_tasks: int
    period_grid: list
    baseline_latency: float
    intensity: dict
    comparisons: list = field(default_factory=lambda: [["RMS", "EDF"]])
    notes: dict = field(default_factory=dict)


@dataclass
class Condition:
    id: str
    scheduler: str
    ipc: str
    protocol: object
    utilization: float
    intensity: str
    arm: str
    tag: str
    overrides: dict
    d_factor: float = 1.0

    def params(self, settings):
        """Intensity values + overrides, with latency defaults filled in."""
        p = dict(settings.intensity[self.intensity])
        p.update(self.overrides)
        p.setdefault("baseline_latency", settings.baseline_latency)
        p.setdefault("msg_latency", p["baseline_latency"])
        p.setdefault("msg_capacity", None)
        return p


def make_condition(d):
    d = dict(d)
    for k in ("scheduler", "ipc", "utilization", "intensity"):
        if k not in d:
            raise ValueError(f"condition {d} is missing '{k}'")
    if d["scheduler"] not in SCHEDULERS:
        raise ValueError(f"bad scheduler in {d}")
    if d["ipc"] not in IPC_MODES:
        raise ValueError(f"bad ipc in {d}")
    protocol = d.get("protocol")
    if d["ipc"] == "message_passing" and protocol is not None:
        raise ValueError(f"message_passing takes protocol=null: {d}")
    overrides = dict(d.get("overrides", {}))
    bad = set(overrides) - OVERRIDE_KEYS
    if bad:
        raise ValueError(f"unknown overrides {sorted(bad)} in {d}")
    arm, tag = d.get("arm", d["scheduler"]), d.get("tag", "")
    cid = d.get("id") or "|".join([arm, d["ipc"], str(protocol), f"U{d['utilization']}",
                                   d["intensity"], tag])
    d_factor = float(d.get("d_factor", 1.0))
    return Condition(cid, d["scheduler"], d["ipc"], protocol, float(d["utilization"]),
                     d["intensity"], arm, tag, overrides, d_factor)


def load_config(path):
    """-> (Settings, [Condition])"""
    with open(path) as f:
        raw = json.load(f)
    s = raw["settings"]
    settings = Settings(
        time_unit=s["time_unit"], base_seed=int(s["base_seed"]), n_task_sets=int(s["n_task_sets"]),
        n_tasks=int(s["n_tasks"]), period_grid=list(s["period_grid"]),
        baseline_latency=float(s["baseline_latency"]), intensity=dict(s["intensity"]),
        comparisons=[list(c) for c in raw.get("comparisons", [["RMS", "EDF"]])],
        notes=dict(s.get("notes", {})))
    conditions = [make_condition(c) for c in raw["conditions"]]
    ids = [c.id for c in conditions]
    if len(set(ids)) != len(ids):
        dup = sorted({i for i in ids if ids.count(i) > 1})
        raise ValueError(f"duplicate condition ids: {dup}")
    for c in conditions:
        if c.intensity not in settings.intensity:
            raise ValueError(f"{c.id}: unknown intensity {c.intensity!r}")
    return settings, conditions


def required_min_wcet(settings, conditions):
    """Smallest per-task WCET that leaves compute time after the largest message carve-out
    (2x margin). Task sets with a smaller wcet are rejected at generation (all conditions
    share the same sets, so pairing is preserved)."""
    worst = 0.0
    for c in conditions:
        if c.ipc == "message_passing":
            p = c.params(settings)
            worst = max(worst, p["msgs_per_job"] * p["baseline_latency"])
    return 2.0 * worst
