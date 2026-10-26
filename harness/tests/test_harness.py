import copy
import glob
import hashlib
import json
import os
import random

import numpy as np
import pytest

import harness
from harness.aggregate import paired_differences, summarize
from harness.conditions import load_config, make_condition, required_min_wcet
from harness.cosim import cosim
from harness.plotting import blocking_distributions, regime_map
from harness.report import headline, verdict_text, write_summary
from harness.runner import run_matrix
from harness.stats import t_crit, t_interval
from harness.taskgen import generate_task_sets, hyperperiod

from config import generate_specs                   # ipc
from schedulers import metrics, simulate            # core
from sim_ipc import simulate_ipc                    # ipc reference simulator
from task import Task                               # core
from uunifast import make_taskset                   # core

CONFIG = os.path.join(harness.ROOT, "harness", "configs", "baseline.json")


def _bank(settings, conditions, n_sets):
    us = sorted({c.utilization for c in conditions})
    return generate_task_sets(us, n_sets, settings.n_tasks, settings.period_grid,
                              settings.base_seed, min_wcet=required_min_wcet(settings, conditions))


def _finish_map(jobs):
    return {(j.task.name, j.release): j.finish for j in jobs}


# ---------------------------------------------------------------- (i) integration anchor
@pytest.mark.parametrize("scheduler", ["RMS", "EDF"])
@pytest.mark.parametrize("ipc", ["shared_memory", "message_passing"])
def test_matches_core_without_locks(scheduler, ipc):
    """With no locks (and message overhead entirely inside C'), the co-simulation loop
    reproduces core.simulate() exactly: same finish time for every job."""
    rng = np.random.default_rng(7)
    for _ in range(40):
        n = int(rng.integers(2, 7))
        u = float(rng.uniform(0.3, 1.1))
        tasks = make_taskset(n, u, rng)
        horizon = 200.0
        ref = simulate(copy.deepcopy(tasks), scheduler, horizon)
        kw = dict(msgs_per_job=2, baseline_latency=0.0) if ipc == "message_passing" else {}
        out = cosim(tasks, scheduler, ipc, None, specs={} if ipc == "shared_memory" else None,
                    horizon=horizon, **kw)
        assert not out.deadlock
        a, b = _finish_map(ref), _finish_map(out.jobs)
        assert a.keys() == b.keys()
        for k in a:
            assert a[k] == pytest.approx(b[k], abs=1e-9), k
        assert metrics(out.jobs) == pytest.approx(metrics(ref), abs=1e-9)


def test_matches_core_without_locks_on_harness_task_sets():
    settings, conditions = load_config(CONFIG)
    bank = _bank(settings, conditions, 5)
    for u in (0.5, 0.9):
        for tasks in bank[u]:
            for sched in ("RMS", "EDF"):
                ref = simulate(copy.deepcopy(tasks), sched, hyperperiod(tasks))
                out = cosim(tasks, sched, "shared_memory", None, specs={})
                a, b = _finish_map(ref), _finish_map(out.jobs)
                assert all(a[k] == pytest.approx(b[k], abs=1e-9) for k in a) and a.keys() == b.keys()


@pytest.mark.parametrize("scheduler,protocol", [("RMS", "PIP"), ("EDF", "SRP"), ("RMS", "SRP"),
                                                ("RMS", "ICPP"), ("RMS", "NONE")])
def test_cosim_matches_priya_reference_with_locks(scheduler, protocol):
    """My loop vs ipc/sim_ipc.simulate_ipc on random sets with critical sections:
    identical finish times and per-job blocking."""
    rng = np.random.default_rng(11)
    for s in range(25):
        tasks = make_taskset(int(rng.integers(3, 6)), float(rng.uniform(0.4, 0.9)), rng)
        specs = generate_specs(tasks, 2, 3, 0.3, random.Random(s))
        ref, info = simulate_ipc(copy.deepcopy(tasks), scheduler, protocol, specs, 200.0)
        out = cosim(tasks, scheduler, "shared_memory", protocol, specs=specs, horizon=200.0, check_select=True)
        assert out.deadlock == info["deadlock"]
        if info["deadlock"]:
            continue
        a, b = _finish_map(ref), _finish_map(out.jobs)
        assert a.keys() == b.keys()
        for k in a:
            assert a[k] == pytest.approx(b[k], abs=1e-9)
        ra = {(j.task.name, j.release): j.blocking for j in ref}
        rb = {(j.task.name, j.release): j.blocking for j in out.jobs}
        assert all(ra[k] == pytest.approx(rb[k], abs=1e-9) for k in ra)


def test_blocking_events_sum_matches_job_blocking():
    rng = np.random.default_rng(3)
    tasks = make_taskset(5, 0.8, rng)
    specs = generate_specs(tasks, 2, 4, 0.3, random.Random(1))
    out = cosim(tasks, "RMS", "shared_memory", "PIP", specs=specs, horizon=200.0)
    from harness.runner import _job_blocking
    per = _job_blocking(out.api)
    for j in out.jobs:
        assert per.get((j.task.name, j.release), (0.0,))[0] == pytest.approx(j.blocking, abs=1e-6)


# ---------------------------------------------------------------- task sets / stats
def test_task_sets_shared_stable_and_on_grid():
    settings, conditions = load_config(CONFIG)
    a = _bank(settings, conditions, 6)
    b = _bank(settings, conditions, 3)                       # fewer sets -> same first 3
    for u in a:
        for i in range(3):
            assert [(t.name, t.period, t.wcet) for t in a[u][i]] == [(t.name, t.period, t.wcet) for t in b[u][i]]
        for ts in a[u]:
            assert sum(t.wcet / t.period for t in ts) == pytest.approx(u)
            assert len({t.period for t in ts}) == len(ts)
            assert all(t.period in settings.period_grid for t in ts)
            assert hyperperiod(ts) <= 4480.0


def test_t_crit_known_values():
    assert t_crit(49) == pytest.approx(2.00957, abs=1e-4)
    assert t_crit(1) == pytest.approx(12.7062, abs=1e-3)
    assert t_crit(10) == pytest.approx(2.2281, abs=1e-4)
    n, mean, sd, lo, hi = t_interval([0.0, 0.0, 0.0])
    assert (mean, sd, lo, hi) == (0.0, 0.0, 0.0, 0.0)


# ---------------------------------------------------------------- (ii)-(iv) full matrix
@pytest.fixture(scope="module")
def small_run(tmp_path_factory):
    settings, conditions = load_config(CONFIG)
    n_sets = 4
    bank = _bank(settings, conditions, n_sets)
    result = run_matrix(conditions, bank, settings)
    return settings, conditions, result, n_sets, tmp_path_factory.mktemp("out")


def test_all_40_conditions_run(small_run):
    settings, conditions, result, n_sets, _ = small_run
    assert len(conditions) == 40
    assert result.raw["condition"].nunique() == 40
    assert (result.raw.groupby("condition").size() == n_sets).all()
    assert not result.raw["deadlock"].any()
    assert not result.raw["overload"].any()
    assert set(result.blocking["condition"]) == {c.id for c in conditions if c.ipc == "shared_memory"}


def test_n_sd_ci_always_present(small_run):
    _, _, result, n_sets, _ = small_run
    summary = summarize(result)
    for metric in ("miss_rate", "max_lateness"):
        for col in ("n", "mean", "sd", "ci_lo", "ci_hi"):
            c = f"{metric}_{col}"
            assert c in summary and summary[c].notna().all(), c
        assert (summary[f"{metric}_n"] == n_sets).all()
        assert (summary[f"{metric}_ci_lo"] <= summary[f"{metric}_mean"] + 1e-12).all()
    paired, diffs = paired_differences(result)
    for c in ("n", "mean_diff", "sd_diff", "ci_lo", "ci_hi", "winner"):
        assert paired[c].notna().all(), c
    assert (paired["n"] == n_sets).all() and len(diffs) == len(paired) * n_sets
    assert len(paired) == 20                                  # 2 IPC x 5 U x 2 intensity


def test_message_passing_baseline_equals_plain_core(small_run):
    """Consequence of the locked convention: all overhead inside C' -> baseline message
    passing is identical across intensities and equals the plain RMS/EDF schedule."""
    _, _, result, _, _ = small_run
    r = result.raw[result.raw.ipc == "message_passing"]
    wide = r.pivot_table(index=["arm", "utilization", "set_index"], columns="intensity", values="miss_rate")
    assert np.allclose(wide["low"], wide["high"])
    assert (r["effective_u"] == r["target_u"]).all()


def test_regime_map_and_blocking_plot_render(small_run):
    settings, _, result, _, out = small_run
    summary = summarize(result)
    paired, _ = paired_differences(result)
    p1, p2, p3 = out / "regime_map.png", out / "blocking.png", out / "summary.md"
    regime_map(paired, str(p1))
    blocking_distributions(result.blocking, summary, str(p2))
    write_summary(str(p3), summary, paired, settings)
    assert p1.stat().st_size > 5000 and p2.stat().st_size > 5000 and p3.stat().st_size > 500
    assert verdict_text(paired) and headline(paired)


# ---------------------------------------------------------------- (v) extensibility
def test_extra_condition_needs_no_py_changes(tmp_path):
    def digest():
        h = hashlib.sha256()
        for f in sorted(glob.glob(os.path.join(harness.ROOT, "harness", "*.py"))):
            h.update(open(f, "rb").read())
        return h.hexdigest()

    before = digest()
    cfg = json.load(open(CONFIG))
    cfg["conditions"] = [c for c in cfg["conditions"] if c["utilization"] == 0.8]
    base = [c for c in cfg["conditions"] if c["ipc"] == "shared_memory" and c["intensity"] == "high"]
    extras = [
        # post-baseline entries, as plain dicts:
        dict(scheduler="RMS", ipc="shared_memory", protocol="SRP", utilization=0.8, intensity="high",
             arm="RMS+SRP"),
        dict(scheduler="RMS", ipc="shared_memory", protocol="ICPP", utilization=0.8, intensity="high",
             arm="RMS+ICPP"),
        dict(scheduler="RMS", ipc="shared_memory", protocol="PIP", utilization=0.8, intensity="high",
             tag="csf=0.2", overrides={"cs_fraction": 0.2}),
        dict(scheduler="EDF", ipc="shared_memory", protocol="SRP", utilization=0.8, intensity="high",
             tag="csf=0.2", overrides={"cs_fraction": 0.2}),
        dict(scheduler="RMS", ipc="message_passing", protocol=None, utilization=0.8, intensity="high",
             tag="lat=0.5", overrides={"msg_latency": 0.5}),
        dict(scheduler="EDF", ipc="message_passing", protocol=None, utilization=0.8, intensity="high",
             tag="lat=0.5", overrides={"msg_latency": 0.5}),
    ]
    cfg["conditions"] += extras
    cfg["comparisons"] = [["RMS", "EDF"], ["RMS+SRP", "EDF"], ["RMS+ICPP", "EDF"]]
    path = tmp_path / "extended.json"
    path.write_text(json.dumps(cfg))
    settings, conditions = load_config(str(path))
    assert len(conditions) == 8 + len(extras)          # 8 baseline conditions at U=0.8 + extras
    result = run_matrix(conditions, _bank(settings, conditions, 3), settings)
    paired, _ = paired_differences(result)
    got = {(r.arm_a, r.arm_b, r.tag, r.ipc) for _, r in paired.iterrows()}
    assert ("RMS+SRP", "EDF", "", "shared_memory") in got
    assert ("RMS+ICPP", "EDF", "", "shared_memory") in got
    assert ("RMS", "EDF", "csf=0.2", "shared_memory") in got
    assert ("RMS", "EDF", "lat=0.5", "message_passing") in got
    sweep = result.raw[result.raw.tag == "lat=0.5"]
    assert (sweep.effective_u > sweep.target_u).all()         # on-top overhead raises effective U
    assert digest() == before                                  # no .py file touched


def test_latency_sweep_marks_overload():
    settings, _ = load_config(CONFIG)
    c = make_condition(dict(scheduler="EDF", ipc="message_passing", protocol=None, utilization=0.9,
                            intensity="high", tag="lat=big", overrides={"msg_latency": 3.0}))
    tasks = [[Task("T0", 100.0, 45.0), Task("T1", 200.0, 90.0)]]          # U = 0.9
    result = run_matrix([c], {0.9: tasks}, settings)
    assert result.raw["overload"].all() and result.raw["effective_u"].iloc[0] > 1
