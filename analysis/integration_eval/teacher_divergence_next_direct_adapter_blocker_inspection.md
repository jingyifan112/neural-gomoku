# Teacher-divergence next direct adapter blocker inspection

## Branch

`exp/15x15-teacher-divergence-next-direct-adapter-blocker-inspection`

## Scope

- Inspects direct manifest rows one by one.
- Does not train.
- Does not run model eval.
- Does not read checkpoint contents.
- Does not write checkpoints.
- Does not overwrite `checkpoints/15x15_current_best.pt`.
- Does not C export.
- Does not run public benchmark.
- Does not promote.

## Inspection decision

`DIRECT_ADAPTER_BLOCKER_INSPECTION_READY_FOR_NORMALIZATION_REVIEW`

## Recommended next

Normalize ready/repairable rows into a stricter manifest; keep eval disabled.

## Row-level summary

| metric | value |
|---|---:|
| manifest_rows | 10 |
| ready_rows | 3 |
| needs_repair_rows | 1 |
| not_ready_rows | 6 |
| quarantine_rows | 6 |
| schema_repair_rows | 0 |
| provenance_repair_rows | 0 |

## Row inspection table

| row | eval_manifest_id | path_exists | schema | provenance | leakage | readiness | action | problems |
|---:|---|---:|---|---|---|---|---|---|
| 1 | run1_direct_probe_eval_001 | 1 | HAS_CONTEXT_BUT_NEEDS_REVIEW | CLEAN_HELDOUT_OR_DIRECT_SOURCE | MEDIUM | NEEDS_REPAIR | MANUAL_REVIEW | route_derived_artifact |
| 2 | run1_direct_probe_eval_002 | 1 | OK | CLEAN_HELDOUT_OR_DIRECT_SOURCE | LOW | READY_FOR_FUTURE_GUARDED_EVAL_REVIEW | KEEP_AS_CANDIDATE_FOR_NORMALIZATION |  |
| 3 | run1_direct_probe_eval_003 | 1 | OK | CLEAN_HELDOUT_OR_DIRECT_SOURCE | LOW | READY_FOR_FUTURE_GUARDED_EVAL_REVIEW | KEEP_AS_CANDIDATE_FOR_NORMALIZATION |  |
| 4 | run1_direct_probe_eval_004 | 1 | OK | CLEAN_HELDOUT_OR_DIRECT_SOURCE | LOW | READY_FOR_FUTURE_GUARDED_EVAL_REVIEW | KEEP_AS_CANDIDATE_FOR_NORMALIZATION |  |
| 5 | run1_direct_probe_eval_005 | 1 | HAS_CONTEXT_BUT_NEEDS_REVIEW | DEBUG_OR_LEGACY_SOURCE | MEDIUM | NOT_READY | QUARANTINE_FOR_NOW | debug_or_legacy_artifact |
| 6 | run1_direct_probe_eval_006 | 1 | HAS_CONTEXT_BUT_NEEDS_REVIEW | DEBUG_OR_LEGACY_SOURCE | MEDIUM | NOT_READY | QUARANTINE_FOR_NOW | debug_or_legacy_artifact |
| 7 | run1_direct_probe_eval_007 | 1 | HAS_CONTEXT_BUT_NEEDS_REVIEW | DEBUG_OR_LEGACY_SOURCE | MEDIUM | NOT_READY | QUARANTINE_FOR_NOW | debug_or_legacy_artifact |
| 8 | run1_direct_probe_eval_008 | 1 | HAS_CONTEXT_BUT_NEEDS_REVIEW | DEBUG_OR_LEGACY_SOURCE | MEDIUM | NOT_READY | QUARANTINE_FOR_NOW | debug_or_legacy_artifact |
| 9 | run1_direct_probe_eval_009 | 1 | HAS_CONTEXT_BUT_NEEDS_REVIEW | DEBUG_OR_LEGACY_SOURCE | MEDIUM | NOT_READY | QUARANTINE_FOR_NOW | debug_or_legacy_artifact |
| 10 | run1_direct_probe_eval_010 | 1 | HAS_CONTEXT_BUT_NEEDS_REVIEW | DEBUG_OR_LEGACY_SOURCE | MEDIUM | NOT_READY | QUARANTINE_FOR_NOW | debug_or_legacy_artifact |

## Summary metrics

| metric | value | status | notes |
|---|---:|---|---|
| inspection_decision | DIRECT_ADAPTER_BLOCKER_INSPECTION_READY_FOR_NORMALIZATION_REVIEW | INFO | Inspection only; no model eval. |
| recommended_next | Normalize ready/repairable rows into a stricter manifest; keep eval disabled. | INFO |  |
| plan_decision | DIRECT_PROBE_INPUT_REPAIR_PLAN_READY | INFO |  |
| direct_adapter_decision | DIRECT_PROBE_EVAL_ADAPTER_BLOCKED | INFO |  |
| direct_adapter_blocker_count | 2 | WARN | controlled review is blocked; controlled review blockers present: 2 |
| direct_adapter_warning_count | 2 | WARN | controlled review warnings carried forward: 5; deferred adapter inputs remain: 88 |
| repair_action_count | 6 | INFO |  |
| manifest_rows | 10 | INFO |  |
| ready_rows | 3 | INFO |  |
| needs_repair_rows | 1 | INFO |  |
| not_ready_rows | 6 | INFO |  |
| quarantine_rows | 6 | WARN |  |
| schema_repair_rows | 0 | PASS |  |
| provenance_repair_rows | 0 | PASS |  |
| blocker_count | 0 | PASS |  |
| warning_count | 6 | WARN | combined WARN rows carried forward: 2; protected probability regressions carried forward: 11; tail probability regressions carried forward: 8; direct adapter blocker notes carried forward: controlled review is blocked; controlled review blockers present: 2; direct adapter warning notes carried forward: controlled review warnings carried forward: 5; deferred adapter inputs remain: 88; rows recommended for quarantine: 6 |
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
| count_direct_eval_readiness:NEEDS_REPAIR | 1 | INFO |  |
| count_direct_eval_readiness:NOT_READY | 6 | INFO |  |
| count_direct_eval_readiness:READY_FOR_FUTURE_GUARDED_EVAL_REVIEW | 3 | INFO |  |
| count_leakage_risk:LOW | 3 | INFO |  |
| count_leakage_risk:MEDIUM | 7 | INFO |  |
| count_provenance_status:CLEAN_HELDOUT_OR_DIRECT_SOURCE | 4 | INFO |  |
| count_provenance_status:DEBUG_OR_LEGACY_SOURCE | 6 | INFO |  |
| count_recommended_action:KEEP_AS_CANDIDATE_FOR_NORMALIZATION | 3 | INFO |  |
| count_recommended_action:MANUAL_REVIEW | 1 | INFO |  |
| count_recommended_action:QUARANTINE_FOR_NOW | 6 | INFO |  |
| count_risk_level:HIGH | 6 | INFO |  |
| count_risk_level:LOW | 3 | INFO |  |
| count_risk_level:MEDIUM | 1 | INFO |  |
| count_schema_status:HAS_CONTEXT_BUT_NEEDS_REVIEW | 7 | INFO |  |
| count_schema_status:OK | 3 | INFO |  |

## Blockers

- None.

## Warnings

- combined WARN rows carried forward: 2
- protected probability regressions carried forward: 11
- tail probability regressions carried forward: 8
- direct adapter blocker notes carried forward: controlled review is blocked; controlled review blockers present: 2
- direct adapter warning notes carried forward: controlled review warnings carried forward: 5; deferred adapter inputs remain: 88
- rows recommended for quarantine: 6

## Interpretation

At least one direct row looks repairable/normalizable enough for a future guarded-input manifest review. This is still not an eval executor.

## Final guardrails

- Keep the run1 candidate checkpoint isolated.
- No current_best overwrite.
- No C export.
- No public benchmark.
- No promotion.
- Do not add local checkpoint artifacts to git.
