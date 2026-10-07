# Reproducibility

## Extended run

Command (from repo root):

    python -m harness.cli --config harness/configs/extended.json --out results/extended --prefix extended --extended --baseline-csv results/baseline.csv

Master seed: 2026
Per-task-set seed: SeedSequence([2026, round(1000*U), i]) for set i at utilization U
Critical-section RNG: random.Random seeded from "2026|U|set|n_resources|cs_per_job"

Environment:
- Python 3.12.3
- numpy 2.4.4
- pandas 3.0.2
- matplotlib 3.10.8

Settings:
- N = 50 task sets per condition
- 6 tasks per set
- 13-value period grid
- Placeholder L0 = 0.01 ms per message
