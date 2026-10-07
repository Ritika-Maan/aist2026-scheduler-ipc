# Extended results (post-baseline controls and sweeps)

N = 50 task sets per condition (same UUniFast seeds per (U, index) as the baseline); paired differences pair on task-set index. Miss rates are mean % [95% t-interval] (SD). Tie = 95% paired t-interval of RMS-EDF includes 0.

## Regression check

PASS: all 40 baseline conditions reproduce results/baseline.csv exactly (miss_rate_mean, miss_rate_sd, max_lateness_mean, blocking_frac_jobs, blocking_max).

## How to read message passing

Baseline message-passing overhead sits inside WCET (D2), so message passing = plain RMS/EDF scheduling, identical across intensity. It is the control that shared-memory results are compared against. Latency affects it only in the sweep, where the excess m*(L-L0) is added on top and effective U is reported.

## Verdict (all utilizations in this run, RMS+PIP vs EDF+SRP; plain RMS vs EDF)

No flip found: scheduler ranking is robust to IPC choice under these conditions.

## Headline

under shared memory, RMS's miss rate exceeds EDF's by 2.71 percentage points (2.71% vs 0.00%, N=50, 95% paired CI [+1.99, +3.43] pp on RMS-EDF) at 0.98 utilization (high intensity), a gap that does appear under message passing.

## Controls: any flip?

No flip in any control: for RMS+PIP, RMS+SRP and RMS+ICPP against EDF+SRP, the shared-memory winner never reverses the plain-scheduling winner at any U, intensity.

| shared arm vs EDF+SRP | U | intensity | shared winner | plain winner | shared diff (pp) | plain diff (pp) | flip |
|---|---|---|---|---|---|---|---|
| RMS+PIP | 0.9 | high | EDF | EDF | +0.27 | +0.27 | no |
| RMS+PIP | 0.9 | low | EDF | EDF | +0.27 | +0.27 | no |
| RMS+PIP | 0.95 | high | EDF | EDF | +0.57 | +0.57 | no |
| RMS+PIP | 0.95 | low | EDF | EDF | +0.57 | +0.57 | no |
| RMS+PIP | 0.98 | high | EDF | EDF | +2.71 | +2.70 | no |
| RMS+PIP | 0.98 | low | EDF | EDF | +2.70 | +2.70 | no |
| RMS+ICPP | 0.9 | high | EDF | EDF | +0.27 | +0.27 | no |
| RMS+ICPP | 0.9 | low | EDF | EDF | +0.27 | +0.27 | no |
| RMS+ICPP | 0.95 | high | EDF | EDF | +0.57 | +0.57 | no |
| RMS+ICPP | 0.95 | low | EDF | EDF | +0.57 | +0.57 | no |
| RMS+ICPP | 0.98 | high | EDF | EDF | +2.71 | +2.70 | no |
| RMS+ICPP | 0.98 | low | EDF | EDF | +2.70 | +2.70 | no |
| RMS+SRP | 0.9 | high | EDF | EDF | +0.27 | +0.27 | no |
| RMS+SRP | 0.9 | low | EDF | EDF | +0.27 | +0.27 | no |
| RMS+SRP | 0.95 | high | EDF | EDF | +0.57 | +0.57 | no |
| RMS+SRP | 0.95 | low | EDF | EDF | +0.57 | +0.57 | no |
| RMS+SRP | 0.98 | high | EDF | EDF | +2.71 | +2.70 | no |
| RMS+SRP | 0.98 | low | EDF | EDF | +2.70 | +2.70 | no |

(Rows shown for U >= 0.9; all cells are in `extended_control_flips.csv`.)

## Control summary at U = 0.9

Message passing has no locking protocol, so its rows are plain RMS / plain EDF.

| IPC | intensity | config | N | miss rate % [95% CI] (SD) | diff vs EDF (pp) [95% CI] | winner vs EDF |
|---|---|---|---|---|---|---|
| shared_memory | low | RMS+PIP | 50 | 0.27 [0.01, 0.53] (0.92) | +0.27 [+0.01, +0.53] | EDF |
| shared_memory | low | RMS+SRP | 50 | 0.27 [0.01, 0.53] (0.92) | +0.27 [+0.01, +0.53] | EDF |
| shared_memory | low | RMS+ICPP | 50 | 0.27 [0.01, 0.53] (0.92) | +0.27 [+0.01, +0.53] | EDF |
| shared_memory | low | EDF+SRP | 50 | 0.00 [0.00, 0.00] (0.00) | - | - |
| message_passing | low | RMS (plain) | 50 | 0.27 [0.01, 0.53] (0.92) | +0.27 [+0.01, +0.53] | EDF |
| message_passing | low | EDF (plain) | 50 | 0.00 [0.00, 0.00] (0.00) | - | - |
| shared_memory | high | RMS+PIP | 50 | 0.27 [0.01, 0.53] (0.92) | +0.27 [+0.01, +0.53] | EDF |
| shared_memory | high | RMS+SRP | 50 | 0.27 [0.01, 0.53] (0.92) | +0.27 [+0.01, +0.53] | EDF |
| shared_memory | high | RMS+ICPP | 50 | 0.27 [0.01, 0.53] (0.92) | +0.27 [+0.01, +0.53] | EDF |
| shared_memory | high | EDF+SRP | 50 | 0.00 [0.00, 0.00] (0.00) | - | - |
| message_passing | high | RMS (plain) | 50 | 0.27 [0.01, 0.53] (0.92) | +0.27 [+0.01, +0.53] | EDF |
| message_passing | high | EDF (plain) | 50 | 0.00 [0.00, 0.00] (0.00) | - | - |

Protocol effect within RMS at U = 0.9 (PIP minus the control, pp):

| intensity | PIP vs | N | PIP mean % | control mean % | mean diff (pp) | SD | 95% CI (pp) | sets differing | winner |
|---|---|---|---|---|---|---|---|---|---|
| high | RMS+SRP | 50 | 0.27 | 0.27 | +0.00 | 0.00 | [+0.00, +0.00] | 0/50 | tie |
| high | RMS+ICPP | 50 | 0.27 | 0.27 | +0.00 | 0.00 | [+0.00, +0.00] | 0/50 | tie |
| low | RMS+SRP | 50 | 0.27 | 0.27 | +0.00 | 0.00 | [+0.00, +0.00] | 0/50 | tie |
| low | RMS+ICPP | 50 | 0.27 | 0.27 | +0.00 | 0.00 | [+0.00, +0.00] | 0/50 | tie |

## Extended utilization: RMS vs EDF cells at U >= 0.9

| IPC | U | intensity | N | RMS mean % | EDF mean % | mean diff (pp) | SD diff | 95% CI diff (pp) | sets differing | winner |
|---|---|---|---|---|---|---|---|---|---|---|
| message_passing | 0.9 | high | 50 | 0.27 | 0.00 | 0.27 | 0.92 | [0.01, 0.53] | 7/50 | EDF |
| message_passing | 0.9 | low | 50 | 0.27 | 0.00 | 0.27 | 0.92 | [0.01, 0.53] | 7/50 | EDF |
| message_passing | 0.95 | high | 50 | 0.57 | 0.00 | 0.57 | 0.93 | [0.30, 0.83] | 21/50 | EDF |
| message_passing | 0.95 | low | 50 | 0.57 | 0.00 | 0.57 | 0.93 | [0.30, 0.83] | 21/50 | EDF |
| message_passing | 0.98 | high | 50 | 2.70 | 0.00 | 2.70 | 2.55 | [1.97, 3.42] | 42/50 | EDF |
| message_passing | 0.98 | low | 50 | 2.70 | 0.00 | 2.70 | 2.55 | [1.97, 3.42] | 42/50 | EDF |
| shared_memory | 0.9 | high | 50 | 0.27 | 0.00 | 0.27 | 0.92 | [0.01, 0.53] | 7/50 | EDF |
| shared_memory | 0.9 | low | 50 | 0.27 | 0.00 | 0.27 | 0.92 | [0.01, 0.53] | 7/50 | EDF |
| shared_memory | 0.95 | high | 50 | 0.57 | 0.00 | 0.57 | 0.93 | [0.30, 0.83] | 21/50 | EDF |
| shared_memory | 0.95 | low | 50 | 0.57 | 0.00 | 0.57 | 0.93 | [0.30, 0.83] | 21/50 | EDF |
| shared_memory | 0.98 | high | 50 | 2.71 | 0.00 | 2.71 | 2.55 | [1.99, 3.43] | 42/50 | EDF |
| shared_memory | 0.98 | low | 50 | 2.70 | 0.00 | 2.70 | 2.55 | [1.97, 3.42] | 42/50 | EDF |

## IPC effect on a scheduler's own miss rate (shared memory minus plain, same task sets), U >= 0.9

| config | U | intensity | N | shared mean % | plain mean % | mean diff (pp) | SD | 95% CI (pp) | sets differing |
|---|---|---|---|---|---|---|---|---|---|
| RMS+PIP | 0.9 | low | 50 | 0.27 | 0.27 | +0.00 | 0.00 | [+0.00, +0.00] | 0/50 |
| RMS+PIP | 0.9 | high | 50 | 0.27 | 0.27 | +0.00 | 0.00 | [+0.00, +0.00] | 0/50 |
| EDF+SRP | 0.9 | low | 50 | 0.00 | 0.00 | +0.00 | 0.00 | [+0.00, +0.00] | 0/50 |
| EDF+SRP | 0.9 | high | 50 | 0.00 | 0.00 | +0.00 | 0.00 | [+0.00, +0.00] | 0/50 |
| RMS+PIP | 0.95 | low | 50 | 0.57 | 0.57 | +0.00 | 0.00 | [+0.00, +0.00] | 0/50 |
| RMS+PIP | 0.95 | high | 50 | 0.57 | 0.57 | +0.00 | 0.00 | [+0.00, +0.00] | 0/50 |
| EDF+SRP | 0.95 | low | 50 | 0.00 | 0.00 | +0.00 | 0.00 | [+0.00, +0.00] | 0/50 |
| EDF+SRP | 0.95 | high | 50 | 0.00 | 0.00 | +0.00 | 0.00 | [+0.00, +0.00] | 0/50 |
| RMS+PIP | 0.98 | low | 50 | 2.70 | 2.70 | +0.00 | 0.00 | [+0.00, +0.00] | 0/50 |
| RMS+PIP | 0.98 | high | 50 | 2.71 | 2.70 | +0.01 | 0.09 | [-0.01, +0.04] | 1/50 |
| EDF+SRP | 0.98 | low | 50 | 0.00 | 0.00 | +0.00 | 0.00 | [+0.00, +0.00] | 0/50 |
| EDF+SRP | 0.98 | high | 50 | 0.00 | 0.00 | +0.00 | 0.00 | [+0.00, +0.00] | 0/50 |
| RMS+SRP | 0.9 | low | 50 | 0.27 | 0.27 | +0.00 | 0.00 | [+0.00, +0.00] | 0/50 |
| RMS+SRP | 0.9 | high | 50 | 0.27 | 0.27 | +0.00 | 0.00 | [+0.00, +0.00] | 0/50 |
| RMS+SRP | 0.95 | low | 50 | 0.57 | 0.57 | +0.00 | 0.00 | [+0.00, +0.00] | 0/50 |
| RMS+SRP | 0.95 | high | 50 | 0.57 | 0.57 | +0.00 | 0.00 | [+0.00, +0.00] | 0/50 |
| RMS+SRP | 0.98 | low | 50 | 2.70 | 2.70 | +0.00 | 0.00 | [+0.00, +0.00] | 0/50 |
| RMS+SRP | 0.98 | high | 50 | 2.71 | 2.70 | +0.01 | 0.09 | [-0.01, +0.04] | 1/50 |
| RMS+ICPP | 0.9 | low | 50 | 0.27 | 0.27 | +0.00 | 0.00 | [+0.00, +0.00] | 0/50 |
| RMS+ICPP | 0.9 | high | 50 | 0.27 | 0.27 | +0.00 | 0.00 | [+0.00, +0.00] | 0/50 |
| RMS+ICPP | 0.95 | low | 50 | 0.57 | 0.57 | +0.00 | 0.00 | [+0.00, +0.00] | 0/50 |
| RMS+ICPP | 0.95 | high | 50 | 0.57 | 0.57 | +0.00 | 0.00 | [+0.00, +0.00] | 0/50 |
| RMS+ICPP | 0.98 | low | 50 | 2.70 | 2.70 | +0.00 | 0.00 | [+0.00, +0.00] | 0/50 |
| RMS+ICPP | 0.98 | high | 50 | 2.71 | 2.70 | +0.01 | 0.09 | [-0.01, +0.04] | 1/50 |

## Critical-section-fraction sweep (shared memory, high intensity)

vs plain = paired difference (shared minus plain RMS/EDF on the same sets).

| U | cs frac | config | N | miss % [95% CI] (SD) | vs plain (pp) [95% CI] | sets differing | blocked jobs % | RMS-EDF (pp) [95% CI] | winner |
|---|---|---|---|---|---|---|---|---|---|
| 0.9 | 0.1 | EDF+SRP | 50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | 3.9 | - | - |
| 0.9 | 0.2 | EDF+SRP | 50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | 8.4 | - | - |
| 0.9 | 0.3 | EDF+SRP | 50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | 12.9 | - | - |
| 0.9 | 0.4 | EDF+SRP | 50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | 16.9 | - | - |
| 0.9 | 0.5 | EDF+SRP | 50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | 21.3 | - | - |
| 0.9 | 0.1 | RMS+PIP | 50 | 0.27 [0.01, 0.53] (0.92) | +0.00 [+0.00, +0.00] | 0/50 | 5.1 | +0.27 [+0.01, +0.53] | EDF |
| 0.9 | 0.2 | RMS+PIP | 50 | 0.27 [0.01, 0.53] (0.92) | +0.00 [+0.00, +0.00] | 0/50 | 11.0 | +0.27 [+0.01, +0.53] | EDF |
| 0.9 | 0.3 | RMS+PIP | 50 | 0.27 [0.01, 0.53] (0.92) | +0.00 [+0.00, +0.00] | 0/50 | 17.7 | +0.27 [+0.01, +0.53] | EDF |
| 0.9 | 0.4 | RMS+PIP | 50 | 0.27 [0.01, 0.53] (0.92) | +0.00 [+0.00, +0.00] | 0/50 | 23.2 | +0.27 [+0.01, +0.53] | EDF |
| 0.9 | 0.5 | RMS+PIP | 50 | 0.27 [0.01, 0.53] (0.92) | +0.00 [+0.00, +0.00] | 0/50 | 29.1 | +0.27 [+0.01, +0.53] | EDF |
| 0.95 | 0.1 | EDF+SRP | 50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | 5.2 | - | - |
| 0.95 | 0.2 | EDF+SRP | 50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | 10.0 | - | - |
| 0.95 | 0.3 | EDF+SRP | 50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | 15.1 | - | - |
| 0.95 | 0.4 | EDF+SRP | 50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | 19.8 | - | - |
| 0.95 | 0.5 | EDF+SRP | 50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | 25.6 | - | - |
| 0.95 | 0.1 | RMS+PIP | 50 | 0.57 [0.30, 0.83] (0.93) | +0.00 [+0.00, +0.00] | 0/50 | 6.6 | +0.57 [+0.30, +0.83] | EDF |
| 0.95 | 0.2 | RMS+PIP | 50 | 0.57 [0.30, 0.83] (0.93) | +0.00 [+0.00, +0.00] | 0/50 | 13.0 | +0.57 [+0.30, +0.83] | EDF |
| 0.95 | 0.3 | RMS+PIP | 50 | 0.57 [0.30, 0.83] (0.93) | +0.00 [+0.00, +0.00] | 0/50 | 19.7 | +0.57 [+0.30, +0.83] | EDF |
| 0.95 | 0.4 | RMS+PIP | 50 | 0.57 [0.30, 0.83] (0.93) | +0.00 [+0.00, +0.00] | 0/50 | 25.9 | +0.57 [+0.30, +0.83] | EDF |
| 0.95 | 0.5 | RMS+PIP | 50 | 0.57 [0.30, 0.83] (0.93) | +0.00 [+0.00, +0.00] | 0/50 | 33.3 | +0.57 [+0.30, +0.83] | EDF |
| 0.98 | 0.1 | EDF+SRP | 50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | 5.2 | - | - |
| 0.98 | 0.2 | EDF+SRP | 50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | 10.5 | - | - |
| 0.98 | 0.3 | EDF+SRP | 50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | 14.9 | - | - |
| 0.98 | 0.4 | EDF+SRP | 50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | 19.6 | - | - |
| 0.98 | 0.5 | EDF+SRP | 50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | 24.4 | - | - |
| 0.98 | 0.1 | RMS+PIP | 50 | 2.70 [1.97, 3.42] (2.55) | +0.00 [+0.00, +0.00] | 0/50 | 7.7 | +2.70 [+1.97, +3.42] | EDF |
| 0.98 | 0.2 | RMS+PIP | 50 | 2.70 [1.97, 3.42] (2.55) | +0.00 [+0.00, +0.00] | 0/50 | 15.5 | +2.70 [+1.97, +3.42] | EDF |
| 0.98 | 0.3 | RMS+PIP | 50 | 2.71 [1.99, 3.43] (2.55) | +0.01 [-0.01, +0.04] | 1/50 | 21.5 | +2.71 [+1.99, +3.43] | EDF |
| 0.98 | 0.4 | RMS+PIP | 50 | 2.71 [1.99, 3.43] (2.55) | +0.01 [-0.01, +0.04] | 1/50 | 28.7 | +2.71 [+1.99, +3.43] | EDF |
| 0.98 | 0.5 | RMS+PIP | 50 | 2.73 [2.01, 3.46] (2.54) | +0.04 [-0.04, +0.11] | 1/50 | 36.2 | +2.73 [+2.01, +3.46] | EDF |

## Message-latency sweep (message passing, high intensity)

Overload = effective U > 1 in at least one task set: shown but **not compared** (diff vs plain and RMS-EDF winner suppressed).

| U | L (ms) | config | N | mean eff. U | overload sets | miss % [95% CI] (SD) | vs plain (pp) [95% CI] | sets differing | RMS-EDF winner |
|---|---|---|---|---|---|---|---|---|---|
| 0.5 | 0.01 | EDF (plain) | 50 | 0.500 | 0/50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | - |
| 0.5 | 0.1 | EDF (plain) | 50 | 0.510 | 0/50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | - |
| 0.5 | 0.5 | EDF (plain) | 50 | 0.557 | 0/50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | - |
| 0.5 | 1 | EDF (plain) | 50 | 0.614 | 0/50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | - |
| 0.5 | 2 | EDF (plain) | 50 | 0.730 | 0/50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | - |
| 0.5 | 5 | EDF (plain) | 50 | 1.076 | 35/50 | 40.56 [29.37, 51.74] (39.36) | overload | - | overload |
| 0.5 | 0.01 | RMS (plain) | 50 | 0.500 | 0/50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | tie |
| 0.5 | 0.1 | RMS (plain) | 50 | 0.510 | 0/50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | tie |
| 0.5 | 0.5 | RMS (plain) | 50 | 0.557 | 0/50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | tie |
| 0.5 | 1 | RMS (plain) | 50 | 0.614 | 0/50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | tie |
| 0.5 | 2 | RMS (plain) | 50 | 0.730 | 0/50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | tie |
| 0.5 | 5 | RMS (plain) | 50 | 1.076 | 35/50 | 9.75 [6.76, 12.74] (10.51) | overload | - | overload |
| 0.7 | 0.01 | EDF (plain) | 50 | 0.700 | 0/50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | - |
| 0.7 | 0.1 | EDF (plain) | 50 | 0.710 | 0/50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | - |
| 0.7 | 0.5 | EDF (plain) | 50 | 0.757 | 0/50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | - |
| 0.7 | 1 | EDF (plain) | 50 | 0.815 | 0/50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | - |
| 0.7 | 2 | EDF (plain) | 50 | 0.931 | 1/50 | 0.02 [-0.02, 0.07] (0.16) | overload | - | overload |
| 0.7 | 5 | EDF (plain) | 50 | 1.278 | 50/50 | 80.75 [74.81, 86.69] (20.90) | overload | - | overload |
| 0.7 | 0.01 | RMS (plain) | 50 | 0.700 | 0/50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | tie |
| 0.7 | 0.1 | RMS (plain) | 50 | 0.710 | 0/50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | tie |
| 0.7 | 0.5 | RMS (plain) | 50 | 0.757 | 0/50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | tie |
| 0.7 | 1 | RMS (plain) | 50 | 0.815 | 0/50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | tie |
| 0.7 | 2 | RMS (plain) | 50 | 0.931 | 1/50 | 1.60 [0.87, 2.33] (2.57) | overload | - | overload |
| 0.7 | 5 | RMS (plain) | 50 | 1.278 | 50/50 | 21.74 [18.05, 25.42] (12.97) | overload | - | overload |
| 0.9 | 0.01 | EDF (plain) | 50 | 0.900 | 0/50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | - |
| 0.9 | 0.1 | EDF (plain) | 50 | 0.910 | 0/50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | - |
| 0.9 | 0.5 | EDF (plain) | 50 | 0.954 | 0/50 | 0.00 [0.00, 0.00] (0.00) | +0.00 [+0.00, +0.00] | 0/50 | - |
| 0.9 | 1 | EDF (plain) | 50 | 1.009 | 30/50 | 11.25 [5.15, 17.36] (21.50) | overload | - | overload |
| 0.9 | 2 | EDF (plain) | 50 | 1.120 | 50/50 | 60.77 [53.54, 67.99] (25.42) | overload | - | overload |
| 0.9 | 5 | EDF (plain) | 50 | 1.452 | 50/50 | 89.62 [87.68, 91.55] (6.81) | overload | - | overload |
| 0.9 | 0.01 | RMS (plain) | 50 | 0.900 | 0/50 | 0.27 [0.01, 0.53] (0.92) | +0.00 [+0.00, +0.00] | 0/50 | EDF |
| 0.9 | 0.1 | RMS (plain) | 50 | 0.910 | 0/50 | 0.32 [0.05, 0.58] (0.93) | +0.05 [-0.01, +0.10] | 3/50 | EDF |
| 0.9 | 0.5 | RMS (plain) | 50 | 0.954 | 0/50 | 1.42 [0.68, 2.17] (2.62) | +1.16 [+0.61, +1.71] | 30/50 | EDF |
| 0.9 | 1 | RMS (plain) | 50 | 1.009 | 30/50 | 5.84 [4.39, 7.28] (5.09) | overload | - | overload |
| 0.9 | 2 | RMS (plain) | 50 | 1.120 | 50/50 | 10.59 [8.03, 13.16] (9.02) | overload | - | overload |
| 0.9 | 5 | RMS (plain) | 50 | 1.452 | 50/50 | 26.23 [21.87, 30.58] (15.32) | overload | - | overload |

## Assumptions and placeholders

- **intensity values**: PLACEHOLDER (ipc/interface.py INTENSITY_PLACEHOLDER); awaiting team confirmation. cs_fraction = total critical-section time as a fraction of WCET.
- **baseline_latency**: PLACEHOLDER 0.01 ms per message (CPU cost, inside WCET). Does not affect baseline schedules (all overhead inside C'); matters only for the post-baseline latency sweep. Awaiting L4/Quest-V constants in ipc/NOTES.md.
- **period grid**: HARNESS CHOICE, bounded by D3 ranges (80 ms scale: Park et al. 2022; 160-1120 ms: Banfic et al.). 13 divisors of 4480 ms in [80,1120] so the hyperperiod is exactly 4480 ms; replaced by stage-specific ranges in Step 5. Not a per-stage structure.
- **n_tasks**: PLACEHOLDER 6 tasks per set (not specified in the plan); distinct periods per set drawn without replacement.
- **horizon**: One hyperperiod of each task set (synchronous release at t=0).
- **extended U**: U = 0.95 and 0.98 added to the baseline matrix (same task-set seeds per (U, index)); the 40 baseline conditions are included unchanged and reproduce results/baseline.csv.
- **controls**: RMS+SRP and RMS+ICPP (arms 'RMS+SRP', 'RMS+ICPP') on the shared-memory matrix at all 7 utilizations. The baseline RMS arm is RMS+PIP. Message passing has no protocol, so its column is plain RMS/EDF.
- **cs_fraction sweep**: SWEEP POINTS CHOSEN BY HARNESS: cs_fraction 0.1..0.5 (as specified) at U = 0.9, 0.95, 0.98, high intensity only (4 sections per job, 2 resources), RMS+PIP vs EDF+SRP. Tag csf=<fraction>.
- **latency sweep**: SWEEP POINTS CHOSEN BY HARNESS (PLACEHOLDER; L4/Quest-V constants still TODO in ipc/NOTES.md): per-message CPU cost L in {0.01 (=baseline L0), 0.1, 0.5, 1, 2, 5} ms at U = 0.5, 0.7, 0.9, high intensity (4 msgs/job). Only m*(L-L0) is added on top; effective U reported per set; overload (effective U > 1) is not compared. Tag lat=<L>.
