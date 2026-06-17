# Retention Family Threshold Train-and-Gate Smoke Closeout

## Scope

This branch runs a threshold-policy train-and-gate smoke through the gated-training wrapper.

Explicit non-actions:

- No final checkpoint promotion.
- No C export.
- No public benchmark.
- No model promotion.
- The generated probe checkpoint is a local smoke artifact and must not be committed.

## Command mode

Wrapper mode:

- mode: `train-and-gate`
- threshold flag: `--eval-prob-epsilon 0.0005`
- promote on pass: `False`
- quarantine on fail: `False`

The wrapper ran two command phases:

1. `train`
2. `gate_1`

Both phases exited with returncode `0`.

## Wrapper result

- overall_status: `gates_passed`
- gates_passed: `True`
- setup_errors: `[]`
- manifest_validation_errors: `[]`
- checkpoint action: `gates_passed_no_promotion_requested`
- candidate checkpoint exists: `True`
- final checkpoint: empty
- promote_on_pass: `False`
- quarantine_on_fail: `False`

## Gate evaluator result

The threshold gate evaluator produced:

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

## Critical protected row

The protected eval row remained safe:

- family: `bd:ea22cc14729b88fd`
- target: `7,9`
- rank: `4 -> 4`
- probability: `0.09005976 -> 0.09247528`
- probability delta: `+0.00241552`
- class: `not_regressed`

## Checkpoint handling

The smoke run created:

- `checkpoints/probes/retention_family_threshold_train_gate_smoke_candidate.pt`

This checkpoint is intentionally excluded from the commit.

The wrapper did not promote it because `--promote-on-pass` was not set.

## Interpretation

This smoke confirms that the threshold policy can pass through the full wrapper train-and-gate path:

- tiny training completes,
- before/after probes are generated,
- evaluator receives `--eval-prob-epsilon 0.0005`,
- gate passes with probability-only warning rows,
- no checkpoint promotion occurs.

This is a pipeline smoke result, not a model promotion result.
