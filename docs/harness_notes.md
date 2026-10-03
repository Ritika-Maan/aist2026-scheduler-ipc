# Harness method notes (what the code does; for the team to adapt, not paper prose)

**Co-simulation.** `harness/cosim.py` is a plain event loop that drives Priya's `IPCInterface`
in the order given in `ipc/NOTES.md` (Integration A.2). It reuses core's `Task`, `Job`,
RMS priority assignment and `metrics`; it does not call `core.simulate()`. With no locks it
reproduces `core.simulate()` job-for-job (`test_matches_core_without_locks`), and with locks it
reproduces `ipc/sim_ipc.simulate_ipc` (finish times and blocking). Time unit: ms.

**Task sets.** UUniFast generates utilizations summing to U; WCET C' = u*T is the total, including
critical-section time and message overhead (D2). Periods are drawn without replacement from a
13-value grid inside [80, 1120] ms (all divisors of 4480 ms), so the hyperperiod is exactly
4480 ms and each run simulates one hyperperiod. Task set i at utilization U depends only on
(seed, U, i), so every condition at that U sees the same set (pairing key = set index). The
grid and n_tasks = 6 are harness choices pending Step 5 / team confirmation.

**Shared memory.** `generate_specs` places critical sections inside C'; the layout RNG depends
on (seed, U, set, n_resources, cs_per_job) only, so RMS+PIP and EDF+SRP see identical sections.
Blocking is never added to WCET; it is measured from `blocking_events` (time pending while a
running job has strictly worse base priority, per ipc/NOTES.md).

**Message passing.** Overhead m*L0 is carved out of C' (`message_passing_tasks`, baseline_latency
convention); only m*(L-L0) is added on top, and effective U is reported per run (overload flagged,
not compared). At baseline L = L0, so the message-passing schedule equals the plain core schedule
and is identical across latency values and across intensity levels.
Task sets whose smallest WCET is <= 2*max(m)*L0 are rejected at generation (same for all conditions).

**Statistics (D4).** Per condition: N, mean, SD, 95% t-interval. Per cell: paired differences
(RMS - EDF miss rate, paired by set index), mean, SD, 95% t-interval, winner = lower mean unless
the interval includes 0 (tie). Per-set differences are written to `*_paired_diffs.csv`.

**Adding conditions.** Append dicts to `conditions` in the JSON config (see `harness/conditions.py`
docstring): `arm`, `tag`, `protocol`, `overrides` (cs_fraction, msg_latency, ...) cover the
RMS+SRP / ICPP controls and both sweeps; list extra pairs in `comparisons`.

Run: `python -m harness.cli --config harness/configs/baseline.json --out results`
Tests: `python -m pytest harness/tests -v`
