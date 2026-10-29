"""End-to-end cases for the synchronous arm, run through run_cosim.
Expected values are hand calculations (see sync_arm_rule.md)."""
from task import Task                                          # noqa: E402
from example_harness_usage import run_cosim                    # noqa: E402


def make(*specs):
    return [Task(name=n, wcet=c, period=t, deadline=d) for n, c, t, d in specs]


def by_name(out):
    return {j.task.name: j for j in out["jobs"]}


def test_case1_handoff_sender_first():
    # S (high) sends after 1 unit, R (low) receives after 2 units.
    sync = {"S": [(1, "send", "R")], "R": [(2, "recv", None)]}
    out = run_cosim(make(("S", 3, 8, 8), ("R", 4, 10, 10)), "DM", "sync_message",
                    horizon=1, sync_specs=sync)
    j = by_name(out)
    assert not out["deadlock"]
    assert j["S"].finish == 5 and j["R"].finish == 7
    assert j["S"].blocking == 2
    assert out["api"].message_log[0].latency == 2


def test_case2_two_task_cycle_deadlocks_at_t1():
    sync = {"A": [(0, "send", "B")], "B": [(1, "send", "A")]}
    out = run_cosim(make(("A", 2, 8, 8), ("B", 3, 10, 10)), "DM", "sync_message",
                    horizon=1, sync_specs=sync)
    assert out["deadlock"]
    assert out["api"].deadlock_time == 1


def test_case3_blocked_sender_misses_deadline():
    sync = {"H": [(0, "send", "L")], "L": [(5, "recv", None)]}
    out = run_cosim(make(("H", 2, 12, 6), ("L", 6, 20, 20)), "DM", "sync_message",
                    horizon=1, sync_specs=sync)
    j = by_name(out)
    assert not out["deadlock"]
    assert j["H"].blocking == 5
    assert j["H"].finish == 7 and j["H"].finish > j["H"].release + 6   # misses 6 by 1
    assert j["L"].finish == 8


def test_case4_receiver_first_accepts_at_once():
    # R (high) waits at its receive from t=0; S (low) sends after 1 unit.
    sync = {"R": [(0, "recv", None)], "S": [(1, "send", "R")]}
    out = run_cosim(make(("R", 2, 8, 8), ("S", 3, 10, 10)), "DM", "sync_message",
                    horizon=1, sync_specs=sync)
    j = by_name(out)
    assert not out["deadlock"]
    assert j["R"].finish == 3 and j["S"].finish == 5
    assert j["R"].blocking == 1
    assert out["api"].message_log[0].latency == 0


def test_receiver_waiting_for_a_later_release_is_not_a_deadlock():
    tasks = [Task(name="R", wcet=2, period=18, deadline=18),
             Task(name="S", wcet=1, period=20, deadline=20, arrival=5)]
    sync = {"R": [(0, "recv", None)], "S": [(0, "send", "R")]}
    out = run_cosim(tasks, "DM", "sync_message", horizon=6, sync_specs=sync)
    j = by_name(out)
    assert not out["deadlock"]
    assert j["R"].finish == 7 and j["S"].finish == 8
