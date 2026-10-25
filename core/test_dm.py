import math
import random

from task import Task
from schedulers import simulate, metrics, job_log


def hand_tasks():
    return [Task("A", period=10, wcet=3, deadline=4),
            Task("B", period=5, wcet=2, deadline=5)]


def test_hand_example_rms_misses_dm_and_edf_do_not():
    assert metrics(simulate(hand_tasks(), "RMS", 10))["missed"] == 1
    assert metrics(simulate(hand_tasks(), "DM", 10))["missed"] == 0
    assert metrics(simulate(hand_tasks(), "EDF", 10))["missed"] == 0


def test_job_log_slack():
    rows = job_log(simulate(hand_tasks(), "RMS", 10))
    a1 = [r for r in rows if r["task"] == "A"][0]
    assert a1["finish"] == 5 and a1["response"] == 5
    assert a1["slack"] == -1
    dm = job_log(simulate(hand_tasks(), "DM", 10))
    assert min(r["slack"] for r in dm) >= 0


def test_dm_equals_rms_when_deadline_is_period():
    rng = random.Random(42)
    periods = [10, 20, 25, 40, 50, 100]
    for _ in range(100):
        n = rng.randint(2, 5)
        tasks = [Task(f"t{k}", period=(p := rng.choice(periods)),
                      wcet=p * rng.uniform(0.02, 0.8 / n)) for k in range(n)]
        if len({t.period for t in tasks}) < n:   # equal periods tie differently
            continue
        r = {(j.task.name, j.release): j.finish for j in simulate(tasks, "RMS", 200)}
        d = {(j.task.name, j.release): j.finish for j in simulate(tasks, "DM", 200)}
        assert r == d


def rta_schedulable(tasks):
    """Exact response-time analysis for deadline-monotonic, D <= T, arrival 0."""
    order = sorted(tasks, key=lambda t: (t.deadline, t.period))
    for i, t in enumerate(order):
        hp = order[:i]
        r = t.wcet
        while True:
            new = t.wcet + sum(math.ceil(r / h.period) * h.wcet for h in hp)
            if new > t.deadline:
                return False
            if new == r:
                break
            r = new
    return True


def test_dm_matches_exact_analysis_for_constrained_deadlines():
    rng = random.Random(7)
    periods = [10, 20, 25, 40, 50, 100]      # hyperperiod 200
    seen = {True: 0, False: 0}
    for _ in range(400):
        n = rng.randint(2, 5)
        tasks = []
        for k in range(n):
            p = rng.choice(periods)
            d = max(1, round(p * rng.choice([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])))
            c = rng.randint(1, max(1, int(d * 0.5)))
            tasks.append(Task(f"t{k}", period=p, wcet=c, deadline=d))
        expected = rta_schedulable(tasks)
        got = metrics(simulate(tasks, "DM", 200))["missed"] == 0
        assert got == expected
        seen[expected] += 1
    assert seen[True] > 20 and seen[False] > 20
