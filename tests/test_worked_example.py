"""Section 4.2 worked example, run through the IPC layer.

L: C=8, T=D=20, arrives at 0, holds R for its first 7 units of execution.
H: C=3, T=D=8,  arrives at 1, asks for R as soon as it starts.
By hand: H is blocked from 1 to 7 (6 units), runs 7 to 10, misses its
deadline of 9 by 1. Without locks H runs 1 to 4 and meets it.
Run from the repo root:  python -m pytest tests -v
"""
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
for p in ("ipc", "core"):
    sys.path.insert(0, os.path.join(ROOT, p))

import pytest                                              # noqa: E402
from task import Task                                      # noqa: E402
from config import CriticalSection as CS                   # noqa: E402
from example_harness_usage import run_cosim                # noqa: E402

SPECS = {"L": [CS("R", 0, 7)], "H": [CS("R", 0, 1)]}


def tasks():
    return [Task("L", 20, 8, arrival=0), Task("H", 8, 3, arrival=1)]


def first_h(out):
    return min((j for j in out["jobs"] if j.task.name == "H"),
               key=lambda j: j.release)


@pytest.mark.parametrize("sched,proto", [
    ("RMS", "PIP"), ("RMS", "ICPP"), ("RMS", "SRP"), ("EDF", "SRP")])
def test_blocking_causes_the_miss(sched, proto):
    out = run_cosim(tasks(), sched, "shared_memory", proto, specs=SPECS, horizon=20)
    h = first_h(out)
    assert not out["deadlock"]
    assert h.blocking == pytest.approx(6)
    assert h.finish == pytest.approx(10)
    assert h.missed
    assert h.finish - h.abs_deadline == pytest.approx(1)


@pytest.mark.parametrize("sched", ["RMS", "EDF"])
def test_without_locks_h_meets_deadline(sched):
    out = run_cosim(tasks(), sched, "shared_memory", None, specs={}, horizon=20)
    h = first_h(out)
    assert h.start == pytest.approx(1)
    assert h.finish == pytest.approx(4)
    assert not h.missed