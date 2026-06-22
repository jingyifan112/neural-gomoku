# Teacher-divergence normalized trainer compatibility audit

## Branch

`exp/15x15-teacher-divergence-normalized-trainer-compat-audit`

## Scope

- Audits compatibility between the 44-row legacy-normalized dry-run dataset and the existing policy-margin trainer.
- Confirms the dataset uses single-suppress schema: one `target_rc` and one `suppress_rc` per sample.
- Confirms protected top10 and tail rank > 50 rows are excluded from the trainable dry-run dataset.
- Proposes isolated output paths for a later tiny training probe.
- Does not train.
- Does not save a checkpoint.
- Does not C export.
- Does not run public benchmark.
- Does not promote.

## Inputs

- dataset JSON: `analysis/integration_eval/teacher_divergence_round2_trainable_dryrun_dataset_legacy_normalized.json`
- normalized manifest: `analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_legacy_suppress_normalized.csv`
- trainer: `scripts/train_rapfi_teacher_policy_margin.py`

## Summary

| metric | value |
|---|---:|
| dataset samples | 44 |
| legacy-normalized samples | 9 |
| manifest trainable ready rows | 44 |
| audit PASS | 20 |
| audit WARN | 0 |
| audit FAIL | 0 |

## Audit results

| audit_item | status | detail |
|---|---|---|
| dataset_sample_count | PASS | sample_count=44 |
| dataset_not_training_metadata | PASS | metadata.not_training is true |
| dataset_required_sample_fields | PASS | all 44 samples contain required single-suppress fields |
| dataset_manifest_id_unique | PASS | unique_ids=44 |
| legacy_rows_in_dataset | PASS | all 9 legacy-normalized rows are present |
| manifest_trainable_ready_count | PASS | trainable_ready=44 |
| dataset_manifest_id_match | PASS | dataset sample IDs exactly match manifest trainable ready IDs |
| trainer_has_samples_loader | PASS | found expected trainer marker |
| trainer_references_target_rc | PASS | found expected trainer marker |
| trainer_references_suppress_rc | PASS | found expected trainer marker |
| trainer_has_margin_tensor_builder | PASS | found expected trainer marker |
| trainer_looks_single_suppress | PASS | found expected trainer marker |
| trainer_has_checkpoint_output_arg | PASS | found expected trainer marker |
| trainer_has_metrics_or_logging | PASS | found expected trainer marker |
| multi_suppress_not_consumed | PASS | trainer appears compatible with one suppress_rc per sample; suppress_candidates can remain audit metadata |
| safe_checkpoint_path | PASS | checkpoints/15x15_teacher_divergence_round2_policy_margin_probe.pt |
| safe_metrics_path | PASS | analysis/integration_eval/teacher_divergence_round2_policy_margin_probe_train_metrics.csv |
| protected_top10_excluded | PASS | dataset selects only trainable_rank_11_50 |
| tail_rank_gt50_excluded | PASS | dataset selects only trainable_rank_11_50 |
| no_training_executed | PASS | audit only; no trainer invocation |

## Source counts

| source | rows |
|---|---:|
| retention_candidate_dataset | 20 |
| retention_metadata_manifest | 10 |
| canonical_full_schema_seed | 7 |
| corpus8_teacher_candidate_csv | 7 |

## Suppress candidate count distribution

| suppress candidate count | rows |
|---|---:|
| 5 | 44 |

## Target rank distribution

| target rank | rows |
|---|---:|
| 11 | 1 |
| 12 | 1 |
| 13 | 1 |
| 14 | 6 |
| 15 | 1 |
| 17 | 2 |
| 18 | 5 |
| 21 | 1 |
| 23 | 8 |
| 39 | 5 |
| 43 | 6 |
| 47 | 7 |

## Later training probe constraints

Use isolated output paths only:

- checkpoint: `checkpoints/15x15_teacher_divergence_round2_policy_margin_probe.pt`
- metrics: `analysis/integration_eval/teacher_divergence_round2_policy_margin_probe_train_metrics.csv`

Do not overwrite `checkpoints/15x15_current_best.pt`.

Do not export C weights from this probe.

Do not run public benchmark from this probe.

Do not promote this probe unless a later validation branch explicitly supports it.

## Recommended next step

Run a tiny training dry-run/probe branch only after this compatibility audit is pushed. The first training probe should be intentionally small and isolated, with a new checkpoint path and metrics path.

## Outputs

- `analysis/integration_eval/teacher_divergence_normalized_trainer_compat_summary.csv`
- `analysis/integration_eval/teacher_divergence_normalized_trainer_compat_audit.md`

## Decision

Compatibility audit only.

No training.

No checkpoint.

No C export.

No public benchmark.

No promotion.
