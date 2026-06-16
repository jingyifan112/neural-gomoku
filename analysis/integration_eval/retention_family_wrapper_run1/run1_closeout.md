# Retention family wrapper-controlled run1 closeout

Scope: one tiny wrapper-controlled gated training probe. No C export, public benchmark, or promotion decision was run.

## Wrapper result

- overall_status: `gates_failed`
- gates_passed: `False`
- checkpoint_action: `quarantined_failed_candidate_checkpoint`
- candidate_checkpoint: `checkpoints/probes/retention_family_wrapper_run1_candidate.pt`
- quarantine_path: `checkpoints/failed_retention_family_probe/retention_family_wrapper_run1_candidate.pt`
- final_checkpoint: `checkpoints/retention_family_wrapper_run1_pass.pt`
- final_exists_before: `False`

## Command results

| label | returncode | passed | stdout | stderr |
| --- | --- | --- | --- | --- |
| train | 0 | True | `eval_logs/integration_eval/retention_family_wrapper_run1/train.stdout.log` | `eval_logs/integration_eval/retention_family_wrapper_run1/train.stderr.log` |
| gate_1 | 1 | False | `eval_logs/integration_eval/retention_family_wrapper_run1/gate_1.stdout.log` | `eval_logs/integration_eval/retention_family_wrapper_run1/gate_1.stderr.log` |

## Gate result

- decision: `FAIL`
- failures: `['eval rank regressions 8 > 0', 'eval top1 losses: 3', 'critical 7,9 eval gate regressed', 'no train-side row improved']`
- counts: `{'eval_prob_regressed': 0, 'eval_rank_regressed': 8, 'side_counts': {'eval': 9, 'train': 2}, 'train_improved': 0}`

## Training observation

- The tiny training command completed and produced a candidate checkpoint.
- The training log reported `loss=nan`, `main_ce=nan`, and `anchor_kl=nan`.
- Because adapter-aware gates failed, the candidate checkpoint was quarantined and no final pass checkpoint was created.

## Interpretation

Run1 is a valid negative/failed gated probe. It proves the wrapper-controlled flow can execute training, probe before/after, evaluate adapter-aware gates, and prevent an unsafe checkpoint from becoming a final pass checkpoint.

The result should not be interpreted as a model improvement. The observed NaN loss and gate regressions indicate the next probe should first diagnose train-row target/probability validity or adjust the tiny training objective before any larger run.

## Explicit non-actions

- No C weights were exported.
- No public benchmark was run.
- No current-best checkpoint was overwritten.
- No model promotion decision was made.
