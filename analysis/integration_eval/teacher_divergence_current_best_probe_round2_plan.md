# Teacher-divergence current_best probe round2 plan

## Branch

exp/15x15-teacher-divergence-current-best-probe-round2-plan

## Scope

Planning only.

No current_best probe, Rapfi requery, suppress build, training, checkpoint save, C export, public benchmark, or promotion is run on this branch.

## Input

Previous branch:

exp/15x15-teacher-divergence-manifest-update-with-board-joins

Input manifest:

- analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_with_board_joins.csv

Latest non-duplicate manifest status:

| status | rows |
|---|---:|
| needs_current_best_probe | 140 |
| needs_board_join | 41 |
| ready_full_schema | 36 |
| needs_rapfi_requery | 22 |
| skipped_invalid | 8 |

## Why round2 is needed

The board join fill converted many previously incomplete rows into rows with validated board hashes.

These rows are not training-ready yet.

They still need current_best rank/prob fields:

- before_target_rank;
- before_target_prob;
- current_best_direct_rc;
- current_best_direct_prob;
- top policy candidate list;
- target legality check.

Only after current_best probe can we assign buckets and decide whether suppress build is possible.

## Round2 selection policy

Select rows from:

- analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_with_board_joins.csv

A row is eligible if:

1. status == needs_current_best_probe;
2. duplicate_of is empty;
3. board_available == 1;
4. board_hash is non-empty;
5. target_available == 1;
6. side_available == 1;
7. teacher_eval_available == 1;
8. rank_prob_available == 0.

Expected selected rows:

- 140

## Probe behavior

For each selected row:

1. Reconstruct or fetch the board from validated board source records.
2. Run current_best policy inference.
3. Compute target legality.
4. If target is legal:
   - compute target policy rank;
   - compute target policy probability;
   - record current_best direct move;
   - record top policy move list.
5. If target is illegal:
   - mark excluded/skipped invalid.

## Bucket assignment after probe

Use the same bucket policy as prior fill:

| condition | bucket |
|---|---|
| target illegal or rank missing | unknown_rank |
| target rank <= 10 | protected_top10 |
| 11 <= target rank <= 50 | trainable_rank_11_50 |
| target rank > 50 | tail_rank_gt50 |

## Status after probe

### If target illegal

Set:

- status_after = excluded_target_illegal

### If target legal and rank/prob available

Set:

- status_after = needs_suppress_build

Reason:

- current_best probe is complete;
- suppress candidates still need to be built.

### If board cannot be reconstructed despite board_hash

Set:

- status_after = needs_board_repair

Reason:

- manifest has a board hash but probe input cannot be reconstructed.

## Expected outputs

The round2 probe branch should write:

- analysis/integration_eval/teacher_divergence_current_best_probe_fill_round2.csv
- analysis/integration_eval/teacher_divergence_current_best_probe_fill_round2_report.md

Recommended CSV fields:

- manifest_id
- status_before
- status_after
- bucket_after
- target_rc
- target_legal
- before_target_rank
- before_target_prob
- current_best_direct_rc
- current_best_direct_prob
- current_best_top_policy_rcs
- current_best_top_policy_probs
- board_hash
- probe_source
- excluded
- exclude_reason
- notes

## Expected downstream sequence

After round2 current_best probe:

### Step 1

Run suppress build fill round2 on legal probed rows.

Expected branch:

exp/15x15-teacher-divergence-suppress-build-fill-round2

### Step 2

Merge round2 probe and suppress fill into manifest.

Expected branch:

exp/15x15-teacher-divergence-manifest-update-with-probe-round2

### Step 3

Recompute ready_full_schema and bucket counts.

Only then decide whether data volume is enough for a dry-run dataset export.

## Do not include these rows yet

Do not include in current_best probe round2:

- needs_rapfi_requery rows;
- needs_board_join rows;
- ambiguous_join rows;
- no_join rows;
- duplicate rows;
- skipped_invalid rows;
- protected/eval rows already complete.

## No-training rule

Do not train until:

1. current_best probe round2 finishes;
2. suppress build round2 finishes;
3. manifest update records full-schema rows;
4. trainable_rank_11_50 count is large enough;
5. protected_top10 rows remain eval/protection only;
6. tail_rank_gt50 rows remain diagnostic-only;
7. no ambiguous/no-join rows are included.

## Decision

Proceed to current_best probe round2 implementation for eligible needs_current_best_probe rows.

Do not run Rapfi requery in this step.

Do not train.

Do not save checkpoint.

Do not export.

Do not run public benchmark.

Do not promote.
