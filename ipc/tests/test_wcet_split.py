"""WCET split tests. Run from the repo root:  python -m pytest ipc/tests -v"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "core"))

import pytest                                                   # noqa: E402
from task import Task                                           # noqa: E402
from schedulers import simulate                                 # noqa: E402
from messaging import MessagePassingConfig                      # noqa: E402
from interface import (split_wcet, message_passing_tasks,       # noqa: E402
                       effective_utilization, INTENSITY_PLACEHOLDER)
from example_harness_usage import run_cosim                     # noqa: E402


def mk():
    return [Task("a", 10, 3), Task("b", 15, 5), Task("c", 40, 8)]


def finishes(jobs):
    return sorted((j.task.name, j.release, round(j.finish, 9)) for j in jobs)


def test_split_inside_wcet_keeps_total_and_carves_out_overhead():
    cfg = MessagePassingConfig(latency=0.25)
    s = split_wcet(Task("a", 10, 3), 4, cfg)
    assert (s.total, s.comm, s.extra) == (3, pytest.approx(1.0), 0)
    assert s.compute == pytest.approx(2.0) and s.sim_wcet == pytest.approx(3)


def test_utilization_is_unchanged_when_overhead_is_inside_wcet():
    tasks = mk()
    new, splits = message_passing_tasks(tasks, 2, MessagePassingConfig(latency=0.5))
    assert sum(t.utilization for t in new) == pytest.approx(sum(t.utilization for t in tasks))
    assert all(s.extra == 0 for s in splits.values())


@pytest.mark.parametrize("sched", ["RMS", "EDF"])
def test_inside_wcet_makes_latency_irrelevant_to_the_schedule(sched):
    """Documents a modelling consequence: with overhead carved out of a fixed total
    WCET the schedule is the same for every latency (and equals plain core)."""
    ref = finishes(simulate(mk(), sched, 120))
    for lat in (0.0, 0.2, 1.0):
        tasks, _ = message_passing_tasks(mk(), 2, MessagePassingConfig(latency=lat))
        out = run_cosim(tasks, sched, "message_passing", None, horizon=120,
                        msg_cfg=MessagePassingConfig(latency=lat), msgs_per_job=0)
        assert finishes(out["jobs"]) == ref


def test_baseline_latency_adds_only_the_excess_on_top():
    base = 0.2
    at_base = split_wcet(Task("a", 10, 3), 2, MessagePassingConfig(latency=base), baseline_latency=base)
    assert at_base.extra == 0 and at_base.sim_wcet == pytest.approx(3)
    swept = split_wcet(Task("a", 10, 3), 2, MessagePassingConfig(latency=1.0), baseline_latency=base)
    assert swept.comm == pytest.approx(0.4) and swept.extra == pytest.approx(1.6)
    assert swept.sim_wcet == pytest.approx(3 + 1.6)


@pytest.mark.parametrize("sched", ["RMS", "EDF"])
def test_latency_sweep_with_baseline_changes_the_schedule(sched):
    def run(lat):
        tasks, _ = message_passing_tasks(mk(), 2, MessagePassingConfig(latency=lat),
                                         baseline_latency=0.1)
        out = run_cosim(tasks, sched, "message_passing", None, horizon=120,
                        msg_cfg=MessagePassingConfig(latency=lat), msgs_per_job=0)
        return max(j.finish - j.release for j in out["jobs"])
    assert run(0.1) < run(0.5) < run(1.0)


def test_per_task_message_counts():
    new, splits = message_passing_tasks(mk(), {"a": 2}, MessagePassingConfig(latency=0.5))
    assert splits["a"].comm == pytest.approx(1.0) and splits["b"].comm == 0
    assert [t.wcet for t in new] == [3, 5, 8]


def test_inputs_are_not_modified():
    tasks = mk()
    message_passing_tasks(tasks, 2, MessagePassingConfig(latency=0.2), baseline_latency=0.1)
    assert [t.wcet for t in tasks] == [3, 5, 8]


def test_rejects_overhead_that_leaves_no_compute_time():
    with pytest.raises(ValueError):
        split_wcet(Task("a", 10, 1), 4, MessagePassingConfig(latency=0.25))   # 4 * 0.25 = 1.0 >= 1
    with pytest.raises(ValueError):
        split_wcet(Task("a", 10, 3), 2, MessagePassingConfig(latency=0.05), baseline_latency=0.1)


def test_intensity_placeholders_are_defined():
    assert set(INTENSITY_PLACEHOLDER) == {"low", "high"}
    for level in INTENSITY_PLACEHOLDER.values():
        assert {"n_resources", "cs_per_job", "cs_fraction", "msgs_per_job"} <= set(level)
    assert INTENSITY_PLACEHOLDER["high"]["cs_per_job"] > INTENSITY_PLACEHOLDER["low"]["cs_per_job"]


def test_effective_utilization_equals_target_at_baseline_and_rises_in_sweep():
    tasks = mk()
    cfg0 = MessagePassingConfig(latency=0.1)
    _, s0 = message_passing_tasks(tasks, 2, cfg0, baseline_latency=0.1)
    target, eff, over = effective_utilization(tasks, s0)
    assert eff == pytest.approx(target) and not over          # baseline point == main experiment
    _, s1 = message_passing_tasks(tasks, 2, MessagePassingConfig(latency=0.5), baseline_latency=0.1)
    t1, e1, _ = effective_utilization(tasks, s1)
    assert t1 == pytest.approx(target)
    assert e1 == pytest.approx(target + sum(2 * 0.4 / t.period for t in tasks))


def test_effective_utilization_flags_overload():
    tasks = [Task("a", 10, 4), Task("b", 15, 6), Task("c", 40, 8)]    # U = 0.4+0.4+0.2 = 1.0 - eps? exactly 1.0
    tasks[2] = Task("c", 40, 7.6)                                      # U = 0.98
    _, s = message_passing_tasks(tasks, 2, MessagePassingConfig(latency=0.5), baseline_latency=0.1)
    _, eff, over = effective_utilization(tasks, s)
    assert eff > 1 and over
    assert effective_utilization(tasks)[2] is False
