"""A.2 interface tests. Run from the repo root:  python -m pytest ipc/tests -v"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "core"))

import pytest                                                  # noqa: E402
from task import Task                                          # noqa: E402
from schedulers import simulate                                # noqa: E402
from config import CriticalSection as CS, generate_specs       # noqa: E402
from sim_ipc import simulate_ipc                               # noqa: E402
from messaging import MessagePassingConfig                     # noqa: E402
from interface import (IPCInterface, SyncPoint, inflate_wcet,  # noqa: E402
                       BlockingEvent)
from example_harness_usage import run_cosim                    # noqa: E402

H = 100.0

# scenarios shared with test_protocols.py (same numbers)
def inversion_tasks():
    return [Task("H", 100, 2, arrival=1), Task("M", 110, 10, arrival=2),
            Task("L", 120, 4, arrival=0)]


INV_SPECS = {"L": [CS("R", 0, 3)], "H": [CS("R", 0, 1)]}


def chain_tasks():
    return [Task("H", 100, 3, arrival=2), Task("L1", 110, 3, arrival=1),
            Task("L2", 120, 3, arrival=0)]


CHAIN_SPECS = {"H": [CS("R1", 0, 1), CS("R2", 1, 1)],
               "L1": [CS("R1", 0, 3)], "L2": [CS("R2", 0, 3)]}


def deadlock_tasks():
    return [Task("H", 100, 3, arrival=0.5), Task("L", 120, 3, arrival=0)]


DL_SPECS = {"L": [CS("R1", 0, 3), CS("R2", 1, 1)],
            "H": [CS("R2", 0, 2), CS("R1", 1, 1)]}


def job_of(jobs, name):
    return next(j for j in jobs if j.task.name == name)


def start_L_holding_R(proto, sched="RMS"):
    """L (released 0) is running and holds R; returns the interface."""
    api = IPCInterface(inversion_tasks(), sched, "shared_memory", proto, INV_SPECS)
    api.on_job_release("L", 0.0)
    api.on_job_start("L", 0.0, 0.0)
    assert api.next_sync_point("L", 0.0) == SyncPoint(0, "lock", "R")
    assert api.on_lock_request("L", 0.0, "R", 0.0) is True
    api.record_run("L", 0.0, 0.0, 1.0)            # L runs 0..1, inside its section
    api.on_job_release("H", 1.0)                  # H arrives at t=1
    return api


# ------------------------------------------------------------------ dispatch query
@pytest.mark.parametrize("sched", ["RMS", "EDF"])
def test_can_dispatch_srp_gates_job_start(sched):
    api = start_L_holding_R("SRP", sched)
    assert api.can_dispatch("L", 0.0, 1.0) is True       # started job keeps running
    assert api.can_dispatch("H", 1.0, 1.0) is False      # pi(H) <= system ceiling
    api.record_run("L", 0.0, 1.0, 3.0)
    assert api.next_sync_point("L", 0.0) == SyncPoint(3, "unlock", "R")
    assert api.on_lock_release("L", 0.0, "R", 3.0) == []   # SRP: nobody waits on a lock
    assert api.can_dispatch("H", 1.0, 3.0) is True       # ceiling dropped


def test_can_dispatch_false_for_lock_blocked_job_pip():
    api = start_L_holding_R("PIP")
    assert api.can_dispatch("H", 1.0, 1.0) is True       # PIP lets H start...
    api.on_job_start("H", 1.0, 1.0)
    assert api.on_lock_request("H", 1.0, "R", 1.0) is False
    assert api.can_dispatch("H", 1.0, 1.0) is False      # ...then it is blocked
    assert api.can_dispatch("L", 0.0, 1.0) is True


# ------------------------------------------------------------------ lock request / release
def test_lock_request_granted_then_blocked_and_release_unblocks():
    api = start_L_holding_R("PIP")
    api.on_job_start("H", 1.0, 1.0)
    assert api.on_lock_request("H", 1.0, "R", 1.0) is False
    assert not api.deadlock
    api.record_run("L", 0.0, 1.0, 3.0)                   # L finishes its section
    unblocked = api.on_lock_release("L", 0.0, "R", 3.0)
    assert unblocked == [("H", 1.0)]                     # identity = (task.name, release)
    assert api.can_dispatch("H", 1.0, 3.0) is True
    assert api.next_sync_point("H", 1.0) == SyncPoint(1, "unlock", "R")   # lock was handed over


def test_lock_calls_validate_the_next_sync_point():
    api = start_L_holding_R("PIP")
    with pytest.raises(ValueError):
        api.on_lock_release("L", 0.0, "R", 1.0)          # section not finished yet
    with pytest.raises(ValueError):
        api.on_lock_request("H", 1.0, "WRONG", 1.0)      # wrong resource


# ------------------------------------------------------------------ priority override
def test_priority_override_pip_inheritance():
    api = start_L_holding_R("PIP")
    api.on_job_start("H", 1.0, 1.0)
    h_prio = api.tasks[[t.name for t in api.tasks].index("H")].priority
    assert api.priority_override("L", 0.0, 1.0) is None          # nothing waiting yet
    api.on_lock_request("H", 1.0, "R", 1.0)
    assert api.priority_override("L", 0.0, 1.0) == (h_prio, 1.0)   # L inherits H's key
    assert api.priority_override("H", 1.0, 1.0) is None
    api.record_run("L", 0.0, 1.0, 3.0)
    api.on_lock_release("L", 0.0, "R", 3.0)
    assert api.priority_override("L", 0.0, 3.0) is None          # inheritance dropped


def test_priority_override_icpp_ceiling():
    api = IPCInterface(inversion_tasks(), "RMS", "shared_memory", "ICPP", INV_SPECS)
    api.on_job_release("L", 0.0)
    assert api.priority_override("L", 0.0, 0.0) is None
    api.on_job_start("L", 0.0, 0.0)
    api.on_lock_request("L", 0.0, "R", 0.0)
    h_prio = next(t.priority for t in api.tasks if t.name == "H")
    assert api.priority_override("L", 0.0, 0.0) == (h_prio, 0.0)   # runs at ceiling(R)


# ------------------------------------------------------------------ blocking_events
def test_blocking_events_exposed_with_fields():
    api = start_L_holding_R("PIP")
    api.on_job_start("H", 1.0, 1.0)
    api.on_lock_request("H", 1.0, "R", 1.0)
    api.record_run("L", 0.0, 1.0, 2.0)
    api.record_run("L", 0.0, 2.0, 3.0)                   # contiguous -> merged
    ev = api.blocking_events
    assert len(ev) == 1 and isinstance(ev[0], BlockingEvent)
    assert (ev[0].task_name, ev[0].release) == ("H", 1.0) and ev[0].job == ("H", 1.0)
    assert (ev[0].start, ev[0].end) == (1.0, 3.0) and ev[0].duration == pytest.approx(2.0)
    assert (ev[0].resource, ev[0].cause) == ("R", "lock")
    assert api.blocking_time("H", 1.0) == pytest.approx(2.0)


def test_blocking_events_causes_per_protocol():
    for proto, cause in [("SRP", "srp_ceiling"), ("ICPP", "ceiling")]:
        api = IPCInterface(inversion_tasks(), "RMS", "shared_memory", proto, INV_SPECS)
        api.on_job_release("L", 0.0)
        api.on_job_start("L", 0.0, 0.0)
        api.on_lock_request("L", 0.0, "R", 0.0)
        api.on_job_release("H", 1.0)
        api.record_run("L", 0.0, 1.0, 3.0)
        (e,) = api.blocking_events
        assert (e.task_name, e.cause, e.resource) == ("H", cause, "R")


@pytest.mark.parametrize("proto,n_events,total", [("PIP", 2, 4), ("ICPP", 1, 1), ("SRP", 1, 1)])
def test_blocking_events_match_totals_on_chain(proto, n_events, total):
    out = run_cosim(chain_tasks(), "RMS", "shared_memory", proto, CHAIN_SPECS, H)
    h_ev = [e for e in out["api"].blocking_events if e.task_name == "H"]
    assert len(h_ev) == n_events                          # PIP: two separate blocking intervals
    assert sum(e.duration for e in h_ev) == pytest.approx(total)
    for j in out["jobs"]:                                 # events add up to every job's total
        s = sum(e.duration for e in out["api"].blocking_events if e.job == (j.task.name, j.release))
        assert s == pytest.approx(j.blocking)


# ------------------------------------------------------------------ integration + equivalence
def key_map(jobs):
    return {(j.task.name, j.release): (j.finish, j.blocking) for j in jobs}


def assert_equivalent(tasks_fn, policy, proto, specs, horizon):
    ref_jobs, ref_info = simulate_ipc(tasks_fn(), policy, proto, specs, horizon)
    out = run_cosim(tasks_fn(), policy, "shared_memory", proto, specs, horizon, check_select=True)
    assert out["deadlock"] == ref_info["deadlock"]
    ref, got = key_map(ref_jobs), key_map(out["jobs"])
    assert set(got) <= set(ref)
    if not ref_info["deadlock"]:
        assert set(got) == set(ref)
    for k, (fin, blk) in got.items():
        assert fin == pytest.approx(ref[k][0]) and blk == pytest.approx(ref[k][1]), k


SHARED_COMBOS = [("RMS", "NONE"), ("RMS", "PIP"), ("RMS", "ICPP"), ("RMS", "SRP"),
                 ("EDF", "NONE"), ("EDF", "SRP")]


@pytest.mark.parametrize("policy,proto", SHARED_COMBOS)
@pytest.mark.parametrize("name,tasks_fn,specs", [
    ("inversion", inversion_tasks, INV_SPECS),
    ("chain", chain_tasks, CHAIN_SPECS),
    ("deadlock", deadlock_tasks, DL_SPECS)])
def test_interface_matches_sim_ipc_on_scenarios(name, tasks_fn, specs, policy, proto):
    assert_equivalent(tasks_fn, policy, proto, specs, H)


def test_rms_pip_integration_numbers():
    out = run_cosim(inversion_tasks(), "RMS", "shared_memory", "PIP", INV_SPECS, H)
    h = job_of(out["jobs"], "H")
    assert h.finish == pytest.approx(5) and h.blocking == pytest.approx(2)


def test_edf_srp_integration_numbers():
    out = run_cosim(inversion_tasks(), "EDF", "shared_memory", "SRP", INV_SPECS, H)
    h = job_of(out["jobs"], "H")
    assert h.finish == pytest.approx(5) and h.blocking == pytest.approx(2)
    assert not out["deadlock"]


def test_pip_deadlock_is_reported():
    out = run_cosim(deadlock_tasks(), "RMS", "shared_memory", "PIP", DL_SPECS, H)
    assert out["deadlock"] and out["api"].deadlock_time is not None
    assert all(j.finish == math.inf for j in out["jobs"])


@pytest.mark.parametrize("seed", range(15))
@pytest.mark.parametrize("policy,proto", [("RMS", "PIP"), ("RMS", "ICPP"),
                                          ("RMS", "SRP"), ("EDF", "SRP")])
def test_interface_matches_sim_ipc_on_random_sets(seed, policy, proto):
    def mk():
        r = random.Random(seed)
        periods = r.sample([10, 15, 20, 30, 40, 60, 80], 4)
        return [Task(f"t{i}", p, p * 0.15) for i, p in enumerate(periods)]

    specs = generate_specs(mk(), n_resources=2, cs_per_job=2, cs_fraction=0.4,
                           rng=random.Random(seed + 1000))
    assert_equivalent(mk, policy, proto, specs, 200)


# ------------------------------------------------------------------ message passing
@pytest.mark.parametrize("sched", ["RMS", "EDF"])
def test_message_send_uses_configurable_latency(sched):
    avail = {}
    for lat in (0.5, 2.0):
        api = IPCInterface(inversion_tasks(), sched, "message_passing",
                           msg_cfg=MessagePassingConfig(latency=lat))
        api.on_job_release("H", 1.0)
        r = api.on_message_send("H", 1.0, "M", 10.0, size=64)
        assert not r.dropped and r.latency == pytest.approx(lat)
        assert (r.sender, r.receiver, r.release) == ("H", "M", 1.0)
        avail[lat] = r.available_time
        assert api.on_message_receive("M", 10.0 + lat - 0.1) is None     # not there yet
        assert api.on_message_receive("M", 10.0 + lat).latency == pytest.approx(lat)
        assert api.message_overhead == pytest.approx(lat)
    assert avail == {0.5: pytest.approx(10.5), 2.0: pytest.approx(12.0)}


def test_message_send_never_blocks_and_reports_full_buffer():
    api = IPCInterface(inversion_tasks(), "RMS", "message_passing",
                       msg_cfg=MessagePassingConfig(latency=1.0, capacity=1))
    api.on_job_release("H", 1.0)
    first = api.on_message_send("H", 1.0, "M", 1.0)
    second = api.on_message_send("H", 1.0, "M", 1.1)       # buffer full: no exception
    assert not first.dropped and second.dropped and second.available_time is None
    assert api.dropped_messages == 1 and len(api.message_log) == 2
    assert api.blocking_events == []                       # sending never blocks the sender
    assert api.can_dispatch("H", 1.0, 1.1) is True


def test_inflate_wcet_reads_latency_from_config():
    tasks = inversion_tasks()
    for lat in (0.0, 0.25, 1.0):
        out = inflate_wcet(tasks, 2, MessagePassingConfig(latency=lat))
        assert [t.wcet for t in out] == pytest.approx([t.wcet + 2 * lat for t in tasks])
    assert [t.wcet for t in tasks] == [2, 10, 4]           # originals untouched
    per_task = inflate_wcet(tasks, {"H": 3}, MessagePassingConfig(latency=0.5))
    assert [t.wcet for t in per_task] == pytest.approx([3.5, 10, 4])


@pytest.mark.parametrize("sched", ["RMS", "EDF"])
def test_message_passing_integration_matches_core(sched):
    def mk():
        return [Task("a", 10, 2), Task("b", 15, 3), Task("c", 40, 5)]
    cfg = MessagePassingConfig(latency=0.25)
    out = run_cosim(mk(), sched, "message_passing", None, horizon=120,
                    msg_cfg=cfg, msgs_per_job=2, check_select=True)
    ref = simulate(inflate_wcet(mk(), 2, cfg), sched, 120)          # core, inflated WCET
    f = lambda js: sorted((j.task.name, j.release, round(j.finish, 9)) for j in js)
    assert f(out["jobs"]) == f(ref)
    assert out["api"].blocking_events == [] and not out["deadlock"]    # async: no blocking
    assert len(out["api"].message_log) == 2 * len(out["jobs"])
    assert out["api"].dropped_messages == 0


@pytest.mark.parametrize("sched", ["RMS", "EDF"])
def test_message_latency_changes_schedule(sched):
    def mk():
        return [Task("a", 10, 4), Task("b", 15, 6), Task("c", 40, 8)]
    lo = run_cosim(mk(), sched, "message_passing", None, horizon=120,
                   msg_cfg=MessagePassingConfig(latency=0.0), msgs_per_job=2)
    hi = run_cosim(mk(), sched, "message_passing", None, horizon=120,
                   msg_cfg=MessagePassingConfig(latency=0.8), msgs_per_job=2)
    assert max(j.finish - j.release for j in hi["jobs"]) > max(j.finish - j.release for j in lo["jobs"])


# ------------------------------------------------------------------ construction / identity
@pytest.mark.parametrize("kwargs", [
    dict(scheduler="EDF", ipc="shared_memory", protocol="ICPP", specs=INV_SPECS),   # ICPP is fixed-priority
    dict(scheduler="FIFO", ipc="shared_memory"),
    dict(scheduler="RMS", ipc="pipes"),
    dict(scheduler="RMS", ipc="shared_memory", protocol="BOGUS"),
    dict(scheduler="RMS", ipc="message_passing", protocol="PIP"),
    dict(scheduler="RMS", ipc="message_passing", specs=INV_SPECS),
    dict(scheduler="RMS", ipc="shared_memory", msg_cfg=MessagePassingConfig()),
])
def test_invalid_combinations_rejected(kwargs):
    with pytest.raises(ValueError):
        IPCInterface(inversion_tasks(), **kwargs)


def test_job_identity_is_task_name_and_release():
    api = IPCInterface(inversion_tasks(), "RMS", "shared_memory", "PIP", INV_SPECS)
    assert api.on_job_release("L", 0.0) == ("L", 0.0)
    assert api.pending() == [("L", 0.0)] and isinstance(api.pending()[0][0], str)
    with pytest.raises(ValueError):
        api.on_job_release("L", 0.0)                       # duplicate job
    with pytest.raises(KeyError):
        api.can_dispatch("L", 5.0)                         # unknown job
    api.on_job_release("L", 120.0)                         # same task, another release: distinct job
    assert sorted(api.pending()) == [("L", 0.0), ("L", 120.0)]


def test_harness_can_swap_scheduler_ipc_protocol_without_code_changes():
    combos = [("RMS", "shared_memory", "PIP"), ("EDF", "shared_memory", "SRP"),
              ("RMS", "shared_memory", "SRP"), ("RMS", "shared_memory", "ICPP"),
              ("RMS", "shared_memory", None), ("RMS", "message_passing", None),
              ("EDF", "message_passing", None)]
    for sched, ipc, proto in combos:
        kw = dict(specs=INV_SPECS) if ipc == "shared_memory" else \
             dict(msg_cfg=MessagePassingConfig(latency=0.1), msgs_per_job=1)
        out = run_cosim(inversion_tasks(), sched, ipc, proto, horizon=H, **kw)
        assert not out["deadlock"] and all(j.finish < math.inf for j in out["jobs"])
