# Retention family trainer finite-loss guard smoke

Scope: negative smoke for trainer guard only. No accepted training, checkpoint, C export, benchmark, or promotion was run.

## Expected behavior

- A zero-weight adapter training dataset must fail before `backward()` / `optimizer.step()`.
- No checkpoint should be written.
- The failure should be explicit, not a silent NaN checkpoint.

## Smoke input

- dataset: `analysis/integration_eval/retention_family_wrapper_run1/train_plain_dataset.json`
- base checkpoint: `checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`
- out checkpoint: `checkpoints/probes/retention_family_trainer_finite_loss_guard_smoke_candidate.pt`

## Smoke stdout

```text
dataset=analysis/integration_eval/retention_family_wrapper_run1/train_plain_dataset.json
rows=2
split_counts={'train_candidate': 2}
role_counts={'nonheldout_retention_anchor': 2}
label_type_counts={'nonheldout_retention_anchor': 2}
device=cpu
base_checkpoint=checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt
out_checkpoint=checkpoints/probes/retention_family_trainer_finite_loss_guard_smoke_candidate.pt
ce_training_rows=2
anchor_kl_splits=('train_candidate',)
anchor_kl_rows=2
mixed_ce_splits=('train_teacher_divergence',)
mixed_ce_label_types=()
mixed_ce_rows=0
mixed_ce_weight_scale=0.1
IMPORTANT: no C export, no benchmark, no promotion/current-best overwrite.
```

## Smoke stderr

```text
Traceback (most recent call last):
  File "/Users/jing1fan/neural-gomoku/scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py", line 981, in <module>
    main()
    ~~~~^^
  File "/Users/jing1fan/neural-gomoku/scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py", line 977, in main
    train(args)
    ~~~~~^^^^^^
  File "/Users/jing1fan/neural-gomoku/scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py", line 794, in train
    train_weight_sum = require_positive_finite_weight_sum(
        "train_candidate",
        weights[train_index_tensor],
    )
  File "/Users/jing1fan/neural-gomoku/scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py", line 787, in require_positive_finite_weight_sum
    raise ValueError(
    ...<3 lines>...
    )
ValueError: train_candidate weight sum must be positive and finite before training: sum=0.0 rows=2
```

## Result

- PASS: positive finite weight-sum guard fired.
- PASS: no checkpoint was written, as verified by the shell smoke check.

## Interpretation

The trainer now rejects the run1 zero-weight adapter dataset before entering the unsafe NaN path. This prevents non-finite policy-head parameters and prevents writing an unsafe checkpoint.

## Explicit non-actions

- No successful training was run.
- No checkpoint was accepted.
- No C weights were exported.
- No benchmark was run.
- No promotion decision was made.
