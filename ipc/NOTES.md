# IPC layer notes

Owner: Priya (branch `ipc`). `core/` is frozen (Ritika); `harness/` is Garima's.
Run all tests from the repo root: `python -m pytest ipc/tests -v`
(Python 3.10+, because messaging.py uses `int | None`.)

## Files
- `config.py`      CriticalSection (offset/length in CPU time), spec validation, `generate_specs`
- `protocols.py`   PIP, ICPP, SRP (SRP runs under RMS and EDF), `make_protocol`
- `sim_ipc.py`     lock-aware standalone simulator (reference implementation)
- `messaging.py`   asynchronous/buffered message passing, configurable latency/capacity
- `interface.py`   A.2 adapter for the co-simulation harness (wraps the above, no logic copied)
- `example_harness_usage.py`  minimal demo loop showing the call order
- `INTENSITY_PLACEHOLDER` (interface.py): low/high intensity values; PLACEHOLDERS, not final

## Conventions
- Task id = `Task.name` (str). Job identity = `(task.name, release)`.
  Always pass the same `release` value you gave to `on_job_release`.
- Lower priority number / earlier deadline wins.
- U is defined on the generated TOTAL WCET (C'). Critical-section time is inside C'
  (`generate_specs`); message overhead is carved out of C' by `split_wcet` /
  `message_passing_tasks`. Lock BLOCKING is never added to WCET: it is measured
  (blocking_events / job.blocking).
- CONSEQUENCE: with all overhead inside a fixed C', the message-passing schedule is the same
  for every latency value (it equals plain core), so a latency sweep would change nothing.
  For the sweep use `baseline_latency=L0`: m*L0 stays inside C', and only the excess
  m*(L-L0) is added on top (utilization then rises above target: report effective U).
  `inflate_wcet` (adds m*L on top for every latency) is the alternative "on top" convention.
- Blocking time of a job = time it is pending while a running job has a strictly worse
  BASE priority (same definition in sim_ipc.py and interface.py).

## Integration (A.2)

```python
from interface import IPCInterface, inflate_wcet
api = IPCInterface(tasks, scheduler="RMS"|"EDF", ipc="shared_memory"|"message_passing",
                   protocol="PIP"|"ICPP"|"SRP"|"NONE"/None, specs=..., msg_cfg=...)
```

| A.2 call | Signature | Returns |
|---|---|---|
| can_dispatch | `(task_name, release, time)` | bool: not lock-blocked, and (SRP) allowed to start |
| on_lock_request | `(task_name, release, resource, time)` | True granted / False now blocked (`api.deadlock` set if a wait cycle forms) |
| on_lock_release | `(task_name, release, resource, time)` | `[(task_name, release)]` of jobs unblocked (they now hold the lock) |
| priority_override | `(task_name, release, time)` | effective key (PIP inheritance, ICPP ceiling) or None = base key |
| on_message_send | `(sender, release, receiver, time, size=0, payload=None)` | `MessageResult` (available_time = time + latency; `dropped=True` if buffer full; never blocks) |
| blocking_events | property | `[BlockingEvent(task_name, release, start, end, resource, cause)]`, causes: lock / srp_ceiling / ceiling / inheritance |

Supporting calls: `on_job_release`, `on_job_start`, `record_run(t0, t1)`, `on_job_finish`,
`next_sync_point`, `executed`, `remaining`, `effective_key`, `select`,
`on_message_receive`, `report_no_dispatchable`, `finalize_deadlock`,
`blocking_time`, `jobs`, `pending`, `deadlock`, `message_log`, `dropped_messages`.

### Event order the harness must follow (per scheduling step)
1. `on_job_release` for every job with release <= now (message passing: `on_message_send` for its messages).
2. candidates = jobs with `can_dispatch` True; run the one with the smallest `effective_key`.
   Jobs pending but none dispatchable -> `report_no_dispatchable(time)` (treat as deadlock).
3. `on_job_start`; fire every lock/unlock the job has reached (`next_sync_point().offset <= executed`):
   `on_lock_request` / `on_lock_release`. If any fired, return to step 2.
4. Run until the earliest of finish / next release / next sync point; call `record_run(t0, t1)`;
   fire sync points reached; `on_job_finish` if done.

`example_harness_usage.run_cosim` implements exactly this; the tests prove it reproduces
`sim_ipc.simulate_ipc` (finish times and blocking) on the scenarios and on random sets.
Switching scheduler / IPC / protocol only changes constructor arguments.

## Notes and assumptions
- `RMS` priorities are assigned in place on the Task objects (as core does).
- PIP and ICPP+EDF: ICPP is fixed-priority only and raises ValueError under EDF; use SRP for EDF.
- Message passing in the baseline is asynchronous/buffered; `size` is recorded but latency is flat.
- Synchronous (rendezvous) messaging is NOT implemented.

## Message latency semantics (CPU time vs transit delay)
Two different things can be called "latency":
- CPU cost: send/receive copy and kernel path executed on the processor. It consumes
  processor time, so it belongs INSIDE WCET and counts toward U.
- Transit delay: time before the receiver may use the data while the CPU is free. It does
  NOT change U; it would delay the receiver (end-to-end pipeline latency).

What the code does today: the configured `latency` is treated as CPU cost per message and is
charged through `split_wcet` / `message_passing_tasks` / `inflate_wcet`. `AsyncMessageChannel`
also records `available_time = send_time + latency`, but nothing in scheduling uses it
(tasks are independent periodic tasks with per-task deadlines, no precedence), so transit delay
currently has NO effect on miss rates. If the paper needs end-to-end speech-pipeline latency,
add a separate `transit_delay` field to MessagePassingConfig and model the receiver waiting on it.

Latency sweep: `baseline_latency=L0` keeps m*L0 inside C'; only m*(L-L0) is added on top.
`effective_utilization(tasks, splits)` returns (target_U, effective_U, overload); points with
effective_U > 1 are marked overload and are not compared directly.

### Constants (fill in from the papers; classify each as CPU cost or transit delay)
| Constant | Value | Unit / cycles @ clock | Source (paper, section/table) | CPU cost or transit delay? | Used as |
|---|---|---|---|---|---|
| L4 IPC | TODO | TODO | TODO | TODO | TODO |
| Quest-V inter-sandbox communication | TODO | TODO | TODO | TODO | TODO |
