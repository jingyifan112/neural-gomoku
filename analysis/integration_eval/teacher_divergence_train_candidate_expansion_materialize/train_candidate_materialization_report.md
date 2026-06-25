# Teacher-divergence train candidate expansion materialization dry-run

## Scope

- Train candidate materialization dry-run only.
- Accepted rows are added only to `samples`.
- `protected_eval_samples`, `tail_eval_samples`, and `quarantine_samples` are unchanged.
- No training.
- No checkpoint save.
- No C export, no public benchmark, no promotion.

## Inputs

- base dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_conservative_plus_generated_tail_guards_dryrun.json`
- source manifest: `analysis/integration_eval/teacher_divergence_expansion_source_audit_next/source_candidate_manifest.csv`
- max new train candidates: `15`
- rank band: `11` to `50`

## Counts

| group | before | after | delta |
|---|---:|---:|---:|
| samples | 4 | 4 | 0 |
| protected_eval_samples | 15 | 15 | 0 |
| tail_eval_samples | 15 | 15 | 0 |
| quarantine_samples | 3 | 3 | 0 |

## Review decisions

| decision | count |
|---|---:|
| case_id_already_exists | 11 |
| rank_outside_train_band | 15 |

## Accepted rows

| case_id | rank | prob | source_path | source_json_path |
|---|---:|---:|---|---|
| _none_ |  |  |  |  |

## Decision

`TRAIN_CANDIDATE_MATERIALIZATION_DRYRUN_NO_ACCEPTED_ROWS`

## Final note

This dry-run does not authorize training, checkpoint save, C export, public benchmark, promotion, or current_best overwrite.
