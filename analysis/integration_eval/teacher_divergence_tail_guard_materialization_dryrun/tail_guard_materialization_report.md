# Teacher-divergence tail guard materialization dry-run

## Scope

- Materialization dry-run only.
- Generated tail candidates are added only to `tail_eval_samples`.
- `samples` train rows are unchanged.
- No training.
- No checkpoint save.
- No C export, no public benchmark, no promotion.

## Inputs

- base dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_conservative_selection_next.json`
- candidate source: `analysis/integration_eval/teacher_divergence_tail_guard_candidate_generation/tail_guard_candidate_source.json`
- max new tail guards: `12`

## Counts

| group | before | after | delta |
|---|---:|---:|---:|
| samples | 4 | 4 | 0 |
| protected_eval_samples | 15 | 15 | 0 |
| tail_eval_samples | 3 | 15 | 12 |
| quarantine_samples | 3 | 3 | 0 |

## Review decisions

| decision | count |
|---|---:|
| accepted_but_over_max_new_tail_guard_cap | 4 |
| accepted_tail_eval_heldout | 12 |
| board_target_identity_already_exists | 1 |

## Accepted rows

| case_id | game | move | side | target_rc | rank | prob | source_field |
|---|---:|---:|---|---|---:|---:|---|
| `tailgen_g2_m7_t0_9_5` | 2 | 7 | white | `[9, 5]` | 200 | 3.91636e-06 | `direct` |
| `tailgen_g1_m6_t0_9_7` | 1 | 6 | black | `[9, 7]` | 172 | 1.09029e-05 | `direct` |
| `tailgen_g2_m9_t0_9_5` | 2 | 9 | white | `[9, 5]` | 170 | 1.34869e-05 | `direct` |
| `tailgen_g4_m23_t2_12_9` | 4 | 23 | white | `[12, 9]` | 166 | 1.2981e-05 | `policy_safety` |
| `tailgen_g5_m28_t1_7_3` | 5 | 28 | black | `[7, 3]` | 161 | 1.44085e-05 | `direct` |
| `tailgen_g5_m30_t1_7_3` | 5 | 30 | black | `[7, 3]` | 152 | 1.50188e-05 | `direct` |
| `tailgen_g5_m16_t0_7_5` | 5 | 16 | black | `[7, 5]` | 140 | 7.15315e-05 | `direct` |
| `tailgen_g5_m10_t0_10_7` | 5 | 10 | black | `[10, 7]` | 116 | 0.000317205 | `direct` |
| `tailgen_g2_m21_t1_2_4` | 2 | 21 | white | `[2, 4]` | 108 | 4.50069e-06 | `direct` |
| `tailgen_g4_m17_t2_10_6` | 4 | 17 | white | `[10, 6]` | 104 | 2.84858e-06 | `policy_safety` |
| `tailgen_g1_m40_t1_12_6` | 1 | 40 | black | `[12, 6]` | 97 | 9.62003e-05 | `policy_safety` |
| `tailgen_g1_m4_t0_7_6` | 1 | 4 | black | `[7, 6]` | 82 | 0.000451137 | `direct` |

## Decision

`TAIL_GUARD_MATERIALIZATION_DRYRUN_TARGET_MET`

## Final note

This dry-run does not authorize training, checkpoint save, C export, public benchmark, promotion, or current_best overwrite.
