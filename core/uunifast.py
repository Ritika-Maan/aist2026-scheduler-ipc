import numpy as np
from task import Task

PERIODS = [10, 20, 25, 40, 50, 100]   # hyperperiod = 200


def uunifast(n, total_u, rng):
    """Bini & Buttazzo (2005): n utilizations summing to total_u, unbiased."""
    utils, remaining = [], total_u
    for i in range(1, n):
        nxt = remaining * rng.random() ** (1.0 / (n - i))
        utils.append(remaining - nxt)
        remaining = nxt
    utils.append(remaining)
    return utils


def make_taskset(n, total_u, rng):
    utils = uunifast(n, total_u, rng)
    periods = rng.choice(PERIODS, size=n)
    return [Task(f"T{i}", period=float(p), wcet=u * p)
            for i, (u, p) in enumerate(zip(utils, periods))]