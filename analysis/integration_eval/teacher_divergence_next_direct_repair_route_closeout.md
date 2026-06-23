# 15x15 teacher-divergence next direct repair route closeout

## Branch

`exp/15x15-teacher-divergence-next-direct-repair-route-closeout`

## Purpose

Static-only route closeout after the direct repair field spec branch.

This branch only reads the tracked field-spec JSON and records the next safe route. It does not train, run model evaluation, read checkpoint contents, write checkpoints, export C, run public benchmarks, promote candidates, or overwrite current-best.

## Upstream

- Upstream branch: `exp/15x15-teacher-divergence-next-direct-repair-field-spec`
- Upstream commit: `1d2b4c9`
- Upstream artifact: `analysis/integration_eval/teacher_divergence_next_direct_repair_field_spec.json`

## Field-spec result

| Field | Value |
|---|---|
| field_spec_decision | `DIRECT_REPAIR_FIELD_SPEC_STATIC_CANDIDATES_FOUND` |
| field_spec_recommended_next_branch | `exp/15x15-teacher-divergence-next-direct-repair-static-patch-plan` |
| scan_summary.tracked_files_scanned | `75` |
| scan_summary.json_marker_candidates | `33` |
| scan_summary.csv_marker_candidates | `33` |
| scan_summary.markdown_marker_hits | `65` |
| scan_summary.specific_issue_candidates | `18` |

## Route decision

`ROUTE_TO_STATIC_PATCH_PLAN`

The field-spec scan found static candidate evidence, so the next safe step is a static patch plan rather than another broad scan.

## Selected next branch

`exp/15x15-teacher-divergence-next-direct-repair-static-patch-plan`

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

## Acceptance checks

| Check | Result |
|---|---|
| uses_only_tracked_static_artifacts | PASS |
| uses_field_spec_json_only | PASS |
| does_not_train | PASS |
| does_not_run_model_eval | PASS |
| does_not_read_checkpoint_content | PASS |
| does_not_write_checkpoints | PASS |
| does_not_export_c | PASS |
| does_not_run_public_benchmark | PASS |
| does_not_promote | PASS |
| does_not_overwrite_current_best | PASS |

## Closeout decision

`DIRECT_REPAIR_ROUTE_CLOSEOUT_COMPLETE_STATIC_ONLY`

## Promotion decision

`NO_PROMOTION__ROUTE_CLOSEOUT_ONLY`
