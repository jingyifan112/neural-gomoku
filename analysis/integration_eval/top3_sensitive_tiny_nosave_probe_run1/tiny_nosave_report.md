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

- dataset: `analysis/integration_eval/top3_sensitive_tiny_nosave_probe_run1/tiny_primary_positive_ce_train_candidate_dataset.json`
- base_checkpoint: `checkpoints/15x15_current_best.pt`
- out_checkpoint: `analysis/integration_eval/top3_sensitive_tiny_nosave_probe_run1/SHOULD_NOT_SAVE.pt`
- eval_csv: `analysis/integration_eval/top3_sensitive_tiny_nosave_probe_run1/tiny_nosave_eval.csv`
- rows: 3
- split_counts: `{'train_candidate': 3}`
- role_counts: `{'top3_sensitive_positive_ce': 3}`
- label_type_counts: `{'neighbor': 1, 'late_loss_window': 1, 'first_losing_value': 1}`

## Training config

- train_scope: `policy_head`
- epochs: 30
- lr: 1e-07
- kl_weight: 0.35
- weight_decay: 0.0
- seed: 17
- saved_checkpoint: False

## Summary by split

| phase | split | rows | top1 | top1_rate | mean_rank | mean_target_prob | mean_target_ce |
|---|---|---:|---:|---:|---:|---:|---:|
| before | train_candidate | 3 | 0 | 0.000 | 25.33 | 0.000803 | 7.707536 |
| before | ALL | 3 | 0 | 0.000 | 25.33 | 0.000803 | 7.707536 |
| after | train_candidate | 3 | 0 | 0.000 | 26.00 | 0.000522 | 8.297368 |
| after | ALL | 3 | 0 | 0.000 | 26.00 | 0.000522 | 8.297368 |

## Before/after movement

| split | rank_improved | rank_same | rank_regressed | prob_improved | prob_same | prob_regressed |
|---|---:|---:|---:|---:|---:|---:|
| train_candidate | 0 | 1 | 2 | 0 | 0 | 3 |
| train_teacher_divergence | 0 | 0 | 0 | 0 | 0 | 0 |
| heldout_retention | 0 | 0 | 0 | 0 | 0 | 0 |

## Train candidate rows

| id | label_type | side | target | weight |
|---|---|---|---|---:|
| `legacy_g2_m11` | `neighbor` | white | 9,7 | 3.75 |
| `legacy_g2_m21` | `late_loss_window` | white | 7,9 | 3.00 |
| `legacy_g5_m14` | `first_losing_value` | black | 7,9 | 6.99 |

## Decision

This artifact only measures whether the accepted 8-row candidate subset can move policy mass toward its targets while tracking retention/teacher-divergence side effects. It is not an export, benchmark, promotion, or capacity decision.
