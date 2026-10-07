# Baseline summary

Time unit: ms. Task sets per condition: N = 50; 6 tasks each; seed 2026.
Miss rate is shown as mean % [95% t-interval] (SD, N). Max lateness is core's definition (max over jobs of finish - deadline; negative = all jobs had slack).

Task sets rejected at generation (tiny WCET): {0.5: 1, 0.6: 2, 0.7: 1, 0.8: 0, 0.9: 1, 0.95: 1, 0.98: 1}

## How to read the message-passing results

At baseline, message-passing overhead (m x baseline latency) is carved out of the generated total WCET C' (D2), so the message-passing schedule is identical to plain RMS/EDF scheduling and identical across low/high intensity. The message-passing rows (and the right regime-map panel) are therefore the **plain-scheduling control**, not a separate effect, and are flat across intensity by construction. The question the baseline answers is whether shared-memory blocking (RMS+PIP, EDF+SRP) changes that plain ranking. Message-latency effects appear only in the post-baseline sweep (baseline_latency convention, effective U reported).

## Verdict

No flip found: scheduler ranking is robust to IPC choice under these conditions.

## Headline

under shared memory, RMS's miss rate exceeds EDF's by 2.71 percentage points (2.71% vs 0.00%, N=50, 95% paired CI [+1.99, +3.43] pp on RMS-EDF) at 0.98 utilization (high intensity), a gap that does appear under message passing.

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
| message_passing | 0.95 | high | 50 | 0.57 | 0.00 | 0.57 | 0.93 | [0.30, 0.83] | 21/50 | EDF |
| message_passing | 0.95 | low | 50 | 0.57 | 0.00 | 0.57 | 0.93 | [0.30, 0.83] | 21/50 | EDF |
| message_passing | 0.98 | high | 50 | 2.70 | 0.00 | 2.70 | 2.55 | [1.97, 3.42] | 42/50 | EDF |
| message_passing | 0.98 | low | 50 | 2.70 | 0.00 | 2.70 | 2.55 | [1.97, 3.42] | 42/50 | EDF |
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
| shared_memory | 0.95 | high | 50 | 0.57 | 0.00 | 0.57 | 0.93 | [0.30, 0.83] | 21/50 | EDF |
| shared_memory | 0.95 | low | 50 | 0.57 | 0.00 | 0.57 | 0.93 | [0.30, 0.83] | 21/50 | EDF |
| shared_memory | 0.98 | high | 50 | 2.71 | 0.00 | 2.71 | 2.55 | [1.99, 3.43] | 42/50 | EDF |
| shared_memory | 0.98 | low | 50 | 2.70 | 0.00 | 2.70 | 2.55 | [1.97, 3.42] | 42/50 | EDF |

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
| RMS|shared_memory|PIP|U0.95|low| | 50 | 0.57 [0.30, 0.83] (0.93) | 59.60 [22.27, 96.92] (131.34) | 0 | 5.1 | 8.251 | 44.067 |
| RMS|shared_memory|PIP|U0.95|high| | 50 | 0.57 [0.30, 0.83] (0.93) | 60.43 [23.29, 97.56] (130.67) | 0 | 19.7 | 6.658 | 48.860 |
| EDF|shared_memory|SRP|U0.95|low| | 50 | 0.00 [0.00, 0.00] (0.00) | -67.01 [-73.17, -60.85] (21.68) | 0 | 4.2 | 8.995 | 44.067 |
| EDF|shared_memory|SRP|U0.95|high| | 50 | 0.00 [0.00, 0.00] (0.00) | -64.13 [-70.79, -57.46] (23.46) | 0 | 15.1 | 6.865 | 48.634 |
| RMS|message_passing|None|U0.95|low| | 50 | 0.57 [0.30, 0.83] (0.93) | 59.16 [21.72, 96.60] (131.74) | 0 | n/a | n/a | n/a |
| RMS|message_passing|None|U0.95|high| | 50 | 0.57 [0.30, 0.83] (0.93) | 59.16 [21.72, 96.60] (131.74) | 0 | n/a | n/a | n/a |
| EDF|message_passing|None|U0.95|low| | 50 | 0.00 [0.00, 0.00] (0.00) | -70.93 [-77.37, -64.49] (22.67) | 0 | n/a | n/a | n/a |
| EDF|message_passing|None|U0.95|high| | 50 | 0.00 [0.00, 0.00] (0.00) | -70.93 [-77.37, -64.49] (22.67) | 0 | n/a | n/a | n/a |
| RMS|shared_memory|PIP|U0.98|low| | 50 | 2.70 [1.97, 3.42] (2.55) | 264.47 [179.35, 349.58] (299.50) | 0 | 5.7 | 10.226 | 59.190 |
| RMS|shared_memory|PIP|U0.98|high| | 50 | 2.71 [1.99, 3.43] (2.55) | 264.47 [179.35, 349.58] (299.50) | 0 | 21.5 | 6.938 | 60.413 |
| EDF|shared_memory|SRP|U0.98|low| | 50 | 0.00 [0.00, 0.00] (0.00) | -50.95 [-56.30, -45.60] (18.83) | 0 | 3.9 | 9.874 | 64.328 |
| EDF|shared_memory|SRP|U0.98|high| | 50 | 0.00 [0.00, 0.00] (0.00) | -50.16 [-55.25, -45.06] (17.93) | 0 | 14.9 | 7.716 | 63.348 |
| RMS|message_passing|None|U0.98|low| | 50 | 2.70 [1.97, 3.42] (2.55) | 264.47 [179.35, 349.58] (299.50) | 0 | n/a | n/a | n/a |
| RMS|message_passing|None|U0.98|high| | 50 | 2.70 [1.97, 3.42] (2.55) | 264.47 [179.35, 349.58] (299.50) | 0 | n/a | n/a | n/a |
| EDF|message_passing|None|U0.98|low| | 50 | 0.00 [0.00, 0.00] (0.00) | -53.29 [-59.04, -47.53] (20.25) | 0 | n/a | n/a | n/a |
| EDF|message_passing|None|U0.98|high| | 50 | 0.00 [0.00, 0.00] (0.00) | -53.29 [-59.04, -47.53] (20.25) | 0 | n/a | n/a | n/a |
| RMS+SRP|shared_memory|SRP|U0.5|low| | 50 | 0.00 [0.00, 0.00] (0.00) | -93.85 [-103.33, -84.37] (33.36) | 0 | 1.9 | 4.382 | 22.015 |
| RMS+SRP|shared_memory|SRP|U0.5|high| | 50 | 0.00 [0.00, 0.00] (0.00) | -90.60 [-100.18, -81.02] (33.71) | 0 | 6.0 | 4.086 | 20.650 |
| RMS+SRP|shared_memory|SRP|U0.6|low| | 50 | 0.00 [0.00, 0.00] (0.00) | -92.38 [-101.94, -82.83] (33.62) | 0 | 1.8 | 6.909 | 27.786 |
| RMS+SRP|shared_memory|SRP|U0.6|high| | 50 | 0.00 [0.00, 0.00] (0.00) | -90.37 [-99.98, -80.75] (33.83) | 0 | 8.4 | 4.355 | 32.736 |
| RMS+SRP|shared_memory|SRP|U0.7|low| | 50 | 0.00 [0.00, 0.00] (0.00) | -85.32 [-92.43, -78.20] (25.03) | 0 | 2.3 | 5.419 | 32.154 |
| RMS+SRP|shared_memory|SRP|U0.7|high| | 50 | 0.00 [0.00, 0.00] (0.00) | -81.81 [-88.73, -74.89] (24.36) | 0 | 10.1 | 4.492 | 30.823 |
| RMS+SRP|shared_memory|SRP|U0.8|low| | 50 | 0.00 [0.00, 0.00] (0.00) | -80.14 [-86.55, -73.73] (22.56) | 0 | 3.9 | 6.751 | 33.446 |
| RMS+SRP|shared_memory|SRP|U0.8|high| | 50 | 0.00 [0.00, 0.00] (0.00) | -77.00 [-83.45, -70.56] (22.67) | 0 | 13.5 | 4.594 | 33.914 |
| RMS+SRP|shared_memory|SRP|U0.9|low| | 50 | 0.27 [0.01, 0.53] (0.92) | -31.99 [-51.88, -12.10] (70.00) | 0 | 4.2 | 8.606 | 53.823 |
| RMS+SRP|shared_memory|SRP|U0.9|high| | 50 | 0.27 [0.01, 0.53] (0.92) | -30.15 [-49.80, -10.50] (69.14) | 0 | 17.4 | 5.859 | 50.600 |
| RMS+SRP|shared_memory|SRP|U0.95|low| | 50 | 0.57 [0.30, 0.83] (0.93) | 59.60 [22.27, 96.92] (131.34) | 0 | 5.0 | 8.544 | 44.067 |
| RMS+SRP|shared_memory|SRP|U0.95|high| | 50 | 0.57 [0.30, 0.83] (0.93) | 60.43 [23.29, 97.56] (130.67) | 0 | 19.3 | 6.610 | 48.860 |
| RMS+SRP|shared_memory|SRP|U0.98|low| | 50 | 2.70 [1.97, 3.42] (2.55) | 264.47 [179.35, 349.58] (299.50) | 0 | 5.6 | 10.253 | 59.190 |
| RMS+SRP|shared_memory|SRP|U0.98|high| | 50 | 2.71 [1.99, 3.43] (2.55) | 264.47 [179.35, 349.58] (299.50) | 0 | 21.0 | 6.927 | 60.413 |
| RMS+ICPP|shared_memory|ICPP|U0.5|low| | 50 | 0.00 [0.00, 0.00] (0.00) | -93.85 [-103.33, -84.37] (33.36) | 0 | 1.9 | 4.382 | 22.015 |
| RMS+ICPP|shared_memory|ICPP|U0.5|high| | 50 | 0.00 [0.00, 0.00] (0.00) | -90.60 [-100.18, -81.02] (33.71) | 0 | 6.0 | 4.086 | 20.650 |
| RMS+ICPP|shared_memory|ICPP|U0.6|low| | 50 | 0.00 [0.00, 0.00] (0.00) | -92.38 [-101.94, -82.83] (33.62) | 0 | 1.8 | 6.909 | 27.786 |
| RMS+ICPP|shared_memory|ICPP|U0.6|high| | 50 | 0.00 [0.00, 0.00] (0.00) | -90.37 [-99.98, -80.75] (33.83) | 0 | 8.4 | 4.355 | 32.736 |
| RMS+ICPP|shared_memory|ICPP|U0.7|low| | 50 | 0.00 [0.00, 0.00] (0.00) | -85.32 [-92.43, -78.20] (25.03) | 0 | 2.3 | 5.419 | 32.154 |
| RMS+ICPP|shared_memory|ICPP|U0.7|high| | 50 | 0.00 [0.00, 0.00] (0.00) | -81.81 [-88.73, -74.89] (24.36) | 0 | 10.1 | 4.492 | 30.823 |
| RMS+ICPP|shared_memory|ICPP|U0.8|low| | 50 | 0.00 [0.00, 0.00] (0.00) | -80.14 [-86.55, -73.73] (22.56) | 0 | 3.9 | 6.751 | 33.446 |
| RMS+ICPP|shared_memory|ICPP|U0.8|high| | 50 | 0.00 [0.00, 0.00] (0.00) | -77.00 [-83.45, -70.56] (22.67) | 0 | 13.5 | 4.594 | 33.914 |
| RMS+ICPP|shared_memory|ICPP|U0.9|low| | 50 | 0.27 [0.01, 0.53] (0.92) | -31.99 [-51.88, -12.10] (70.00) | 0 | 4.2 | 8.606 | 53.823 |
| RMS+ICPP|shared_memory|ICPP|U0.9|high| | 50 | 0.27 [0.01, 0.53] (0.92) | -30.15 [-49.80, -10.50] (69.14) | 0 | 17.4 | 5.859 | 50.600 |
| RMS+ICPP|shared_memory|ICPP|U0.95|low| | 50 | 0.57 [0.30, 0.83] (0.93) | 59.60 [22.27, 96.92] (131.34) | 0 | 5.0 | 8.544 | 44.067 |
| RMS+ICPP|shared_memory|ICPP|U0.95|high| | 50 | 0.57 [0.30, 0.83] (0.93) | 60.43 [23.29, 97.56] (130.67) | 0 | 19.3 | 6.610 | 48.860 |
| RMS+ICPP|shared_memory|ICPP|U0.98|low| | 50 | 2.70 [1.97, 3.42] (2.55) | 264.47 [179.35, 349.58] (299.50) | 0 | 5.6 | 10.253 | 59.190 |
| RMS+ICPP|shared_memory|ICPP|U0.98|high| | 50 | 2.71 [1.99, 3.43] (2.55) | 264.47 [179.35, 349.58] (299.50) | 0 | 21.0 | 6.927 | 60.413 |
| RMS|shared_memory|PIP|U0.9|high|csf=0.1 | 50 | 0.27 [0.01, 0.53] (0.92) | -34.62 [-55.06, -14.17] (71.94) | 0 | 5.1 | 2.063 | 8.430 |
| EDF|shared_memory|SRP|U0.9|high|csf=0.1 | 50 | 0.00 [0.00, 0.00] (0.00) | -79.75 [-87.33, -72.18] (26.65) | 0 | 3.9 | 2.130 | 8.082 |
| RMS|shared_memory|PIP|U0.9|high|csf=0.2 | 50 | 0.27 [0.01, 0.53] (0.92) | -32.66 [-52.71, -12.61] (70.56) | 0 | 11.0 | 4.159 | 28.437 |
| EDF|shared_memory|SRP|U0.9|high|csf=0.2 | 50 | 0.00 [0.00, 0.00] (0.00) | -76.78 [-83.98, -69.58] (25.34) | 0 | 8.4 | 3.938 | 28.437 |
| RMS|shared_memory|PIP|U0.9|high|csf=0.3 | 50 | 0.27 [0.01, 0.53] (0.92) | -30.15 [-49.80, -10.50] (69.14) | 0 | 17.7 | 5.865 | 50.600 |
| EDF|shared_memory|SRP|U0.9|high|csf=0.3 | 50 | 0.00 [0.00, 0.00] (0.00) | -73.41 [-80.68, -66.13] (25.59) | 0 | 12.9 | 5.737 | 37.412 |
| RMS|shared_memory|PIP|U0.9|high|csf=0.4 | 50 | 0.27 [0.01, 0.53] (0.92) | -26.64 [-45.65, -7.63] (66.89) | 0 | 23.2 | 7.885 | 70.345 |
| EDF|shared_memory|SRP|U0.9|high|csf=0.4 | 50 | 0.00 [0.00, 0.00] (0.00) | -68.12 [-75.20, -61.05] (24.90) | 0 | 16.9 | 8.092 | 70.345 |
| RMS|shared_memory|PIP|U0.9|high|csf=0.5 | 50 | 0.27 [0.01, 0.53] (0.92) | -24.19 [-42.84, -5.53] (65.64) | 0 | 29.1 | 9.550 | 87.138 |
| EDF|shared_memory|SRP|U0.9|high|csf=0.5 | 50 | 0.00 [0.00, 0.00] (0.00) | -64.32 [-71.39, -57.25] (24.87) | 0 | 21.3 | 9.989 | 87.138 |
| RMS|shared_memory|PIP|U0.95|high|csf=0.1 | 50 | 0.57 [0.30, 0.83] (0.93) | 59.25 [21.84, 96.67] (131.66) | 0 | 6.6 | 2.282 | 14.069 |
| EDF|shared_memory|SRP|U0.95|high|csf=0.1 | 50 | 0.00 [0.00, 0.00] (0.00) | -69.88 [-76.30, -63.46] (22.60) | 0 | 5.2 | 2.291 | 14.069 |
| RMS|shared_memory|PIP|U0.95|high|csf=0.2 | 50 | 0.57 [0.30, 0.83] (0.93) | 59.76 [22.46, 97.05] (131.22) | 0 | 13.0 | 4.212 | 30.117 |
| EDF|shared_memory|SRP|U0.95|high|csf=0.2 | 50 | 0.00 [0.00, 0.00] (0.00) | -67.55 [-74.05, -61.05] (22.88) | 0 | 10.0 | 4.391 | 30.117 |
| RMS|shared_memory|PIP|U0.95|high|csf=0.3 | 50 | 0.57 [0.30, 0.83] (0.93) | 60.43 [23.29, 97.56] (130.67) | 0 | 19.7 | 6.658 | 48.860 |
| EDF|shared_memory|SRP|U0.95|high|csf=0.3 | 50 | 0.00 [0.00, 0.00] (0.00) | -64.13 [-70.79, -57.46] (23.46) | 0 | 15.1 | 6.865 | 48.634 |
| RMS|shared_memory|PIP|U0.95|high|csf=0.4 | 50 | 0.57 [0.30, 0.83] (0.93) | 61.60 [24.70, 98.51] (129.85) | 0 | 25.9 | 8.558 | 63.347 |
| EDF|shared_memory|SRP|U0.95|high|csf=0.4 | 50 | 0.00 [0.00, 0.00] (0.00) | -60.31 [-67.06, -53.56] (23.76) | 0 | 19.8 | 8.956 | 67.754 |
| RMS|shared_memory|PIP|U0.95|high|csf=0.5 | 50 | 0.57 [0.30, 0.83] (0.93) | 62.15 [25.36, 98.95] (129.47) | 0 | 33.3 | 10.291 | 84.342 |
| EDF|shared_memory|SRP|U0.95|high|csf=0.5 | 50 | 0.00 [0.00, 0.00] (0.00) | -56.43 [-63.47, -49.39] (24.76) | 0 | 25.6 | 10.528 | 84.342 |
| RMS|shared_memory|PIP|U0.98|high|csf=0.1 | 50 | 2.70 [1.97, 3.42] (2.55) | 264.47 [179.35, 349.58] (299.50) | 0 | 7.7 | 2.020 | 21.493 |
| EDF|shared_memory|SRP|U0.98|high|csf=0.1 | 50 | 0.00 [0.00, 0.00] (0.00) | -52.84 [-58.50, -47.17] (19.92) | 0 | 5.2 | 2.326 | 21.493 |
| RMS|shared_memory|PIP|U0.98|high|csf=0.2 | 50 | 2.70 [1.97, 3.42] (2.55) | 264.47 [179.35, 349.58] (299.50) | 0 | 15.5 | 4.379 | 42.534 |
| EDF|shared_memory|SRP|U0.98|high|csf=0.2 | 50 | 0.00 [0.00, 0.00] (0.00) | -51.65 [-57.06, -46.24] (19.03) | 0 | 10.5 | 4.823 | 35.363 |
| RMS|shared_memory|PIP|U0.98|high|csf=0.3 | 50 | 2.71 [1.99, 3.43] (2.55) | 264.47 [179.35, 349.58] (299.50) | 0 | 21.5 | 6.938 | 60.413 |
| EDF|shared_memory|SRP|U0.98|high|csf=0.3 | 50 | 0.00 [0.00, 0.00] (0.00) | -50.16 [-55.25, -45.06] (17.93) | 0 | 14.9 | 7.716 | 63.348 |
| RMS|shared_memory|PIP|U0.98|high|csf=0.4 | 50 | 2.71 [1.99, 3.43] (2.55) | 264.47 [179.35, 349.58] (299.50) | 0 | 28.7 | 9.476 | 78.291 |
| EDF|shared_memory|SRP|U0.98|high|csf=0.4 | 50 | 0.00 [0.00, 0.00] (0.00) | -48.10 [-52.84, -43.36] (16.67) | 0 | 19.6 | 10.183 | 81.226 |
| RMS|shared_memory|PIP|U0.98|high|csf=0.5 | 50 | 2.73 [2.01, 3.46] (2.54) | 264.47 [179.35, 349.58] (299.50) | 0 | 36.2 | 11.829 | 103.141 |
| EDF|shared_memory|SRP|U0.98|high|csf=0.5 | 50 | 0.00 [0.00, 0.00] (0.00) | -45.27 [-49.77, -40.77] (15.83) | 0 | 24.4 | 12.298 | 103.141 |
| RMS|message_passing|None|U0.5|high|lat=0.01 | 50 | 0.00 [0.00, 0.00] (0.00) | -95.18 [-104.71, -85.65] (33.54) | 0 | n/a | n/a | n/a |
| EDF|message_passing|None|U0.5|high|lat=0.01 | 50 | 0.00 [0.00, 0.00] (0.00) | -95.18 [-104.71, -85.65] (33.54) | 0 | n/a | n/a | n/a |
| RMS|message_passing|None|U0.5|high|lat=0.1 | 50 | 0.00 [0.00, 0.00] (0.00) | -94.78 [-104.31, -85.25] (33.54) | 0 | n/a | n/a | n/a |
| EDF|message_passing|None|U0.5|high|lat=0.1 | 50 | 0.00 [0.00, 0.00] (0.00) | -94.78 [-104.31, -85.25] (33.54) | 0 | n/a | n/a | n/a |
| RMS|message_passing|None|U0.5|high|lat=0.5 | 50 | 0.00 [0.00, 0.00] (0.00) | -93.00 [-102.53, -83.47] (33.53) | 0 | n/a | n/a | n/a |
| EDF|message_passing|None|U0.5|high|lat=0.5 | 50 | 0.00 [0.00, 0.00] (0.00) | -93.00 [-102.53, -83.47] (33.53) | 0 | n/a | n/a | n/a |
| RMS|message_passing|None|U0.5|high|lat=1 | 50 | 0.00 [0.00, 0.00] (0.00) | -90.70 [-100.22, -81.18] (33.50) | 0 | n/a | n/a | n/a |
| EDF|message_passing|None|U0.5|high|lat=1 | 50 | 0.00 [0.00, 0.00] (0.00) | -90.70 [-100.22, -81.18] (33.50) | 0 | n/a | n/a | n/a |
| RMS|message_passing|None|U0.5|high|lat=2 | 50 | 0.00 [0.00, 0.00] (0.00) | -85.37 [-95.02, -75.73] (33.92) | 0 | n/a | n/a | n/a |
| EDF|message_passing|None|U0.5|high|lat=2 | 50 | 0.00 [0.00, 0.00] (0.00) | -85.81 [-95.31, -76.32] (33.42) | 0 | n/a | n/a | n/a |
| RMS|message_passing|None|U0.5|high|lat=5 | 50 | 9.75 [6.76, 12.74] (10.51) | 1995.79 [1528.46, 2463.12] (1644.39) | 0 | n/a | n/a | n/a |
| EDF|message_passing|None|U0.5|high|lat=5 | 50 | 40.56 [29.37, 51.74] (39.36) | 372.19 [233.19, 511.19] (489.09) | 0 | n/a | n/a | n/a |
| RMS|message_passing|None|U0.7|high|lat=0.01 | 50 | 0.00 [0.00, 0.00] (0.00) | -87.39 [-94.18, -80.60] (23.89) | 0 | n/a | n/a | n/a |
| EDF|message_passing|None|U0.7|high|lat=0.01 | 50 | 0.00 [0.00, 0.00] (0.00) | -87.39 [-94.18, -80.60] (23.89) | 0 | n/a | n/a | n/a |
| RMS|message_passing|None|U0.7|high|lat=0.1 | 50 | 0.00 [0.00, 0.00] (0.00) | -86.91 [-93.70, -80.12] (23.90) | 0 | n/a | n/a | n/a |
| EDF|message_passing|None|U0.7|high|lat=0.1 | 50 | 0.00 [0.00, 0.00] (0.00) | -86.91 [-93.70, -80.12] (23.90) | 0 | n/a | n/a | n/a |
| RMS|message_passing|None|U0.7|high|lat=0.5 | 50 | 0.00 [0.00, 0.00] (0.00) | -84.56 [-91.39, -77.74] (24.02) | 0 | n/a | n/a | n/a |
| EDF|message_passing|None|U0.7|high|lat=0.5 | 50 | 0.00 [0.00, 0.00] (0.00) | -84.71 [-91.52, -77.91] (23.95) | 0 | n/a | n/a | n/a |
| RMS|message_passing|None|U0.7|high|lat=1 | 50 | 0.00 [0.00, 0.00] (0.00) | -79.85 [-87.34, -72.37] (26.33) | 0 | n/a | n/a | n/a |
| EDF|message_passing|None|U0.7|high|lat=1 | 50 | 0.00 [0.00, 0.00] (0.00) | -81.70 [-88.56, -74.84] (24.14) | 0 | n/a | n/a | n/a |
| RMS|message_passing|None|U0.7|high|lat=2 | 50 | 1.60 [0.87, 2.33] (2.57) | 61.79 [13.95, 109.62] (168.33) | 0 | n/a | n/a | n/a |
| EDF|message_passing|None|U0.7|high|lat=2 | 50 | 0.02 [-0.02, 0.07] (0.16) | -67.77 [-77.20, -58.34] (33.19) | 0 | n/a | n/a | n/a |
| RMS|message_passing|None|U0.7|high|lat=5 | 50 | 21.74 [18.05, 25.42] (12.97) | 3924.24 [3604.15, 4244.33] (1126.30) | 0 | n/a | n/a | n/a |
| EDF|message_passing|None|U0.7|high|lat=5 | 50 | 80.75 [74.81, 86.69] (20.90) | 1113.88 [961.24, 1266.51] (537.07) | 0 | n/a | n/a | n/a |
| RMS|message_passing|None|U0.9|high|lat=0.01 | 50 | 0.27 [0.01, 0.53] (0.92) | -35.65 [-56.26, -15.04] (72.53) | 0 | n/a | n/a | n/a |
| EDF|message_passing|None|U0.9|high|lat=0.01 | 50 | 0.00 [0.00, 0.00] (0.00) | -81.76 [-89.44, -74.07] (27.04) | 0 | n/a | n/a | n/a |
| RMS|message_passing|None|U0.9|high|lat=0.1 | 50 | 0.32 [0.05, 0.58] (0.93) | -26.29 [-47.76, -4.83] (75.54) | 0 | n/a | n/a | n/a |
| EDF|message_passing|None|U0.9|high|lat=0.1 | 50 | 0.00 [0.00, 0.00] (0.00) | -80.73 [-88.45, -73.01] (27.16) | 0 | n/a | n/a | n/a |
| RMS|message_passing|None|U0.9|high|lat=0.5 | 50 | 1.42 [0.68, 2.17] (2.62) | 107.17 [59.52, 154.82] (167.67) | 0 | n/a | n/a | n/a |
| EDF|message_passing|None|U0.9|high|lat=0.5 | 50 | 0.00 [0.00, 0.00] (0.00) | -71.14 [-79.46, -62.82] (29.27) | 0 | n/a | n/a | n/a |
| RMS|message_passing|None|U0.9|high|lat=1 | 50 | 5.84 [4.39, 7.28] (5.09) | 1241.28 [884.09, 1598.48] (1256.87) | 0 | n/a | n/a | n/a |
| EDF|message_passing|None|U0.9|high|lat=1 | 50 | 11.25 [5.15, 17.36] (21.50) | 45.56 [13.84, 77.29] (111.64) | 0 | n/a | n/a | n/a |
| RMS|message_passing|None|U0.9|high|lat=2 | 50 | 10.59 [8.03, 13.16] (9.02) | 2945.31 [2597.01, 3293.62] (1225.58) | 0 | n/a | n/a | n/a |
| EDF|message_passing|None|U0.9|high|lat=2 | 50 | 60.77 [53.54, 67.99] (25.42) | 518.09 [448.37, 587.82] (245.34) | 0 | n/a | n/a | n/a |
| RMS|message_passing|None|U0.9|high|lat=5 | 50 | 26.23 [21.87, 30.58] (15.32) | 4759.23 [4429.96, 5088.49] (1158.59) | 0 | n/a | n/a | n/a |
| EDF|message_passing|None|U0.9|high|lat=5 | 50 | 89.62 [87.68, 91.55] (6.81) | 1954.25 [1773.51, 2135.00] (635.98) | 0 | n/a | n/a | n/a |

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
