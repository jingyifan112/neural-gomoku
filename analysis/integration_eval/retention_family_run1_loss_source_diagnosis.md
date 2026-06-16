# Retention family run1 loss source diagnosis

Scope: forward-level diagnosis only. No training loop, optimizer step, checkpoint save, C export, benchmark, or promotion was run.

## Inputs

- train_dataset: `analysis/integration_eval/retention_family_wrapper_run1/train_plain_dataset.json`
- train_script: `scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py`
- base_checkpoint: `checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`
- candidate_checkpoint: `checkpoints/failed_retention_family_probe/retention_family_wrapper_run1_candidate.pt`
- candidate_checkpoint_exists: `True`
- model config: board_size=15, channels=64, blocks=4

## Checkpoint summaries

| checkpoint | params finite | bad params | forwardable rows | nonfinite logits rows | nonfinite CE rows | nonfinite KL rows | row errors |
| --- | --- | --- | --- | --- | --- | --- | --- |
| base | True | 0 | 0 | 0 | 0 | 0 | {'missing_feature_tensor': 2, 'missing_mask_tensor': 2} |
| candidate_quarantined | False | 101607 | 0 | 0 | 0 | 0 | {'missing_feature_tensor': 2, 'missing_mask_tensor': 2} |

## Row-level loss checks

| checkpoint | row | label_type | target | target legal | logits bad | logprob bad | target_prob | weighted_ce | anchor_kl | errors |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 1 | nonheldout_retention_anchor | (7, 10) |  |  |  |  |  |  | missing_feature_tensor;missing_mask_tensor |
| base | 2 | nonheldout_retention_anchor | (10, 7) |  |  |  |  |  |  | missing_feature_tensor;missing_mask_tensor |
| candidate_quarantined | 1 | nonheldout_retention_anchor | (7, 10) |  |  |  |  |  |  | missing_feature_tensor;missing_mask_tensor |
| candidate_quarantined | 2 | nonheldout_retention_anchor | (10, 7) |  |  |  |  |  |  | missing_feature_tensor;missing_mask_tensor |

## Likely causes

- `candidate_checkpoint_contains_nonfinite_parameters`

## Interpretation

If the base checkpoint has finite parameters and finite per-row CE, but the quarantined candidate has non-finite parameters/logits/CE/KL, then the NaN was introduced during the tiny training step rather than by invalid adapter rows.

If both base and candidate forward checks are finite, then the NaN likely comes from the legacy trainer's aggregation/reporting path rather than the raw forward CE/KL calculations.

## Explicit non-actions

- No training loop was run.
- No optimizer step was run.
- No checkpoint was saved.
- No C weights were exported.
- No benchmark was run.
- No promotion decision was made.
