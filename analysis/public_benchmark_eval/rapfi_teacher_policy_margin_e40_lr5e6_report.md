# Rapfi Teacher Policy Margin e40 lr5e-6 Probe

## Summary

- Init checkpoint: `checkpoints/15x15_current_best.pt`
- Trained checkpoint: `checkpoints/15x15_rapfi_teacher_policy_margin_e40_lr5e6.pt`
- Trainer: `scripts/train_rapfi_teacher_policy_margin.py`
- Dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_margin_dataset_corpus8_selected.json`
- Training scope: policy head only
- Epochs: 40
- Learning rate: 5e-6
- Margin: 1.0
- Anchor KL weight: 0.05
- CE weight: 0.10

## Fixed-position direct move result

- current_best direct teacher match: 7/32
- policy_head_e40_lr1e5 direct teacher match: 7/32
- margin_e40_lr5e6 direct teacher match: 7/32
- direct top-move changes vs current_best: 2
- teacher gains: 0
- teacher losses: 0
- off-teacher changes: 2

Changed direct moves:

| sample_id | current_best direct | margin direct | Rapfi teacher | interpretation |
|---|---:|---:|---:|---|
| legacy_g1_m6 | 6,6 | 9,7 | 7,8 | off-teacher change |
| legacy_g2_m11 | 6,5 | 7,4 | 9,7 | off-teacher change |

## Interpretation

This margin run is not a useful candidate.
It did not improve the 32-position direct teacher-match count, and the only direct top-move changes are off-teacher.
The training-phase margin gaps improved slightly, but eval-mode diagnostics did not translate into action-level gains.
This suggests the policy-head BatchNorm train/eval behavior may be interfering with conservative policy-head margin repair.

## Decision

- Do not promote this checkpoint.
- Do not run Rapfi score-gap re-evaluation for this checkpoint.
- Record as a negative margin probe.
- Next step: freeze BatchNorm running stats during policy-head margin training, including policy-head BatchNorm.

