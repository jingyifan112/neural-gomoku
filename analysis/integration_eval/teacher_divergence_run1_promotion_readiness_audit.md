# Teacher-divergence run1 promotion-readiness audit

## Branch

`exp/15x15-teacher-divergence-run1-promotion-readiness-audit`

## Scope

- Audits promotion readiness after controlled gated training run1.
- Does not promote.
- Does not overwrite `checkpoints/15x15_current_best.pt`.
- Does not C export.
- Does not run public benchmark.
- Does not add checkpoint artifacts to git.

## Decision

`NOT_PROMOTION_READY__READY_FOR_EPSILON_GATED_LOCAL_REVIEW`

## Run1 pass evidence

| metric | value |
|---|---:|
| wrapper decision | EXECUTION_PASS_KEEP_ISOLATED_CANDIDATE |
| wrapper hard failures | 0 |
| wrapper warnings | 2 |
| trainable gap improved rows | 44/44 |
| trainable mean gap delta | 0.0086329092 |
| trainable min gap delta | 0.0036530495 |
| trainable rank regressions | 0 |
| protected_top10 rank regressions | 0 |
| tail_rank_gt50 rank regressions | 0 |
| anchor top1 changed rows | 0 |
| anchor max KL | 0.0000060956 |

## Remaining warnings

| bucket | rows | raw prob regressions | rank regressions | mean prob delta | max prob loss |
|---|---:|---:|---:|---:|---:|
| protected_top10 | 23 | 11 | 0 | 0.0002250703 | -0.0009978712 |
| tail_rank_gt50 | 66 | 8 | 0 | 0.0000002956 | -0.0000006610 |

## Why this is not promotion-ready

- no epsilon-aware protected/tail probability review has been run yet
- no heldout/fixed-probe comparison against current_best has been run yet
- no C export has been generated in this workflow
- no public benchmark has been run in this workflow
- candidate checkpoint is local isolated artifact and has not been approved for promotion

## Required next evidence

- epsilon-aware protected_top10 probability review for 11 raw regressions
- epsilon-aware tail_rank_gt50 probability review for 8 raw regressions
- local fixed-probe/heldout comparison using candidate checkpoint vs current_best
- promotion gate design requiring no protected rank regression and bounded epsilon probability loss
- only after local gates pass: decide whether C export/public benchmark is justified

## Bucket/status context

| item | count |
|---|---:|
| bucket:tail_rank_gt50 | 66 |
| bucket:protected_top10 | 23 |
| status:evaluated | 89 |

## Summary table

| metric | value | status | notes |
|---|---:|---|---|
| readiness_decision | NOT_PROMOTION_READY__READY_FOR_EPSILON_GATED_LOCAL_REVIEW | INFO | Promotion-readiness audit decision. |
| wrapper_decision | EXECUTION_PASS_KEEP_ISOLATED_CANDIDATE | PASS |  |
| wrapper_hard_failure_count | 0 | PASS |  |
| wrapper_warning_count | 2 | WARN | protected_top10 raw probability regressions 11; tail_rank_gt50 raw probability regressions 8 |
| candidate_checkpoint_exists_locally | 1 | PASS | Local artifact only; do not add to git. |
| current_best_exists | 1 | PASS |  |
| candidate_same_as_current_best | 0 | PASS |  |
| trainable_rows | 44 | PASS |  |
| trainable_gap_improved_rows | 44 | PASS |  |
| trainable_target_prob_improved_rows | 44 | INFO |  |
| trainable_rank_regressed_rows | 0 | PASS |  |
| trainable_mean_gap_delta | 0.0086329092 | PASS |  |
| trainable_min_gap_delta | 0.0036530495 | INFO |  |
| trainable_max_gap_delta | 0.0105009079 | INFO |  |
| protected_top10_rows | 23 | INFO |  |
| protected_top10_rank_regressed_rows | 0 | PASS |  |
| protected_top10_prob_regressed_rows | 11 | WARN |  |
| protected_top10_mean_prob_delta | 0.0002250703 | INFO |  |
| protected_top10_max_prob_loss | -0.0009978712 | WARN |  |
| tail_rank_gt50_rows | 66 | INFO |  |
| tail_rank_gt50_rank_regressed_rows | 0 | PASS |  |
| tail_rank_gt50_prob_regressed_rows | 8 | WARN |  |
| tail_rank_gt50_mean_prob_delta | 0.0000002956 | INFO |  |
| tail_rank_gt50_max_prob_loss | -0.0000006610 | WARN |  |
| anchor_rows | 32 | PASS |  |
| anchor_top1_changed_rows | 0 | PASS |  |
| anchor_mean_kl | 0.0000018348 | INFO |  |
| anchor_max_kl | 0.0000060956 | PASS |  |
| promotion_blocker_count | 5 | FAIL | no epsilon-aware protected/tail probability review has been run yet; no heldout/fixed-probe comparison against current_best has been run yet; no C export has been generated in this workflow; no public benchmark has been run in this workflow; candidate checkpoint is local isolated artifact and has not been approved for promotion |
| next_evidence_count | 5 | INFO | epsilon-aware protected_top10 probability review for 11 raw regressions; epsilon-aware tail_rank_gt50 probability review for 8 raw regressions; local fixed-probe/heldout comparison using candidate checkpoint vs current_best; promotion gate design requiring no protected rank regression and bounded epsilon probability loss; only after local gates pass: decide whether C export/public benchmark is justified |

## Recommendation

Do not promote run1.

Proceed to an epsilon-aware protected/tail probability regression review branch. That branch should classify raw probability regressions by magnitude and decide whether warnings are acceptable noise or require objective/gate repair.

Only after local epsilon-aware guards and fixed-probe/heldout checks pass should C export or public benchmark be considered.

## Final guardrails

- No current_best overwrite.
- No C export.
- No public benchmark.
- No promotion.
- Do not add local checkpoint artifacts to git.
