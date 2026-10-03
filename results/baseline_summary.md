# Baseline summary

Time unit: ms. Task sets per condition: N = 50; 6 tasks each; seed 2026.
Miss rate is shown as mean % [95% t-interval] (SD, N). Max lateness is core's definition (max over jobs of finish - deadline; negative = all jobs had slack).

Task sets rejected at generation (tiny WCET): {0.5: 1, 0.6: 2, 0.7: 1, 0.8: 0, 0.9: 1}

## How to read the message-passing results

At baseline, message-passing overhead (m x baseline latency) is carved out of the generated total WCET C' (D2), so the message-passing schedule is identical to plain RMS/EDF scheduling and identical across low/high intensity. The message-passing rows (and the right regime-map panel) are therefore the **plain-scheduling control**, not a separate effect, and are flat across intensity by construction. The question the baseline answers is whether shared-memory blocking (RMS+PIP, EDF+SRP) changes that plain ranking. Message-latency effects appear only in the post-baseline sweep (baseline_latency convention, effective U reported).

## Verdict

No flip found: scheduler ranking is robust to IPC choice under these conditions.

## Headline

under shared memory, RMS's miss rate exceeds EDF's by 0.27 percentage points (0.27% vs 0.00%, N=50, 95% paired CI [+0.01, +0.53] pp on RMS-EDF) at 0.9 utilization (high intensity), a gap that does appear under message passing.

## Winner per cell

Paired by task-set index; diff = RMS - EDF miss rate in percentage points (positive = RMS misses more). Tie = 95% paired t-interval includes 0.

| IPC | U | intensity | N | RMS mean % | EDF mean % | mean diff (pp) | SD diff | 95% CI diff (pp) | sets differing | winner |
|---|---|---|---|---|---|---|---|---|---|---|
| message_passing | 0.5 | high | 50 | 0.00 | 0.00 | 0.00 | 0.00 | [0.00, 0.00] | 0/50 | tie |
| message_passing | 0.5 | low | 50 | 0.00 | 0.00 | 0.00 | 0.00 | [0.00, 0.00] | 0/50 | tie |
| message_passing | 0.6 | high | 50 | 0.00 | 0.00 | 0.00 | 0.00 | [0.00, 0.00] | 0/50 | tie |
| message_passing | 0.6 | low | 50 | 0.00 | 0.00 | 0.00 | 0.00 | [0.00, 0.00] | 0/50 | tie |
| message_passing | 0.7 | high | 50 | 0.00 | 0.00 | 0.00 | 0.00 | [0.00, 0.00] | 0/50 | tie |
| message_passing | 0.7 | low | 50 | 0.00 | 0.00 | 0.00 | 0.00 | [0.00, 0.00] | 0/50 | tie |
| message_passing | 0.8 | high | 50 | 0.00 | 0.00 | 0.00 | 0.00 | [0.00, 0.00] | 0/50 | tie |
| message_passing | 0.8 | low | 50 | 0.00 | 0.00 | 0.00 | 0.00 | [0.00, 0.00] | 0/50 | tie |
| message_passing | 0.9 | high | 50 | 0.27 | 0.00 | 0.27 | 0.92 | [0.01, 0.53] | 7/50 | EDF |
| message_passing | 0.9 | low | 50 | 0.27 | 0.00 | 0.27 | 0.92 | [0.01, 0.53] | 7/50 | EDF |
| shared_memory | 0.5 | high | 50 | 0.00 | 0.00 | 0.00 | 0.00 | [0.00, 0.00] | 0/50 | tie |
| shared_memory | 0.5 | low | 50 | 0.00 | 0.00 | 0.00 | 0.00 | [0.00, 0.00] | 0/50 | tie |
| shared_memory | 0.6 | high | 50 | 0.00 | 0.00 | 0.00 | 0.00 | [0.00, 0.00] | 0/50 | tie |
| shared_memory | 0.6 | low | 50 | 0.00 | 0.00 | 0.00 | 0.00 | [0.00, 0.00] | 0/50 | tie |
| shared_memory | 0.7 | high | 50 | 0.00 | 0.00 | 0.00 | 0.00 | [0.00, 0.00] | 0/50 | tie |
| shared_memory | 0.7 | low | 50 | 0.00 | 0.00 | 0.00 | 0.00 | [0.00, 0.00] | 0/50 | tie |
| shared_memory | 0.8 | high | 50 | 0.00 | 0.00 | 0.00 | 0.00 | [0.00, 0.00] | 0/50 | tie |
| shared_memory | 0.8 | low | 50 | 0.00 | 0.00 | 0.00 | 0.00 | [0.00, 0.00] | 0/50 | tie |
| shared_memory | 0.9 | high | 50 | 0.27 | 0.00 | 0.27 | 0.92 | [0.01, 0.53] | 7/50 | EDF |
| shared_memory | 0.9 | low | 50 | 0.27 | 0.00 | 0.27 | 0.92 | [0.01, 0.53] | 7/50 | EDF |

## Per-condition metrics

| condition | N | miss rate % mean [95% CI] (SD) | max lateness mean [95% CI] (SD) | deadlock sets | blocked jobs % | blocking mean of blocked (ms) | blocking max (ms) |
|---|---|---|---|---|---|---|---|
| RMS|shared_memory|PIP|U0.5|low| | 50 | 0.00 [0.00, 0.00] (0.00) | -93.57 [-103.05, -84.09] (33.36) | 0 | 1.6 | 4.277 | 22.015 |
| RMS|shared_memory|PIP|U0.5|high| | 50 | 0.00 [0.00, 0.00] (0.00) | -90.60 [-100.18, -81.02] (33.71) | 0 | 6.0 | 4.090 | 20.650 |
| EDF|shared_memory|SRP|U0.5|low| | 50 | 0.00 [0.00, 0.00] (0.00) | -93.85 [-103.33, -84.37] (33.36) | 0 | 1.8 | 4.492 | 22.015 |
| EDF|shared_memory|SRP|U0.5|high| | 50 | 0.00 [0.00, 0.00] (0.00) | -90.60 [-100.18, -81.02] (33.71) | 0 | 5.7 | 4.200 | 20.650 |
| RMS|message_passing|None|U0.5|low| | 50 | 0.00 [0.00, 0.00] (0.00) | -95.18 [-104.71, -85.65] (33.54) | 0 | n/a | n/a | n/a |
| RMS|message_passing|None|U0.5|high| | 50 | 0.00 [0.00, 0.00] (0.00) | -95.18 [-104.71, -85.65] (33.54) | 0 | n/a | n/a | n/a |
| EDF|message_passing|None|U0.5|low| | 50 | 0.00 [0.00, 0.00] (0.00) | -95.18 [-104.71, -85.65] (33.54) | 0 | n/a | n/a | n/a |
| EDF|message_passing|None|U0.5|high| | 50 | 0.00 [0.00, 0.00] (0.00) | -95.18 [-104.71, -85.65] (33.54) | 0 | n/a | n/a | n/a |
| RMS|shared_memory|PIP|U0.6|low| | 50 | 0.00 [0.00, 0.00] (0.00) | -92.28 [-101.85, -82.70] (33.68) | 0 | 1.6 | 5.724 | 26.280 |
| RMS|shared_memory|PIP|U0.6|high| | 50 | 0.00 [0.00, 0.00] (0.00) | -90.37 [-99.98, -80.75] (33.83) | 0 | 8.3 | 4.381 | 32.736 |
| EDF|shared_memory|SRP|U0.6|low| | 50 | 0.00 [0.00, 0.00] (0.00) | -92.38 [-101.94, -82.83] (33.62) | 0 | 1.7 | 7.143 | 27.786 |
| EDF|shared_memory|SRP|U0.6|high| | 50 | 0.00 [0.00, 0.00] (0.00) | -90.41 [-100.03, -80.80] (33.84) | 0 | 7.8 | 4.336 | 32.415 |
| RMS|message_passing|None|U0.6|low| | 50 | 0.00 [0.00, 0.00] (0.00) | -94.97 [-104.37, -85.56] (33.09) | 0 | n/a | n/a | n/a |
| RMS|message_passing|None|U0.6|high| | 50 | 0.00 [0.00, 0.00] (0.00) | -94.97 [-104.37, -85.56] (33.09) | 0 | n/a | n/a | n/a |
| EDF|message_passing|None|U0.6|low| | 50 | 0.00 [0.00, 0.00] (0.00) | -94.97 [-104.37, -85.56] (33.09) | 0 | n/a | n/a | n/a |
| EDF|message_passing|None|U0.6|high| | 50 | 0.00 [0.00, 0.00] (0.00) | -94.97 [-104.37, -85.56] (33.09) | 0 | n/a | n/a | n/a |
| RMS|shared_memory|PIP|U0.7|low| | 50 | 0.00 [0.00, 0.00] (0.00) | -85.05 [-92.11, -77.99] (24.83) | 0 | 2.0 | 5.534 | 32.154 |
| RMS|shared_memory|PIP|U0.7|high| | 50 | 0.00 [0.00, 0.00] (0.00) | -81.81 [-88.73, -74.89] (24.36) | 0 | 10.3 | 4.425 | 30.823 |
| EDF|shared_memory|SRP|U0.7|low| | 50 | 0.00 [0.00, 0.00] (0.00) | -85.40 [-92.48, -78.33] (24.90) | 0 | 2.2 | 5.875 | 32.154 |
| EDF|shared_memory|SRP|U0.7|high| | 50 | 0.00 [0.00, 0.00] (0.00) | -81.99 [-88.92, -75.07] (24.37) | 0 | 8.9 | 4.671 | 30.823 |
| RMS|message_passing|None|U0.7|low| | 50 | 0.00 [0.00, 0.00] (0.00) | -87.39 [-94.18, -80.60] (23.89) | 0 | n/a | n/a | n/a |
| RMS|message_passing|None|U0.7|high| | 50 | 0.00 [0.00, 0.00] (0.00) | -87.39 [-94.18, -80.60] (23.89) | 0 | n/a | n/a | n/a |
| EDF|message_passing|None|U0.7|low| | 50 | 0.00 [0.00, 0.00] (0.00) | -87.39 [-94.18, -80.60] (23.89) | 0 | n/a | n/a | n/a |
| EDF|message_passing|None|U0.7|high| | 50 | 0.00 [0.00, 0.00] (0.00) | -87.39 [-94.18, -80.60] (23.89) | 0 | n/a | n/a | n/a |
| RMS|shared_memory|PIP|U0.8|low| | 50 | 0.00 [0.00, 0.00] (0.00) | -78.87 [-85.65, -72.09] (23.86) | 0 | 4.0 | 7.025 | 33.446 |
| RMS|shared_memory|PIP|U0.8|high| | 50 | 0.00 [0.00, 0.00] (0.00) | -76.90 [-83.35, -70.44] (22.72) | 0 | 13.5 | 4.611 | 33.914 |
| EDF|shared_memory|SRP|U0.8|low| | 50 | 0.00 [0.00, 0.00] (0.00) | -81.02 [-87.45, -74.58] (22.65) | 0 | 3.3 | 7.426 | 33.446 |
| EDF|shared_memory|SRP|U0.8|high| | 50 | 0.00 [0.00, 0.00] (0.00) | -77.32 [-83.79, -70.85] (22.77) | 0 | 11.8 | 4.512 | 33.914 |
| RMS|message_passing|None|U0.8|low| | 50 | 0.00 [0.00, 0.00] (0.00) | -84.32 [-90.74, -77.90] (22.58) | 0 | n/a | n/a | n/a |
| RMS|message_passing|None|U0.8|high| | 50 | 0.00 [0.00, 0.00] (0.00) | -84.32 [-90.74, -77.90] (22.58) | 0 | n/a | n/a | n/a |
| EDF|message_passing|None|U0.8|low| | 50 | 0.00 [0.00, 0.00] (0.00) | -84.87 [-91.31, -78.43] (22.66) | 0 | n/a | n/a | n/a |
| EDF|message_passing|None|U0.8|high| | 50 | 0.00 [0.00, 0.00] (0.00) | -84.87 [-91.31, -78.43] (22.66) | 0 | n/a | n/a | n/a |
| RMS|shared_memory|PIP|U0.9|low| | 50 | 0.27 [0.01, 0.53] (0.92) | -31.99 [-51.88, -12.10] (70.00) | 0 | 4.2 | 8.268 | 53.823 |
| RMS|shared_memory|PIP|U0.9|high| | 50 | 0.27 [0.01, 0.53] (0.92) | -30.15 [-49.80, -10.50] (69.14) | 0 | 17.7 | 5.865 | 50.600 |
| EDF|shared_memory|SRP|U0.9|low| | 50 | 0.00 [0.00, 0.00] (0.00) | -76.26 [-83.48, -69.05] (25.39) | 0 | 3.1 | 8.972 | 53.823 |
| EDF|shared_memory|SRP|U0.9|high| | 50 | 0.00 [0.00, 0.00] (0.00) | -73.41 [-80.68, -66.13] (25.59) | 0 | 12.9 | 5.737 | 37.412 |
| RMS|message_passing|None|U0.9|low| | 50 | 0.27 [0.01, 0.53] (0.92) | -35.65 [-56.26, -15.04] (72.53) | 0 | n/a | n/a | n/a |
| RMS|message_passing|None|U0.9|high| | 50 | 0.27 [0.01, 0.53] (0.92) | -35.65 [-56.26, -15.04] (72.53) | 0 | n/a | n/a | n/a |
| EDF|message_passing|None|U0.9|low| | 50 | 0.00 [0.00, 0.00] (0.00) | -81.76 [-89.44, -74.07] (27.04) | 0 | n/a | n/a | n/a |
| EDF|message_passing|None|U0.9|high| | 50 | 0.00 [0.00, 0.00] (0.00) | -81.76 [-89.44, -74.07] (27.04) | 0 | n/a | n/a | n/a |

## Assumptions and placeholders

- **intensity values**: PLACEHOLDER (ipc/interface.py INTENSITY_PLACEHOLDER); awaiting team confirmation. cs_fraction = total critical-section time as a fraction of WCET.
- **baseline_latency**: PLACEHOLDER 0.01 ms per message (CPU cost, inside WCET). Does not affect baseline schedules (all overhead inside C'); matters only for the post-baseline latency sweep. Awaiting L4/Quest-V constants in ipc/NOTES.md.
- **period grid**: HARNESS CHOICE, bounded by D3 ranges (80 ms scale: Park et al. 2022; 160-1120 ms: Banfic et al.). 13 divisors of 4480 ms in [80,1120] so the hyperperiod is exactly 4480 ms; replaced by stage-specific ranges in Step 5. Not a per-stage structure.
- **n_tasks**: PLACEHOLDER 6 tasks per set (not specified in the plan); distinct periods per set drawn without replacement.
- **horizon**: One hyperperiod of each task set (synchronous release at t=0).
