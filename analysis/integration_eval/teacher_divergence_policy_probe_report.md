# Teacher-divergence policy probe report

## Scope

- Small policy-focused signal probe only.
- Trains only `split == train_candidate` rows.
- Value head has no explicit loss in this probe.
- No C export.
- No benchmark.
- No promotion or current-best overwrite.
- No model-capacity conclusion.

## Inputs

- dataset: `analysis/integration_eval/teacher_divergence_retention_safety_v3_dataset.json`
- base_checkpoint: `checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`
- out_checkpoint: `checkpoints/15x15_teacher_divergence_policy_probe.pt`
- eval_csv: `analysis/integration_eval/teacher_divergence_policy_probe_eval.csv`
- rows: 44
- split_counts: `{'heldout_retention': 11, 'train_candidate': 8, 'train_teacher_divergence': 25}`
- role_counts: `{'heldout_retention_anchor': 11, 'teacher_divergence': 33}`
- label_type_counts: `{'policy_target': 11, 'policy_teacher': 3, 'policy_teacher_safety_block': 5, 'late_loss_window': 7, 'first_direct_vs_mcts_divergence;neighbor': 1, 'neighbor': 10, 'first_direct_vs_mcts_divergence': 2, 'first_direct_vs_mcts_divergence;late_loss_window': 1, 'neighbor;late_loss_window': 1, 'first_losing_value;neighbor': 1, 'first_losing_value': 2}`

## Training config

- train_scope: `policy_head`
- epochs: 80
- lr: 3e-05
- kl_weight: 0.25
- weight_decay: 0.0001
- seed: 17
- saved_checkpoint: True

## Summary by split

| phase | split | rows | top1 | top1_rate | mean_rank | mean_target_prob | mean_target_ce |
|---|---|---:|---:|---:|---:|---:|---:|
| before | train_candidate | 8 | 0 | 0.000 | 30.75 | 0.016975 | 5.259307 |
| before | train_teacher_divergence | 25 | 0 | 0.000 | 17.32 | 0.025559 | 5.021928 |
| before | heldout_retention | 11 | 3 | 0.273 | 21.82 | 0.163256 | 3.768061 |
| before | ALL | 44 | 3 | 0.068 | 20.89 | 0.058423 | 4.751621 |
| after | train_candidate | 8 | 0 | 0.000 | 15.88 | 0.087917 | 3.944442 |
| after | train_teacher_divergence | 25 | 0 | 0.000 | 14.68 | 0.023285 | 5.605874 |
| after | heldout_retention | 11 | 4 | 0.364 | 21.45 | 0.192500 | 4.337299 |
| after | ALL | 44 | 4 | 0.091 | 16.59 | 0.077340 | 4.986652 |

## Before/after movement

| split | rank_improved | rank_same | rank_regressed | prob_improved | prob_same | prob_regressed |
|---|---:|---:|---:|---:|---:|---:|
| train_candidate | 8 | 0 | 0 | 8 | 0 | 0 |
| train_teacher_divergence | 7 | 10 | 8 | 6 | 0 | 19 |
| heldout_retention | 2 | 6 | 3 | 4 | 0 | 7 |

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
