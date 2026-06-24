# Capacity-data pairing preflight

## Branch

`exp/15x15-capacity-data-pairing-preflight`

## Purpose

This route checks whether the project has enough concrete script/path information to request a later explicit no-promotion training authorization for the capacity-data pairing design.

This is preflight only.

## Non-execution scope

Not performed:

- no checkpoint content read
- no checkpoint inspection
- no training
- no checkpoint write
- no C export
- no public benchmark
- no promotion
- no overwrite of `current_best`
- no overwrite of manifests
- no modification of old untracked local artifacts

## Input design

`analysis/integration_eval/capacity_data_pairing_design.json`

Design decision:

`CAPACITY_DATA_PAIRING_DESIGN_COMPLETE_READY_FOR_PREFLIGHT_NO_TRAINING`

## Required input paths

| Path | Exists |
|---|---:|
| `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json` | `True` |
| `analysis/integration_eval/policy_only_multisuppress_dryrun_metrics.csv` | `True` |
| `analysis/integration_eval/policy_only_rank_topk_gate_run1_metrics.csv` | `True` |
| `analysis/integration_eval/retention_family_training_consumer_adapter_eval_dataset.json` | `True` |
| `analysis/integration_eval/retention_family_materialized_split_manifest.csv` | `True` |
| `analysis/integration_eval/capacity_data_pairing_design.json` | `True` |
| `analysis/integration_eval/capacity_data_pairing_design.md` | `True` |

## Checkpoint candidates

Existence-only check; no checkpoint content was read.

| Path | Exists |
|---|---:|
| `checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt` | `True` |
| `checkpoints/15x15_current_best.pt` | `True` |

## Likely script discovery

| Script | Exists | Arg lines | Checkpoint refs | Guards |
|---|---:|---:|---:|---:|
| `scripts/init_capacity_candidate_b_b4c96.py` | `True` | 9 | 2 | 0 |
| `scripts/init_capacity_candidate_a_b6c64.py` | `True` | 9 | 2 | 0 |
| `scripts/policy_only_multisuppress_dryrun.py` | `False` | 0 | 0 | 0 |
| `scripts/train_teacher_divergence_policy_probe.py` | `True` | 22 | 7 | 3 |
| `scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py` | `True` | 27 | 7 | 3 |
| `scripts/probe_retention_family_adapter_dataset.py` | `True` | 15 | 2 | 0 |
| `scripts/evaluate_retention_family_adapter_gates.py` | `True` | 13 | 0 | 0 |
| `scripts/run_retention_family_gated_training_probe.py` | `True` | 13 | 0 | 0 |

## Existing training script candidates

- `scripts/apply_retention_family_adapter_train_weights.py`
- `scripts/apply_retention_family_materialized_split.py`
- `scripts/audit_retention_family_run1_loss_path.py`
- `scripts/audit_retention_family_training_consumers.py`
- `scripts/audit_teacher_divergence_board_join.py`
- `scripts/audit_teacher_divergence_normalized_trainer_compat.py`
- `scripts/audit_teacher_divergence_round2_readiness.py`
- `scripts/audit_teacher_divergence_run1_fixed_probe_heldout_inputs.py`
- `scripts/audit_teacher_divergence_tiny_posttrain_guards.py`
- `scripts/build_rapfi_teacher_policy_multisuppress_dataset.py`
- `scripts/build_retention_family_split_proposal.py`
- `scripts/build_retention_family_training_consumer_adapter.py`
- `scripts/build_retention_family_training_input_dryrun.py`
- `scripts/build_teacher_divergence_expanded_manifest.py`
- `scripts/design_retention_family_splits.py`
- `scripts/design_teacher_divergence_run1_local_comparison_adapters.py`
- `scripts/diagnose_retention_family_run1_loss_source.py`
- `scripts/diagnose_retention_family_run1_nan.py`
- `scripts/evaluate_candidate_g_policy.py`
- `scripts/evaluate_candidate_h_value.py`
- `scripts/evaluate_policy_rank_topk_gate.py`
- `scripts/evaluate_rapfi_failure_set.py`
- `scripts/evaluate_retention_family_adapter_gates.py`
- `scripts/export_teacher_divergence_round2_trainable_dryrun.py`
- `scripts/export_teacher_divergence_round2_trainable_dryrun_legacy_normalized.py`
- `scripts/fill_teacher_divergence_board_join.py`
- `scripts/fill_teacher_divergence_current_best_probe.py`
- `scripts/fill_teacher_divergence_current_best_probe_round2.py`
- `scripts/fill_teacher_divergence_suppress_build_round2.py`
- `scripts/inspect_teacher_divergence_next_direct_adapter_blockers.py`

## Future probe paths reserved for later authorization

These are proposed paths only. This route does not create these probe outputs.

| Role | Path | Already exists |
|---|---|---:|
| candidate_checkpoint | `checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt` | `False` |
| train_report | `analysis/integration_eval/capacity_data_pairing_probe/train_report.md` | `False` |
| train_metrics | `analysis/integration_eval/capacity_data_pairing_probe/train_metrics.csv` | `False` |
| gate_eval_json | `analysis/integration_eval/capacity_data_pairing_probe/gate_eval.json` | `False` |
| gate_eval_md | `analysis/integration_eval/capacity_data_pairing_probe/gate_eval.md` | `False` |
| closeout | `analysis/integration_eval/capacity_data_pairing_probe/closeout.md` | `False` |

## Preflight checks

| Check | Result |
|---|---:|
| `design_json_exists` | `True` |
| `primary_multisuppress_dataset_exists` | `True` |
| `retention_eval_dataset_exists` | `True` |
| `capacity_b_init_script_exists` | `True` |
| `at_least_one_training_script_candidate_found` | `True` |
| `future_probe_outputs_do_not_exist_yet` | `True` |
| `checkpoint_content_read` | `False` |
| `training_executed` | `False` |
| `checkpoint_written` | `False` |
| `export_executed` | `False` |
| `benchmark_executed` | `False` |
| `promotion_executed` | `False` |

## Pass conditions

| Check | Result |
|---|---:|
| `design_json_exists` | `True` |
| `primary_multisuppress_dataset_exists` | `True` |
| `retention_eval_dataset_exists` | `True` |
| `capacity_b_init_script_exists` | `True` |
| `at_least_one_training_script_candidate_found` | `True` |
| `future_probe_outputs_do_not_exist_yet` | `True` |
| `checkpoint_content_not_read` | `True` |
| `training_not_executed` | `True` |
| `checkpoint_not_written` | `True` |
| `export_not_executed` | `True` |
| `benchmark_not_executed` | `True` |
| `promotion_not_executed` | `True` |

## Recommended later authorization template

Status:

`TEMPLATE_ONLY_NOT_AUTHORIZATION`

Primary train dataset:

`analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json`

Gate dataset:

`analysis/integration_eval/retention_family_training_consumer_adapter_eval_dataset.json`

Base checkpoint:

`checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`

Candidate checkpoint:

`checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt`

Forbidden actions:

- overwrite current_best
- overwrite original manifest
- C export
- public benchmark
- promotion
- modification of old untracked files

## Codex status

Codex needed now:

`False`

Codex possible next:

Codex may be useful only if the existing training scripts cannot safely express b4c96 capacity plus the selected multi-suppress dataset and retention gate.

## Decision

`CAPACITY_DATA_PAIRING_PREFLIGHT_PASS_READY_FOR_EXPLICIT_TRAINING_AUTHORIZATION`
