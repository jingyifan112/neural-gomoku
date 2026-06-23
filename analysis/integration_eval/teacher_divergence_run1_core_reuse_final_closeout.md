# Teacher-divergence run1 core-reuse final closeout

## Branch

`exp/15x15-teacher-divergence-run1-core-reuse-final-closeout`

## Scope

- Final conservative closeout for run1.
- Does not train.
- Does not run model eval.
- Does not read checkpoint contents.
- Does not write checkpoints.
- Does not overwrite `checkpoints/15x15_current_best.pt`.
- Does not C export.
- Does not run public benchmark.
- Does not promote.

## Final decision

`RUN1_CORE_REUSE_FINAL_CLOSEOUT_COMPLETE_WITH_WARNINGS`

## Promotion decision

`NO_PROMOTION__KEEP_RUN1_CANDIDATE_ISOLATED`

## Recommended next

Stop the run1 promotion/eval path here. Keep candidate checkpoint isolated. Use future work to build cleaner direct-probe or heldout eval inputs before any promotion path.

## Why this is a conservative closeout

- The isolated run1 candidate improved all 44 trainable gaps in the reused guard summary.
- No trainable/protected/tail rank regression is present in the reused guard summary.
- Anchor top-1 changed rows are zero, and anchor max KL remains low.
- Direct-probe routing did not become a safe eval path.
- Protected/tail raw probability regression warnings remain.
- Therefore this is not a promotion path.

## Summary

| metric | value | status | notes |
|---|---:|---|---|
| final_decision | RUN1_CORE_REUSE_FINAL_CLOSEOUT_COMPLETE_WITH_WARNINGS | INFO | Final closeout only; no model eval. |
| promotion_decision | NO_PROMOTION__KEEP_RUN1_CANDIDATE_ISOLATED | INFO |  |
| recommended_next | Stop the run1 promotion/eval path here. Keep candidate checkpoint isolated. Use future work to build cleaner direct-probe or heldout eval inputs before any promotion path. | INFO |  |
| followup_decision | ROUTING_PATCH_OR_CORE_CLOSEOUT_READY | INFO |  |
| blocker_review_decision | BLOCKED_REVIEW_RECOMMENDS_ROUTING_PATCH_OR_CORE_CLOSEOUT | INFO |  |
| blocker_review_root_causes |  | INFO | direct_probe_adapter_blocked; probability_regression_warnings_remain |
| blocker_count | 0 | PASS |  |
| warning_count | 15 | WARN | combined WARN rows carried forward: 2; protected raw probability regressions carried forward: 11; tail raw probability regressions carried forward: 8; blocker follow-up warnings: combined WARN rows carried forward: 2; protected raw probability regressions carried forward: 11; tail raw probability regressions carried forward: 8; followup_json: dispatch warnings carried forward: 4; followup_json: combined WARN rows carried forward: 2; followup_json: protected raw probability regressions carried forward: 11; followup_json: tail raw probability regressions carried forward: 8; dispatch_json: upstream next-stage warnings carried forward: 5; dispatch_json: combined local comparison WARN rows carried forward: 2; dispatch_json: protected raw probability regressions carried forward: 11; dispatch_json: tail raw probability regressions carried forward: 8; followup json: combined WARN rows carried forward: 2; followup json: protected raw probability regressions carried forward: 11; followup json: tail raw probability regressions carried forward: 8; followup json: followup_json: dispatch warnings carried forward: 4; followup json: followup_json: combined WARN rows carried forward: 2; followup json: followup_json: protected raw probability regressions carried forward: 11; followup json: followup_json: tail raw probability regressions carried forward: 8; followup json: dispatch_json: upstream next-stage warnings carried forward: 5; followup json: dispatch_json: combined local comparison WARN rows carried forward: 2; followup json: dispatch_json: protected raw probability regressions carried forward: 11; followup json: dispatch_json: tail raw probability regressions carried forward: 8 |
| candidate_checkpoint_exists_locally | 1 | PASS | Existence only; do not add to git. |
| current_best_exists | 1 | PASS |  |
| direct_adapter_decision | DIRECT_PROBE_EVAL_ADAPTER_BLOCKED | INFO |  |
| direct_manifest_rows | 10 | INFO |  |
| combined_summary_rows | 12 | INFO |  |
| combined_fail_rows | 0 | PASS |  |
| combined_warn_rows | 2 | WARN |  |
| trainable_gap_improved | 44 | PASS |  |
| trainable_rank_regressed | 0 | PASS |  |
| protected_rank_regressed | 0 | PASS |  |
| tail_rank_regressed | 0 | PASS |  |
| protected_prob_regressed | 11 | WARN |  |
| tail_prob_regressed | 8 | WARN |  |
| anchor_top1_changed | 0 | PASS |  |
| anchor_max_kl | 0.0000060956 | PASS |  |
| would_train | 0 | PASS |  |
| would_eval_model_now | 0 | PASS |  |
| would_read_checkpoint_contents_now | 0 | PASS |  |
| would_write_checkpoint | 0 | PASS |  |
| would_c_export | 0 | PASS |  |
| would_public_benchmark | 0 | PASS |  |
| would_promote | 0 | PASS |  |

## Blockers

- None.

## Warnings

- combined WARN rows carried forward: 2
- protected raw probability regressions carried forward: 11
- tail raw probability regressions carried forward: 8
- blocker follow-up warnings: combined WARN rows carried forward: 2; protected raw probability regressions carried forward: 11; tail raw probability regressions carried forward: 8; followup_json: dispatch warnings carried forward: 4; followup_json: combined WARN rows carried forward: 2; followup_json: protected raw probability regressions carried forward: 11; followup_json: tail raw probability regressions carried forward: 8; dispatch_json: upstream next-stage warnings carried forward: 5; dispatch_json: combined local comparison WARN rows carried forward: 2; dispatch_json: protected raw probability regressions carried forward: 11; dispatch_json: tail raw probability regressions carried forward: 8
- followup json: combined WARN rows carried forward: 2
- followup json: protected raw probability regressions carried forward: 11
- followup json: tail raw probability regressions carried forward: 8
- followup json: followup_json: dispatch warnings carried forward: 4
- followup json: followup_json: combined WARN rows carried forward: 2
- followup json: followup_json: protected raw probability regressions carried forward: 11
- followup json: followup_json: tail raw probability regressions carried forward: 8
- followup json: dispatch_json: upstream next-stage warnings carried forward: 5
- followup json: dispatch_json: combined local comparison WARN rows carried forward: 2
- followup json: dispatch_json: protected raw probability regressions carried forward: 11
- followup json: dispatch_json: tail raw probability regressions carried forward: 8

## Final guardrails

- Keep the run1 candidate checkpoint isolated.
- No current_best overwrite.
- No C export.
- No public benchmark.
- No promotion.
- Do not add local checkpoint artifacts to git.
