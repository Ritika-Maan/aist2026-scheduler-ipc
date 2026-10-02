"""Resource-access protocols: PIP, ICPP (immediate ceiling), SRP.

All protocols share one interface, used by sim_ipc.simulate_ipc:

    prepare(tasks)            precompute ceilings once priorities are assigned
    key(job, state)           effective priority key, LOWER = runs first
    can_start(job, state)     SRP start test (True for the other protocols)
    request(job, res, state)  lock request -> True if granted, False if blocked
    release(job, res, state)  unlock; may hand the lock to a waiting job

Priority convention matches core: lower number / earlier deadline wins.
"""
import math


class State:
    def __init__(self):
        self.ready = []        # all pending jobs (running, preempted, lock-blocked)
        self.holder = {}       # resource -> job holding it
        self.waiters = {}      # resource -> list of jobs blocked on it
        self.deadlock = False


class Protocol:
    name = "BASE"

    def __init__(self, policy, specs):
        if policy not in ("RMS", "EDF"):
            raise ValueError("policy must be 'RMS' or 'EDF'")
        self.policy = policy
        self.specs = specs

    def prepare(self, tasks):
        pass

    def base_key(self, job):
        if self.policy == "RMS":
            return (job.task.priority, job.release)
        return (job.abs_deadline, job.release)

    def key(self, job, state):
        return self.base_key(job)

    def can_start(self, job, state):
        return True

    def select(self, state):
        """Pick the job to run, or None if every pending job is lock-blocked."""
        live = [j for j in state.ready if j.blocked_on is None]
        if not live:
            return None
        cand = min(live, key=lambda j: self.key(j, state))
        if self.can_start(cand, state):
            return cand
        # SRP: top-priority job may not start yet; a started job keeps running.
        started = [j for j in live if j.start is not None]
        if not started:
            raise RuntimeError("SRP inconsistency: top job blocked but nothing started")
        return min(started, key=lambda j: self.key(j, state))

    def request(self, job, res, state):
        raise NotImplementedError

    def release(self, job, res, state):
        raise NotImplementedError

    @staticmethod
    def _grant(job, res, state):
        state.holder[res] = job
        job.ev_idx += 1


class PIP(Protocol):
    """Priority Inheritance Protocol (transitive). inherit=False gives plain
    locks with no protocol, used to demonstrate unbounded priority inversion."""
    name = "PIP"

    def __init__(self, policy, specs, inherit=True):
        super().__init__(policy, specs)
        self.inherit = inherit
        if not inherit:
            self.name = "NONE"

    def key(self, job, state, _seen=None):
        k = self.base_key(job)
        if not self.inherit:
            return k
        seen = (_seen or frozenset()) | {id(job)}
        for res, h in state.holder.items():
            if h is job:
                for w in state.waiters.get(res, []):
                    if id(w) not in seen:
                        k = min(k, self.key(w, state, seen))
        return k

    def request(self, job, res, state):
        if state.holder.get(res) is None:
            self._grant(job, res, state)
            return True
        job.blocked_on = res
        state.waiters.setdefault(res, []).append(job)
        if self._cycle(job, state):
            state.deadlock = True
        return False

    def release(self, job, res, state):
        if state.holder.get(res) is not job:
            raise RuntimeError(f"{job.task.name} releases {res} it does not hold")
        del state.holder[res]
        waiting = state.waiters.get(res, [])
        if waiting:   # hand the lock to the highest effective-priority waiter
            nxt = min(waiting, key=lambda x: self.key(x, state))
            waiting.remove(nxt)
            nxt.blocked_on = None
            self._grant(nxt, res, state)

    @staticmethod
    def _cycle(job, state):
        seen, cur = set(), job
        while cur.blocked_on is not None:
            if id(cur) in seen:
                return True
            seen.add(id(cur))
            cur = state.holder[cur.blocked_on]
        return False


class ICPP(Protocol):
    """Immediate priority ceiling (fixed priority only). A job that locks a
    resource immediately runs at that resource's ceiling, so a lock request
    never finds the resource held and deadlock is impossible."""
    name = "ICPP"

    def __init__(self, policy, specs):
        if policy != "RMS":
            raise ValueError("ICPP is a fixed-priority protocol; use policy='RMS'")
        super().__init__(policy, specs)

    def prepare(self, tasks):
        prio = {t.name: t.priority for t in tasks}
        self.ceil = {}
        for name, cs_list in self.specs.items():
            for cs in cs_list:
                self.ceil[cs.resource] = min(self.ceil.get(cs.resource, math.inf), prio[name])

    def key(self, job, state):
        k = self.base_key(job)
        for res, h in state.holder.items():
            if h is job:
                k = min(k, (self.ceil[res], job.release))
        return k

    def request(self, job, res, state):
        if res in state.holder:
            raise RuntimeError(f"ICPP invariant violated: {res} already held")
        self._grant(job, res, state)
        return True

    def release(self, job, res, state):
        if state.holder.get(res) is not job:
            raise RuntimeError(f"{job.task.name} releases {res} it does not hold")
        del state.holder[res]


class SRP(Protocol):
    """Stack Resource Policy (Baker). Scheduler-agnostic: preemption level is
    derived from relative deadline under EDF, from RMS priority under RMS, so
    the same class gives EDF+SRP and the RMS+SRP control.

    A job may START only if its preemption level exceeds the system ceiling
    (highest ceiling among currently locked resources). Once started it never
    blocks on a lock, and deadlock is impossible."""
    name = "SRP"

    def prepare(self, tasks):
        if self.policy == "EDF":
            self.pi = {t.name: -t.deadline for t in tasks}
        else:
            self.pi = {t.name: -t.priority for t in tasks}
        self.ceil = {}
        for name, cs_list in self.specs.items():
            for cs in cs_list:
                self.ceil[cs.resource] = max(self.ceil.get(cs.resource, -math.inf), self.pi[name])

    def system_ceiling(self, state):
        return max((self.ceil[r] for r in state.holder), default=-math.inf)

    def can_start(self, job, state):
        return job.start is not None or self.pi[job.task.name] > self.system_ceiling(state)

    def request(self, job, res, state):
        if res in state.holder:
            raise RuntimeError(f"SRP invariant violated: {res} already held")
        self._grant(job, res, state)
        return True

    def release(self, job, res, state):
        if state.holder.get(res) is not job:
            raise RuntimeError(f"{job.task.name} releases {res} it does not hold")
        del state.holder[res]


def make_protocol(name, policy, specs):
    name = name.upper()
    if name == "NONE":
        return PIP(policy, specs, inherit=False)
    if name == "PIP":
        return PIP(policy, specs)
    if name == "ICPP":
        return ICPP(policy, specs)
    if name == "SRP":
        return SRP(policy, specs)
    raise ValueError(f"unknown protocol {name!r}")
