# Teacher-divergence mixed-CE anchored policy probe report

## Scope

- Mixed-CE anchored policy-focused signal probe only.
- Main cross-entropy trains `split == train_candidate` rows.
- Low-weight mixed CE can also train selected anchor rows.
- KL anchors `train_candidate` and `train_teacher_divergence` to the base policy distribution.
- `heldout_retention` is evaluation-only and is not used in the loss.
- Value head has no explicit loss in this probe.
- No C export.
- No benchmark.
- No promotion or current-best overwrite.
- No model-capacity conclusion.

## Inputs

- dataset: `analysis/integration_eval/teacher_divergence_retention_safety_v3_dataset.json`
- base_checkpoint: `checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`
- out_checkpoint: `checkpoints/15x15_teacher_divergence_policy_mixed_ce_anchor_probe_w0025_gated.pt`
- eval_csv: `analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_w0025_gated_eval.csv`
- rows: 44
- split_counts: `{'heldout_retention': 11, 'train_candidate': 8, 'train_teacher_divergence': 25}`
- role_counts: `{'heldout_retention_anchor': 11, 'teacher_divergence': 33}`
- label_type_counts: `{'policy_target': 11, 'policy_teacher': 3, 'policy_teacher_safety_block': 5, 'late_loss_window': 7, 'first_direct_vs_mcts_divergence;neighbor': 1, 'neighbor': 10, 'first_direct_vs_mcts_divergence': 2, 'first_direct_vs_mcts_divergence;late_loss_window': 1, 'neighbor;late_loss_window': 1, 'first_losing_value;neighbor': 1, 'first_losing_value': 2}`

## Training config

- train_scope: `policy_head`
- epochs: 80
- lr: 3e-05
- kl_weight: 0.35
- anchor_kl_splits: `train_candidate,train_teacher_divergence`
- mixed_ce_anchor_splits: `train_teacher_divergence`
- mixed_ce_anchor_label_types: ``
- mixed_ce_anchor_weight_scale: 0.025
- mixed_ce_anchor_max_rows: 0
- weight_decay: 0.0001
- seed: 17
- saved_checkpoint: False

## Summary by split

| phase | split | rows | top1 | top1_rate | mean_rank | mean_target_prob | mean_target_ce |
|---|---|---:|---:|---:|---:|---:|---:|
| before | train_candidate | 8 | 0 | 0.000 | 30.75 | 0.016975 | 5.259307 |
| before | train_teacher_divergence | 25 | 0 | 0.000 | 17.32 | 0.025559 | 5.021928 |
| before | heldout_retention | 11 | 3 | 0.273 | 21.82 | 0.163256 | 3.768061 |
| before | ALL | 44 | 3 | 0.068 | 20.89 | 0.058423 | 4.751621 |
| after | train_candidate | 8 | 0 | 0.000 | 15.88 | 0.088438 | 3.946572 |
| after | train_teacher_divergence | 25 | 0 | 0.000 | 12.76 | 0.034864 | 4.929464 |
| after | heldout_retention | 11 | 4 | 0.364 | 20.82 | 0.192396 | 4.262980 |
| after | ALL | 44 | 4 | 0.091 | 15.34 | 0.083988 | 4.584135 |

## Before/after movement

| split | rank_improved | rank_same | rank_regressed | prob_improved | prob_same | prob_regressed |
|---|---:|---:|---:|---:|---:|---:|
| train_candidate | 8 | 0 | 0 | 8 | 0 | 0 |
| train_teacher_divergence | 14 | 9 | 2 | 17 | 0 | 8 |
| heldout_retention | 3 | 4 | 4 | 4 | 0 | 7 |

## Train candidate rows

| id | label_type | side | target | weight |
|---|---|---|---|---:|
| `tdiv_candidate_g_g1_p22_black` | `policy_teacher` | black | 4,8 | 2.00 |
| `tdiv_candidate_g_g2_p15_white` | `policy_teacher` | white | 7,9 | 1.50 |
| `tdiv_candidate_g_g2_p17_white` | `policy_teacher` | white | 9,10 | 2.00 |
| `tdiv_safety_block_current_best_legacy_g1_m44` | `policy_teacher_safety_block` | black | 2,10 | 1.50 |
| `tdiv_safety_block_current_best_legacy_g1_m46` | `policy_teacher_safety_block` | black | 4,12 | 1.50 |
| `tdiv_safety_block_current_best_legacy_g1_m48` | `policy_teacher_safety_block` | black | 8,11 | 1.50 |
| `tdiv_safety_block_current_best_legacy_g2_m29` | `policy_teacher_safety_block` | white | 4,9 | 1.50 |
| `tdiv_safety_block_current_best_legacy_g2_m33` | `policy_teacher_safety_block` | white | 9,6 | 1.50 |

## Decision

This artifact only measures whether the accepted 8-row candidate subset can move policy mass toward its targets while tracking retention/teacher-divergence side effects. It is not an export, benchmark, promotion, or capacity decision.
