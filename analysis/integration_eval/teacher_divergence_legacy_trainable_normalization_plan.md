# Teacher-divergence legacy trainable normalization plan

## Branch

`exp/15x15-teacher-divergence-legacy-trainable-normalization-plan`

## Scope

- Audits the 9 legacy `trainable_rank_11_50` rows excluded from round2 dry-run export.
- Determines which export-schema fields are missing.
- Determines whether suppress fields can be reconstructed from existing top-policy fields.
- Does not update the manifest.
- Does not export a training dataset.
- Does not train.
- Does not save a checkpoint.
- Does not C export.
- Does not run public benchmark.
- Does not promote.

## Inputs

- manifest: `analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_with_suppress_round2.csv`
- dry-run JSON: `analysis/integration_eval/teacher_divergence_round2_trainable_dryrun_dataset.json`

## Summary

| metric | value |
|---|---:|
| legacy trainable rows needing normalization | 9 |
| rows with reconstructable suppress from top-policy | 0 |
| rows not reconstructable from top-policy | 9 |

## Proposed actions

| proposed_action | rows |
|---|---:|
| manual_schema_review:missing_top_policy_lists | 9 |

## Missing required fields

| field | rows_missing |
|---|---:|
| target_action | 9 |
| suppress_rc | 9 |
| suppress_prob | 9 |
| suppress_candidates_rcs | 9 |
| suppress_candidates_probs | 9 |

## Source counts

| source | rows |
|---|---:|
| canonical_full_schema_seed | 7 |
| retention_candidate_dataset | 2 |

## Row-level plan

| manifest_id | case_id | missing_required_fields | can_reconstruct_suppress | proposed_action |
|---|---|---|---:|---|
| td_exp_00008 | legacy_g2_m11 | `["target_action", "suppress_rc", "suppress_prob", "suppress_candidates_rcs", "suppress_candidates_probs"]` | 0 | manual_schema_review:missing_top_policy_lists |
| td_exp_00009 | legacy_g2_m21 | `["target_action", "suppress_rc", "suppress_prob", "suppress_candidates_rcs", "suppress_candidates_probs"]` | 0 | manual_schema_review:missing_top_policy_lists |
| td_exp_00013 | legacy_g4_m13 | `["target_action", "suppress_rc", "suppress_prob", "suppress_candidates_rcs", "suppress_candidates_probs"]` | 0 | manual_schema_review:missing_top_policy_lists |
| td_exp_00015 | legacy_g4_m23 | `["target_action", "suppress_rc", "suppress_prob", "suppress_candidates_rcs", "suppress_candidates_probs"]` | 0 | manual_schema_review:missing_top_policy_lists |
| td_exp_00019 | legacy_g5_m14 | `["target_action", "suppress_rc", "suppress_prob", "suppress_candidates_rcs", "suppress_candidates_probs"]` | 0 | manual_schema_review:missing_top_policy_lists |
| td_exp_00021 | legacy_g5_m28 | `["target_action", "suppress_rc", "suppress_prob", "suppress_candidates_rcs", "suppress_candidates_probs"]` | 0 | manual_schema_review:missing_top_policy_lists |
| td_exp_00024 | legacy_g6_m17 | `["target_action", "suppress_rc", "suppress_prob", "suppress_candidates_rcs", "suppress_candidates_probs"]` | 0 | manual_schema_review:missing_top_policy_lists |
| td_exp_00055 | holdout_candidate_e_g2_m17_white_last_9_9_target_block_left_7_9_over_live_final_9_10 | `["target_action", "suppress_rc", "suppress_prob", "suppress_candidates_rcs", "suppress_candidates_probs"]` | 0 | manual_schema_review:missing_top_policy_lists |
| td_exp_00058 | holdout_candidate_e_g2_m13_white_target_5_8_over_8_8 | `["target_action", "suppress_rc", "suppress_prob", "suppress_candidates_rcs", "suppress_candidates_probs"]` | 0 | manual_schema_review:missing_top_policy_lists |

## Recommended next step

If all 9 rows are reconstructable from existing top-policy fields, run a dedicated normalization fill branch that writes suppress fields for only these 9 legacy rows, then rerun dry-run export expecting 44 exportable samples.

If any row is not reconstructable, rerun current_best probe/suppress build only for those specific legacy rows before updating the manifest.

## Outputs

- `analysis/integration_eval/teacher_divergence_legacy_trainable_normalization_plan.csv`
- `analysis/integration_eval/teacher_divergence_legacy_trainable_normalization_plan.md`

## Decision

No manifest update.

No training.

No checkpoint.

No C export.

No public benchmark.

No promotion.
