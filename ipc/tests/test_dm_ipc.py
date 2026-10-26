"""DM (deadline-monotonic) through the IPC layer. Run: python -m pytest ipc/tests -v"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "core"))

import pytest                                                  # noqa: E402
from task import Task                                          # noqa: E402
from schedulers import simulate, metrics                       # noqa: E402
from config import CriticalSection as CS                       # noqa: E402
from sim_ipc import simulate_ipc                               # noqa: E402
from interface import IPCInterface                             # noqa: E402
from example_harness_usage import run_cosim                    # noqa: E402


def ab():   # A: T=10, C=3, D=4   B: T=5, C=2, D=5
    return [Task("A", 10, 3, deadline=4), Task("B", 5, 2, deadline=5)]


def missed(jobs):
    return sum(j.missed for j in jobs)


def test_rms_misses_dm_does_not_through_the_ipc_layer():
    out_rms = run_cosim(ab(), "RMS", "shared_memory", None, specs={}, horizon=10)
    out_dm = run_cosim(ab(), "DM", "shared_memory", None, specs={}, horizon=10)
    assert missed(out_rms["jobs"]) == 1
    assert missed(out_dm["jobs"]) == 0


def test_simulate_ipc_accepts_dm():
    jobs_rms, _ = simulate_ipc(ab(), "RMS", "NONE", {}, 10)
    jobs_dm, _ = simulate_ipc(ab(), "DM", "NONE", {}, 10)
    assert missed(jobs_rms) == 1
    assert missed(jobs_dm) == 0


def test_dm_equals_core_dm_without_locks():
    core = {(j.task.name, j.release): j.finish for j in simulate(ab(), "DM", 20)}
    ipc = {(j.task.name, j.release): j.finish
           for j in run_cosim(ab(), "DM", "shared_memory", None, specs={}, horizon=20)["jobs"]}
    assert core == ipc


@pytest.mark.parametrize("proto", ["NONE", "PIP", "ICPP", "SRP"])
def test_dm_runs_with_every_protocol_and_locks(proto):
    tasks = [Task("L", 20, 8, arrival=0, deadline=18), Task("H", 8, 3, arrival=1, deadline=7)]
    specs = {"L": [CS("R", 0, 7)], "H": [CS("R", 0, 1)]}
    out = run_cosim(tasks, "DM", "shared_memory", proto, specs=specs, horizon=20)
    assert not out["deadlock"]
    assert all(j.finish is not None for j in out["jobs"])


@pytest.mark.parametrize("proto", ["PIP", "ICPP", "SRP", "NONE"])
def test_dm_equals_rms_when_deadline_is_period(proto):
    def tasks():
        return [Task("L", 20, 8, arrival=0), Task("H", 8, 3, arrival=1), Task("M", 12, 2)]
    specs = {"L": [CS("R", 0, 7)], "H": [CS("R", 0, 1)]}
    a = run_cosim(tasks(), "RMS", "shared_memory", proto, specs=specs, horizon=48)
    b = run_cosim(tasks(), "DM", "shared_memory", proto, specs=specs, horizon=48)
    fa = {(j.task.name, j.release): j.finish for j in a["jobs"]}
    fb = {(j.task.name, j.release): j.finish for j in b["jobs"]}
    assert fa == fb


def test_unknown_scheduler_still_rejected():
    with pytest.raises(ValueError):
        IPCInterface(ab(), "FIFO", "shared_memory", None, {}, None)