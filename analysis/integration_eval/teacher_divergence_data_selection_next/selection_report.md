# Teacher-divergence data selection next audit

## Scope

- Data selection audit only.
- No training.
- No checkpoint read or write.
- No C export, no public benchmark, no promotion.

## Inputs

- base_dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json`
- split_dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_protected_train_11_50_weightcap3.json`
- forensics_csv: `analysis/integration_eval/b4c96_stagec_failure_forensics.csv`
- run1_summary: `analysis/integration_eval/b4c96_nosave_objective_ablation_run1/run1_summary.csv`
- run2_summary: `analysis/integration_eval/b4c96_tail_aware_nosave_ablation_run2/run2_summary.csv`
- stop_review: `analysis/integration_eval/b4c96_capacity_route_stop_review.md`

## Why this audit exists

The b4c96 capacity route is stopped. Pairing capacity with increased multi-suppress data was completed, but Stage C, run1, and run2 all failed.

The next safe step is not more b4c96 training. The next safe step is to classify teacher-divergence rows into train candidates, protected guards, tail guards, and quarantine rows.

## Counts

- base rows: 25
- manifest rows: 25
- train_candidate_review rows: 4
- strict_train_candidate rows: 4

## Recommended role counts

| role | rows |
|---|---:|
| protected_guard_holdout | 15 |
| quarantine_regression_sensitive | 3 |
| tail_guard_holdout | 3 |
| train_candidate_review | 4 |

## Risk counts

| risk | rows |
|---|---:|
| hard_guard | 18 |
| high | 3 |
| medium | 4 |

## Rank bucket counts

| rank_bucket | rows |
|---|---:|
| protected_top10 | 4 |
| protected_top3 | 5 |
| protected_top5 | 6 |
| tail_rank_gt50 | 3 |
| trainable_rank_11_50 | 7 |

## Candidate lists

### Strict train candidates
- `legacy_g4_m13` rank=21 flags=directionally_useful
- `legacy_g4_m23` rank=23 flags=directionally_useful
- `legacy_g5_m28` rank=17 flags=directionally_useful
- `legacy_g6_m17` rank=15 flags=directionally_useful

### All train-candidate review rows
- `legacy_g4_m13` role=train_candidate_review rank=21 risk=medium flags=directionally_useful
- `legacy_g4_m23` role=train_candidate_review rank=23 risk=medium flags=directionally_useful
- `legacy_g5_m28` role=train_candidate_review rank=17 risk=medium flags=directionally_useful
- `legacy_g6_m17` role=train_candidate_review rank=15 risk=medium flags=directionally_useful

### Quarantine rows
- `legacy_g2_m11` rank=12 flags=severe_core_regression;core_regressed;rank_regression;prob_regression
- `legacy_g2_m21` rank=47 flags=severe_core_regression;core_regressed;tail_regression;rank_regression;prob_regression
- `legacy_g5_m14` rank=17 flags=severe_core_regression;core_regressed;tail_regression;rank_regression;prob_regression

## Interpretation

This audit should not be treated as a final training dataset.

Rows marked as protected or tail guards should remain held out from ordinary training and used as gate/guard evidence.

Rows marked as quarantine should not be used for checkpoint-producing training without manual review because previous b4c96 forensics or ablations linked them to protected/tail instability.

Rows marked as train-candidate review are only candidates for the next materialization step.

## Decision

`TEACHER_DIVERGENCE_DATA_SELECTION_AUDIT_READY`

Recommended next step: manually review the train-candidate review rows and then materialize a conservative next dataset in a separate branch.
