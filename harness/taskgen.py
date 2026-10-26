"""Task-set generation: UUniFast utilizations on a period grid.

D2: UUniFast produces the TOTAL WCET C' = u*T. Communication (critical sections or
message overhead) is carved out of C' later, so one task set per (U, index) is shared
by every condition at that U.
"""
import math

import numpy as np

from task import Task
from uunifast import uunifast

def hyperperiod(tasks_or_periods):
    ps = [getattr(t, "period", t) for t in tasks_or_periods]
    ints = []
    for p in ps:
        if abs(p - round(p)) > 1e-9:
            raise ValueError(f"period {p} is not an integer number of time units; use an integer period grid")
        ints.append(int(round(p)))
    return float(math.lcm(*ints))


class TaskSetBank(dict):
    """{utilization: [task set, ...]} plus `.rejected` = {utilization: n_rejected_draws}."""
    rejected: dict


def _u_key(u):
    return int(round(u * 1000))


def generate_task_sets(utilizations, n_sets, n_tasks, period_grid, base_seed, min_wcet=0.0, d_factor=1.0):
    """Task set i at utilization U depends only on (base_seed, U, i)."""
    if not (0 < d_factor <= 1.0):
        raise ValueError(f"d_factor must be in (0, 1], got {d_factor}")

    bank = TaskSetBank()
    bank.rejected = {}
    grid = np.asarray(period_grid, dtype=float)
    for u in utilizations:
        sets, rejected = [], 0
        for i in range(n_sets):
            rng = np.random.default_rng(np.random.SeedSequence([base_seed, _u_key(u), i]))
            while True:
                utils = uunifast(n_tasks, u, rng)
                periods = rng.choice(grid, size=n_tasks, replace=n_tasks > len(grid))
                order = np.argsort(periods, kind="stable")
                tasks = [Task(f"T{k}", 
                              period=float(periods[j]), 
                              wcet=float(utils[j] * periods[j]),
                              deadline=float(periods[j] * d_factor))
                         for k, j in enumerate(order)]
                
                # Reject if any task is too small (leaves no compute time after carve-out) 
                # or if the task is impossible to schedule (wcet > deadline).
                if all(t.wcet > min_wcet and t.wcet <= t.deadline for t in tasks):
                    break
                rejected += 1
            sets.append(tasks)
        bank[u] = sets
        bank.rejected[u] = rejected
    return bank