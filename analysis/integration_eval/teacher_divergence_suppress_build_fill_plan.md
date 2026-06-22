# Teacher-divergence suppress build fill plan

## Branch

exp/15x15-teacher-divergence-suppress-build-fill-plan

## Scope

Planning only.

No suppress dataset build, training, checkpoint save, C export, public benchmark, or promotion is run on this branch.

## Input

Previous branch:

exp/15x15-teacher-divergence-current-best-probe-fill

Input artifacts:

- analysis/integration_eval/teacher_divergence_current_best_probe_fill.csv
- analysis/integration_eval/teacher_divergence_current_best_probe_fill_report.md

Current_best probe fill summary:

| metric | value |
|---|---:|
| selected rows | 14 |
| filled rows | 14 |
| target legal rows | 11 |
| status_after needs_suppress_build | 14 |

Bucket after fill:

| bucket_after | rows |
|---|---:|
| protected_top10 | 3 |
| trainable_rank_11_50 | 2 |
| tail_rank_gt50 | 6 |
| unknown_rank | 3 |

## Interpretation

The current_best probe fill successfully added rank/prob/direct-move diagnostics for the 14 selected rows.

However, none of the 14 rows are full-schema training rows yet, because all are still missing suppress candidates.

The 3 `unknown_rank` rows are target-illegal rows. These rows should not enter suppress build or training. They should be marked invalid/excluded unless a source-specific board/target correction is later justified.

The 11 legal-target rows can proceed to suppress candidate construction.

## Suppress build eligibility

### Eligible

A row is eligible for suppress build only if:

- status_after == needs_suppress_build;
- target_legal == True;
- bucket_after is one of:
  - protected_top10;
  - trainable_rank_11_50;
  - tail_rank_gt50;
- current_best_top_policy_rcs is available;
- current_best_direct_rc is available;
- target_rc is legal.

Expected eligible count:

| bucket_after | eligible rows |
|---|---:|
| protected_top10 | 3 |
| trainable_rank_11_50 | 2 |
| tail_rank_gt50 | 6 |
| total | 11 |

### Excluded for now

Rows with:

- target_legal == False;
- bucket_after == unknown_rank;
- missing board;
- missing target;
- missing current_best top policy list.

Expected excluded count:

| reason | rows |
|---|---:|
| target illegal / unknown rank | 3 |

## Suppress candidate rule

For each eligible row, build suppress candidates from current_best policy output.

Recommended rule:

1. Start with current_best_direct_rc.
2. Add current_best top policy moves in descending probability order.
3. Exclude target_rc.
4. Exclude illegal moves.
5. Remove duplicates.
6. Keep max_suppress = 5.
7. Require at least min_suppress = 3.

Primary suppress:

- current_best_direct_rc if it is legal and not equal to target_rc;
- otherwise first top policy move that is legal and not target_rc.

## Output fields for suppress fill

The suppress fill CSV should include:

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
- suppress_count
- primary_suppress_rc
- suppress_rcs
- suppress_source
- needs_suppress_build_after
- excluded
- exclude_reason

## Expected statuses after suppress fill

For eligible legal rows:

- if suppress_count >= 3 and teacher_eval is available:
  - status_after = ready_full_schema
- if suppress_count < 3:
  - status_after = skipped_invalid or needs_manual_review
- if teacher_eval is missing:
  - status_after = needs_rapfi_requery

Expected from current input:

- the 11 legal rows should likely become ready_full_schema if suppress candidates can be built from top policy moves;
- the 3 illegal-target rows should become skipped_invalid or excluded_target_illegal.

## Important bucket policy

Even if suppress fill succeeds, do not train yet.

The filled rows should be classified as:

### protected_top10

- eval/protection only;
- no training.

### trainable_rank_11_50

- possible future training candidates;
- only 2 new rows from this fill, far below minimum training size.

### tail_rank_gt50

- diagnostic-only;
- no training.

### unknown_rank / illegal target

- excluded.

## No-training rule

After suppress fill, do not build a training dataset unless:

1. ready_full_schema count is substantially larger than 25;
2. trainable_rank_11_50 has enough rows;
3. protected_top10 and tail_rank_gt50 remain eval-only;
4. board joins for the 203 missing-board rows have been audited;
5. duplicates remain resolved.

## Recommended next branch

exp/15x15-teacher-divergence-suppress-build-fill

Goal:

- read current_best probe fill CSV;
- select 11 legal rows;
- build suppress candidates from current_best top policy list;
- exclude 3 target-illegal rows;
- write suppress fill CSV/report;
- no training.

Expected outputs:

- analysis/integration_eval/teacher_divergence_suppress_build_fill.csv
- analysis/integration_eval/teacher_divergence_suppress_build_fill_report.md

## Decision

Proceed with suppress build fill for legal rows only.

Do not train.

Do not save checkpoint.

Do not export.

Do not run public benchmark.

Do not promote.
