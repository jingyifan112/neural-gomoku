# b4c96-safe policy-only rank/top-k gate report

## Scope

- Evaluation only: no optimizer, no training, no checkpoint save.
- No C export, no public benchmark, no promotion, and manifest files are not modified.
- Dataset: analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json
- Model A: checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt
- Model B: checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt
- Margin: 1.0
- Dataset name: rapfi_teacher_policy_multisuppress_dataset_corpus8_selected

## Architecture

- board_size: 15
- win_length: 5
- model_a_channels: 64
- model_a_blocks: 4
- model_b_channels: 96
- model_b_blocks: 4

## Summary

| metric | model_a | model_b | delta |
|---|---:|---:|---:|
| target top-3 rows | 7 | 7 | 0.0 |
| target top-5 rows | 11 | 9 | -2.0 |
| target top-10 rows | 14 | 15 | 1.0 |
| target rank > 50 rows | 3 | 4 | 1.0 |
| mean target rank | 17.32 | 19.52 | 2.1999999999999993 |
| mean worst suppress gap | -4.4300531387329105 | -4.915171098709107 | -0.4851179599761961 |
| mean multi-pair hinge | 3.1204478454589837 | 3.3942427883148194 | 0.2737949428558357 |
| teacher beats worst suppress rows | 0 | 0 | 0.0 |
| teacher beats all suppressors rows | 0 | 0 | 0.0 |

## Protected checks

| check | value |
|---|---:|
| rows | 25 |
| protected top-10 regressions | 1 |
| finite numeric checks passed | True |
| anchor rows loaded | 32 |
| anchor status | loaded |

## Gate checks

| check | result |
|---|---|
| top3_delta >= +2: 0.0 | recorded |
| top5_delta >= +3: -2.0 | recorded |
| top10_delta >= +3: 1.0 | recorded |
| rank_gt50_delta <= 0: 1.0 | recorded |
| protected_top10_regressions == 0: 1 | recorded |
| mean_worst_suppress_gap_delta > 0: -0.4851179599761961 | recorded |
| mean_multi_pair_hinge_delta < 0: 0.2737949428558357 | recorded |
| teacher_beats_worst_delta >= +2: 0.0 | recorded |
| teacher_beats_all_suppressors_delta >= +1: 0.0 | recorded |

## Worst target-rank rows after model B

| case_id | target_rank_a | target_rank_b | target_prob_a | target_prob_b | worst_gap_a | worst_gap_b |
|---|---:|---:|---:|---:|---:|---:|
| legacy_g5_m12 | 69 | 106 | 0.00083295 | 0.00018624 | -6.156615 | -7.504747 |
| legacy_g1_m8 | 102 | 75 | 0.00038893 | 0.00076429 | -6.780863 | -5.891213 |
| legacy_g5_m14 | 11 | 56 | 0.00661942 | 0.00080527 | -4.123430 | -6.573371 |
| legacy_g2_m21 | 39 | 51 | 0.00030841 | 0.00003364 | -7.981966 | -10.238297 |
| legacy_g5_m30 | 53 | 48 | 0.00066022 | 0.00049970 | -6.481031 | -5.794907 |
| legacy_g2_m11 | 12 | 20 | 0.00094675 | 0.00019027 | -6.464814 | -8.045073 |
| legacy_g4_m13 | 28 | 18 | 0.00031777 | 0.00116715 | -7.411632 | -5.876796 |
| legacy_g3_m4 | 11 | 16 | 0.00638845 | 0.00202391 | -4.635986 | -6.061881 |
| legacy_g6_m17 | 14 | 14 | 0.00403065 | 0.00565321 | -4.910375 | -3.790089 |
| legacy_g3_m26 | 7 | 13 | 0.00514369 | 0.00139435 | -5.169128 | -6.448565 |
| legacy_g2_m5 | 4 | 8 | 0.01439602 | 0.00086503 | -4.068874 | -7.023594 |
| legacy_g4_m23 | 21 | 8 | 0.00350194 | 0.00727156 | -4.536165 | -4.477715 |
| legacy_g5_m28 | 16 | 7 | 0.00493708 | 0.02499621 | -4.291985 | -2.887359 |
| legacy_g4_m17 | 4 | 6 | 0.00406494 | 0.00046738 | -5.468346 | -7.633388 |
| legacy_g6_m5 | 3 | 6 | 0.00779676 | 0.01649907 | -4.687284 | -3.151553 |

## Verdict

FAIL_CANDIDATE_GATE

## Decision

Evaluation only. Do not train, export, public benchmark, promote, or modify manifest files from this wrapper.
