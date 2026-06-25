# Teacher-divergence generated train candidate materialization dry-run

## Scope

- Generated train candidate materialization dry-run only.
- Accepted rows are added only to `samples`.
- `protected_eval_samples`, `tail_eval_samples`, and `quarantine_samples` are unchanged.
- No training.
- No checkpoint save.
- No C export, no public benchmark, no promotion.

## Inputs

- base dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_conservative_plus_generated_tail_guards_dryrun.json`
- candidate source: `analysis/integration_eval/teacher_divergence_train_candidate_generation/train_candidate_source.json`
- max new train candidates: `8`
- min new train candidates: `8`
- rank band: `11` to `50`

## Counts

| group | before | after | delta |
|---|---:|---:|---:|
| samples | 4 | 12 | 8 |
| protected_eval_samples | 15 | 15 | 0 |
| tail_eval_samples | 15 | 15 | 0 |
| quarantine_samples | 3 | 3 | 0 |

## Review decisions

| decision | count |
|---|---:|
| accepted_generated_train_candidate | 8 |

## Accepted rows

| case_id | game | move | side | target_rc | rank | prob | source_field |
|---|---:|---:|---|---|---:|---:|---|
| `traingen_g5_m30_t2_4_9` | 5 | 30 | black | `[4, 9]` | 48 | 0.00082598 | `policy_safety` |
| `traingen_g6_m17_t0_7_9` | 6 | 17 | white | `[7, 9]` | 47 | 0.000386197 | `direct` |
| `traingen_g1_m38_t1_12_8` | 1 | 38 | black | `[12, 8]` | 46 | 0.000913961 | `direct` |
| `traingen_g4_m21_t1_10_8` | 4 | 21 | white | `[10, 8]` | 44 | 0.00013093 | `direct` |
| `traingen_g4_m13_t0_8_4` | 4 | 13 | white | `[8, 4]` | 23 | 0.000450608 | `direct` |
| `traingen_g5_m8_t1_8_5` | 5 | 8 | black | `[8, 5]` | 20 | 0.00317801 | `policy_safety` |
| `traingen_g5_m28_t2_5_11` | 5 | 28 | black | `[5, 11]` | 18 | 0.00423876 | `policy_safety` |
| `traingen_g5_m30_t0_9_9` | 5 | 30 | black | `[9, 9]` | 17 | 0.00433257 | `previous_rapfi_bestline` |

## Decision

`GENERATED_TRAIN_CANDIDATE_MATERIALIZATION_DRYRUN_TARGET_MET`

## Final note

This dry-run does not authorize training, checkpoint save, C export, public benchmark, promotion, or current_best overwrite.
