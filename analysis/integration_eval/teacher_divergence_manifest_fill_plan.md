# Teacher-divergence manifest fill plan

## Branch

exp/15x15-teacher-divergence-manifest-fill-plan

## Scope

Planning only.

No training, checkpoint save, C export, public benchmark, or promotion is run on this branch.

## Input manifest

Input:

- analysis/integration_eval/teacher_divergence_expanded_candidate_manifest.csv
- analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_report.md

Builder summary:

| metric | value |
|---|---:|
| total manifest rows | 362 |
| non-duplicate rows | 247 |
| duplicate rows | 115 |
| ready_full_schema | 25 |
| needs_board_join | 203 |
| needs_current_best_probe | 14 |
| skipped_invalid | 5 |

Bucket summary for non-duplicate rows:

| bucket | rows |
|---|---:|
| unknown_rank | 222 |
| protected_top10 | 15 |
| trainable_rank_11_50 | 7 |
| tail_rank_gt50 | 3 |

## Interpretation

The expanded manifest is not yet a training dataset.

Only the 25 canonical multi-suppress seed rows are ready for full diagnostics. The other rows are useful candidates, but most are missing either board information or current_best rank/prob/suppress fields.

The next stage should fill missing fields in a controlled order.

## Fill priority

### Priority 1: current_best probe for 14 board-ready rows

Status:

- needs_current_best_probe
- count: 14

These rows already have enough board/side/target information to run current_best policy diagnostics.

Required fill fields:

- before_target_rank
- before_target_prob
- current_best_direct_rc
- current_best_direct_move
- current_best top policy moves
- bucket assignment
- rank_prob_available

After rank/prob probe, run suppress build if suppress fields remain missing.

Reason this comes first:

- small row count;
- low risk;
- can quickly increase ready diagnostic rows beyond the canonical 25;
- does not require complicated board joins.

Expected next branch:

exp/15x15-teacher-divergence-current-best-probe-fill

### Priority 2: board join for 203 rows

Status:

- needs_board_join
- count: 203

These rows should not be probed until board state is recovered.

Required join fields:

- board
- board_hash
- current_player
- side_to_move
- source trace validation

Likely join keys:

- source
- game_number
- move_count
- case_id
- target_rc

Candidate join sources:

- analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json
- tracked retention datasets with board fields
- tracked failure snapshot JSONs, only after source-specific schema audit

Reason this comes second:

- large potential expansion;
- more schema ambiguity;
- needs careful source-specific join validation;
- wrong board joins would poison downstream rank/prob labels.

Expected next branch after priority 1:

exp/15x15-teacher-divergence-board-join-audit

### Priority 3: keep ready_full_schema canonical seed as eval reference

Status:

- ready_full_schema
- count: 25

These rows should remain the canonical reference set.

Use:

- regression/protection baseline;
- validation for future probe scripts;
- duplicate detection reference;
- no immediate retraining.

Important:

- do not reintroduce the protected split JSON as independent data;
- do not double-count duplicated margin/multisuppress rows.

### Priority 4: skipped_invalid rows stay excluded

Status:

- skipped_invalid
- count: 5

Action:

- keep in manifest with skip_reason;
- do not repair until source-specific need arises;
- do not train.

## No-training rule

Do not train until all of these are true:

1. ready_full_schema rows are significantly larger than 25;
2. protected_top10, trainable_rank_11_50, and tail_rank_gt50 buckets are separated;
3. duplicates are resolved;
4. board joins are validated;
5. current_best rank/prob probe is complete;
6. suppress candidates are built;
7. teacher_eval missing rows are either re-queried or excluded.

## Immediate next implementation

Implement current_best probe fill for the 14 `needs_current_best_probe` rows.

The implementation should:

1. read `teacher_divergence_expanded_candidate_manifest.csv`;
2. select non-duplicate rows with status `needs_current_best_probe`;
3. require board_available, side_available, and target_available;
4. run current_best policy inference only;
5. fill rank/prob/direct move fields;
6. assign rank bucket;
7. write a filled manifest candidate CSV and report;
8. not save checkpoint;
9. not train;
10. not export.

Expected outputs:

- analysis/integration_eval/teacher_divergence_current_best_probe_fill.csv
- analysis/integration_eval/teacher_divergence_current_best_probe_fill_report.md

## Decision

Proceed with current_best probe fill first.

No training.

No checkpoint.

No C export.

No public benchmark.

No promotion.
