# Policy-only rank/top-k gate dry-run report

## Scope

- Evaluation only: no optimizer, no training, no checkpoint save.
- No C export, no public benchmark, no promotion.
- Dataset: analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json
- Model A: checkpoints/15x15_current_best.pt
- Model B: checkpoints/15x15_current_best.pt
- Margin: 1.0
- Dataset name: rapfi_teacher_policy_multisuppress_dataset_corpus8_selected

## Summary

| metric | model_a | model_b | delta |
|---|---:|---:|---:|
| target top-3 rows | 5 | 5 | 0.0 |
| target top-5 rows | 11 | 11 | 0.0 |
| target top-10 rows | 15 | 15 | 0.0 |
| target rank > 50 rows | 3 | 3 | 0.0 |
| mean target rank | 18.56 | 18.56 | 0.0 |
| mean worst suppress gap | -4.9541279983520505 | -4.9541279983520505 | 0.0 |
| mean multi-pair hinge | 3.524614627838135 | 3.524614627838135 | 0.0 |
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
| baseline-vs-baseline self-check; improvement thresholds are not applied | recorded |

## Worst target-rank rows after model B

| case_id | target_rank_a | target_rank_b | target_prob_a | target_prob_b | worst_gap_a | worst_gap_b |
|---|---:|---:|---:|---:|---:|---:|
| legacy_g1_m8 | 102 | 102 | 0.00018429 | 0.00018429 | -7.888449 | -7.888449 |
| legacy_g5_m30 | 73 | 73 | 0.00021954 | 0.00021954 | -7.507614 | -7.507614 |
| legacy_g5_m12 | 69 | 69 | 0.00039491 | 0.00039491 | -7.094744 | -7.094744 |
| legacy_g2_m21 | 47 | 47 | 0.00014416 | 0.00014416 | -8.742455 | -8.742455 |
| legacy_g4_m23 | 23 | 23 | 0.00152231 | 0.00152231 | -5.669407 | -5.669407 |
| legacy_g4_m13 | 21 | 21 | 0.00024368 | 0.00024368 | -7.601815 | -7.601815 |
| legacy_g5_m14 | 17 | 17 | 0.00194023 | 0.00194023 | -5.492826 | -5.492826 |
| legacy_g5_m28 | 17 | 17 | 0.00365030 | 0.00365030 | -4.650936 | -4.650936 |
| legacy_g6_m17 | 15 | 15 | 0.00270314 | 0.00270314 | -5.259431 | -5.259431 |
| legacy_g2_m11 | 12 | 12 | 0.00032455 | 0.00032455 | -7.170754 | -7.170754 |
| legacy_g3_m4 | 9 | 9 | 0.00723689 | 0.00723689 | -4.646803 | -4.646803 |
| legacy_g3_m24 | 7 | 7 | 0.00318027 | 0.00318027 | -5.701507 | -5.701507 |
| legacy_g6_m19 | 7 | 7 | 0.02625631 | 0.02625631 | -3.034372 | -3.034372 |
| legacy_g6_m5 | 6 | 6 | 0.00362991 | 0.00362991 | -5.461506 | -5.461506 |
| legacy_g2_m5 | 5 | 5 | 0.01223993 | 0.01223993 | -4.265397 | -4.265397 |

## Verdict

PASS_SELF_CHECK

## Decision

Dry-run only. Do not train, export, public benchmark, or promote from this branch.
If this baseline self-check passes, the next step can compare a real candidate checkpoint with the same evaluator.
