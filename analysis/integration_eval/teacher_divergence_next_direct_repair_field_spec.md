# 15x15 teacher-divergence next direct repair field spec

## Branch

`exp/15x15-teacher-divergence-next-direct-repair-field-spec`

## Purpose

Static-only scan to identify the field-level issue for the one direct repair-queue row.

This branch does not train, run model evaluation, read checkpoint contents, write checkpoints, export C, run public benchmarks, promote candidates, or overwrite current-best.

## Upstream

- Upstream branch: `exp/15x15-teacher-divergence-next-direct-repair-materialization-dryrun`
- Upstream commit: `4ddb33a`
- Upstream decision: `DIRECT_REPAIR_MATERIALIZATION_DRYRUN_COMPLETE_STATIC_ONLY`
- Upstream promotion decision: `NO_PROMOTION__STATIC_DRYRUN_ONLY`

## Expected boundary

| Field | Value |
|---|---:|
| direct_manifest_rows | 10 |
| normalized_ready_rows | 3 |
| repair_queue_rows | 1 |
| quarantine_rows | 6 |
| eval_allowed_now | 0 |
| checkpoint_read_allowed_now | 0 |

## Safety permissions

| Permission | Allowed now |
|---|---:|
| training_allowed_now | 0 |
| model_eval_allowed_now | 0 |
| checkpoint_read_allowed_now | 0 |
| checkpoint_write_allowed_now | 0 |
| c_export_allowed_now | 0 |
| public_benchmark_allowed_now | 0 |
| promotion_allowed_now | 0 |
| current_best_overwrite_allowed_now | 0 |

## Scan summary

| Metric | Value |
|---|---:|
| tracked_files_scanned | 75 |
| json_marker_candidates | 33 |
| csv_marker_candidates | 33 |
| markdown_marker_hits | 65 |
| specific_issue_candidates | 18 |

## Specific issue candidates

| Source | Location | Evidence keys |
|---|---|---|
| `analysis/integration_eval/teacher_divergence_next_direct_repair_materialization_dryrun.json` | $ | branch, purpose, upstream_branch, execution_permissions, source_state, materialized_buckets, acceptance_checks, dryrun_decision, promotion_decision, recommended_next_branch |
| `analysis/integration_eval/teacher_divergence_next_direct_repair_materialization_dryrun.json` | $.materialized_buckets[1] | bucket, dryrun_status, allowed_next_handling, eval_allowed_now, checkpoint_read_allowed_now |
| `analysis/integration_eval/teacher_divergence_next_direct_repair_queue_review_decision.json` | $ | normalization_decision, outputs, recommended_next, repair_queue_review_decision, row_counts, warnings |
| `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection_rows.csv` | 6 | schema_keys, schema_status, provenance_status, recommended_action, clean_source_tokens |
| `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection_rows.csv` | 7 | schema_keys, schema_status, provenance_status, recommended_action, clean_source_tokens |
| `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection_rows.csv` | 8 | schema_keys, schema_status, provenance_status, recommended_action, clean_source_tokens |
| `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection_rows.csv` | 9 | schema_keys, schema_status, provenance_status, recommended_action, clean_source_tokens |
| `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection_rows.csv` | 10 | schema_keys, schema_status, provenance_status, recommended_action, clean_source_tokens |
| `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection_rows.csv` | 11 | schema_keys, schema_status, provenance_status, recommended_action, clean_source_tokens |
| `analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review_quarantine.csv` | 2 | quarantine_id, source_manifest_row_id, source_eval_manifest_id, source_adapter_kind, source_path, schema_status, provenance_status, recommended_action, quarantine_reason, eval_allowed_now |
| `analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review_quarantine.csv` | 3 | quarantine_id, source_manifest_row_id, source_eval_manifest_id, source_adapter_kind, source_path, schema_status, provenance_status, recommended_action, quarantine_reason, eval_allowed_now |
| `analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review_quarantine.csv` | 4 | quarantine_id, source_manifest_row_id, source_eval_manifest_id, source_adapter_kind, source_path, schema_status, provenance_status, recommended_action, quarantine_reason, eval_allowed_now |
| `analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review_quarantine.csv` | 5 | quarantine_id, source_manifest_row_id, source_eval_manifest_id, source_adapter_kind, source_path, schema_status, provenance_status, recommended_action, quarantine_reason, eval_allowed_now |
| `analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review_quarantine.csv` | 6 | quarantine_id, source_manifest_row_id, source_eval_manifest_id, source_adapter_kind, source_path, schema_status, provenance_status, recommended_action, quarantine_reason, eval_allowed_now |
| `analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review_quarantine.csv` | 7 | quarantine_id, source_manifest_row_id, source_eval_manifest_id, source_adapter_kind, source_path, schema_status, provenance_status, recommended_action, quarantine_reason, eval_allowed_now |
| `analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review_repair_queue.csv` | 2 | repair_queue_id, source_manifest_row_id, source_eval_manifest_id, source_adapter_kind, source_path, schema_status, provenance_status, direct_eval_readiness, repair_status, eval_allowed_now, notes |
| `analysis/integration_eval/teacher_divergence_next_direct_repair_queue_review_pending.csv` | 2 | pending_id, source_repair_queue_id, source_manifest_row_id, source_eval_manifest_id, source_path, schema_status, provenance_status, pending_reasons, next_action, eval_allowed_now, notes |
| `analysis/integration_eval/teacher_divergence_next_direct_repair_queue_review_rows.csv` | 2 | repair_queue_id, source_manifest_row_id, source_eval_manifest_id, source_adapter_kind, source_path, source_path_exists, schema_status, provenance_status, direct_eval_readiness, inspection_clean_source_tokens, repair_review_decision, repair_review_bucket, candidate_reasons, pending_reasons, quarantine_reasons, next_action, eval_allowed_now, checkpoint_read_allowed_now, notes |

## Markdown marker hits preview

| Source | Line | Text |
|---|---:|---|
| `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection.md` | 33 | \| needs_repair_rows \| 1 \| |
| `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection.md` | 35 | \| quarantine_rows \| 6 \| |
| `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection.md` | 43 | \| 1 \| run1_direct_probe_eval_001 \| 1 \| HAS_CONTEXT_BUT_NEEDS_REVIEW \| CLEAN_HELDOUT_OR_DIRECT_SOURCE \| MEDIUM \| NEEDS_REPAIR \| MANUAL_REVIEW \| route_derived_artifact \| |
| `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection.md` | 47 | \| 5 \| run1_direct_probe_eval_005 \| 1 \| HAS_CONTEXT_BUT_NEEDS_REVIEW \| DEBUG_OR_LEGACY_SOURCE \| MEDIUM \| NOT_READY \| QUARANTINE_FOR_NOW \| debug_or_legacy_artifact \| |
| `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection.md` | 48 | \| 6 \| run1_direct_probe_eval_006 \| 1 \| HAS_CONTEXT_BUT_NEEDS_REVIEW \| DEBUG_OR_LEGACY_SOURCE \| MEDIUM \| NOT_READY \| QUARANTINE_FOR_NOW \| debug_or_legacy_artifact \| |
| `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection.md` | 49 | \| 7 \| run1_direct_probe_eval_007 \| 1 \| HAS_CONTEXT_BUT_NEEDS_REVIEW \| DEBUG_OR_LEGACY_SOURCE \| MEDIUM \| NOT_READY \| QUARANTINE_FOR_NOW \| debug_or_legacy_artifact \| |
| `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection.md` | 50 | \| 8 \| run1_direct_probe_eval_008 \| 1 \| HAS_CONTEXT_BUT_NEEDS_REVIEW \| DEBUG_OR_LEGACY_SOURCE \| MEDIUM \| NOT_READY \| QUARANTINE_FOR_NOW \| debug_or_legacy_artifact \| |
| `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection.md` | 51 | \| 9 \| run1_direct_probe_eval_009 \| 1 \| HAS_CONTEXT_BUT_NEEDS_REVIEW \| DEBUG_OR_LEGACY_SOURCE \| MEDIUM \| NOT_READY \| QUARANTINE_FOR_NOW \| debug_or_legacy_artifact \| |
| `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection.md` | 52 | \| 10 \| run1_direct_probe_eval_010 \| 1 \| HAS_CONTEXT_BUT_NEEDS_REVIEW \| DEBUG_OR_LEGACY_SOURCE \| MEDIUM \| NOT_READY \| QUARANTINE_FOR_NOW \| debug_or_legacy_artifact \| |
| `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection.md` | 67 | \| needs_repair_rows \| 1 \| INFO \|  \| |
| `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection.md` | 69 | \| quarantine_rows \| 6 \| WARN \|  \| |
| `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection.md` | 73 | \| warning_count \| 6 \| WARN \| combined WARN rows carried forward: 2; protected probability regressions carried forward: 11; tail probability regressions carried forward: 8; direct adapter blocker notes carried forward: controlled review is blocked; controlled review blockers present: 2; direct adapter warning notes carried forward: controlled review warnings carried forward: 5; deferred adapter inputs remain: 88; rows recommended for quarantine: 6 \| |
| `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection.md` | 93 | \| count_direct_eval_readiness:NEEDS_REPAIR \| 1 \| INFO \|  \| |
| `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection.md` | 102 | \| count_recommended_action:QUARANTINE_FOR_NOW \| 6 \| INFO \|  \| |
| `analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection.md` | 120 | - rows recommended for quarantine: 6 |
| `analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review.md` | 11 | - Places unsafe/not-ready rows into quarantine. |
| `analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review.md` | 23 | `DIRECT_MANIFEST_NORMALIZATION_REVIEW_READY_WITH_REPAIR_QUEUE` |
| `analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review.md` | 34 | \| repair_queue_rows \| 1 \| |
| `analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review.md` | 35 | \| quarantine_rows \| 6 \| |
| `analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review.md` | 40 | \| normalized_manifest_id \| source_manifest_row_id \| source_eval_manifest_id \| source_path \| status \| eval_allowed_now \| |
| `analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review.md` | 48 | \| repair_queue_id \| source_manifest_row_id \| source_eval_manifest_id \| action \| problems \| |
| `analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review.md` | 52 | ## Quarantine preview |
| `analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review.md` | 54 | \| quarantine_id \| source_manifest_row_id \| source_eval_manifest_id \| provenance \| action \| problems \| |
| `analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review.md` | 56 | \| direct_quarantine_001 \| 5 \| run1_direct_probe_eval_005 \| DEBUG_OR_LEGACY_SOURCE \| QUARANTINE_FOR_NOW \| debug_or_legacy_artifact \| |
| `analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review.md` | 57 | \| direct_quarantine_002 \| 6 \| run1_direct_probe_eval_006 \| DEBUG_OR_LEGACY_SOURCE \| QUARANTINE_FOR_NOW \| debug_or_legacy_artifact \| |
| `analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review.md` | 58 | \| direct_quarantine_003 \| 7 \| run1_direct_probe_eval_007 \| DEBUG_OR_LEGACY_SOURCE \| QUARANTINE_FOR_NOW \| debug_or_legacy_artifact \| |
| `analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review.md` | 59 | \| direct_quarantine_004 \| 8 \| run1_direct_probe_eval_008 \| DEBUG_OR_LEGACY_SOURCE \| QUARANTINE_FOR_NOW \| debug_or_legacy_artifact \| |
| `analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review.md` | 60 | \| direct_quarantine_005 \| 9 \| run1_direct_probe_eval_009 \| DEBUG_OR_LEGACY_SOURCE \| QUARANTINE_FOR_NOW \| debug_or_legacy_artifact \| |
| `analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review.md` | 61 | \| direct_quarantine_006 \| 10 \| run1_direct_probe_eval_010 \| DEBUG_OR_LEGACY_SOURCE \| QUARANTINE_FOR_NOW \| debug_or_legacy_artifact \| |
| `analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review.md` | 67 | \| normalization_decision \| DIRECT_MANIFEST_NORMALIZATION_REVIEW_READY_WITH_REPAIR_QUEUE \| INFO \| Review only; no model eval. \| |

## Interpretation

Specific field-level issue candidates were found in tracked static artifacts.

## Decision

`DIRECT_REPAIR_FIELD_SPEC_STATIC_CANDIDATES_FOUND`

## Recommended next branch

`exp/15x15-teacher-divergence-next-direct-repair-static-patch-plan`

## Promotion decision

`NO_PROMOTION__STATIC_FIELD_SPEC_ONLY`

