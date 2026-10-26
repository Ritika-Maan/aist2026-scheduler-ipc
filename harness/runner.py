"""run_matrix(conditions, task_sets): runs every condition on every task set."""
import random
from dataclasses import dataclass

import pandas as pd

from . import ROOT  # noqa: F401
from config import EPS, generate_specs                   # ipc/config.py
from messaging import MessagePassingConfig              # ipc/messaging.py
from schedulers import metrics                           # core/schedulers.py
from .cosim import cosim


@dataclass
class MatrixResult:
    raw: pd.DataFrame        # one row per (condition, task-set index)
    blocking: pd.DataFrame   # one row per job, shared-memory conditions only
    conditions: list
    settings: object


def make_specs(tasks, utilization, set_index, params, base_seed):
    """Critical sections for one task set. The RNG depends on (seed, U, set, n_resources,
    cs_per_job) only -- NOT on scheduler, protocol or cs_fraction -- so RMS and EDF see the
    same critical-section layout and a cs_fraction sweep rescales the same draws."""
    rng = random.Random(f"{base_seed}|{utilization}|{set_index}|{params['n_resources']}|{params['cs_per_job']}")
    return generate_specs(tasks, params["n_resources"], params["cs_per_job"], params["cs_fraction"], rng)


def _job_blocking(api):
    """Per-job blocking from api.blocking_events: {(task, release): (total, n_events, dominant_cause)}."""
    acc = {}
    for ev in api.blocking_events:
        tot, n, causes = acc.get(ev.job, (0.0, 0, {}))
        causes[ev.cause] = causes.get(ev.cause, 0.0) + ev.duration
        acc[ev.job] = (tot + ev.duration, n + 1, causes)
    return {k: (tot, n, max(c, key=c.get)) for k, (tot, n, c) in acc.items()}


def run_one(cond, tasks, set_index, settings):
    p = cond.params(settings)
    specs, msg_cfg = None, None
    if cond.ipc == "shared_memory":
        specs = make_specs(tasks, cond.utilization, set_index, p, settings.base_seed)
    else:
        msg_cfg = MessagePassingConfig(latency=p["msg_latency"], capacity=p["msg_capacity"])
    res = cosim(tasks, cond.scheduler, cond.ipc, cond.protocol, specs, msg_cfg=msg_cfg,
                msgs_per_job=p["msgs_per_job"] if cond.ipc == "message_passing" else 0,
                baseline_latency=p["baseline_latency"] if cond.ipc == "message_passing" else None)
    m = metrics(res.jobs)                                 # core metrics: jobs, missed, miss_rate, max_lateness
    
    row = dict(condition=cond.id, arm=cond.arm, scheduler=cond.scheduler, ipc=cond.ipc,
               protocol=cond.protocol or "none", utilization=cond.utilization,
               intensity=cond.intensity, tag=cond.tag, set_index=set_index,
               d_factor=getattr(cond, "d_factor", 1.0),
               jobs=m["jobs"], missed=m["missed"], miss_rate=m["miss_rate"],
               max_lateness=m["max_lateness"], deadlock=res.deadlock,
               target_u=res.target_u, effective_u=res.effective_u, overload=res.overload,
               dropped_messages=res.api.dropped_messages, horizon=res.horizon)
    blk_rows = []
    if cond.ipc == "shared_memory":
        per_job = _job_blocking(res.api)
        for j in res.jobs:
            tot, n, cause = per_job.get((j.task.name, j.release), (0.0, 0, ""))
            blk_rows.append(dict(condition=cond.id, set_index=set_index, task=j.task.name,
                                 release=j.release, blocking=tot, n_events=n, cause=cause))
        row["blocked_jobs"] = sum(1 for r in blk_rows if r["blocking"] > EPS)
    return row, blk_rows


def run_matrix(conditions, task_sets, settings, progress=False):
    """conditions: [Condition]; task_sets: {utilization: [task set, ...]} (e.g. a TaskSetBank).
    Set i at a given U is shared by every condition at that U (pairing key = set_index)."""
    rows, blk = [], []
    for ci, cond in enumerate(conditions):
        if cond.utilization not in task_sets:
            raise KeyError(f"{cond.id}: no task sets for utilization {cond.utilization}")
        for i, tasks in enumerate(task_sets[cond.utilization]):
            row, b = run_one(cond, tasks, i, settings)
            rows.append(row)
            blk.extend(b)
        if progress:
            print(f"[{ci + 1}/{len(conditions)}] {cond.id}", flush=True)
    raw = pd.DataFrame(rows)
    blocking = pd.DataFrame(blk, columns=["condition", "set_index", "task", "release",
                                          "blocking", "n_events", "cause"])
    return MatrixResult(raw, blocking, list(conditions), settings)