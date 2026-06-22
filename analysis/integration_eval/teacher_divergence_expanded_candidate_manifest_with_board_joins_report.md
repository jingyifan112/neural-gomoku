# Teacher-divergence expanded manifest with board joins report

## Branch

`exp/15x15-teacher-divergence-manifest-update-with-board-joins`

## Scope

- Manifest update only.
- Merges conservative board join fill results.
- Does not run current_best probe.
- Does not run Rapfi requery.
- Does not build suppress candidates.
- No training.
- No checkpoint save.
- No C export.
- No public benchmark.
- No promotion.

## Inputs

- base manifest: `analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_with_fills.csv`
- board join fill: `analysis/integration_eval/teacher_divergence_board_join_fill.csv`

## Update summary

| metric | value |
|---|---:|
| total manifest rows | 362 |
| non-duplicate rows | 247 |
| update log rows | 203 |
| applied board joins | 162 |
| retained unfilled rows | 41 |

## Status counts before

| status | rows |
|---|---:|
| needs_board_join | 203 |
| duplicate | 115 |
| ready_full_schema | 36 |
| skipped_invalid | 8 |

## Status counts after

| status | rows |
|---|---:|
| needs_current_best_probe | 140 |
| duplicate | 115 |
| needs_board_join | 41 |
| ready_full_schema | 36 |
| needs_rapfi_requery | 22 |
| skipped_invalid | 8 |

## Non-duplicate status counts after

| status | rows |
|---|---:|
| needs_current_best_probe | 140 |
| needs_board_join | 41 |
| ready_full_schema | 36 |
| needs_rapfi_requery | 22 |
| skipped_invalid | 8 |

## Update actions

| action | rows |
|---|---:|
| applied_board_join | 162 |
| retained_unfilled_no_join | 21 |
| retained_unfilled_ambiguous_join | 20 |

## Join strength for applied rows

| join_strength | rows |
|---|---:|
| game_move | 157 |
| game_move_target | 5 |

## Interpretation

The manifest now records conservative board joins for unique-join rows.

Most newly joined rows now require current_best rank/prob probing. They are not training-ready.

Rows retained as no_join or ambiguous_join remain incomplete and must not be included in future training datasets.

## Decision

No current_best probe on this branch.

No Rapfi requery on this branch.

No suppress build on this branch.

No training.

No checkpoint.

No C export.

No public benchmark.

No promotion.
