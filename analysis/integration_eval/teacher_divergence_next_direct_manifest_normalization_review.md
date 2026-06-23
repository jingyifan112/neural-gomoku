# Teacher-divergence next direct manifest normalization review

## Branch

`exp/15x15-teacher-divergence-next-direct-manifest-normalization-review`

## Scope

- Normalizes ready direct manifest rows into a stricter review-only manifest.
- Places repairable rows into a repair queue.
- Places unsafe/not-ready rows into quarantine.
- Does not train.
- Does not run model eval.
- Does not read checkpoint contents.
- Does not write checkpoints.
- Does not overwrite `checkpoints/15x15_current_best.pt`.
- Does not C export.
- Does not run public benchmark.
- Does not promote.

## Normalization decision

`DIRECT_MANIFEST_NORMALIZATION_REVIEW_READY_WITH_REPAIR_QUEUE`

## Recommended next

Use the normalized ready manifest as a review-only candidate. Repair queued rows separately. Do not build eval executor yet.

## Row split

| bucket | rows |
|---|---:|
| normalized_ready_rows | 3 |
| repair_queue_rows | 1 |
| quarantine_rows | 6 |
| unclassified_rows | 0 |

## Normalized manifest preview

| normalized_manifest_id | source_manifest_row_id | source_eval_manifest_id | source_path | status | eval_allowed_now |
|---|---:|---|---|---|---:|
| direct_norm_001 | 2 | run1_direct_probe_eval_002 | `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_design.md` | NORMALIZED_REVIEW_READY | 0 |
| direct_norm_002 | 3 | run1_direct_probe_eval_003 | `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_script_audit.md` | NORMALIZED_REVIEW_READY | 0 |
| direct_norm_003 | 4 | run1_direct_probe_eval_004 | `analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_blocker_position_review.md` | NORMALIZED_REVIEW_READY | 0 |

## Repair queue preview

| repair_queue_id | source_manifest_row_id | source_eval_manifest_id | action | problems |
|---|---:|---|---|---|
| direct_repair_001 | 1 | run1_direct_probe_eval_001 | MANUAL_REVIEW | route_derived_artifact |

## Quarantine preview

| quarantine_id | source_manifest_row_id | source_eval_manifest_id | provenance | action | problems |
|---|---:|---|---|---|---|
| direct_quarantine_001 | 5 | run1_direct_probe_eval_005 | DEBUG_OR_LEGACY_SOURCE | QUARANTINE_FOR_NOW | debug_or_legacy_artifact |
| direct_quarantine_002 | 6 | run1_direct_probe_eval_006 | DEBUG_OR_LEGACY_SOURCE | QUARANTINE_FOR_NOW | debug_or_legacy_artifact |
| direct_quarantine_003 | 7 | run1_direct_probe_eval_007 | DEBUG_OR_LEGACY_SOURCE | QUARANTINE_FOR_NOW | debug_or_legacy_artifact |
| direct_quarantine_004 | 8 | run1_direct_probe_eval_008 | DEBUG_OR_LEGACY_SOURCE | QUARANTINE_FOR_NOW | debug_or_legacy_artifact |
| direct_quarantine_005 | 9 | run1_direct_probe_eval_009 | DEBUG_OR_LEGACY_SOURCE | QUARANTINE_FOR_NOW | debug_or_legacy_artifact |
| direct_quarantine_006 | 10 | run1_direct_probe_eval_010 | DEBUG_OR_LEGACY_SOURCE | QUARANTINE_FOR_NOW | debug_or_legacy_artifact |

## Summary

| metric | value | status | notes |
|---|---:|---|---|
| normalization_decision | DIRECT_MANIFEST_NORMALIZATION_REVIEW_READY_WITH_REPAIR_QUEUE | INFO | Review only; no model eval. |
| recommended_next | Use the normalized ready manifest as a review-only candidate. Repair queued rows separately. Do not build eval executor yet. | INFO |  |
| inspection_decision | DIRECT_ADAPTER_BLOCKER_INSPECTION_READY_FOR_NORMALIZATION_REVIEW | INFO |  |
| plan_decision | DIRECT_PROBE_INPUT_REPAIR_PLAN_READY | INFO |  |
| repair_plan_decision | DIRECT_PROBE_INPUT_REPAIR_PLAN_READY | INFO |  |
| original_manifest_rows | 10 | INFO |  |
| inspection_rows | 10 | INFO |  |
| normalized_ready_rows | 3 | INFO |  |
| repair_queue_rows | 1 | WARN |  |
| quarantine_rows | 6 | WARN |  |
| unclassified_rows | 0 | PASS |  |
| blocker_count | 0 | PASS |  |
| warning_count | 5 | WARN | combined WARN rows carried forward: 2; protected probability regressions carried forward: 11; tail probability regressions carried forward: 8; repair queue rows: 1; quarantine rows excluded: 6 |
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
- repair queue rows: 1
- quarantine rows excluded: 6

## Interpretation

Three ready rows can be preserved in a stricter manifest, while repair/quarantine rows remain excluded from any eval path.

## Final guardrails

- Normalized manifest is review-only.
- `eval_allowed_now` is 0 for every row.
- Keep the run1 candidate checkpoint isolated.
- No current_best overwrite.
- No C export.
- No public benchmark.
- No promotion.
- Do not add local checkpoint artifacts to git.
