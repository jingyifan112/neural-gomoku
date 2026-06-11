# Rapfi Teacher Policy Margin BN-freeze e40 lr5e-6 Probe

## Summary

- Init checkpoint: `checkpoints/15x15_current_best.pt`
- Trained checkpoint: `checkpoints/15x15_rapfi_teacher_policy_margin_bnfreeze_e40_lr5e6.pt`
- Trainer: `scripts/train_rapfi_teacher_policy_margin.py`
- Dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_margin_dataset_corpus8_selected.json`
- Training scope: policy head only
- BatchNorm mode: frozen/eval, including policy-head BatchNorm
- Epochs: 40
- Learning rate: 5e-6
- Margin: 1.0
- Anchor KL weight: 0.05
- CE weight: 0.10

## Fixed-position direct move result

- current_best direct teacher match: 7/32
- policy_head_e40_lr1e5 direct teacher match: 7/32
- margin_e40_lr5e6 direct teacher match: 7/32
- margin_bnfreeze_e40_lr5e6 direct teacher match: 7/32
- direct top-move changes vs current_best: 1
- teacher gains: 0
- teacher losses: 0
- off-teacher changes: 1

Changed direct moves:

| sample_id | current_best direct | BN-freeze margin direct | Rapfi teacher | interpretation |
|---|---:|---:|---:|---|
| legacy_g1_m6 | 6,6 | 9,7 | 7,8 | off-teacher change |

## Interpretation

This run fixed the train/eval inconsistency seen in the earlier non-BN-freeze margin run.
Training gaps and eval-mode AFTER diagnostics now move in the same direction.
However, the effect size is still too small: direct teacher-match count remains 7/32, and the only changed direct top move is off-teacher.

## Decision

- Do not promote this checkpoint.
- Do not run Rapfi score-gap re-evaluation for this checkpoint.
- Record as a partial/negative BN-freeze margin probe.
- If continuing this direction, use BN-freeze as the required trainer mode, but increase margin-repair strength carefully.

