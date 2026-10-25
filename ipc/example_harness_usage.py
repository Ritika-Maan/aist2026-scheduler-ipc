"""Minimal example: how harness/ drives the IPC layer through ipc/interface.py.

NOT the experiment harness. It is a ~60-line co-simulation loop that shows the
order in which the A.2 calls are made. Scheduler, IPC mechanism and protocol
are chosen ONLY by constructor arguments; nothing in ipc/ or core/ changes:

    run_cosim(tasks, scheduler="RMS", ipc="shared_memory", protocol="PIP", specs=...)
    run_cosim(tasks, scheduler="EDF", ipc="shared_memory", protocol="SRP", specs=...)
    run_cosim(tasks, scheduler="RMS", ipc="shared_memory", protocol="SRP", specs=...)  # control
    run_cosim(tasks, scheduler="EDF", ipc="message_passing", msg_cfg=MessagePassingConfig(latency=0.2),
              msgs_per_job=2)

Event order per scheduling step (what Garima's harness must follow):
    1. on_job_release for every job whose release <= now
       (message passing: on_message_send for the messages it sends)
    2. candidates = jobs with can_dispatch(...) True; choose min effective_key(...)
       (no candidates while jobs are pending -> report_no_dispatchable = deadlock)
    3. on_job_start; then fire every lock/unlock the job has reached
       (next_sync_point vs executed): on_lock_request / on_lock_release.
       If any lock event fired, go back to step 2 (priorities may have changed).
    4. run the job until the earliest of: it finishes, next release, next sync point
       -> record_run(t0, t1); fire sync points reached; on_job_finish if done.
Run from the repo root:  python ipc/example_harness_usage.py
"""
import math
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (_HERE, os.path.join(_HERE, "..", "core")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from config import EPS, CriticalSection as CS              # noqa: E402
from interface import IPCInterface, inflate_wcet           # noqa: E402
from messaging import MessagePassingConfig                 # noqa: E402


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


def run_cosim(tasks, scheduler, ipc="shared_memory", protocol=None, specs=None,
              horizon=100.0, msg_cfg=None, msgs_per_job=0, check_select=False):
    """Returns {"jobs": [IPCJob], "deadlock": bool, "api": IPCInterface}."""
    tasks = list(tasks)
    if ipc == "message_passing":                  # overhead goes into WCET, latency from config
        msg_cfg = msg_cfg or MessagePassingConfig()
        tasks = inflate_wcet(tasks, msgs_per_job, msg_cfg)
    api = IPCInterface(tasks, scheduler, ipc, protocol, specs, msg_cfg)
    names = [t.name for t in api.tasks]
    next_stage = {n: names[(i + 1) % len(names)] for i, n in enumerate(names)}  # pipeline order

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
                for _ in range(msgs_per_job):
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
    return {"jobs": api.jobs, "deadlock": api.deadlock, "api": api}


if __name__ == "__main__":
    from task import Task
    from schedulers import metrics

    def toy_tasks():   # tiny priority-inversion scenario; a demo, NOT an experiment
        return [Task("H", 100, 2, arrival=1), Task("M", 110, 10, arrival=2),
                Task("L", 120, 4, arrival=0)]
    toy_specs = {"L": [CS("R", 0, 3)], "H": [CS("R", 0, 1)]}

    combos = [("RMS", "shared_memory", "NONE"), ("RMS", "shared_memory", "PIP"),
              ("RMS", "shared_memory", "ICPP"), ("RMS", "shared_memory", "SRP"),
              ("EDF", "shared_memory", "SRP"),
              ("RMS", "message_passing", None), ("EDF", "message_passing", None)]
    print(f"{'scheduler':9} {'ipc':15} {'protocol':8} {'missed':>6} {'max blocking':>12}")
    for sched, ipc, proto in combos:
        kw = dict(specs=toy_specs) if ipc == "shared_memory" else \
             dict(msg_cfg=MessagePassingConfig(latency=0.2), msgs_per_job=2)
        out = run_cosim(toy_tasks(), sched, ipc, proto, **kw)
        done = [j for j in out["jobs"] if j.finish is not None and j.finish < math.inf]
        m = metrics(done)
        print(f"{sched:9} {ipc:15} {str(proto):8} {m['missed']:>6} "
              f"{max(j.blocking for j in out['jobs']):>12.2f}")
