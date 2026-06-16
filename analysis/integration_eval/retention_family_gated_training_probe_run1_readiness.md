# Retention family gated training probe run1 readiness

Scope: readiness review only. No training, checkpoint save, C export, benchmark, or promotion was run.

## Discovery result

The existing runner `scripts/run_teacher_divergence_regression_gated_policy_probe.py` has useful gating behavior, including `--save-on-pass`, but it still operates around the older teacher-divergence probe split contract.

Relevant observed properties:

- It supports `--save-on-pass`.
- It supports `--out-checkpoint`.
- It supports heldout regression gates.
- It still references `heldout_retention` directly.
- It does not expose `--train-manifest` / `--eval-manifest` inputs for the retention-family training-input dry-run contract.

## Readiness decision

Decision: **BLOCK actual training for run1 until the train command consumes the retention-family manifest contract.**

The next actual training probe must not rely only on old `heldout_retention` labels. It must explicitly consume:

- `analysis/integration_eval/retention_family_training_input_dryrun_train_manifest.csv`
- `analysis/integration_eval/retention_family_training_input_dryrun_eval_manifest.csv`

and must enforce:

- `train_use_policy=include_as_nonheldout_retention_anchor_candidate`
- `eval_use_policy`
- `gate_scope`
- `allowed_as_only_sibling_family_gate`

## Critical family rule

For `bd:ea22cc14729b88fd`:

- `7,10` must be training-side / non-heldout retention anchor candidate.
- `10,7` must be training-side / non-heldout retention anchor candidate.
- `7,9` may remain eval-side only with restricted gate scope.
- `7,9` must not be the only sibling-family heldout gate for `7,10` or `10,7`.

## Required next implementation step

Add or adapt a training-consumer wrapper that:

1. Builds an actual temporary training dataset from the train manifest.
2. Builds an actual gate/eval dataset from the eval manifest.
3. Calls the existing Python training script only on the derived train-side dataset.
4. Calls gates only on the derived eval-side dataset with retention-family restrictions.
5. Saves/promotes checkpoint only through `scripts/run_retention_family_gated_training_probe.py`.
6. Produces a run report.
7. Does not export C weights.
8. Does not run public benchmarks.
9. Does not make a promotion decision.

## Explicit non-actions

- No model training was run.
- No checkpoint was saved.
- No C weights were exported.
- No benchmark was run.
- No promotion decision was made.
