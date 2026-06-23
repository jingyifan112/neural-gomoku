# Teacher-divergence tiny post-training guard audit

## Branch

`exp/15x15-teacher-divergence-tiny-posttrain-guard-audit`

## Scope

- Compares `checkpoints/15x15_current_best.pt` against local tiny probe checkpoint.
- Evaluates 44 trainable teacher-divergence samples.
- Evaluates protected_top10 and tail_rank_gt50 ready rows from the normalized manifest.
- Evaluates corpus8 anchor snapshots for policy drift.
- Does not overwrite current_best.
- Does not C export.
- Does not run public benchmark.
- Does not promote.

## Inputs

- baseline checkpoint: `checkpoints/15x15_current_best.pt`
- candidate checkpoint: `checkpoints/15x15_teacher_divergence_round2_policy_margin_gated_run1_e10.pt`
- trainer-ready dataset: `analysis/integration_eval/teacher_divergence_round2_trainable_trainer_ready_dataset.json`
- normalized manifest: `analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_legacy_suppress_normalized.csv`
- anchor snapshots: `analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json`

## Summary

| metric | value |
|---|---:|
| trainable rows evaluated | 44 |
| trainable gap improved rows | 44 |
| trainable target prob improved rows | 44 |
| trainable target rank regressed rows | 0 |
| trainable mean gap delta | 0.0086329092 |
| protected/tail rows considered | 89 |
| protected/tail rows evaluated | 89 |
| protected/tail target prob regressed rows | 19 |
| protected/tail target rank regressed rows | 0 |
| anchor rows evaluated | 32 |
| anchor top1 changed rows | 0 |
| anchor mean KL ref->candidate | 0.0000018348 |
| anchor max KL ref->candidate | 0.0000060956 |

## Protected/tail bucket counts

| bucket | rows |
|---|---:|
| tail_rank_gt50 | 66 |
| protected_top10 | 23 |

## Protected/tail evaluation status

| status | rows |
|---|---:|
| evaluated | 89 |

## Worst trainable gap deltas

| row_index | case_id | gap_before | gap_after | gap_delta | target_prob_delta | target_rank_delta |
|---:|---|---:|---:|---:|---:|---:|
| 0 | legacy_g2_m11 | -7.1707544327 | -7.1671013832 | 0.0036530495 | 0.0000022003 | 0 |
| 5 | legacy_g5_m28 | -4.6509361267 | -4.6441907883 | 0.0067453384 | 0.0000253997 | 0 |
| 9 | tdiv_legacy_g5_m28 | -4.9748649597 | -4.9679603577 | 0.0069046021 | 0.0000187953 | 0 |
| 18 | tdiv_legacy_g5_m28 | -4.9748649597 | -4.9679603577 | 0.0069046021 | 0.0000187953 | 0 |
| 25 | tdiv_legacy_g5_m28 | -4.9748649597 | -4.9679603577 | 0.0069046021 | 0.0000187953 | 0 |
| 31 | td_exp_00271 | -4.9748649597 | -4.9679603577 | 0.0069046021 | 0.0000187953 | 0 |
| 42 | td_exp_00357 | -4.9748649597 | -4.9679603577 | 0.0069046021 | 0.0000187953 | 0 |
| 6 | legacy_g6_m17 | -5.2594308853 | -5.2518758774 | 0.0075550079 | 0.0000154821 | 0 |
| 27 | td_exp_00253 | -4.5401363373 | -4.5325069427 | 0.0076293945 | 0.0000268170 | 0 |
| 38 | td_exp_00340 | -4.5401363373 | -4.5325069427 | 0.0076293945 | 0.0000268170 | 0 |

## Largest protected/tail rank regressions

| manifest_id | bucket | case_id | rank_before | rank_after | rank_delta | prob_delta |
|---|---|---|---:|---:|---:|---:|
| td_exp_00001 | protected_top10 | legacy_g1_m4 | 4 | 4 | 0 | -0.0000041313 |
| td_exp_00002 | protected_top10 | legacy_g1_m6 | 4 | 4 | 0 | -0.0000414792 |
| td_exp_00003 | tail_rank_gt50 | legacy_g1_m8 | 102 | 102 | 0 | 0.0000010240 |
| td_exp_00004 | protected_top10 | legacy_g1_m40 | 3 | 3 | 0 | -0.0006852001 |
| td_exp_00005 | protected_top10 | legacy_g2_m5 | 5 | 5 | 0 | 0.0000656368 |
| td_exp_00006 | protected_top10 | legacy_g2_m7 | 4 | 4 | 0 | -0.0000556540 |
| td_exp_00007 | protected_top10 | legacy_g2_m9 | 3 | 3 | 0 | -0.0000539273 |
| td_exp_00010 | protected_top10 | legacy_g3_m4 | 9 | 9 | 0 | 0.0000022743 |
| td_exp_00011 | protected_top10 | legacy_g3_m24 | 7 | 7 | 0 | 0.0000056068 |
| td_exp_00012 | protected_top10 | legacy_g3_m26 | 5 | 5 | 0 | 0.0000067605 |
| td_exp_00014 | protected_top10 | legacy_g4_m17 | 4 | 4 | 0 | 0.0000046613 |
| td_exp_00016 | protected_top10 | legacy_g5_m6 | 3 | 3 | 0 | 0.0000288733 |
| td_exp_00017 | protected_top10 | legacy_g5_m8 | 2 | 2 | 0 | 0.0004508868 |
| td_exp_00018 | tail_rank_gt50 | legacy_g5_m12 | 69 | 69 | 0 | 0.0000002243 |
| td_exp_00020 | protected_top10 | legacy_g5_m16 | 2 | 2 | 0 | -0.0000125021 |

## Largest anchor KL rows

| anchor_index | case_id | top1_changed | KL | baseline_top_rc | candidate_top_rc | top_prob_delta |
|---:|---|---:|---:|---|---|---:|
| 3 | anchor_g1_m38 | 0 | 0.0000060956 | `[8, 12]` | `[8, 12]` | -0.0013506413 |
| 1 | anchor_g1_m6 | 0 | 0.0000056708 | `[6, 6]` | `[6, 6]` | -0.0012237728 |
| 6 | anchor_g2_m7 | 0 | 0.0000050254 | `[5, 6]` | `[5, 6]` | 0.0013868809 |
| 24 | anchor_g5_m14 | 0 | 0.0000045886 | `[6, 6]` | `[6, 6]` | -0.0010204017 |
| 31 | anchor_g6_m19 | 0 | 0.0000044847 | `[9, 7]` | `[9, 7]` | 0.0012887120 |
| 30 | anchor_g6_m17 | 0 | 0.0000040423 | `[9, 4]` | `[9, 4]` | -0.0009578466 |
| 4 | anchor_g1_m40 | 0 | 0.0000039165 | `[8, 5]` | `[8, 5]` | 0.0006749630 |
| 7 | anchor_g2_m9 | 0 | 0.0000036565 | `[5, 9]` | `[5, 9]` | -0.0011466742 |
| 8 | anchor_g2_m11 | 0 | 0.0000034964 | `[5, 6]` | `[5, 6]` | 0.0013126433 |
| 29 | anchor_g6_m15 | 0 | 0.0000030417 | `[8, 4]` | `[8, 4]` | -0.0002506226 |

## Outputs

- trainable guard CSV: `analysis/integration_eval/teacher_divergence_gated_training_run1_e10_trainable_gap_guard.csv`
- manifest bucket guard CSV: `analysis/integration_eval/teacher_divergence_gated_training_run1_e10_manifest_bucket_guard.csv`
- anchor drift guard CSV: `analysis/integration_eval/teacher_divergence_gated_training_run1_e10_anchor_drift_guard.csv`
- report: `analysis/integration_eval/teacher_divergence_gated_training_run1_e10_guard_audit.md`

## Decision

This is a post-training guard audit only.

No C export.

No public benchmark.

No promotion.

Use this audit to decide whether a larger gated training run is justified.
