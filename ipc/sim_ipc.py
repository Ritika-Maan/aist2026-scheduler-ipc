"""Lock-aware version of core's simulate(). core/ is NOT modified.

Same preemptive uniprocessor loop as core/schedulers.py, plus:
  * lock/unlock events at critical-section boundaries (CPU time executed)
  * pluggable protocol (NONE / PIP / ICPP / SRP) deciding priority and blocking
  * per-job blocking time and deadlock detection

Blocking time of a job = total time it is pending (ready or lock-blocked)
while the running job has a strictly worse BASE priority. In plain preemptive
scheduling that never happens, so every such interval is protocol-induced
priority inversion (direct blocking, chained blocking, ceiling/SRP holds,
and indirect delay through inheritance).

Deadlock: simulation stops, every unfinished and unreleased job gets
finish = inf (counts as missed, infinite lateness) and info["deadlock"] = True.
"""
import math
import os
import sys
from dataclasses import dataclass, field

_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (_HERE, os.path.join(_HERE, "..", "core")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from task import Job                                   # noqa: E402  (core)
from schedulers import assign_rms_priorities, metrics  # noqa: E402  (core)
from config import EPS, build_events, validate_specs   # noqa: E402
from protocols import State, make_protocol             # noqa: E402


@dataclass
class IPCJob(Job):
    events: list = field(default_factory=list)   # [(point, 'lock'|'unlock', res)]
    ev_idx: int = 0
    blocked_on: str = None
    blocking: float = 0.0

    @property
    def executed(self):
        return self.task.wcet - self.remaining


def _advance_events(job, prot, state):
    """Process every lock/unlock event the job has reached. True if anything happened."""
    changed = False
    while job.ev_idx < len(job.events) and job.events[job.ev_idx][0] <= job.executed + EPS:
        _, kind, res = job.events[job.ev_idx]
        changed = True
        if kind == "lock":
            if not prot.request(job, res, state):
                break                      # blocked (ev_idx advances when granted)
        else:
            prot.release(job, res, state)
            job.ev_idx += 1
    return changed


def simulate_ipc(tasks, policy, protocol, specs, horizon):
    """policy: 'RMS'|'EDF'.  protocol: 'NONE'|'PIP'|'ICPP'|'SRP'.
    specs: {task_name: [CriticalSection]} (use {} for no sharing).
    Returns (jobs, info) where info = {'deadlock': bool}."""
    validate_specs(tasks, specs)
    if policy == "RMS":
        assign_rms_priorities(tasks)
    prot = make_protocol(protocol, policy, specs)
    prot.prepare(tasks)
    state = State()
    ready = state.ready

    releases = []
    for t in tasks:
        events = build_events(specs.get(t.name, []))
        r = t.arrival
        while r < horizon:
            releases.append(IPCJob(t, r, r + t.deadline, t.wcet, events=events))
            r += t.period
    releases.sort(key=lambda j: j.release)

    time, i, done = 0.0, 0, []
    while i < len(releases) or ready:
        if not ready:                               # idle: jump to next release
            time = max(time, releases[i].release)
        while i < len(releases) and releases[i].release <= time:
            ready.append(releases[i])
            i += 1

        job = prot.select(state)
        if job is None:                             # all pending jobs lock-blocked
            state.deadlock = True
            break
        if job.start is None:                       # must precede lock events (SRP test)
            job.start = time
        if _advance_events(job, prot, state):       # lock state changed: re-pick
            if state.deadlock:
                break
            continue

        next_rel = releases[i].release if i < len(releases) else math.inf
        next_ev = job.events[job.ev_idx][0] - job.executed if job.ev_idx < len(job.events) else math.inf
        run = min(job.remaining, next_rel - time, next_ev)

        bk = prot.base_key(job)                     # blocking accounting
        for j in ready:
            if j is not job and prot.base_key(j) < bk:
                j.blocking += run

        time += run
        job.remaining -= run
        _advance_events(job, prot, state)           # events reached at segment end
        if state.deadlock:
            break
        if job.remaining <= EPS:
            job.remaining = 0.0
            job.finish = time
            ready.remove(job)
            done.append(job)

    if state.deadlock:
        for j in ready + releases[i:]:
            j.finish = math.inf
            done.append(j)
        ready.clear()
    return done, {"deadlock": state.deadlock}


def metrics_ipc(jobs, info):
    """core metrics + blocking statistics."""
    m = metrics(jobs)
    b = [j.blocking for j in jobs]
    m.update(max_blocking=max(b), mean_blocking=sum(b) / len(b),
             deadlock=info["deadlock"])
    return m
