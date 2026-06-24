# b4c96 Stage C failure forensics review

## Branch

`exp/15x15-b4c96-stagec-failure-forensics`

## Purpose

Review the failed b4c96-safe Stage C rank/top-k gate after the capacity/data pairing chain.

This route is analysis only. It reads the existing Stage C gate CSV and produces row-level failure buckets.

## Inputs

- Gate CSV: `analysis/integration_eval/capacity_data_pairing_probe/gate_eval.csv`
- Prior final review: `analysis/integration_eval/capacity_data_pairing_final_review.md`
- Forensics script: `scripts/analyze_b4c96_stagec_gate_failure.py`

## Generated outputs

- `analysis/integration_eval/b4c96_stagec_failure_forensics.csv`
- `analysis/integration_eval/b4c96_stagec_failure_forensics_summary.json`
- `analysis/integration_eval/b4c96_stagec_failure_forensics.md`

## Diagnosis

`B4C96_STAGEC_FAILED_DUE_TO_PROTECTED_OR_OBJECTIVE_REGRESSION`

The Stage C failure is not merely a strict-threshold issue. Model B shows real regression across protected and objective metrics.

## Top-k movement

| metric | Model A | Model B | delta |
|---|---:|---:|---:|
| target top-3 rows | 7 | 7 | 0 |
| target top-5 rows | 11 | 9 | -2 |
| target top-10 rows | 14 | 15 | +1 |
| target rank > 50 rows | 3 | 4 | +1 |

Model B gained one top-10 row, but lost two top-5 rows and introduced one additional rank>50 tail row.

## Mean deltas

| metric | delta |
|---|---:|
| target rank | +2.200000 |
| target probability | -0.006594 |
| primary gap | -0.193933 |
| worst suppress gap | -0.485118 |
| multi-pair hinge | +0.273795 |

Because lower rank and lower hinge are better, these mean deltas are net negative overall.

## Direction counts

| metric | improved | same | regressed |
|---|---:|---:|---:|
| rank | 8 | 6 | 11 |
| target probability | 11 | 0 | 14 |
| primary gap | 13 | 0 | 12 |
| worst suppress gap | 12 | 0 | 13 |
| multi-pair hinge | 11 | 0 | 14 |

The candidate is split roughly between improvements and regressions, but regressions dominate the gate-critical fields.

## Forensics outcomes

| outcome | rows |
|---|---:|
| directionally_useful | 9 |
| partial_tail_repair_unresolved | 1 |
| mixed_or_regressed | 5 |
| severe_core_regression | 10 |

This is the key result: the candidate has a nontrivial useful subset, but it also has an equally large severe-regression subset.

## Failure tags

| tag | rows |
|---|---:|
| prob_regression | 14 |
| multi_pair_hinge_regression | 14 |
| worst_gap_regression | 13 |
| primary_gap_regression | 12 |
| rank_regression | 11 |
| core_improved | 10 |
| core_regressed | 10 |
| tail_rank_gt50_after_b | 4 |
| top5_lost | 3 |
| new_tail_rank_gt50 | 2 |
| protected_top10_regression | 1 |
| top10_lost | 1 |

## Hard fail reasons

- `protected_top10_regression_nonzero`
- `target_top5_delta_negative`
- `rank_gt50_delta_positive`
- `mean_worst_suppress_gap_delta_negative`
- `mean_multi_pair_hinge_delta_positive`

## Worst regression examples

The worst objective regressions include:

- `legacy_g2_m5`: top-5 lost, rank 4 -> 8, worst gap delta -2.954720
- `legacy_g5_m14`: new tail rank>50, rank 11 -> 56, worst gap delta -2.449941
- `legacy_g5_m8`: rank 2 -> 5, target probability delta -0.081057
- `legacy_g2_m21`: new tail rank>50, rank 39 -> 51, worst gap delta -2.256331
- `legacy_g3_m26`: protected top-10 regression, rank 7 -> 13

## Interpretation

The b4c96 capacity/data pairing did produce some useful row-level movement, but it did not produce a stable candidate.

The failure pattern indicates:

1. Capacity increase plus increased multi-suppress data is not sufficient by itself.
2. The current objective/weighting allows severe regressions on protected and near-protected rows.
3. Tail rows remain unstable and can become worse.
4. The route should not continue into another b4c96 training run without objective/data controls.

## Recommended next route

Open a new design/probe route focused on gate-informed training controls:

`exp/15x15-b4c96-gate-informed-objective-ablation`

The next route should compare, without promotion:

1. protected-row anchor weighting
2. tail-row prune or cap policy
3. severe-regression family downweighting
4. objective ablation between CE, rank/top-k, and multi-suppress hinge
5. no-save smoke/probe before any checkpoint candidate is written

## Actions not performed

- no training
- no checkpoint write
- no C export
- no public benchmark
- no promotion
- no overwrite of `current_best`
- no overwrite of manifests
- no modification of old untracked local artifacts

## Final decision

`B4C96_STAGEC_FAILURE_FORENSICS_REVIEW_COMPLETE_NO_PROMOTION`
