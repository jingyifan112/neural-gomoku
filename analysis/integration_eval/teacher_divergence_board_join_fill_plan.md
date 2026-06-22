# Teacher-divergence board join fill plan

## Branch

exp/15x15-teacher-divergence-board-join-fill-plan

## Scope

Planning only.

No manifest update, current_best probe, suppress build, training, checkpoint save, C export, public benchmark, or promotion is run on this branch.

## Input

Previous branch:

exp/15x15-teacher-divergence-board-join-audit

Input artifacts:

- analysis/integration_eval/teacher_divergence_board_join_audit.csv
- analysis/integration_eval/teacher_divergence_board_join_audit.md

Board join audit summary:

| metric | value |
|---|---:|
| needs_board_join rows | 203 |
| board source records | 89 |
| unique_join | 162 |
| ambiguous_join | 20 |
| no_join | 21 |

Join strength summary:

| join_strength | rows |
|---|---:|
| game_move | 158 |
| game_move_target | 24 |
| none | 21 |

## Interpretation

The board join audit found many possible joins, but not all joins should be applied automatically.

A wrong board join would corrupt all downstream labels:

- current_best rank/prob;
- current_best direct move;
- suppress candidates;
- bucket assignment;
- future training/eval split.

Therefore board join fill must be conservative.

## Fill policy

### Automatically fill: unique_join only

A row is eligible for automatic board join fill only if:

1. join_status == unique_join;
2. unique_board_hash_count == 1;
3. matched_board_hash is non-empty;
4. match_count >= 1;
5. matched_sources is non-empty.

Expected maximum auto-fill candidates:

- 162 rows.

### Exclude from automatic fill: ambiguous_join

Rows with:

- join_status == ambiguous_join

must not be filled automatically.

Reason:

- multiple board hashes matched;
- source-specific disambiguation is required.

Expected count:

- 20 rows.

### Keep incomplete: no_join

Rows with:

- join_status == no_join

must remain needs_board_join.

Reason:

- no candidate board was found in tracked board sources.

Expected count:

- 21 rows.

## Join strength policy

### game_move_target

This is the strongest join class in the current audit.

Rule:

- allow automatic fill if join_status == unique_join.

Reason:

- game_number + move_count + target_rc matched;
- unique board hash confirmed.

### game_move

This is weaker but can still be acceptable if the board hash is unique.

Rule:

- allow automatic fill only if join_status == unique_join and unique_board_hash_count == 1.

Reason:

- multiple target rows may point to the same board at the same game/move;
- this is expected when candidate rows represent alternative target labels for one position;
- unique board hash avoids ambiguous board attachment.

### none

Rule:

- do not fill.

## Manifest update behavior

The board join fill branch should not overwrite other completed fields.

For each automatically filled row:

- set board_available = 1;
- set board_hash = matched_board_hash;
- set needs_board_join = 0;
- keep status dependent on remaining missing fields.

Expected status after board join fill:

### If teacher_eval_available == 1 but rank_prob_available == 0

Set:

- status = needs_current_best_probe

Reason:

- board is now available;
- next step is current_best rank/prob probe.

### If teacher_eval_available == 0

Set:

- status = needs_rapfi_requery

Reason:

- board is available, but teacher label/eval remains incomplete.

### If target/side missing

Set:

- status = skipped_invalid

Reason:

- cannot safely probe or train.

### If all fields unexpectedly complete

Set:

- status = ready_full_schema

Reason:

- should be rare in this fill path.

## Required output fields

The board join fill branch should write:

- analysis/integration_eval/teacher_divergence_board_join_fill.csv
- analysis/integration_eval/teacher_divergence_board_join_fill_report.md

Recommended fill CSV fields:

- manifest_id
- old_status
- new_status
- join_status
- join_strength
- matched_board_hash
- board_available_after
- needs_board_join_after
- needs_current_best_probe_after
- needs_rapfi_requery_after
- excluded
- exclude_reason
- notes

## Expected result

Based on the audit:

| category | expected rows |
|---|---:|
| automatic board join candidates | 162 |
| excluded ambiguous_join | 20 |
| retained no_join | 21 |

Most automatically joined rows will likely move from:

- needs_board_join

to either:

- needs_current_best_probe;
- needs_rapfi_requery.

They should not become training rows immediately.

## Post-fill sequence

After board join fill:

### Step 1

Merge board join fill into updated manifest.

Expected branch:

exp/15x15-teacher-divergence-manifest-update-with-board-joins

### Step 2

Run current_best probe fill on rows newly marked needs_current_best_probe.

Expected branch:

exp/15x15-teacher-divergence-current-best-probe-fill-round2

### Step 3

Run suppress build fill on legal rows from round2.

Expected branch:

exp/15x15-teacher-divergence-suppress-build-fill-round2

### Step 4

Only after manifest rows are full-schema, reassess bucket counts.

No training should happen before this.

## No-training rule

Do not train until:

1. ready_full_schema rows are much larger than 36;
2. trainable_rank_11_50 bucket has enough rows;
3. protected_top10 remains eval/protection only;
4. tail_rank_gt50 remains diagnostic-only;
5. ambiguous/no-join rows are not silently included;
6. all rank/prob and suppress fields are generated from validated boards.

## Decision

Proceed with conservative board join fill for unique_join rows only.

Do not fill ambiguous_join rows.

Do not fill no_join rows.

Do not train.

Do not save checkpoint.

Do not export.

Do not run public benchmark.

Do not promote.
