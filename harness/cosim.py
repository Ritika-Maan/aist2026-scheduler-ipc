"""Co-simulation loop: Ritika's Task/Job/RMS priorities + Priya's IPCInterface.

Call order follows ipc/NOTES.md "Integration (A.2)" (and ipc/example_harness_usage.run_cosim):
  1. on_job_release for every job with release <= now (message passing: on_message_send)
  2. dispatch = min effective_key over jobs with can_dispatch; none -> report_no_dispatchable
  3. on_job_start, then fire reached lock/unlock events; if any fired, go back to 2
  4. run to min(finish, next release, next sync point): record_run, fire sync points, on_job_finish
Plain event loop, no SimPy. core/ and ipc/ are not modified.

Differences from the demo run_cosim: message-passing WCET uses message_passing_tasks
(baseline_latency convention, locked) instead of inflate_wcet; tasks are copied so RMS
priorities assigned in place never leak into the shared task sets.
"""
import math
from dataclasses import dataclass, replace

from . import ROOT  # noqa: F401  (puts core/ and ipc/ on sys.path)
from config import EPS                                           # ipc/config.py
from interface import (IPCInterface, effective_utilization,      # ipc/interface.py
                       message_passing_tasks)
from messaging import MessagePassingConfig                       # ipc/messaging.py
from .taskgen import hyperperiod


@dataclass
class CosimResult:
    jobs: list            # IPCJob (task, release, abs_deadline, start, finish, blocking, ...)
    deadlock: bool
    api: IPCInterface
    target_u: float       # sum C'/T  (what UUniFast generated)
    effective_u: float    # target_u + on-top overhead (latency sweep only)
    overload: bool        # effective_u > 1: do not compare directly
    horizon: float


def _fire_sync_points(api, key, time):
    """Fire every lock/unlock the job has reached. True if any fired."""
    fired = False
    while True:
        sp = api.next_sync_point(*key)
        if sp is None or sp.offset > api.executed(*key) + EPS:
            return fired
        fired = True
        if sp.kind == "lock":
            if not api.on_lock_request(*key, sp.resource, time):
                return fired                      # job is now blocked
        else:
            api.on_lock_release(*key, sp.resource, time)


def cosim(tasks, scheduler, ipc="shared_memory", protocol=None, specs=None, horizon=None,
          msg_cfg=None, msgs_per_job=0, baseline_latency=None, check_select=False):
    """tasks carry the generated TOTAL wcet C'. Returns CosimResult.

    shared_memory  : specs={task_name: [CriticalSection]} lie inside C'; blocking is measured.
    message_passing: overhead m*baseline_latency is carved out of C'; only the excess
                     m*(latency-baseline_latency) is added on top (effective_u reports it).
    horizon None   -> hyperperiod of the task set (jobs released in [0, horizon))."""
    tasks = list(tasks)
    if horizon is None:
        horizon = hyperperiod(tasks)
    if ipc == "message_passing":
        msg_cfg = msg_cfg or MessagePassingConfig()
        sim_tasks, splits = message_passing_tasks(tasks, msgs_per_job, msg_cfg, baseline_latency)
        target_u, eff_u, overload = effective_utilization(tasks, splits)
    else:
        sim_tasks = [replace(t) for t in tasks]
        target_u = eff_u = sum(t.utilization for t in tasks)
        overload = eff_u > 1 + EPS

    api = IPCInterface(sim_tasks, scheduler, ipc, protocol, specs, msg_cfg)
    names = [t.name for t in api.tasks]
    next_stage = {n: names[(i + 1) % len(names)] for i, n in enumerate(names)}   # ring pipeline

    releases = []
    for t in api.tasks:
        r = t.arrival
        while r < horizon:
            releases.append((r, t.name))
            r += t.period
    releases.sort(key=lambda x: x[0])

    time, i = 0.0, 0
    while i < len(releases) or api.has_pending():
        if not api.has_pending():                 # idle: jump to next release
            time = max(time, releases[i][0])
        while i < len(releases) and releases[i][0] <= time:        # 1. releases
            r, name = releases[i]
            api.on_job_release(name, r)
            if ipc == "message_passing":
                for _ in range(msgs_per_job.get(name, 0) if isinstance(msgs_per_job, dict) else msgs_per_job):
                    api.on_message_send(name, r, next_stage[name], time)
            i += 1

        cands = [k for k in api.pending() if api.can_dispatch(*k, time)]   # 2. dispatch
        if not cands:
            api.report_no_dispatchable(time)
            break
        chosen = min(cands, key=lambda k: api.effective_key(*k, time))
        if check_select:
            assert api.select(time) == chosen, "select() disagrees with can_dispatch/effective_key"

        api.on_job_start(*chosen, time)                             # 3. lock events
        if _fire_sync_points(api, chosen, time):
            if api.deadlock:
                break
            continue

        next_rel = releases[i][0] if i < len(releases) else math.inf   # 4. run a segment
        sp = api.next_sync_point(*chosen)
        next_ev = sp.offset - api.executed(*chosen) if sp else math.inf
        run = min(api.remaining(*chosen), next_rel - time, next_ev)
        api.record_run(*chosen, time, time + run)
        time += run
        _fire_sync_points(api, chosen, time)
        if api.deadlock:
            break
        if api.remaining(*chosen) <= EPS:
            api.on_job_finish(*chosen, time)

    if api.deadlock:
        api.finalize_deadlock()
    return CosimResult(api.jobs, api.deadlock, api, target_u, eff_u, overload, horizon)
