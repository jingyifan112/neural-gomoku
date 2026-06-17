# Retention family gated training probe runner

Scope: gated training probe wrapper/report. No C export, benchmark, or promotion was run by this wrapper.

## Mode and readiness

- mode: `train-and-gate`
- overall_status: `gates_failed`
- gates_passed: `False`
- train_manifest: `analysis/integration_eval/retention_family_training_input_dryrun_train_manifest.csv`
- eval_manifest: `analysis/integration_eval/retention_family_training_input_dryrun_eval_manifest.csv`
- candidate_checkpoint: `checkpoints/probes/retention_family_wrapper_run2_weighted_candidate.pt`
- final_checkpoint: `checkpoints/retention_family_wrapper_run2_weighted_pass.pt`

## Manifest validation

- validation_errors: `[]`
- train_rows: 2
- eval_rows: 9
- train_policy_counts: `{'include_as_nonheldout_retention_anchor_candidate': 2}`
- eval_policy_counts: `{'restricted_family_level_gate_candidate': 1, 'review_before_eval_gate_use': 8}`

## Critical family

- family_id: `bd:ea22cc14729b88fd`

### Train-side critical rows

| target | source | train_policy | risk_flags | reason |
| --- | --- | --- | --- | --- |
| 7,10 | candidate_d_g2_m15_white_last_8_9_target_live_direct_7_10_over_live_final_8_8 | include_as_nonheldout_retention_anchor_candidate | critical_sibling_conflict_family | repeated heldout blocker; regression signal; sibling target conflict family; mixed signal family |
| 10,7 | candidate_d_g2_m15_white_last_8_9_target_safe_10_7_over_live_final_8_8 | include_as_nonheldout_retention_anchor_candidate | critical_sibling_conflict_family | repeated heldout blocker; regression signal; sibling target conflict family; mixed signal family |

### Eval-side critical rows

| target | source | eval_policy | gate_scope | only_sibling_gate_ok | risk_flags |
| --- | --- | --- | --- | --- | --- |
| 7,9 | candidate_d_g2_m15_white_last_8_9_target_safe_7_9_over_live_final_8_8 | restricted_family_level_gate_candidate | external_or_family_level_only_not_sibling_only | no | critical_sibling_conflict_family;not_only_sibling_family_gate |

## Command results

| label | returncode | passed | stdout_log | stderr_log |
| --- | --- | --- | --- | --- |
| train | 0 | True | eval_logs/integration_eval/retention_family_wrapper_run2_weighted/train.stdout.log | eval_logs/integration_eval/retention_family_wrapper_run2_weighted/train.stderr.log |
| gate_1 | 1 | False | eval_logs/integration_eval/retention_family_wrapper_run2_weighted/gate_1.stdout.log | eval_logs/integration_eval/retention_family_wrapper_run2_weighted/gate_1.stderr.log |

## Checkpoint action

- action: `quarantined_failed_candidate_checkpoint`
- candidate_checkpoint: `checkpoints/probes/retention_family_wrapper_run2_weighted_candidate.pt`
- candidate_exists: `True`
- error: ``
- final_checkpoint: `checkpoints/retention_family_wrapper_run2_weighted_pass.pt`
- final_exists_before: `False`
- promote_on_pass: `True`
- quarantine_on_fail: `True`
- quarantine_path: `checkpoints/failed_retention_family_probe/retention_family_wrapper_run2_weighted_candidate.20260617T011627Z.pt`

## Safety interpretation

- This wrapper requires manifest validation before running training or gates.
- Candidate checkpoints should be written only to the candidate checkpoint path.
- Final checkpoint promotion happens only when all gates pass and `--promote-on-pass` is set.
- On gate failure, the wrapper does not promote the candidate checkpoint.
- This wrapper does not export C weights, does not run public benchmarks, and does not make promotion decisions.
