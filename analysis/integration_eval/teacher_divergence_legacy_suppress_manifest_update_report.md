# Teacher-divergence legacy suppress manifest update

## Branch

`exp/15x15-teacher-divergence-legacy-suppress-manifest-update`

## Scope

- Merges 9 legacy trainable current_best probe/suppress fill rows into a new normalized manifest.
- Keeps status and bucket counts stable.
- Completes export schema for all `trainable_rank_11_50` rows.
- Does not modify the original round2 manifest in place.
- No training.
- No checkpoint save.
- No C export.
- No public benchmark.
- No promotion.

## Inputs

- manifest: `analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_with_suppress_round2.csv`
- legacy probe fill CSV: `analysis/integration_eval/teacher_divergence_legacy_trainable_current_best_probe_fill.csv`
- legacy suppress fill CSV: `analysis/integration_eval/teacher_divergence_legacy_trainable_suppress_fill.csv`

## Summary

| metric | value |
|---|---:|
| manifest rows | 362 |
| non-duplicate rows | 247 |
| legacy rows updated | 9 |
| trainable ready rows before | 44 |
| trainable export-schema-complete before | 35 |
| trainable ready rows after | 44 |
| trainable export-schema-complete after | 44 |

## Status counts after update

| status | rows |
|---|---:|
| ready_full_schema | 133 |
| skipped_invalid | 51 |
| needs_board_join | 41 |
| needs_rapfi_requery | 22 |

## Ready bucket counts after update

| ready_bucket | rows |
|---|---:|
| tail_rank_gt50 | 66 |
| trainable_rank_11_50 | 44 |
| protected_top10 | 23 |

## Updated legacy rows

| manifest_id | before_missing | target_action | suppress_rc | suppress_prob | suppress_count |
|---|---|---:|---|---:|---:|
| td_exp_00008 | `["target_action", "suppress_rc", "suppress_prob", "suppress_candidates_rcs", "suppress_candidates_probs"]` | 114 | `[5, 6]` | 0.4221777617931366 | 5 |
| td_exp_00009 | `["target_action", "suppress_rc", "suppress_prob", "suppress_candidates_rcs", "suppress_candidates_probs"]` | 142 | `[4, 2]` | 0.9029175639152527 | 5 |
| td_exp_00013 | `["target_action", "suppress_rc", "suppress_prob", "suppress_candidates_rcs", "suppress_candidates_probs"]` | 99 | `[4, 6]` | 0.4877963662147522 | 5 |
| td_exp_00015 | `["target_action", "suppress_rc", "suppress_prob", "suppress_candidates_rcs", "suppress_candidates_probs"]` | 142 | `[3, 7]` | 0.44126200675964355 | 5 |
| td_exp_00019 | `["target_action", "suppress_rc", "suppress_prob", "suppress_candidates_rcs", "suppress_candidates_probs"]` | 142 | `[6, 6]` | 0.47136619687080383 | 5 |
| td_exp_00021 | `["target_action", "suppress_rc", "suppress_prob", "suppress_candidates_rcs", "suppress_candidates_probs"]` | 170 | `[4, 5]` | 0.38212400674819946 | 5 |
| td_exp_00024 | `["target_action", "suppress_rc", "suppress_prob", "suppress_candidates_rcs", "suppress_candidates_probs"]` | 98 | `[9, 4]` | 0.5200085639953613 | 5 |
| td_exp_00055 | `["target_action", "suppress_rc", "suppress_prob", "suppress_candidates_rcs", "suppress_candidates_probs"]` | 114 | `[10, 9]` | 0.37028923630714417 | 5 |
| td_exp_00058 | `["target_action", "suppress_rc", "suppress_prob", "suppress_candidates_rcs", "suppress_candidates_probs"]` | 83 | `[8, 8]` | 0.3607815206050873 | 5 |

## Output

- normalized manifest: `analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_legacy_suppress_normalized.csv`
- report: `analysis/integration_eval/teacher_divergence_legacy_suppress_manifest_update_report.md`

## Decision

The normalized manifest is ready for a 44-row dry-run export validation.

No training.

No checkpoint.

No C export.

No public benchmark.

No promotion.
