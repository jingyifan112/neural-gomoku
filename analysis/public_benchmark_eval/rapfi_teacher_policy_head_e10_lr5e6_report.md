# Rapfi Teacher Policy-Head e10 lr5e-6 Probe

## Summary

- Init checkpoint: `checkpoints/15x15_current_best.pt`
- Trained checkpoint: `checkpoints/15x15_rapfi_teacher_policy_head_e10_lr5e6.pt`
- Training scope: `policy_head` only
- Epochs: 10
- Learning rate: 5e-6
- Dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_repair_dataset_corpus8_selected.json`
- Value targets: none

## Fixed-position direct move result

- current_best direct teacher match: 7/32
- policy_head_e10_lr5e6 direct teacher match: 7/32
- direct top-move changes vs current_best: 0

## Teacher move probability/rank probe

- teacher_prob_delta mean: -0.000364801
- teacher_prob_delta median: -0.000658302
- teacher_prob_delta min: -0.004028864
- teacher_prob_delta max: 0.008496031
- teacher rank improved rows: 4
- teacher rank same rows: 17
- teacher rank worsened rows: 4

## Interpretation

This run is too weak to be considered a useful candidate.
It made no action-level direct-policy changes on the 32 selected positions.
Teacher-move rank changes were balanced between improvements and regressions, and average teacher probability slightly decreased.

## Decision

- Do not promote this checkpoint.
- Do not run Rapfi score-gap re-evaluation for this checkpoint because direct top moves did not change.
- Use this as a baseline weak policy-head repair probe before trying a slightly stronger conservative setting.

