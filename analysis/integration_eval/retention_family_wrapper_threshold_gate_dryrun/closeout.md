# Retention Family Wrapper Threshold Gate Dry-run Closeout

## Scope

This branch validates wrapper-level gates-only execution with the evaluator threshold policy.

Explicit non-actions:

- No training.
- No checkpoint creation.
- No checkpoint promotion.
- No C export.
- No public benchmark.
- No model promotion.

## Purpose

The previous branch added evaluator support for `--eval-prob-epsilon`.

This branch verifies that the existing gated-training wrapper can run a `gates-only` command that passes `--eval-prob-epsilon 0.0005` through to `scripts/evaluate_retention_family_adapter_gates.py`.

No wrapper code change was required because `scripts/run_retention_family_gated_training_probe.py` already accepts full `--gate-cmd` strings and executes them as gate commands.

## Wrapper dry-run

Wrapper command mode:

- mode: `gates-only`
- train manifest: `analysis/integration_eval/retention_family_training_input_dryrun_train_manifest.csv`
- eval manifest: `analysis/integration_eval/retention_family_training_input_dryrun_eval_manifest.csv`
- candidate checkpoint: `checkpoints/probes/retention_family_wrapper_run2_weighted_candidate.pt`
- promote on pass: `False`
- quarantine on fail: `False`

Gate command included:

- `--eval-prob-epsilon 0.0005`
- `--max-eval-rank-regressed 0`
- `--max-eval-prob-regressed 0`
- `--require-train-improvement`

## Wrapper result

- overall_status: `gates_passed`
- gates_passed: `True`
- setup_errors: `[]`
- manifest_validation_errors: `[]`
- gate command returncode: `0`
- gate command passed: `True`
- checkpoint action: `gates_passed_no_promotion_requested`
- candidate checkpoint existed: `False`
- final checkpoint: empty
- promotion requested: `False`

The candidate checkpoint path did not need to exist for this dry-run because no promotion was requested.

## Gate evaluator result

The wrapper-invoked gate evaluator produced:

- decision: `PASS`
- failures: `[]`
- eval rows: `9`
- train rows: `2`
- eval rank regressions: `0`
- eval probability regressions: `3`
- eval hard probability regressions: `0`
- eval probability warnings: `3`
- eval probability epsilon: `0.0005`
- train improved rows: `1`

## Interpretation

The wrapper-level gates-only run confirms that the threshold evaluator policy can be wired into the gated-training wrapper by passing the evaluator flag inside `--gate-cmd`.

The gate result remains a dry-run validation only. It does not retroactively promote the run2 checkpoint and does not create or move any checkpoint.
