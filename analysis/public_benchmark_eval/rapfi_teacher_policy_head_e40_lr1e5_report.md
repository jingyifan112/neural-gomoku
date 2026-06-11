# Rapfi Teacher Policy-Head e40 lr1e-5 Probe

## Summary

- Init checkpoint: `checkpoints/15x15_current_best.pt`
- Trained checkpoint: `checkpoints/15x15_rapfi_teacher_policy_head_e40_lr1e5.pt`
- Training scope: `policy_head` only
- Epochs: 40
- Learning rate: 1e-5
- Dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_repair_dataset_corpus8_selected.json`
- Value targets: none

## Fixed-position direct move result

- current_best direct teacher match: 7/32
- policy_head_e40_lr1e5 direct teacher match: 7/32
- direct top-move changes vs current_best: 2
- teacher gains: 0
- teacher losses: 0

Changed direct moves:

| sample_id | current_best direct | e40 direct | Rapfi teacher | interpretation |
|---|---:|---:|---:|---|
| legacy_g1_m6 | 6,6 | 9,7 | 7,8 | off-teacher change |
| legacy_g2_m11 | 6,5 | 7,4 | 9,7 | off-teacher change |

## Teacher move probability/rank probe

- teacher_prob_delta_vs_current mean: 0.004011819
- teacher_prob_delta_vs_current median: -0.000090751
- teacher_prob_delta_vs_current min: -0.003935449
- teacher_prob_delta_vs_current max: 0.051127106
- teacher rank improved rows: 12
- teacher rank same rows: 13
- teacher rank worsened rows: 0

## Interpretation

This run is stronger than the e10 lr5e-6 probe in teacher-rank movement.
However, it still does not improve the 32-position direct teacher-match count.
The two direct top-move changes are both off-teacher moves, so this is not a promotion candidate.

## Decision

- Do not promote this checkpoint.
- Do not run Rapfi score-gap re-evaluation for this checkpoint.
- Record as a weak/partial policy-head-only probe.
- Stop escalating this simple policy-head-only direction unless a future dataset or loss adds stronger constraints.

