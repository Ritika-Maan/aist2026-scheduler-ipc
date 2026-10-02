"""IPC-layer configuration: critical-section model, validation, spec generation.

Core's Task/Job have no notion of resources, so the IPC layer keeps a separate
spec:  specs = {task_name: [CriticalSection, ...]}.

A critical section is expressed in *CPU time executed by the job*:
    lock requested when job has executed `offset`,
    lock released   when job has executed `offset + length`.
Sections may be nested (inner fully inside outer) so that deadlock scenarios
can be modelled; they may not partially overlap.
"""
import random
from dataclasses import dataclass

EPS = 1e-9


@dataclass(frozen=True)
class CriticalSection:
    resource: str
    offset: float   # CPU time into the job when the lock is requested
    length: float   # CPU time the lock is held

    @property
    def end(self):
        return self.offset + self.length


def build_events(cs_list):
    """Turn a task's critical sections into a time-ordered event list.

    Returns [(point, 'lock'|'unlock', resource), ...] with `point` measured in
    CPU time executed by the job. Inner sections unlock before outer ones.
    """
    events, stack = [], []
    for cs in sorted(cs_list, key=lambda c: (c.offset, -c.length)):
        while stack and stack[-1].end <= cs.offset + EPS:
            top = stack.pop()
            events.append((top.end, "unlock", top.resource))
        if stack and cs.end > stack[-1].end + EPS:
            raise ValueError(f"critical sections not properly nested: {stack[-1]} / {cs}")
        if any(s.resource == cs.resource for s in stack):
            raise ValueError(f"resource {cs.resource} nested inside itself")
        events.append((cs.offset, "lock", cs.resource))
        stack.append(cs)
    while stack:
        top = stack.pop()
        events.append((top.end, "unlock", top.resource))
    return events


def validate_specs(tasks, specs):
    by_name = {t.name: t for t in tasks}
    for name, cs_list in specs.items():
        if name not in by_name:
            raise ValueError(f"spec for unknown task {name!r}")
        wcet = by_name[name].wcet
        for cs in cs_list:
            if cs.length <= 0 or cs.offset < 0 or cs.end > wcet + EPS:
                raise ValueError(f"bad critical section for {name}: {cs} (wcet={wcet})")
        build_events(cs_list)   # raises if not properly nested


def generate_specs(tasks, n_resources, cs_per_job, cs_fraction, rng=None):
    """Random flat (non-nested) critical sections for every task.

    Communication intensity knobs (shared-memory case):
      cs_per_job  : number of critical sections per job   (0 = no sharing)
      cs_fraction : fraction of each job's WCET spent inside critical sections
    Each job's WCET is split into cs_per_job equal slots; one section is placed
    at a random offset inside each slot, on a random resource out of n_resources.
    """
    rng = rng or random.Random()
    specs = {}
    if cs_per_job <= 0:
        return specs
    for t in tasks:
        slot = t.wcet / cs_per_job
        length = cs_fraction * slot
        sections = []
        for i in range(cs_per_job):
            off = i * slot + rng.uniform(0, slot - length)
            sections.append(CriticalSection(f"R{rng.randrange(n_resources)}", off, length))
        specs[t.name] = sections
    return specs
