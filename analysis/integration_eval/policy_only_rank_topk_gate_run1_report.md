# Policy-only rank/top-k gate dry-run report

## Scope

- Evaluation only: no optimizer, no training, no checkpoint save.
- No C export, no public benchmark, no promotion.
- Dataset: analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json
- Model A: checkpoints/15x15_current_best.pt
- Model B: checkpoints/15x15_policy_rank_topk_probe_run1.pt
- Margin: 0.25
- Dataset name: rapfi_teacher_policy_multisuppress_dataset_corpus8_selected

## Summary

| metric | model_a | model_b | delta |
|---|---:|---:|---:|
| target top-3 rows | 5 | 7 | 2.0 |
| target top-5 rows | 11 | 11 | 0.0 |
| target top-10 rows | 15 | 16 | 1.0 |
| target rank > 50 rows | 3 | 3 | 0.0 |
| mean target rank | 18.56 | 19.12 | 0.5600000000000023 |
| mean worst suppress gap | -4.9541279983520505 | -5.247486562728882 | -0.29335856437683105 |
| mean multi-pair hinge | 2.879263942718506 | 3.0207434062957765 | 0.1414794635772707 |
| teacher beats worst suppress rows | 0 | 0 | 0.0 |
| teacher beats all suppressors rows | 0 | 0 | 0.0 |

## Protected checks

| check | value |
|---|---:|
| rows | 25 |
| protected top-10 regressions | 0 |
| finite numeric checks passed | True |
| anchor rows loaded | 32 |
| anchor status | loaded |

## Gate checks

| check | result |
|---|---|
| top3_delta >= +2: 2.0 | recorded |
| top5_delta >= +3: 0.0 | recorded |
| top10_delta >= +3: 1.0 | recorded |
| rank_gt50_delta <= 0: 0.0 | recorded |
| protected_top10_regressions == 0: 0 | recorded |
| mean_worst_suppress_gap_delta > 0: -0.29335856437683105 | recorded |
| mean_multi_pair_hinge_delta < 0: 0.1414794635772707 | recorded |
| teacher_beats_worst_delta >= +2: 0.0 | recorded |
| teacher_beats_all_suppressors_delta >= +1: 0.0 | recorded |

## Worst target-rank rows after model B

| case_id | target_rank_a | target_rank_b | target_prob_a | target_prob_b | worst_gap_a | worst_gap_b |
|---|---:|---:|---:|---:|---:|---:|
| legacy_g1_m8 | 102 | 111 | 0.00018429 | 0.00011610 | -7.888449 | -7.744753 |
| legacy_g5_m12 | 69 | 91 | 0.00039491 | 0.00021625 | -7.094744 | -7.526626 |
| legacy_g5_m30 | 73 | 78 | 0.00021954 | 0.00015349 | -7.507614 | -7.904798 |
| legacy_g2_m21 | 47 | 45 | 0.00014416 | 0.00002612 | -8.742455 | -10.528414 |
| legacy_g5_m14 | 17 | 24 | 0.00194023 | 0.00124898 | -5.492826 | -5.850782 |
| legacy_g4_m13 | 21 | 16 | 0.00024368 | 0.00025320 | -7.601815 | -7.687962 |
| legacy_g2_m11 | 12 | 15 | 0.00032455 | 0.00002822 | -7.170754 | -10.349101 |
| legacy_g5_m28 | 17 | 13 | 0.00365030 | 0.00417404 | -4.650936 | -4.937486 |
| legacy_g4_m23 | 23 | 11 | 0.00152231 | 0.00210128 | -5.669407 | -5.532399 |
| legacy_g6_m17 | 15 | 10 | 0.00270314 | 0.00575866 | -5.259431 | -4.520464 |
| legacy_g3_m26 | 5 | 9 | 0.00419021 | 0.00662204 | -5.395764 | -4.686000 |
| legacy_g3_m4 | 9 | 6 | 0.00723689 | 0.00783077 | -4.646803 | -4.657707 |
| legacy_g3_m24 | 7 | 6 | 0.00318027 | 0.01919844 | -5.701507 | -3.650239 |
| legacy_g6_m19 | 7 | 6 | 0.02625631 | 0.00617702 | -3.034372 | -4.895124 |
| legacy_g1_m4 | 4 | 5 | 0.01358208 | 0.00766659 | -3.980762 | -4.672293 |

## Verdict

FAIL_CANDIDATE_GATE

## Decision

Dry-run only. Do not train, export, public benchmark, or promote from this branch.
If this baseline self-check passes, the next step can compare a real candidate checkpoint with the same evaluator.
