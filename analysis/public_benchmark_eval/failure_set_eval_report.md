# Fixed Rapfi Failure-Set Evaluation

## Purpose

This report records the first position-level evaluation after moving away from match-only neural-vs-Rapfi evaluation.

This is not yet a true external public benchmark. It is a small fixed Rapfi failure-set smoke evaluation based on previously extracted 15x15 failure positions.

## Input set

- Source positions: `analysis/rapfi_failure_board_snapshots.json`
- Labels: `analysis/rapfi_failure_set_labeled.csv`
- Evaluated positions: 7
- Immediate/block-required positions: 5
- Board size: 15x15
- Win length: 5

## Models evaluated

| Model | CSV |
|---|---|
| current_best | `analysis/public_benchmark_eval/current_best_failure_set_eval.csv` |
| candidate_g_teacher_policy | `analysis/public_benchmark_eval/candidate_g_failure_set_eval.csv` |
| candidate_h_value_ranking | `analysis/public_benchmark_eval/candidate_h_failure_set_eval.csv` |

## Summary

| Model | Positions | Block-required cases | Direct blocks | Direct block rate | Average model value |
|---|---:|---:|---:|---:|---:|
| current_best | 7 | 5 | 0 | 0.0 | -0.274112 |
| candidate_g_teacher_policy | 7 | 5 | 2 | 0.4 | -0.792015 |
| candidate_h_value_ranking | 7 | 5 | 2 | 0.4 | -0.781513 |

## Per-position observations

### Improved by candidate G/H

- `legacy_g1_m44`: current_best chose `10,7`; candidate G/H chose the required block `2,10`.
- `legacy_g2_m33`: current_best chose `7,5`; candidate G/H chose one required block `9,6`.

### Still missed by candidate G/H

- `legacy_g1_m46`: expected block `4,12`; candidate G/H chose `10,7`.
- `legacy_g1_m48`: expected block `3,11` or `8,11`; candidate G/H chose `10,7`.
- `legacy_g2_m29`: expected block `4,9`; candidate G/H chose `3,4`.

## Interpretation

The candidate G/H checkpoints improve direct-policy behavior on the small labeled Rapfi failure set, increasing direct block rate from 0/5 to 2/5.

However, the set is very small and targeted. This result is useful as a smoke test, but it is not sufficient for promotion and should not be presented as a full public benchmark.

The next evaluation step should be a larger fixed position-level benchmark with Rapfi teacher scores, measuring:

1. Rapfi best move / score.
2. Neural model direct move.
3. Rapfi score for the neural move.
4. Score gap.
5. Top-k agreement.
