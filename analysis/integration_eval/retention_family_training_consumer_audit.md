# Retention family training consumer audit

Scope: consumer audit only. No training, checkpoint save, C export, benchmark, or promotion was run.

## Inputs

- train manifest: `analysis/integration_eval/retention_family_training_input_dryrun_train_manifest.csv`
- eval manifest: `analysis/integration_eval/retention_family_training_input_dryrun_eval_manifest.csv`
- summary JSON: `analysis/integration_eval/retention_family_training_input_dryrun_summary.json`
- scan globs: `['scripts/*.py', 'src/**/*.py']`

## Readiness

- readiness: `blocked_high_risk_consumers_present`
- reason: 15 high-risk consumer files require review/adaptation

## Manifest validation

- train rows: 2
- eval rows: 9
- critical train targets: `['10,7', '7,10']`
- critical eval targets: `['7,9']`
- validation errors: `[]`

## Consumer scan summary

- scanned files: 79
- reported files: 77
- risk counts: `{'high': 15, 'low': 26, 'low_or_adapted': 6, 'medium': 30}`
- category counts: `{'dataset_consumer': 10, 'eval_or_gate_consumer': 4, 'other_python': 1, 'possibly_relevant': 20, 'retention_or_teacher_tool': 5, 'training_script': 37}`
- status counts: `{'mentions_new_retention_family_contract': 6, 'no_relevant_retention_family_signal': 26, 'relevant_consumer_no_retention_family_contract': 10, 'uses_generic_split_or_role_terms': 20, 'uses_old_heldout_retention_without_new_contract': 15}`

## High/medium-risk files

| path | category | risk | status | recommendation | old/ambiguous hits | new contract hits |
| --- | --- | --- | --- | --- | --- | --- |
| scripts/accept_teacher_divergence_retention_clean_v2_dataset.py | dataset_consumer | high | uses_old_heldout_retention_without_new_contract | block training until this consumer is adapted to train/eval manifests and gate_scope | heldout:13;heldout_retention:8;retention_anchor:4;role:17;split:19 |  |
| scripts/audit_mixed_ce_heldout_regressions.py | training_script | high | uses_old_heldout_retention_without_new_contract | block training until this consumer is adapted to train/eval manifests and gate_scope | heldout:6;heldout_retention:1;label_type:5;split:15 |  |
| scripts/audit_teacher_divergence_expansion_sources.py | eval_or_gate_consumer | high | uses_old_heldout_retention_without_new_contract | block training until this consumer is adapted to train/eval manifests and gate_scope | heldout:2;heldout_retention:2;role:32 |  |
| scripts/build_candidate_g_teacher_policy_dataset.py | dataset_consumer | medium | uses_generic_split_or_role_terms | inspect before training; may need explicit retention-family contract support | role:15 |  |
| scripts/build_candidate_g_teacher_seed_dataset.py | dataset_consumer | medium | uses_generic_split_or_role_terms | inspect before training; may need explicit retention-family contract support | role:15 |  |
| scripts/build_safety_block_candidate_manifest.py | eval_or_gate_consumer | high | uses_old_heldout_retention_without_new_contract | block training until this consumer is adapted to train/eval manifests and gate_scope | heldout:2;heldout_retention:2;role:12;split:19 |  |
| scripts/build_teacher_divergence_retention_clean_v2_dataset.py | dataset_consumer | high | uses_old_heldout_retention_without_new_contract | block training until this consumer is adapted to train/eval manifests and gate_scope | heldout:12;heldout_retention:5;label_type:1;retention_anchor:10;role:34;split:28 |  |
| scripts/build_teacher_divergence_retention_dataset.py | dataset_consumer | high | uses_old_heldout_retention_without_new_contract | block training until this consumer is adapted to train/eval manifests and gate_scope | heldout:7;heldout_retention:5;label_type:3;retention_anchor:3;role:12;split:25 |  |
| scripts/build_teacher_divergence_retention_expanded_dataset.py | dataset_consumer | high | uses_old_heldout_retention_without_new_contract | block training until this consumer is adapted to train/eval manifests and gate_scope | heldout:11;heldout_retention:8;label_type:1;retention_anchor:7;role:44;split:20 |  |
| scripts/build_teacher_divergence_retention_safety_v3_dataset.py | dataset_consumer | high | uses_old_heldout_retention_without_new_contract | block training until this consumer is adapted to train/eval manifests and gate_scope | heldout:3;heldout_retention:2;label_type:1;retention_anchor:1;role:8;split:13 |  |
| scripts/build_v12b_forced_line_dataset.py | dataset_consumer | medium | uses_generic_split_or_role_terms | inspect before training; may need explicit retention-family contract support | label_type:11;split:3 |  |
| scripts/build_v12l_margin_repair_dataset.py | dataset_consumer | medium | uses_generic_split_or_role_terms | inspect before training; may need explicit retention-family contract support | split:3 |  |
| scripts/candidate_d_teacher_disagreement_census.py | training_script | medium | uses_generic_split_or_role_terms | inspect before training; may need explicit retention-family contract support | split:5 |  |
| scripts/evaluate_candidate_g_policy.py | training_script | medium | uses_generic_split_or_role_terms | inspect before training; may need explicit retention-family contract support | role:2 |  |
| scripts/evaluate_candidate_h_value.py | training_script | medium | uses_generic_split_or_role_terms | inspect before training; may need explicit retention-family contract support | split:2 |  |
| scripts/evaluate_checkpoint.py | training_script | medium | relevant_consumer_no_retention_family_contract | inspect before training if this script is in the training path |  |  |
| scripts/evaluate_rapfi_failure_set.py | training_script | medium | uses_generic_split_or_role_terms | inspect before training; may need explicit retention-family contract support | label_type:10;split:13 |  |
| scripts/evaluate_tactical_mid_must_block_cases.py | training_script | medium | relevant_consumer_no_retention_family_contract | inspect before training if this script is in the training path |  |  |
| scripts/evaluate_tactical_mid_must_block_cases_c_engine.py | eval_or_gate_consumer | medium | uses_generic_split_or_role_terms | inspect before training; may need explicit retention-family contract support | split:3 |  |
| scripts/evaluate_tactical_mid_preterminal_actionable_cases.py | training_script | medium | uses_generic_split_or_role_terms | inspect before training; may need explicit retention-family contract support | split:1 |  |
| scripts/evaluate_tactical_mid_preterminal_actionable_cases_c_engine.py | eval_or_gate_consumer | medium | uses_generic_split_or_role_terms | inspect before training; may need explicit retention-family contract support | split:4 |  |
| scripts/evaluate_teacher_divergence_policy_probe_gates.py | training_script | high | uses_old_heldout_retention_without_new_contract | block training until this consumer is adapted to train/eval manifests and gate_scope | heldout:21;heldout_retention:9;split:14 |  |
| scripts/init_capacity_candidate_a_b6c64.py | training_script | medium | relevant_consumer_no_retention_family_contract | inspect before training if this script is in the training path |  |  |
| scripts/init_capacity_candidate_b_b4c96.py | training_script | medium | relevant_consumer_no_retention_family_contract | inspect before training if this script is in the training path |  |  |
| scripts/interpolate_checkpoints.py | training_script | medium | relevant_consumer_no_retention_family_contract | inspect before training if this script is in the training path |  |  |
| scripts/probe_teacher_divergence_retention_dataset.py | training_script | high | uses_old_heldout_retention_without_new_contract | block training until this consumer is adapted to train/eval manifests and gate_scope | heldout:5;heldout_retention:2;retention_anchor:2;role:4;split:28 |  |
| scripts/review_mixed_ce_heldout_blocker_positions.py | training_script | medium | uses_generic_split_or_role_terms | inspect before training; may need explicit retention-family contract support | heldout:8;label_type:4;split:2 |  |
| scripts/run_teacher_divergence_regression_gated_policy_probe.py | training_script | high | uses_old_heldout_retention_without_new_contract | block training until this consumer is adapted to train/eval manifests and gate_scope | heldout:29;heldout_retention:8;label_type:4;split:19 |  |
| scripts/train_candidate_g_policy_first_dry_run.py | training_script | medium | uses_generic_split_or_role_terms | inspect before training; may need explicit retention-family contract support | retention_anchor:1;role:23;split:1 |  |
| scripts/train_candidate_g_teacher_policy.py | training_script | medium | relevant_consumer_no_retention_family_contract | inspect before training if this script is in the training path |  |  |
| scripts/train_candidate_h_value_ranking.py | training_script | medium | uses_generic_split_or_role_terms | inspect before training; may need explicit retention-family contract support | role:1 |  |
| scripts/train_greedy_sparring_v10.py | training_script | medium | relevant_consumer_no_retention_family_contract | inspect before training if this script is in the training path |  |  |
| scripts/train_greedy_sparring_v9.py | training_script | medium | relevant_consumer_no_retention_family_contract | inspect before training if this script is in the training path |  |  |
| scripts/train_rapfi_failure_repair.py | training_script | medium | uses_generic_split_or_role_terms | inspect before training; may need explicit retention-family contract support | label_type:6;split:10 |  |
| scripts/train_rapfi_teacher_policy_margin.py | training_script | medium | uses_generic_split_or_role_terms | inspect before training; may need explicit retention-family contract support | split:2 |  |
| scripts/train_teacher_divergence_policy_anchor_probe.py | training_script | high | uses_old_heldout_retention_without_new_contract | block training until this consumer is adapted to train/eval manifests and gate_scope | heldout:7;heldout_retention:7;label_type:12;role:14;split:69 |  |
| scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py | training_script | high | uses_old_heldout_retention_without_new_contract | block training until this consumer is adapted to train/eval manifests and gate_scope | heldout:9;heldout_retention:9;label_type:24;role:14;split:85 |  |
| scripts/train_teacher_divergence_policy_probe.py | training_script | high | uses_old_heldout_retention_without_new_contract | block training until this consumer is adapted to train/eval manifests and gate_scope | heldout:3;heldout_retention:3;label_type:12;role:14;split:52 |  |
| scripts/train_v12l_margin_repair.py | training_script | medium | uses_generic_split_or_role_terms | inspect before training; may need explicit retention-family contract support | split:2 |  |
| scripts/train_v12l_margin_repair_frozen_bn.py | training_script | medium | uses_generic_split_or_role_terms | inspect before training; may need explicit retention-family contract support | split:1 |  |
| scripts/validate_teacher_divergence_retention_dataset.py | dataset_consumer | high | uses_old_heldout_retention_without_new_contract | block training until this consumer is adapted to train/eval manifests and gate_scope | heldout:6;heldout_retention:2;role:3;split:29 |  |
| scripts/verify_candidate_h_c_export.py | training_script | medium | uses_generic_split_or_role_terms | inspect before training; may need explicit retention-family contract support | split:3 |  |
| src/gomoku_agent/checkpoint.py | training_script | medium | relevant_consumer_no_retention_family_contract | inspect before training if this script is in the training path |  |  |
| src/gomoku_agent/play.py | training_script | medium | uses_generic_split_or_role_terms | inspect before training; may need explicit retention-family contract support | split:1 |  |
| src/gomoku_agent/train.py | training_script | medium | relevant_consumer_no_retention_family_contract | inspect before training if this script is in the training path |  |  |

## Files mentioning new retention-family contract

| path | category | risk | new contract hits |
| --- | --- | --- | --- |
| scripts/apply_retention_family_materialized_split.py | training_script | low_or_adapted | allowed_as_only_sibling_family_gate:6;external_or_family_level_only_not_sibling_only:1;gate_scope:13;heldout_retention_gate:9;nonheldout_retention_anchor:3;train_retention_anchor:2 |
| scripts/audit_retention_family_training_consumers.py | training_script | low_or_adapted | allowed_as_only_sibling_family_gate:2;external_or_family_level_only_not_sibling_only:3;gate_scope:7;heldout_retention_gate:1;nonheldout_retention_anchor:3;retention_family_training_input_dryrun_eval_manifest:3;retention_family_training_input_dryrun_train_manifest:3;train_retention_anchor:1 |
| scripts/build_retention_family_split_proposal.py | training_script | low_or_adapted | nonheldout_retention_anchor:13 |
| scripts/build_retention_family_training_input_dryrun.py | training_script | low_or_adapted | allowed_as_only_sibling_family_gate:6;external_or_family_level_only_not_sibling_only:5;gate_scope:16;heldout_retention_gate:3;nonheldout_retention_anchor:3;retention_family_training_input_dryrun_eval_manifest:2;retention_family_training_input_dryrun_train_manifest:2;train_retention_anchor:1 |
| scripts/design_retention_family_splits.py | training_script | low_or_adapted | nonheldout_retention_anchor:1 |
| scripts/materialize_retention_family_split.py | training_script | low_or_adapted | allowed_as_only_sibling_family_gate:4;external_or_family_level_only_not_sibling_only:2;gate_scope:12;heldout_retention_gate:9;nonheldout_retention_anchor:12 |

## Interpretation

- The training-input dry-run artifacts validate the intended split contract for the critical family.
- Current training should remain blocked unless a training/data consumer explicitly reads the train/eval manifests and respects `gate_scope`.
- Any script that still uses `heldout_retention` directly is risky if it is in the active training path.
- The next implementation step should adapt or wrap the training dataset builder to consume `retention_family_training_input_dryrun_train_manifest.csv` and `retention_family_training_input_dryrun_eval_manifest.csv` explicitly.

## Required consumer contract before training

A future training consumer must:

1. Include train-side rows only from the train manifest, with `train_use_policy=include_as_nonheldout_retention_anchor_candidate`.
2. Treat eval manifest rows according to `eval_use_policy` and `gate_scope`.
3. Enforce `external_or_family_level_only_not_sibling_only` as a hard restriction.
4. Avoid using old `heldout_retention` labels alone to decide whether a row is train-side or eval-side.
5. Preserve `family_id`, `policy_target`, and `materialized_reason` in downstream audit artifacts.

## Explicit non-actions

- No model training was run.
- No checkpoint was saved.
- No C weights were exported.
- No benchmark was run.
- No promotion decision was made.
