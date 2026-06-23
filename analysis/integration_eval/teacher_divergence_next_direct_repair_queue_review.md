# Teacher-divergence next direct repair queue review

## Branch

`exp/15x15-teacher-divergence-next-direct-repair-queue-review`

## Scope

- Reviews repair queue rows from direct manifest normalization.
- Does not merge any repair row into the normalized manifest.
- Does not train.
- Does not run model eval.
- Does not read checkpoint contents.
- Does not write checkpoints.
- Does not overwrite `checkpoints/15x15_current_best.pt`.
- Does not C export.
- Does not run public benchmark.
- Does not promote.

## Repair queue review decision

`DIRECT_REPAIR_QUEUE_REVIEW_PENDING_METADATA`

## Recommended next

Do not merge repair row yet; materialize missing schema/provenance metadata first.

## Row split

| bucket | rows |
|---|---:|
| normalized_manifest_rows | 3 |
| repair_queue_rows | 1 |
| repair_candidate_rows | 0 |
| pending_rows | 1 |
| quarantine_addition_rows | 0 |

## Review rows

| repair_queue_id | source_manifest_row_id | source_eval_manifest_id | path_exists | schema | provenance | leakage | decision | bucket | next_action |
|---|---:|---|---:|---|---|---|---|---|---|
| direct_repair_001 | 1 | run1_direct_probe_eval_001 | 1 | HAS_CONTEXT_BUT_NEEDS_REVIEW | CLEAN_HELDOUT_OR_DIRECT_SOURCE | MEDIUM | REPAIR_ROW_MANUAL_REVIEW | pending | Manual review required before any normalization. |

## Summary

| metric | value | status | notes |
|---|---:|---|---|
| repair_queue_review_decision | DIRECT_REPAIR_QUEUE_REVIEW_PENDING_METADATA | INFO | Review only; no eval. |
| recommended_next | Do not merge repair row yet; materialize missing schema/provenance metadata first. | INFO |  |
| normalization_decision | DIRECT_MANIFEST_NORMALIZATION_REVIEW_READY_WITH_REPAIR_QUEUE | INFO |  |
| normalized_manifest_rows | 3 | INFO |  |
| repair_queue_rows | 1 | INFO |  |
| existing_quarantine_rows | 6 | INFO |  |
| reviewed_repair_rows | 1 | INFO |  |
| repair_candidate_rows | 0 | INFO |  |
| pending_rows | 1 | WARN |  |
| quarantine_addition_rows | 0 | PASS |  |
| blocker_count | 0 | PASS |  |
| warning_count | 4 | WARN | combined WARN rows carried forward: 2; protected probability regressions carried forward: 11; tail probability regressions carried forward: 8; repair rows still pending: 1 |
| candidate_checkpoint_exists_locally | 1 | INFO | Existence only; no checkpoint read. |
| current_best_exists | 1 | PASS |  |
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
- protected probability regressions carried forward: 11
- tail probability regressions carried forward: 8
- repair rows still pending: 1

## Interpretation

Repair row remains pending. The next safe step is metadata materialization, not eval.

## Final guardrails

- No repair row is merged into the normalized manifest in this branch.
- `eval_allowed_now` is 0 for all output rows.
- Keep the run1 candidate checkpoint isolated.
- No current_best overwrite.
- No C export.
- No public benchmark.
- No promotion.
- Do not add local checkpoint artifacts to git.
