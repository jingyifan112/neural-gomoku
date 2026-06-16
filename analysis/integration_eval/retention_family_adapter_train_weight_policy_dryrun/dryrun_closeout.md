# Retention family adapter train weight policy dry-run

Scope: guarded trainer dry-run only. No training, checkpoint, C export, benchmark, or promotion was run.

## Input

- weighted dataset: `analysis/integration_eval/retention_family_training_consumer_adapter_train_weighted_dataset.json`
- base checkpoint: `checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`
- dry-run out checkpoint path: `checkpoints/probes/retention_family_adapter_train_weight_policy_dryrun_should_not_write.pt`

## Result

- PASS: weighted adapter train dataset completed trainer `--dry-run`.
- PASS: no checkpoint was written.
- PASS: dry-run did not enter the previous zero-weight NaN path.

## Dry-run stdout

```text
dataset=analysis/integration_eval/retention_family_training_consumer_adapter_train_weighted_dataset.json
rows=2
split_counts={'train_candidate': 2}
role_counts={'nonheldout_retention_anchor': 2}
label_type_counts={'nonheldout_retention_anchor': 2}
device=cpu
base_checkpoint=checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt
out_checkpoint=checkpoints/probes/retention_family_adapter_train_weight_policy_dryrun_should_not_write.pt
ce_training_rows=2
anchor_kl_splits=('train_candidate',)
anchor_kl_rows=2
mixed_ce_splits=('train_teacher_divergence',)
mixed_ce_label_types=()
mixed_ce_rows=0
mixed_ce_weight_scale=0.1
IMPORTANT: no C export, no benchmark, no promotion/current-best overwrite.
loaded checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt
loaded checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt
dry-run: no training, no checkpoint, no eval/report writes
BEFORE holdout_candidate_d_g2_m15_white_last_8_9_target_live_direct_7_10_over_live_final_8_8 target=7,10 rank=5 prob=0.08013161 top=4,7
BEFORE holdout_candidate_d_g2_m15_white_last_8_9_target_safe_10_7_over_live_final_8_8 target=10,7 rank=2 prob=0.10073009 top=4,7
```

## Dry-run stderr

```text

```

## Interpretation

The adapter-side positive train-weight materialization fixes the immediate zero-weight denominator issue discovered in wrapper run1 while preserving the trainer finite-loss guard as a safety backstop.

## Explicit non-actions

- No training was run.
- No optimizer step was run.
- No checkpoint was saved.
- No C weights were exported.
- No benchmark was run.
- No promotion decision was made.
