# Teacher-divergence tiny probe guard decision closeout

## Branch

`exp/15x15-teacher-divergence-tiny-guard-decision-closeout`

## Scope

- Combines the tiny policy-margin training summary and post-training guard audit.
- Produces a decision for whether to continue to a later gated training review.
- Does not train.
- Does not read or write checkpoints.
- Does not overwrite `checkpoints/15x15_current_best.pt`.
- Does not C export.
- Does not run public benchmark.
- Does not promote.

## Inputs

- tiny gap summary: `analysis/integration_eval/teacher_divergence_tiny_policy_margin_probe_e3_gap_summary.csv`
- tiny epoch metrics: `analysis/integration_eval/teacher_divergence_tiny_policy_margin_probe_e3_epoch_metrics.csv`
- posttrain trainable guard: `analysis/integration_eval/teacher_divergence_tiny_posttrain_trainable_gap_guard.csv`
- posttrain bucket guard: `analysis/integration_eval/teacher_divergence_tiny_posttrain_manifest_bucket_guard.csv`
- posttrain anchor drift guard: `analysis/integration_eval/teacher_divergence_tiny_posttrain_anchor_drift_guard.csv`

## Decision

`PASS_TO_GATED_TRAINING_REVIEW_WITH_WARNINGS`

## Summary

| metric | value | status | notes |
|---|---:|---|---|
| decision | PASS_TO_GATED_TRAINING_REVIEW_WITH_WARNINGS | INFO | closeout decision |
| hard_failure_count | 0 | PASS |  |
| warning_count | 2 | WARN | protected_top10 probability regressions observed: 11; tail_rank_gt50 probability regressions observed: 8 |
| tiny_gap_rows | 44 | PASS |  |
| posttrain_trainable_rows | 44 | PASS |  |
| anchor_rows | 32 | PASS |  |
| epoch_rows | 3 | PASS |  |
| tiny_gap_improved_rows | 44 | INFO |  |
| tiny_target_prob_improved_rows | 44 | INFO |  |
| tiny_mean_gap_delta | 0.0025901364 | INFO |  |
| tiny_mean_target_prob_delta | 0.0000031641 | INFO |  |
| tiny_mean_suppress_prob_delta | -0.0001244870 | INFO |  |
| posttrain_gap_improved_rows | 44 | PASS |  |
| posttrain_target_prob_improved_rows | 44 | INFO |  |
| posttrain_target_rank_improved_rows | 0 | INFO |  |
| posttrain_target_rank_regressed_rows | 0 | PASS |  |
| posttrain_mean_gap_delta | 0.0025900711 | PASS |  |
| posttrain_min_gap_delta | 0.0010976791 | INFO |  |
| posttrain_mean_target_prob_delta | 0.0000031649 | INFO |  |
| posttrain_mean_suppress_prob_delta | -0.0001244857 | INFO |  |
| protected_top10_rows | 23 | INFO |  |
| protected_top10_rank_regressed_rows | 0 | PASS |  |
| protected_top10_prob_regressed_rows | 11 | WARN |  |
| tail_rank_gt50_rows | 66 | INFO |  |
| tail_rank_gt50_rank_regressed_rows | 0 | PASS |  |
| tail_rank_gt50_prob_regressed_rows | 8 | WARN |  |
| anchor_top1_changed_rows | 0 | PASS |  |
| anchor_mean_kl | 0.0000001493 | INFO |  |
| anchor_max_kl | 0.0000005536 | PASS |  |
| loss_delta | -0.0018070000 | INFO |  |
| margin_loss_delta | -0.0017290000 | INFO |  |

## Bucket guard context

| item | count |
|---|---:|
| bucket:tail_rank_gt50 | 66 |
| bucket:protected_top10 | 23 |
| status:evaluated | 89 |

## Hard failures

- None.

## Warnings

- protected_top10 probability regressions observed: 11
- tail_rank_gt50 probability regressions observed: 8

## Interpretation

The tiny probe has positive trainable signal but includes guard warnings.

The next step may be a gated training review branch, not promotion. Any larger run should include explicit protected/heldout gates and save-on-pass behavior.

## Output

- summary CSV: `analysis/integration_eval/teacher_divergence_tiny_probe_guard_decision_summary.csv`
- closeout report: `analysis/integration_eval/teacher_divergence_tiny_probe_guard_decision_closeout.md`

## Final guardrails

- No current_best overwrite.
- No C export.
- No public benchmark.
- No promotion.
