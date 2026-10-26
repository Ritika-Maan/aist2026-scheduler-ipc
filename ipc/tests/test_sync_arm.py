"""Hand-built validation cases for the synchronous (rendezvous) arm.
Each expected value comes from the hand calculation in sync_arm_rule.md."""
from interface import IPCInterface                             # noqa: E402
from task import Task                                          # noqa: E402


def make(*specs):
    return [Task(name=n, wcet=c, period=t, deadline=d) for n, c, t, d in specs]


def job(ipc, name):
    return ipc._jobs[(name, 0)]


def test_case1_simple_handoff():
    ipc = IPCInterface(make(("S", 3, 8, 8), ("R", 4, 10, 10)), "DM", ipc="sync_message")
    ipc.on_job_release("S", 0)
    ipc.on_job_release("R", 0)
    assert ipc.select() == ("S", 0)
    ipc.record_run("S", 0, 0, 1)
    assert ipc.on_sync_send("S", 0, "R", 1) is False
    assert ipc.can_dispatch("S", 0) is False
    assert ipc.select() == ("R", 0)
    ipc.record_run("R", 0, 1, 3)
    assert ipc.on_sync_receive("R", 0, 3) == ("S", 0)
    assert ipc.select() == ("S", 0)
    ipc.record_run("S", 0, 3, 5)
    ipc.on_job_finish("S", 0, 5)
    ipc.record_run("R", 0, 5, 7)
    ipc.on_job_finish("R", 0, 7)
    assert ipc.blocking_time("S", 0) == 2
    assert job(ipc, "S").finish == 5 and job(ipc, "R").finish == 7
    assert ipc.message_log[0].latency == 2
    assert not ipc.deadlock


def test_case2_two_task_cycle():
    ipc = IPCInterface(make(("A", 2, 8, 8), ("B", 3, 10, 10)), "DM", ipc="sync_message")
    ipc.on_job_release("A", 0)
    ipc.on_job_release("B", 0)
    assert ipc.select() == ("A", 0)
    assert ipc.on_sync_send("A", 0, "B", 0) is False
    assert not ipc.deadlock
    assert ipc.select() == ("B", 0)
    ipc.record_run("B", 0, 0, 1)
    assert ipc.on_sync_send("B", 0, "A", 1) is False
    assert ipc.deadlock
    assert ipc.deadlock_time == 1


def test_case3_blocked_sender_misses_deadline():
    ipc = IPCInterface(make(("H", 2, 12, 6), ("L", 6, 20, 20)), "DM", ipc="sync_message")
    ipc.on_job_release("H", 0)
    ipc.on_job_release("L", 0)
    assert ipc.select() == ("H", 0)
    assert ipc.on_sync_send("H", 0, "L", 0) is False
    assert ipc.select() == ("L", 0)
    ipc.record_run("L", 0, 0, 5)
    assert ipc.on_sync_receive("L", 0, 5) == ("H", 0)
    assert ipc.select() == ("H", 0)
    ipc.record_run("H", 0, 5, 7)
    ipc.on_job_finish("H", 0, 7)
    ipc.record_run("L", 0, 7, 8)
    ipc.on_job_finish("L", 0, 8)
    assert ipc.blocking_time("H", 0) == 5
    h = job(ipc, "H")
    assert h.finish == 7 and h.finish > h.release + 6      # misses deadline 6 by 1
    assert job(ipc, "L").finish == 8
