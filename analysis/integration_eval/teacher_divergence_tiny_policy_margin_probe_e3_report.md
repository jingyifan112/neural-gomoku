# Teacher-divergence tiny policy-margin probe e3

## Branch

`exp/15x15-teacher-divergence-tiny-policy-margin-probe`

## Scope

- Tiny isolated training probe.
- Uses 44-row trainer-ready teacher-divergence dataset.
- Trains policy head only through the existing policy-margin trainer.
- Epochs: 3.
- Saves checkpoint to isolated local path.
- Does not overwrite `checkpoints/15x15_current_best.pt`.
- No C export.
- No public benchmark.
- No promotion.

## Summary

| metric | value |
|---|---:|
| BEFORE rows | 44 |
| AFTER rows | 44 |
| unique BEFORE case_id rows | 32 |
| duplicate case_id groups | 6 |
| epochs logged | 3 |
| checkpoint exists locally | 1 |
| checkpoint size bytes | 1688611 |
| gap improved rows | 44 |
| target prob improved rows | 44 |
| mean gap delta | 0.0025901364 |
| mean target prob delta | 0.0000031641 |
| mean suppress prob delta | -0.0001244870 |

## Epoch metrics

| epoch | loss | margin_loss | anchor_kl | ce |
|---:|---:|---:|---:|---:|
| 001 | 7.672247 | 7.323538 | 0.000000 | 6.974193 |
| 002 | 7.671343 | 7.322673 | 0.000000 | 6.973403 |
| 003 | 7.670440 | 7.321809 | 0.000000 | 6.972610 |

## Worst gap deltas

| row_index | case_id | gap_before | gap_after | gap_delta | target_prob_delta | suppress_prob_delta |
|---:|---|---:|---:|---:|---:|---:|
| 0 | legacy_g2_m11 | -7.1707540000 | -7.1696570000 | 0.0010970000 | 0.0000006600 | 0.0003941700 |
| 5 | legacy_g5_m28 | -4.6509360000 | -4.6489140000 | 0.0020220000 | 0.0000076000 | 0.0000220500 |
| 9 | tdiv_legacy_g5_m28 | -4.9748650000 | -4.9727950000 | 0.0020700000 | 0.0000056200 | 0.0000220500 |
| 18 | tdiv_legacy_g5_m28 | -4.9748650000 | -4.9727950000 | 0.0020700000 | 0.0000056200 | 0.0000220500 |
| 25 | tdiv_legacy_g5_m28 | -4.9748650000 | -4.9727950000 | 0.0020700000 | 0.0000056200 | 0.0000220500 |
| 31 | td_exp_00271 | -4.9748650000 | -4.9727950000 | 0.0020700000 | 0.0000056200 | 0.0000220500 |
| 42 | td_exp_00357 | -4.9748650000 | -4.9727950000 | 0.0020700000 | 0.0000056200 | 0.0000220500 |
| 6 | legacy_g6_m17 | -5.2594310000 | -5.2571630000 | 0.0022680000 | 0.0000046400 | -0.0002871700 |
| 27 | td_exp_00253 | -4.5401360000 | -4.5378470000 | 0.0022890000 | 0.0000080300 | -0.0002391700 |
| 38 | td_exp_00340 | -4.5401360000 | -4.5378470000 | 0.0022890000 | 0.0000080300 | -0.0002391700 |

## Best gap deltas

| row_index | case_id | gap_before | gap_after | gap_delta | target_prob_delta | suppress_prob_delta |
|---:|---|---:|---:|---:|---:|---:|
| 12 | tdiv_legacy_g2_m9 | -7.3496240000 | -7.3464740000 | 0.0031500000 | 0.0000009900 | -0.0003437400 |
| 15 | tdiv_legacy_g2_m9 | -7.3496240000 | -7.3464740000 | 0.0031500000 | 0.0000009900 | -0.0003437400 |
| 21 | tdiv_legacy_g2_m9 | -7.3496240000 | -7.3464740000 | 0.0031500000 | 0.0000009900 | -0.0003437400 |
| 28 | td_exp_00257 | -7.3496240000 | -7.3464740000 | 0.0031500000 | 0.0000009900 | -0.0003437400 |
| 34 | td_exp_00285 | -7.3496240000 | -7.3464740000 | 0.0031500000 | 0.0000009900 | -0.0003437400 |
| 37 | td_exp_00338 | -7.3496240000 | -7.3464740000 | 0.0031500000 | 0.0000009900 | -0.0003437400 |
| 4 | legacy_g5_m14 | -5.4928260000 | -5.4899640000 | 0.0028620000 | 0.0000043000 | -0.0003058900 |
| 11 | tdiv_legacy_g5_m8 | -6.1860610000 | -6.1832490000 | 0.0028120000 | 0.0000037700 | -0.0002183900 |
| 20 | tdiv_legacy_g5_m8 | -6.1860610000 | -6.1832490000 | 0.0028120000 | 0.0000037700 | -0.0002183900 |
| 24 | tdiv_legacy_g5_m8 | -6.1860610000 | -6.1832490000 | 0.0028120000 | 0.0000037700 | -0.0002183900 |

## Decision

This is a local tiny training probe only.

Do not promote.

Do not C export.

Do not run public benchmark.
