"""A.2 integration interface: lets a co-simulation harness (harness/) drive the
IPC layer without touching core/ or the IPC internals.

The harness owns the clock, the ready queue and the dispatch decision. This
adapter owns the IPC state (lock holders, waiters, ceilings, message buffer)
and answers the harness's queries. It is a THIN wrapper: every decision is made
by the existing code (protocols.py, sim_ipc.IPCJob, messaging.py).

Identity
    task  : Task.name (str)
    job   : (task.name, release)   -- always pass the SAME release value you
            passed to on_job_release (floats are used as dictionary keys).

API (A.2)
    can_dispatch(task_name, release, time)          -> bool
    on_lock_request(task_name, release, res, time)  -> bool   (True = granted)
    on_lock_release(task_name, release, res, time)  -> [(task_name, release)]  unblocked jobs
    priority_override(task_name, release, time)     -> key | None
    on_message_send(sender, release, receiver, time, size=0, payload=None) -> MessageResult
    blocking_events                                 -> [BlockingEvent]

Supporting calls the harness needs to keep the IPC state in step:
    on_job_release / on_job_start / record_run / on_job_finish
    next_sync_point / executed / remaining          (when to fire lock events)
    effective_key / select                          (dispatch ordering)
    report_no_dispatchable / finalize_deadlock      (stall handling)

`time` arguments are accepted for a uniform signature and for bookkeeping
(start times, deadlock time); the protocols themselves are time-independent.

Blocking-time definition (identical to sim_ipc.py): the time a job is pending
while a running job has a strictly worse BASE priority.
"""
import math
import os
import sys
from dataclasses import dataclass, replace

_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (_HERE, os.path.join(_HERE, "..", "core")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from config import EPS, build_events, validate_specs      # noqa: E402
from protocols import State, make_protocol                # noqa: E402
from sim_ipc import IPCJob                                # noqa: E402
from schedulers import assign_rms_priorities, assign_dm_priorities  # noqa: E402  (core)
from messaging import (AsyncMessageChannel,               # noqa: E402
                       MessagePassingConfig, message_overhead)

SCHEDULERS = ("RMS", "EDF", "DM")
IPC_MODES = ("shared_memory", "message_passing", "sync_message")


@dataclass(frozen=True)
class SyncPoint:
    """Next lock/unlock a job will perform, in CPU time executed by the job."""
    offset: float
    kind: str        # "lock" | "unlock"
    resource: str


@dataclass(frozen=True)
class BlockingEvent:
    """A merged interval during which `task_name`'s job (released at `release`)
    was pending while a lower-priority job ran.

    cause: "lock"          job is blocked waiting for `resource`
           "srp_ceiling"   SRP forbids the job from starting (resource = ceiling setter)
           "ceiling"       ICPP: running job holds `resource` at its ceiling
           "inheritance"   PIP: running job runs at an inherited priority
    """
    task_name: str
    release: float
    start: float
    end: float
    resource: str
    cause: str

    @property
    def job(self):
        return (self.task_name, self.release)

    @property
    def duration(self):
        return self.end - self.start


@dataclass(frozen=True)
class MessageResult:
    sender: str
    receiver: str
    release: float                 # release of the sending job
    send_time: float
    available_time: float          # None if dropped
    latency: float
    size: float
    dropped: bool                  # True if the buffer was full


def inflate_wcet(tasks, msgs_per_job, msg_cfg=None):
    """Return COPIES of `tasks` whose WCET includes message-passing overhead:
    wcet + msgs_per_job * message_overhead(msg_cfg).  msgs_per_job is an int or
    {task_name: int}. Latency is read from the config (never hardcoded).
    Only message overhead is folded into WCET; lock blocking is measured."""
    over = message_overhead(msg_cfg)
    out = []
    for t in tasks:
        n = msgs_per_job.get(t.name, 0) if isinstance(msgs_per_job, dict) else msgs_per_job
        out.append(replace(t, wcet=t.wcet + n * over))
    return out


# Intensity levels used so far. PLACEHOLDERS agreed only informally in the team chat:
# the harness may override them, and the paper must state/justify the final values.
INTENSITY_PLACEHOLDER = {
    "low":  dict(n_resources=2, cs_per_job=1, cs_fraction=0.10, msgs_per_job=1),
    "high": dict(n_resources=2, cs_per_job=4, cs_fraction=0.30, msgs_per_job=4),
}


@dataclass(frozen=True)
class WcetSplit:
    """How one task's WCET divides between computation and message passing.

    total   C'  : the WCET the harness generated (U is computed on this)
    compute     : total - comm, the non-communication part
    comm        : message overhead carved OUT of total (m * baseline latency)
    extra       : overhead beyond the baseline latency, ADDED on top (latency sweep only)
    sim_wcet    : what the scheduler must be given = total + extra
    """
    task_name: str
    total: float
    compute: float
    comm: float
    extra: float

    @property
    def sim_wcet(self):
        return self.total + self.extra


def split_wcet(task, msgs_per_job, msg_cfg, baseline_latency=None):
    """Split `task.wcet` (the generated total C') into compute and message overhead.

    * baseline_latency=None: all overhead m*L is inside C' (extra = 0). The schedule
      is then IDENTICAL for every latency value: latency cannot change miss rates.
    * baseline_latency=L0: the baseline overhead m*L0 is inside C'; if the configured
      latency L > L0, the additional m*(L-L0) is added on top (utilization rises above
      target). Use this for a latency sweep. L < L0 is rejected.
    Raises ValueError if the carved-out overhead leaves no computation time."""
    m = msgs_per_job.get(task.name, 0) if isinstance(msgs_per_job, dict) else msgs_per_job
    L = message_overhead(msg_cfg)
    base = L if baseline_latency is None else baseline_latency
    if L < base - EPS:
        raise ValueError(f"latency {L} is below baseline_latency {base}")
    comm, extra = m * base, m * (L - base)
    if comm >= task.wcet - EPS:
        raise ValueError(f"{task.name}: message overhead {comm} leaves no compute time "
                         f"in WCET {task.wcet}")
    return WcetSplit(task.name, task.wcet, task.wcet - comm, comm, extra)


def message_passing_tasks(tasks, msgs_per_job, msg_cfg, baseline_latency=None):
    """Apply split_wcet to every task. Returns (task copies with wcet = sim_wcet,
    {task_name: WcetSplit}). The input tasks are not modified."""
    splits = {t.name: split_wcet(t, msgs_per_job, msg_cfg, baseline_latency) for t in tasks}
    return [replace(t, wcet=splits[t.name].sim_wcet) for t in tasks], splits


def effective_utilization(tasks, splits=None):
    """(target_U, effective_U, overload) for a latency-sweep point.

    tasks  : the ORIGINAL tasks (wcet = generated total C')
    splits : {task_name: WcetSplit} from message_passing_tasks (None = no extra)
    target_U    = sum(C'/T)
    effective_U = target_U + sum(extra/T)   (what the scheduler really sees)
    overload    = effective_U > 1: do not compare such points directly, mark as overload."""
    target = sum(t.wcet / t.period for t in tasks)
    extra = sum(splits[t.name].extra / t.period for t in tasks) if splits else 0.0
    eff = target + extra
    return target, eff, eff > 1 + EPS


class IPCInterface:
    def __init__(self, tasks, scheduler, ipc="shared_memory", protocol=None,
                 specs=None, msg_cfg=None):
        """scheduler: "RMS" | "EDF" | "DM" (deadline-monotonic).   ipc: "shared_memory" | "message_passing".
        protocol: "PIP" | "ICPP" | "SRP" | "NONE"/None (shared_memory only; None = plain
        locks, no protocol).  specs: {task_name: [CriticalSection]} (shared_memory).
        msg_cfg: MessagePassingConfig (message_passing; default latency 0).
        Under "RMS", task priorities are assigned in place (as core does)."""
        if scheduler not in SCHEDULERS:
            raise ValueError(f"scheduler must be one of {SCHEDULERS}")
        if ipc not in IPC_MODES:
            raise ValueError(f"ipc must be one of {IPC_MODES}")
        proto = "NONE" if protocol is None else str(protocol).upper()
        specs = dict(specs or {})
        if ipc == "message_passing":
            if proto != "NONE":
                raise ValueError("message_passing uses no locking protocol (protocol=None)")
            if specs:
                raise ValueError("critical-section specs apply to shared_memory only")
            msg_cfg = msg_cfg or MessagePassingConfig()
            self.channel = AsyncMessageChannel(msg_cfg)
        elif ipc == "sync_message":
            if proto != "NONE":
                raise ValueError("sync_message uses no locking protocol (protocol=None)")
            if specs:
                raise ValueError("critical-section specs apply to shared_memory only")
            if msg_cfg is not None:
                raise ValueError("msg_cfg applies to message_passing only")
            self.channel = None
        else:
            if msg_cfg is not None:
                raise ValueError("msg_cfg applies to message_passing only")
            self.channel = None

        self.tasks = list(tasks)
        names = [t.name for t in self.tasks]
        if len(set(names)) != len(names):
            raise ValueError("task names must be unique")
        self.scheduler, self.ipc, self.protocol_name = scheduler, ipc, proto
        self.specs, self.msg_cfg = specs, msg_cfg

        validate_specs(self.tasks, specs)
        if scheduler == "RMS":
            assign_rms_priorities(self.tasks)
        elif scheduler == "DM":
            assign_dm_priorities(self.tasks)
        # DM is fixed-priority like RMS; only the priority order differs.
        proto_policy = "RMS" if scheduler == "DM" else scheduler
        self._prot = make_protocol(proto, proto_policy, specs)   # ValueError for ICPP+EDF etc.
        self._prot.prepare(self.tasks)
        self._state = State()
        self._by_name = {t.name: t for t in self.tasks}
        self._events = {t.name: build_events(specs.get(t.name, [])) for t in self.tasks}
        self._jobs = {}
        self._blocking = []
        self._last = {}
        self.message_log = []
        self.deadlock_time = None
        self._sync_wait = {}     # receiver_name -> [(blocked sender job, send_time)]
        self._recv_wait = {}     # receiver_name -> job waiting at its receive
        self._sync_target = {}   # blocked sender task name -> receiver task name

    # ------------------------------------------------------------ job lifecycle
    def on_job_release(self, task_name, release):
        key = (task_name, release)
        if key in self._jobs:
            raise ValueError(f"job {key} already released")
        task = self._by_name[task_name]
        job = IPCJob(task, release, release + task.deadline, task.wcet,
                     events=self._events[task_name])
        self._jobs[key] = job
        self._state.ready.append(job)
        return key

    def on_job_start(self, task_name, release, time):
        job = self._pending(task_name, release)
        if job.start is None:
            job.start = time

    def on_job_finish(self, task_name, release, time):
        job = self._pending(task_name, release)
        if any(h is job for h in self._state.holder.values()):
            raise RuntimeError(f"job {(task_name, release)} finished while holding a lock")
        if job.ev_idx < len(job.events):
            raise RuntimeError(f"job {(task_name, release)} finished with unprocessed lock events")
        job.remaining = 0.0
        job.finish = time
        self._state.ready.remove(job)

    def record_run(self, task_name, release, t0, t1):
        """The harness ran this job on the CPU during [t0, t1]. Updates the job's
        progress and the blocking accounting (same rule as sim_ipc.py)."""
        job = self._pending(task_name, release)
        run = t1 - t0
        if run < 0:
            raise ValueError("t1 < t0")
        if job.start is None:
            job.start = t0
        bk = self._prot.base_key(job)
        for j in self._state.ready:
            if j is not job and self._prot.base_key(j) < bk:
                j.blocking += run
                if run > EPS:
                    self._log_blocking(j, job, t0, t1)
        job.remaining -= run

    # ------------------------------------------------------------ dispatch queries
    def can_dispatch(self, task_name, release, time=None):
        """May this job run now? False if it is lock-blocked, or if SRP forbids it
        from starting (it is not the job that would be dispatched, and a started
        job must keep running first)."""
        job = self._pending(task_name, release)
        if job.blocked_on is not None:
            return False
        live = [j for j in self._state.ready if j.blocked_on is None]
        top = min(live, key=lambda j: self._prot.key(j, self._state))
        if self._prot.can_start(top, self._state):
            return True
        return job.start is not None

    def priority_override(self, task_name, release, time=None):
        """Effective priority key if the protocol overrides the base key (PIP
        inheritance, ICPP ceiling); None if the base key applies. Lower = first."""
        job = self._pending(task_name, release)
        k = self._prot.key(job, self._state)
        return None if k == self._prot.base_key(job) else k

    def effective_key(self, task_name, release, time=None):
        """Override if any, else the base key. Harness: pick min over dispatchable jobs."""
        job = self._pending(task_name, release)
        return self._prot.key(job, self._state)

    def select(self, time=None):
        """(task_name, release) the protocol would run next, or None if all are blocked."""
        job = self._prot.select(self._state)
        return None if job is None else (job.task.name, job.release)

    # ------------------------------------------------------------ locks
    def next_sync_point(self, task_name, release):
        """Next lock/unlock of the job as SyncPoint, or None. Run the job until
        executed(...) reaches .offset, then call on_lock_request / on_lock_release."""
        job = self._job(task_name, release)
        if job.ev_idx >= len(job.events):
            return None
        off, kind, res = job.events[job.ev_idx]
        return SyncPoint(off, kind, res)

    def executed(self, task_name, release):
        return self._job(task_name, release).executed

    def remaining(self, task_name, release):
        return self._job(task_name, release).remaining

    def on_lock_request(self, task_name, release, resource, time):
        """True if the lock is granted. False: the job is now blocked (PIP/NONE);
        `deadlock` becomes True if that closes a wait cycle."""
        job = self._pending(task_name, release)
        self._expect(job, "lock", resource)
        if job.blocked_on is not None:
            raise RuntimeError(f"job {(task_name, release)} is already blocked")
        if job.start is None:
            job.start = time
        granted = self._prot.request(job, resource, self._state)
        if self._state.deadlock and self.deadlock_time is None:
            self.deadlock_time = time
        return granted

    def on_lock_release(self, task_name, release, resource, time):
        """Unlock. Returns [(task_name, release)] of jobs that were blocked on this
        resource and now hold it / are unblocked."""
        job = self._pending(task_name, release)
        self._expect(job, "unlock", resource)
        waiting = list(self._state.waiters.get(resource, []))
        self._prot.release(job, resource, self._state)
        job.ev_idx += 1
        return [(w.task.name, w.release) for w in waiting if w.blocked_on is None]

    # ------------------------------------------------------------ messages
    def on_message_send(self, sender_name, release, receiver_name, time, size=0, payload=None):
        """Asynchronous, buffered send: never blocks the sender. Latency comes from
        the MessagePassingConfig. A full buffer is reported as dropped=True (no
        exception). `size` is recorded; the baseline model has a flat latency."""
        if self.channel is None:
            raise RuntimeError("on_message_send requires ipc='message_passing'")
        self._job(sender_name, release)
        if receiver_name not in self._by_name:
            raise KeyError(f"unknown receiver task {receiver_name!r}")
        cfg = self.channel.config
        try:
            ev = self.channel.send(sender_name, receiver_name, time, payload)
            res = MessageResult(sender_name, receiver_name, release, ev.send_time,
                                ev.available_time, ev.latency, size, False)
        except BufferError:
            res = MessageResult(sender_name, receiver_name, release, float(time),
                                None, cfg.latency, size, True)
        self.message_log.append(res)
        return res

    def on_message_receive(self, receiver_name, time):
        """Earliest available message for `receiver_name` (MessageEvent) or None."""
        if self.channel is None:
            raise RuntimeError("on_message_receive requires ipc='message_passing'")
        return self.channel.receive(receiver_name, time)

    @property
    def message_overhead(self):
        return message_overhead(self.msg_cfg) if self.channel else 0.0

    @property
    def dropped_messages(self):
        return sum(m.dropped for m in self.message_log)

    # ------------------------------------------------------------ synchronous (rendezvous) messages
    def on_sync_send(self, sender_name, release, receiver_name, time):
        """Rendezvous send. True: receiver was already waiting, accepted now, sender
        keeps running. False: sender is blocked until the receiver reaches its receive;
        `deadlock` becomes True if that closes a wait cycle."""
        if self.ipc != "sync_message":
            raise RuntimeError("on_sync_send requires ipc='sync_message'")
        job = self._pending(sender_name, release)
        if receiver_name not in self._by_name:
            raise KeyError(f"unknown receiver task {receiver_name!r}")
        if job.blocked_on is not None:
            raise RuntimeError(f"job {(sender_name, release)} is already blocked")
        if job.start is None:
            job.start = time
        rjob = self._recv_wait.pop(receiver_name, None)
        if rjob is not None:                      # receiver already waiting
            rjob.blocked_on = None
            self._log_sync(job, receiver_name, time, time)
            return True
        job.blocked_on = "sync:" + receiver_name
        self._sync_wait.setdefault(receiver_name, []).append((job, time))
        self._sync_target[sender_name] = receiver_name
        if self._sync_cycle(sender_name):
            self._state.deadlock = True
            if self.deadlock_time is None:
                self.deadlock_time = time
        return False

    def on_sync_receive(self, receiver_name, release, time):
        """Receive point. Returns (sender_name, release) if a sender was waiting (it is
        unblocked now). Returns None if the receiver must wait: it is blocked until a
        sender arrives."""
        if self.ipc != "sync_message":
            raise RuntimeError("on_sync_receive requires ipc='sync_message'")
        job = self._pending(receiver_name, release)
        if job.blocked_on is not None:
            raise RuntimeError(f"job {(receiver_name, release)} is already blocked")
        if job.start is None:
            job.start = time
        queue = self._sync_wait.get(receiver_name)
        if queue:
            sender, t_send = queue.pop(0)
            sender.blocked_on = None
            self._sync_target.pop(sender.task.name, None)
            self._log_sync(sender, receiver_name, t_send, time)
            return (sender.task.name, sender.release)
        job.blocked_on = "sync_recv"
        self._recv_wait[receiver_name] = job
        return None

    def _sync_cycle(self, sender_name):
        """True if following 'blocked sender -> its receiver' edges returns to sender_name."""
        seen, cur = set(), self._sync_target.get(sender_name)
        while cur is not None and cur not in seen:
            if cur == sender_name:
                return True
            seen.add(cur)
            cur = self._sync_target.get(cur)
        return False

    def _log_sync(self, sender, receiver_name, t_send, t_accept):
        self.message_log.append(MessageResult(sender.task.name, receiver_name, sender.release,
                                              t_send, t_accept, t_accept - t_send, 0, False))

    # ------------------------------------------------------------ results / state
    @property
    def blocking_events(self):
        return sorted(self._blocking, key=lambda e: (e.start, e.task_name, e.release))

    def blocking_time(self, task_name, release):
        return self._job(task_name, release).blocking

    @property
    def deadlock(self):
        return self._state.deadlock

    @property
    def jobs(self):
        """All released jobs (sim_ipc.IPCJob: .finish, .blocking, .missed, ...)."""
        return list(self._jobs.values())

    def pending(self):
        """[(task_name, release)] of unfinished jobs, in release order."""
        return [(j.task.name, j.release) for j in self._state.ready]

    def has_pending(self):
        return bool(self._state.ready)

    def report_no_dispatchable(self, time):
        """Call when jobs are pending but none can be dispatched: a stall = deadlock."""
        self._state.deadlock = True
        if self.deadlock_time is None:
            self.deadlock_time = time

    def finalize_deadlock(self):
        """After a deadlock, mark unfinished jobs finish=inf (missed), as sim_ipc does."""
        for j in self._state.ready:
            j.finish = math.inf
        self._state.ready.clear()

    # ------------------------------------------------------------ internals
    def _job(self, task_name, release):
        try:
            return self._jobs[(task_name, release)]
        except KeyError:
            raise KeyError(f"unknown job {(task_name, release)}: call on_job_release first") from None

    def _pending(self, task_name, release):
        job = self._job(task_name, release)
        if job not in self._state.ready:
            raise ValueError(f"job {(task_name, release)} already finished")
        return job

    def _expect(self, job, kind, resource):
        sp = self.next_sync_point(job.task.name, job.release)
        if sp is None or sp.kind != kind or sp.resource != resource:
            raise ValueError(f"job {(job.task.name, job.release)}: next sync point is {sp}, "
                             f"not {kind} {resource}")
        if sp.offset > job.executed + EPS:
            raise ValueError(f"job {(job.task.name, job.release)} has not reached {sp} yet "
                             f"(executed {job.executed})")

    def _cause(self, waiting, running):
        st, prot = self._state, self._prot
        if isinstance(waiting.blocked_on, str) and waiting.blocked_on.startswith("sync"):
            return "rendezvous", waiting.blocked_on.split(":", 1)[-1]
        if waiting.blocked_on is not None:
            return "lock", waiting.blocked_on
        held = [r for r, h in st.holder.items() if h is running]
        if self.protocol_name == "SRP":
            return "srp_ceiling", max(st.holder, key=lambda r: prot.ceil[r], default=None)
        if self.protocol_name == "ICPP":
            return "ceiling", (held[0] if held else None)
        return "inheritance", (held[0] if held else None)

    def _log_blocking(self, waiting, running, t0, t1):
        cause, res = self._cause(waiting, running)
        key = (waiting.task.name, waiting.release)
        idx = self._last.get(key)
        if idx is not None:
            last = self._blocking[idx]
            if last.cause == cause and last.resource == res and abs(last.end - t0) <= EPS:
                self._blocking[idx] = replace(last, end=t1)
                return
        self._blocking.append(BlockingEvent(waiting.task.name, waiting.release,
                                            t0, t1, res, cause))
        self._last[key] = len(self._blocking) - 1
