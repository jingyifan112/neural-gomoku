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

- dataset: `analysis/integration_eval/retention_family_training_consumer_adapter_train_weighted_dataset.json`
- base_checkpoint: `checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`
- out_checkpoint: `checkpoints/probes/retention_family_threshold_train_gate_smoke_candidate.pt`
- eval_csv: `analysis/integration_eval/retention_family_threshold_train_gate_smoke/train_script_eval.csv`
- rows: 2
- split_counts: `{'train_candidate': 2}`
- role_counts: `{'nonheldout_retention_anchor': 2}`
- label_type_counts: `{'nonheldout_retention_anchor': 2}`

## Training config

- train_scope: `policy_head`
- epochs: 1
- lr: 1e-05
- kl_weight: 1.0
- anchor_kl_splits: `train_candidate`
- mixed_ce_anchor_splits: `train_teacher_divergence`
- mixed_ce_anchor_label_types: ``
- mixed_ce_anchor_weight_scale: 0.1
- mixed_ce_anchor_max_rows: 0
- weight_decay: 0.0001
- seed: 17
- saved_checkpoint: True

## Summary by split

| phase | split | rows | top1 | top1_rate | mean_rank | mean_target_prob | mean_target_ce |
|---|---|---:|---:|---:|---:|---:|---:|
| before | train_candidate | 2 | 0 | 0.000 | 3.50 | 0.090431 | 2.409698 |
| before | ALL | 2 | 0 | 0.000 | 3.50 | 0.090431 | 2.409698 |
| after | train_candidate | 2 | 0 | 0.000 | 3.50 | 0.092251 | 2.392214 |
| after | ALL | 2 | 0 | 0.000 | 3.50 | 0.092251 | 2.392214 |

## Before/after movement

| split | rank_improved | rank_same | rank_regressed | prob_improved | prob_same | prob_regressed |
|---|---:|---:|---:|---:|---:|---:|
| train_candidate | 0 | 2 | 0 | 1 | 0 | 1 |
| train_teacher_divergence | 0 | 0 | 0 | 0 | 0 | 0 |
| heldout_retention | 0 | 0 | 0 | 0 | 0 | 0 |

## Train candidate rows

| id | label_type | side | target | weight |
|---|---|---|---|---:|
| `holdout_candidate_d_g2_m15_white_last_8_9_target_live_direct_7_10_over_live_final_8_8` | `nonheldout_retention_anchor` | white | 7,10 | 1.00 |
| `holdout_candidate_d_g2_m15_white_last_8_9_target_safe_10_7_over_live_final_8_8` | `nonheldout_retention_anchor` | white | 10,7 | 1.00 |

## Decision

This artifact only measures whether the accepted 8-row candidate subset can move policy mass toward its targets while tracking retention/teacher-divergence side effects. It is not an export, benchmark, promotion, or capacity decision.
