# Capacity-data pairing audit

## Branch

`exp/15x15-capacity-data-pairing-audit`

## Purpose

This route checks whether the project now has enough increased-data artifacts and prior capacity-upgrade history to design a data-supported capacity probe.

This is a static audit only.

## Non-execution scope

Not performed:

- no checkpoint read
- no checkpoint inspection
- no training
- no checkpoint write
- no C export
- no public benchmark
- no promotion
- no overwrite of `current_best`
- no overwrite of manifests
- no modification of old untracked local artifacts

## Data-side inventory

| Name | Path | Exists | Kind | Count | Notes |
|---|---|---:|---|---:|---|
| policy_only_multisuppress_dataset | `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json` | `True` | json | 25 | row_count_from_key=samples |
| policy_only_multisuppress_dryrun_metrics | `analysis/integration_eval/policy_only_multisuppress_dryrun_metrics.csv` | `True` | csv | 25 | csv_count_excludes_header |
| policy_only_rank_topk_gate_run1_metrics | `analysis/integration_eval/policy_only_rank_topk_gate_run1_metrics.csv` | `True` | csv | 25 | csv_count_excludes_header |
| policy_only_rank_topk_protected_group_metrics | `analysis/integration_eval/policy_only_rank_topk_protected_nosave_probe_group_metrics.csv` | `True` | csv | 3 | csv_count_excludes_header |
| teacher_divergence_expanded_candidate_manifest_with_fills | `analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_with_fills.csv` | `True` | csv | 362 | csv_count_excludes_header |
| teacher_divergence_expanded_candidate_manifest_with_board_joins | `analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_with_board_joins.csv` | `True` | csv | 362 | csv_count_excludes_header |
| retention_family_training_consumer_adapter_train_weighted_dataset | `analysis/integration_eval/retention_family_training_consumer_adapter_train_weighted_dataset.json` | `True` | json | 2 | row_count_from_key=rows |
| retention_family_training_consumer_adapter_eval_dataset | `analysis/integration_eval/retention_family_training_consumer_adapter_eval_dataset.json` | `True` | json | 9 | row_count_from_key=rows |

## Capacity-side history inventory

| Name | Path | Exists | Kind | Count | Notes |
|---|---|---:|---|---:|---|
| capacity_upgrade_audit | `analysis/integration_eval/capacity_upgrade_audit.md` | `True` | md | 139 | md_line_count_only; mentions_fail; mentions_non_execution_guard |
| capacity_candidate_a_b6c64_init_report | `analysis/integration_eval/capacity_candidate_a_b6c64_init_report.md` | `True` | md | 90 | md_line_count_only; mentions_pass |
| capacity_candidate_a_b6c64_train_v1_probe | `analysis/integration_eval/capacity_candidate_a_b6c64_train_v1_probe.md` | `True` | md | 92 | md_line_count_only |
| capacity_candidate_a_b6c64_train_v2_probe | `analysis/integration_eval/capacity_candidate_a_b6c64_train_v2_probe.md` | `True` | md | 63 | md_line_count_only; mentions_fail |
| capacity_candidate_b_b4c96_init_report | `analysis/integration_eval/capacity_candidate_b_b4c96_init_report.md` | `True` | md | 75 | md_line_count_only; mentions_pass |
| capacity_candidate_b_b4c96_train_v1_fixed_probe | `analysis/integration_eval/capacity_candidate_b_b4c96_train_v1_fixed_probe.md` | `True` | md | 89 | md_line_count_only |
| capacity_candidate_b_b4c96_train_v2_fixed_probe | `analysis/integration_eval/capacity_candidate_b_b4c96_train_v2_fixed_probe.md` | `True` | md | 72 | md_line_count_only |
| capacity_sweep_a_b_conclusion | `analysis/integration_eval/capacity_sweep_a_b_conclusion.md` | `True` | md | 127 | md_line_count_only; mentions_fail |

## Known CSV/JSON data row total

`813`

This total is only a rough audit count across existing CSV/JSON artifacts and may double-count related views of the same underlying examples. It is not yet a final training-set size.

## Findings

- `DATA_ARTIFACTS_PRESENT`
- `CAPACITY_HISTORY_PRESENT`
- `DATA_VOLUME_CAN_BE_QUANTIFIED_FOR_EXISTING_CSV_JSON_ARTIFACTS`
- `NO_CHECKPOINT_READ_PERFORMED`
- `NO_TRAINING_PERFORMED`
- `NO_EXPORT_PERFORMED`
- `NO_BENCHMARK_PERFORMED`
- `NO_PROMOTION_PERFORMED`

## Interpretation

The mentor requirement is not satisfied by capacity increase alone.

The next route must bind:

1. one increased-data training set,
2. one retention/heldout gate set,
3. one capacity target,
4. one no-promotion training probe protocol,
5. one strict post-training eval/gate policy.

Earlier capacity-only probes should not be treated as sufficient evidence because they were not yet paired with a clearly selected increased-data training set.

## Recommended next route

`exp/15x15-capacity-data-pairing-design`

Purpose:

Define a concrete data-supported capacity probe: choose one increased-data training set, one heldout/retention gate set, one capacity target, and one strict no-promotion training/eval protocol.

Codex needed now:

`False`

Codex note:

Codex is not needed for this audit. Codex may become useful later if the training/eval wrapper needs code changes or if we need to refactor trainer arguments safely.

## Decision

`CAPACITY_DATA_PAIRING_AUDIT_COMPLETE_READY_FOR_DESIGN_NO_TRAINING`
