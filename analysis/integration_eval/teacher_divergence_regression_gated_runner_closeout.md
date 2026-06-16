# Teacher-divergence regression-gated runner closeout

## Scope

This closeout records the first regression-gated teacher-divergence policy runner.

The runner is designed to prevent failed probe configurations from saving checkpoints.

It does not:

- export C weights
- run benchmarks
- promote a model
- overwrite current-best
- make a model-capacity conclusion

## Implemented runner

Script:

- `scripts/run_teacher_divergence_regression_gated_policy_probe.py`

Default outputs:

- eval CSV: `analysis/integration_eval/teacher_divergence_policy_regression_gated_probe_eval.csv`
- training report: `analysis/integration_eval/teacher_divergence_policy_regression_gated_probe_train_report.md`
- gate report: `analysis/integration_eval/teacher_divergence_policy_regression_gated_probe_gate_report.md`
- checkpoint path if allowed: `checkpoints/15x15_teacher_divergence_policy_regression_gated_probe.pt`

## Runner behavior

The runner performs the following sequence:

1. Run the anchored policy probe in no-save mode.
2. Evaluate before/after metrics by split.
3. Apply regression gates.
4. Save checkpoint only if:
   - all gates pass
   - `--save-on-pass` is set

If gates fail, no checkpoint is saved.

## Default validation result

The default configuration matches the previous best failed baseline:

- epochs: 80
- learning rate: 3e-5
- KL weight: 0.35
- CE: train_candidate
- KL anchor: train_candidate + train_teacher_divergence
- heldout_retention: evaluation-only

Result:

- decision: FAIL
- saved_checkpoint: False

Failures:

- train_teacher_divergence prob_regressed 15 > 10
- train_teacher_divergence rank_regressed 6 > 5
- heldout_retention prob_regressed 7 > 4
- heldout_retention rank_regressed 4 > 3

## Decision

Close as: regression-gated checkpoint protection implemented and validated.

The branch does not produce a new candidate model. Its value is procedural: failed probe configurations are blocked from saving checkpoints.

## Next step

Future training variants should run through this gated runner.

No C export, benchmark, promotion, or current-best replacement should occur unless a configuration passes the regression gates first.
