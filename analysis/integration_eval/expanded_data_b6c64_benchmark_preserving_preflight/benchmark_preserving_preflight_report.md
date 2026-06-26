# Expanded b6c64 benchmark-preserving preflight

- decision: `BENCHMARK_PRESERVING_REPAIR_REQUIRED`
- promotion_readiness: `NOT_PROMOTION_READY`
- route: `exp/15x15-expanded-data-capacity-real-public-benchmark`

## Purpose

This preflight records why the expanded-capacity/data candidate must move to benchmark-preserving training before any further candidate attempt.

## Inputs

- expanded dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_conservative_plus_generated_tail_guards_plus_generated_train_candidates_dryrun.json`
- candidate checkpoint: `checkpoints/probes/15x15_expanded_data_b6c64_public_benchmark_candidate.pt`
- candidate C weights: `weights/15x15_expanded_data_b6c64_public_benchmark_candidate_weights.bin`
- tactical-mid game summary: `analysis/integration_eval/expanded_data_b6c64_public_benchmark_candidate/tactical_mid_game_summary.csv`
- public score ladder: `analysis/public_benchmark_eval/gomocup2026_score_ladder_summary.csv`

## Dataset counts

| bucket | count |
|---|---:|
| `samples` | 12 |
| `protected_eval_samples` | 15 |
| `tail_eval_samples` | 15 |
| `quarantine_samples` | 3 |

## Public benchmark comparison

| Model | Engine | Opponent | W | L | D | Score | Score rate |
|---|---|---|---:|---:|---:|---:|---:|
| Before model | `neural_current_best_mcts16` | `tactical_mid` | 6 | 16 | 2 | 7.0/24 | 0.292 |
| After expanded candidate | `expanded_data_b6c64_mcts16` | `tactical_mid` | 2 | 22 | 0 | 2.0/24 | 0.083 |
| Strong reference | `rapfi_full` | `tactical_mid` | 24 | 0 | 0 | 24.0/24 | 1.000 |

## Regression

- after_minus_before_score: `-5.0`
- after_minus_before_score_rate: `-0.209`
- after_minus_strong_score: `-22.0`
- after_minus_strong_score_rate: `-0.917`

## Gate thresholds for next attempt

- no-regression threshold: `>= 7.0/24`
- improvement target: `> 7.0/24`, operational target `>= 8.0/24`

## Recommended next step

Build a benchmark-preserving anchor dry-run before another train. The next candidate should train teacher-divergence rows with CE, while using public benchmark, protected, and tail rows as KL anchors.

Required next-candidate gate:

- tactical_mid public benchmark must be at least `7.0/24` to avoid regression.
- protected/tail guard metrics must not regress.
- no promotion/current_best overwrite from this candidate route.

## Safety

- This report does not promote any checkpoint.
- This report does not overwrite `current_best`.
- The candidate benchmark is evidence only.
