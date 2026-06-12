# Gomocup 2026 Public Benchmark Final Score Report

## Setup

- Opening suite: `gomocup2026_freestyle15_public_openings`
- Board size: `15x15`
- Rule: freestyle Gomoku, rule `0`
- Openings: `12`
- Match mode: repeat openings, both color assignments
- Games per engine/baseline pair: `24`

## Final score table

| Baseline | Engine | W | L | D | Score | Score rate |
|---|---|---:|---:|---:|---:|---:|
| `random` | `rapfi_full` | 24 | 0 | 0 | 24.0 / 24 | 1.000 |
| `random` | `neural_current_best_mcts32` | 24 | 0 | 0 | 24.0 / 24 | 1.000 |
| `tactical_lite` | `rapfi_full` | 24 | 0 | 0 | 24.0 / 24 | 1.000 |
| `tactical_lite` | `neural_current_best_mcts32` | 23 | 1 | 0 | 23.0 / 24 | 0.958 |
| `tactical_mid` | `rapfi_full` | 24 | 0 | 0 | 24.0 / 24 | 1.000 |
| `tactical_mid` | `neural_current_best_mcts16` | 6 | 16 | 2 | 7.0 / 24 | 0.292 |
| `tactical_plus` | `rapfi_full` | 24 | 0 | 0 | 24.0 / 24 | 1.000 |
| `tactical_plus` | `neural_current_best_mcts32` | 1 | 23 | 0 | 1.0 / 24 | 0.042 |
| `tactical_plus` | `neural_current_best_mcts16` | 2 | 20 | 2 | 3.0 / 24 | 0.125 |
| `tactical_plus` | `neural_current_best_mcts8` | 0 | 22 | 2 | 1.0 / 24 | 0.042 |
| `rapfi_fast_depth1` | `rapfi_full` | 24 | 0 | 0 | 24.0 / 24 | 1.000 |
| `rapfi_fast_depth1` | `neural_current_best_mcts32` | 0 | 24 | 0 | 0.0 / 24 | 0.000 |

## Main findings

- `random` is too weak: both neural and `rapfi_full` score perfectly.
- `tactical_lite` gives only light resolution: neural scores `23.0/24`, while `rapfi_full` scores `24.0/24`.
- `tactical_mid` is currently the most useful benchmark for model iteration: neural gets `7.0/24`, while `rapfi_full` gets `24.0/24`.
- `tactical_plus` is too hard but still informative for speed settings: `mcts16` is best among tested neural settings with `3.0/24`.
- `rapfi_fast_depth1` is too strong as a scoring baseline: neural gets `0.0/24`, while `rapfi_full` gets `24.0/24`.

## Current best neural setting by baseline

| Baseline | Best neural setting | Score | Score rate |
|---|---|---:|---:|
| `random` | `neural_current_best_mcts32` | 24.0 / 24 | 1.000 |
| `tactical_lite` | `neural_current_best_mcts32` | 23.0 / 24 | 0.958 |
| `tactical_mid` | `neural_current_best_mcts16` | 7.0 / 24 | 0.292 |
| `tactical_plus` | `neural_current_best_mcts16` | 3.0 / 24 | 0.125 |
| `rapfi_fast_depth1` | `neural_current_best_mcts32` | 0.0 / 24 | 0.000 |

## Interpretation

The public benchmark scoring goal has been completed for the current neural model against the available baselines and the `rapfi_full` reference.

The main unresolved issue is not whether scoring has been done, but benchmark resolution:

- Easy baselines saturate near `1.000`.
- Strong baselines saturate near `0.000`.
- `tactical_mid` currently gives the clearest non-saturated signal for neural progress.

No training result is included in this report. The separate tactical-mid diagnostics explain why the current model loses many `tactical_mid` games, but they are not required for the benchmark score table.
