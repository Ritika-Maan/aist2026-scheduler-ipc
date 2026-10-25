import numpy as np
from uunifast import make_taskset
from schedulers import simulate, metrics

rng = np.random.default_rng(42)
HORIZON = 200      # hyperperiod of PERIODS
RUNS = 200

def ll_bound(n):
    return n * (2 ** (1 / n) - 1)

rms_bad, edf_bad = 0, 0
for _ in range(RUNS):
    n = int(rng.integers(2, 7))
    # RMS check: U just under the L&L bound -> must have zero misses
    ts = make_taskset(n, 0.98 * ll_bound(n), rng)
    if metrics(simulate(ts, "RMS", HORIZON))["missed"] > 0:
        rms_bad += 1
    # EDF check: U just under 1 -> must have zero misses
    ts = make_taskset(n, 0.99, rng)
    if metrics(simulate(ts, "EDF", HORIZON))["missed"] > 0:
        edf_bad += 1

print(f"RMS below L&L bound, sets with misses: {rms_bad}/{RUNS}  (expect 0)")
print(f"EDF at U=0.99, sets with misses:       {edf_bad}/{RUNS}  (expect 0)")

# sanity: RMS above the bound should sometimes miss
over = 0
for _ in range(RUNS):
    ts = make_taskset(5, 0.95, rng)
    if metrics(simulate(ts, "RMS", HORIZON))["missed"] > 0:
        over += 1
print(f"RMS at U=0.95, sets with misses:       {over}/{RUNS}  (expect > 0)")