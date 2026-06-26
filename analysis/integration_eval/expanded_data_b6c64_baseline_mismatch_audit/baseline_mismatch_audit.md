# Expanded b6c64 public benchmark baseline mismatch audit

- decision: `BASELINE_MISMATCH_REQUIRES_RUNNER_AUDIT`
- no training
- no checkpoint
- no promotion/current_best overwrite

## Score comparison

| source | engine | opponent | W | L | D | score | score rate |
|---|---|---|---:|---:|---:|---:|---:|
| archived score ladder | `neural_current_best_mcts16` | `tactical_mid` | 6 | 16 | 2 | 7.0/24 | 0.292 |
| current local before rerun | `neural_current_best_mcts16` | `tactical_mid` | 2 | 22 | 0 | 2.0/24 | 0.083 |
| current local after candidate | `expanded_data_b6c64_mcts16` | `tactical_mid` | 2 | 22 | 0 | 2.0/24 | 0.083 |
| archived strong reference | `rapfi_full` | `tactical_mid` | 24 | 0 | 0 | 24.0/24 | 1.000 |

## Interpretation

The current local before rerun did not reproduce the archived current-best tactical_mid score. Do not use the archived 7.0/24 threshold as if it came from the current local runner until the runner/weights mismatch is resolved.

## Runner paths

- before runner: `analysis/public_benchmark_eval/local_runs/run_neural_current_best_mcts16.sh`
- after runner: `analysis/public_benchmark_eval/local_runs/run_neural_expanded_data_b6c64_mcts16.sh`

## Next step

Inspect the before runner weights/binary. If it points to the b6c64 capacity checkpoint rather than the archived current-best model, then the old 7.0/24 score is not an apples-to-apples local baseline for the current anchor dry-run.
