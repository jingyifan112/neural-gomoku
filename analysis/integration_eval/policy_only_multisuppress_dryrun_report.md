# Policy-only multi-suppress dry-run report

## Scope

- Dry-run only: no optimizer, no training, no checkpoint save.
- Dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json`
- Init checkpoint: `checkpoints/15x15_current_best.pt`
- Anchor snapshots: `analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json`
- Margin: `1.0`
- Loss reduction: `mean`

## Summary

| metric | value |
|---|---:|
| rows | 25 |
| anchor rows | 32 |
| suppress count min | 5 |
| suppress count mean | 5.0 |
| suppress count max | 5 |
| top3 target rows | 5 |
| top5 target rows | 11 |
| top10 target rows | 15 |
| target rank > 10 | 10 |
| target rank > 50 | 3 |
| mean target rank | 18.56 |
| mean primary gap | -4.954128 |
| mean worst suppress gap | -4.954128 |
| median worst suppress gap | -5.318236 |
| mean multi-pair hinge | 3.524615 |

## Worst suppress gaps

| case_id | target_rank | suppress_count | primary_gap | worst_suppress_gap | worst_suppress_rc |
|---|---:|---:|---:|---:|---|
| legacy_g2_m21 | 47 | 5 | -8.742455 | -8.742455 | `[4, 2]` |
| legacy_g1_m8 | 102 | 5 | -7.888449 | -7.888449 | `[6, 6]` |
| legacy_g4_m13 | 21 | 5 | -7.601815 | -7.601815 | `[4, 6]` |
| legacy_g5_m30 | 73 | 5 | -7.507614 | -7.507614 | `[3, 7]` |
| legacy_g2_m11 | 12 | 5 | -7.170754 | -7.170754 | `[5, 6]` |
| legacy_g5_m12 | 69 | 5 | -7.094744 | -7.094744 | `[6, 6]` |
| legacy_g3_m24 | 7 | 5 | -5.701507 | -5.701507 | `[6, 7]` |
| legacy_g4_m23 | 23 | 5 | -5.669407 | -5.669407 | `[3, 7]` |
| legacy_g5_m14 | 17 | 5 | -5.492826 | -5.492826 | `[6, 6]` |
| legacy_g6_m5 | 6 | 5 | -5.461506 | -5.461506 | `[8, 8]` |
| legacy_g3_m26 | 5 | 5 | -5.395764 | -5.395764 | `[6, 7]` |
| legacy_g5_m6 | 3 | 5 | -5.364775 | -5.364775 | `[8, 9]` |
| legacy_g4_m17 | 4 | 5 | -5.318236 | -5.318236 | `[9, 9]` |
| legacy_g6_m17 | 15 | 5 | -5.259431 | -5.259431 | `[9, 4]` |
| legacy_g5_m28 | 17 | 5 | -4.650936 | -4.650936 | `[4, 5]` |

## High target-rank tail

| case_id | target_rank | target_prob | primary_gap | worst_suppress_gap |
|---|---:|---:|---:|---:|
| legacy_g1_m8 | 102 | 0.00018429 | -7.888449 | -7.888449 |
| legacy_g5_m30 | 73 | 0.00021954 | -7.507614 | -7.507614 |
| legacy_g5_m12 | 69 | 0.00039491 | -7.094744 | -7.094744 |
| legacy_g2_m21 | 47 | 0.00014416 | -8.742455 | -8.742455 |
| legacy_g4_m23 | 23 | 0.00152231 | -5.669407 | -5.669407 |
| legacy_g4_m13 | 21 | 0.00024368 | -7.601815 | -7.601815 |
| legacy_g5_m14 | 17 | 0.00194023 | -5.492826 | -5.492826 |
| legacy_g5_m28 | 17 | 0.00365030 | -4.650936 | -4.650936 |
| legacy_g6_m17 | 15 | 0.00270314 | -5.259431 | -5.259431 |
| legacy_g2_m11 | 12 | 0.00032455 | -7.170754 | -7.170754 |

## Interpretation

The multi-suppress dataset can be loaded and legally scored. This is still dry-run only. Training should only be implemented after this schema and diagnostics are accepted.

## Status

Dry-run only. No training, no checkpoint, no C export, no public benchmark, no promotion.
