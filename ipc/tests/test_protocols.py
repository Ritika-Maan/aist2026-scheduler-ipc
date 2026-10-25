"""Protocol validation scenarios. Run from the repo root:  pytest ipc/tests -v"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "core"))

import pytest                                        # noqa: E402
from task import Task                                # noqa: E402
from schedulers import simulate                      # noqa: E402
from config import CriticalSection as CS, generate_specs  # noqa: E402
from sim_ipc import simulate_ipc                     # noqa: E402

H = 100.0   # horizon; periods >= horizon so each task releases exactly one job


def job_of(jobs, name):
    return next(j for j in jobs if j.task.name == name)


# ---------------------------------------------------------------- regression
def test_matches_core_without_locks():
    def mk():
        return [Task("a", 10, 3), Task("b", 15, 4), Task("c", 40, 6)]
    for policy in ("RMS", "EDF"):
        ref = simulate(mk(), policy, 120)
        got, info = simulate_ipc(mk(), policy, "PIP", {}, 120)
        f = lambda js: sorted((j.task.name, j.release, round(j.finish, 9)) for j in js)
        assert f(ref) == f(got) and not info["deadlock"]


# ------------------------------------------- 1/2: priority inversion, then PIP
def inversion_tasks():
    return [Task("H", 100, 2, arrival=1), Task("M", 110, 10, arrival=2),
            Task("L", 120, 4, arrival=0)]


INV_SPECS = {"L": [CS("R", 0, 3)], "H": [CS("R", 0, 1)]}


def test_unbounded_inversion_without_protocol():
    jobs, _ = simulate_ipc(inversion_tasks(), "RMS", "NONE", INV_SPECS, H)
    h = job_of(jobs, "H")
    assert h.finish == pytest.approx(15)       # H waits for all of M
    assert h.blocking == pytest.approx(12)


def test_pip_bounds_inversion_to_one_critical_section():
    jobs, _ = simulate_ipc(inversion_tasks(), "RMS", "PIP", INV_SPECS, H)
    h = job_of(jobs, "H")
    assert h.finish == pytest.approx(5)
    assert h.blocking == pytest.approx(2)      # remainder of L's critical section


# ----------------------------------------------------------- 3: chained blocking
def chain_tasks():
    return [Task("H", 100, 3, arrival=2), Task("L1", 110, 3, arrival=1),
            Task("L2", 120, 3, arrival=0)]


CHAIN_SPECS = {"H": [CS("R1", 0, 1), CS("R2", 1, 1)],
               "L1": [CS("R1", 0, 3)], "L2": [CS("R2", 0, 3)]}


def test_pip_chained_blocking_exceeds_one_cs():
    jobs, _ = simulate_ipc(chain_tasks(), "RMS", "PIP", CHAIN_SPECS, H)
    assert job_of(jobs, "H").blocking == pytest.approx(4)   # 2 + 2, > any single CS remainder


@pytest.mark.parametrize("policy,proto", [("RMS", "ICPP"), ("RMS", "SRP"), ("EDF", "SRP")])
def test_ceiling_protocols_block_at_most_once(policy, proto):
    jobs, info = simulate_ipc(chain_tasks(), policy, proto, CHAIN_SPECS, H)
    h = job_of(jobs, "H")
    assert not info["deadlock"]
    assert h.blocking == pytest.approx(1)
    assert h.blocking <= 3 + 1e-9                           # longest lower-priority CS


# ----------------------------------------------------------------- 4: deadlock
def deadlock_tasks():
    return [Task("H", 100, 3, arrival=0.5), Task("L", 120, 3, arrival=0)]


DL_SPECS = {"L": [CS("R1", 0, 3), CS("R2", 1, 1)],          # R1 then nested R2
            "H": [CS("R2", 0, 2), CS("R1", 1, 1)]}          # R2 then nested R1


def test_pip_deadlocks():
    jobs, info = simulate_ipc(deadlock_tasks(), "RMS", "PIP", DL_SPECS, H)
    assert info["deadlock"]
    assert job_of(jobs, "H").missed and job_of(jobs, "L").missed


@pytest.mark.parametrize("policy,proto", [("RMS", "ICPP"), ("RMS", "SRP"), ("EDF", "SRP")])
def test_ceiling_protocols_never_deadlock(policy, proto):
    jobs, info = simulate_ipc(deadlock_tasks(), policy, proto, DL_SPECS, H)
    assert not info["deadlock"]
    assert all(j.finish < float("inf") for j in jobs)


# ------------------------------------------- 5: random sets, bounded blocking
@pytest.mark.parametrize("seed", range(20))
@pytest.mark.parametrize("policy,proto", [("RMS", "ICPP"), ("RMS", "SRP"), ("EDF", "SRP")])
def test_random_sets_single_blocking_bound(seed, policy, proto):
    rng = random.Random(seed)
    periods = rng.sample([10, 15, 20, 30, 40, 60, 80], 4)
    tasks = [Task(f"t{i}", p, p * 0.15) for i, p in enumerate(periods)]   # U ~ 0.6
    specs = generate_specs(tasks, n_resources=2, cs_per_job=1, cs_fraction=0.5, rng=rng)
    longest = max(cs.length for cl in specs.values() for cs in cl)
    jobs, info = simulate_ipc(tasks, policy, proto, specs, 400)
    assert not info["deadlock"]
    assert max(j.blocking for j in jobs) <= longest + 1e-9
