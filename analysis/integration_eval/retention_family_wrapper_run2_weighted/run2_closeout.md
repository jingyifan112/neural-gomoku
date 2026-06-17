# Retention family wrapper-controlled run2 weighted closeout

Scope: one tiny wrapper-controlled gated training probe using the positive-weight adapter train dataset. No C export, public benchmark, or promotion decision was run.

## Wrapper result

- overall_status: `gates_failed`
- gates_passed: `False`
- checkpoint_action: `quarantined_failed_candidate_checkpoint`
- candidate_checkpoint: `checkpoints/probes/retention_family_wrapper_run2_weighted_candidate.pt`
- quarantine_path: `checkpoints/failed_retention_family_probe/retention_family_wrapper_run2_weighted_candidate.20260617T011627Z.pt`
- final_checkpoint: `checkpoints/retention_family_wrapper_run2_weighted_pass.pt`
- final_exists_before: `False`

## Command results

| label | returncode | passed | stdout | stderr |
| --- | --- | --- | --- | --- |
| train | 0 | True | `eval_logs/integration_eval/retention_family_wrapper_run2_weighted/train.stdout.log` | `eval_logs/integration_eval/retention_family_wrapper_run2_weighted/train.stderr.log` |
| gate_1 | 1 | False | `eval_logs/integration_eval/retention_family_wrapper_run2_weighted/gate_1.stdout.log` | `eval_logs/integration_eval/retention_family_wrapper_run2_weighted/gate_1.stderr.log` |

## Gate result

- decision: `FAIL`
- failures: `['eval prob regressions 3 > 0']`
- counts: `{'eval_prob_regressed': 3, 'eval_rank_regressed': 0, 'side_counts': {'eval': 9, 'train': 2}, 'train_improved': 1}`

## Training observation

- epoch line: `epoch 001/1 loss=2.505464 main_ce=2.375920 mixed_ce_unscaled=0.000000 mixed_ce=0.000000 anchor_kl=0.129543`
- Training completed with finite loss values, unlike run1.
- The positive-weight adapter train dataset avoided the previous zero-weight NaN path.
- The candidate was still rejected by adapter-aware gates because eval probability regressions exceeded the strict threshold.

## Interpretation

Run2 is a valid negative/failed gated probe. It confirms that the train-weight policy and finite-loss guard fixed the run1 NaN failure mode, but the resulting one-epoch policy-head update still does not satisfy retention gates.

This should not be interpreted as a model improvement. The correct next step is analysis of the three eval probability regressions, not C export, benchmark, or promotion.

## Explicit non-actions

- No C weights were exported.
- No public benchmark was run.
- No current-best checkpoint was overwritten.
- No model promotion decision was made.
