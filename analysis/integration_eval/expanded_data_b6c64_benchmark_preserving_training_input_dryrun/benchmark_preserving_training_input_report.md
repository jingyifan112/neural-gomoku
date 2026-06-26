# Expanded b6c64 benchmark-preserving training input dry-run

- decision: `BENCHMARK_PRESERVING_TRAINING_INPUT_DRYRUN_READY`
- no training
- no checkpoint
- no export
- no promotion/current_best overwrite

## Baseline policy

| baseline | score | score rate | role |
|---|---:|---:|---|
| current local b6c64 baseline | 2.0/24 | 0.083 | no-regression gate |
| expanded candidate | 2.0/24 | 0.083 | current candidate evidence |
| archived current-best | 7.0/24 | 0.292 | aspirational recovery target |

## Training input groups

| group | count | loss | weight |
|---|---:|---|---:|
| `teacher_divergence_ce_train` | 12 | `cross_entropy_teacher_target` | 1.00 |
| `public_tactical_mid_kl_anchor_train` | 48 | `kl_to_reference_b6c64_policy` | 0.20 |
| `protected_top10_kl_guard` | 15 | `kl_to_reference_b6c64_policy` | 0.35 |
| `tail_rank_kl_guard` | 15 | `kl_to_reference_b6c64_policy` | 0.35 |

## Diagnostic-only groups

| group | count | use |
|---|---:|---|
| `after_candidate_regression_diagnostic_only` | 192 | not used for training |

## Source counts

| source bucket | count |
|---|---:|
| `teacher_samples` | 12 |
| `protected_eval_samples` | 15 |
| `tail_eval_samples` | 15 |
| `quarantine_samples` | 3 |
| `before_public_kl_anchor_pool` | 192 |
| `before_public_kl_anchor_selected` | 48 |
| `after_diagnostic_anchor_pool` | 192 |

## Next step

Write a benchmark-preserving training adapter dry-run. It must first run in dry-run/no-save mode, using CE for teacher-divergence rows and KL-to-reference for selected public/protected/tail anchors.

Required gates for any later saved candidate:

- current-local tactical_mid score must remain `>= 2.0/24`.
- archived-current-best `7.0/24` is an aspirational recovery target, not a currently reproduced local baseline.
- no promotion/current_best overwrite from this route.

## Artifacts

- dry-run input JSON: `analysis/integration_eval/expanded_data_b6c64_benchmark_preserving_training_input_dryrun/benchmark_preserving_training_input_dryrun.json`
- manifest CSV: `analysis/integration_eval/expanded_data_b6c64_benchmark_preserving_training_input_dryrun/benchmark_preserving_training_input_manifest.csv`
- summary JSON: `analysis/integration_eval/expanded_data_b6c64_benchmark_preserving_training_input_dryrun/benchmark_preserving_training_input_summary.json`
