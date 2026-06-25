# Teacher-divergence leave-one-out guard review

## Scope

- Leave-one-train-candidate-out no-save probes only.
- No checkpoint save.
- No C export, no public benchmark, no promotion.

## Baseline failure

The full conservative dataset improved the train group but failed protected/tail guards.

- protected top5 delta: -1
- tail top10 delta: -1
- tail rank>50 delta: +2
- tail mean rank delta: +24.666667

## Variant decisions

| drop_case_id | decision | train top10 Δ | train mean_rank Δ | protected top5 Δ | protected top10 Δ | tail top10 Δ | tail rank>50 Δ | tail mean_rank Δ |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| legacy_g4_m13 | FAIL_LEAVE_ONE_OUT_GUARDS | 1.000000 | -5.333333 | 0.000000 | 2.000000 | -1.000000 | 2.000000 | 25.666667 |
| legacy_g4_m23 | FAIL_LEAVE_ONE_OUT_GUARDS | 0.000000 | 1.000000 | 0.000000 | 2.000000 | -1.000000 | 2.000000 | 25.666667 |
| legacy_g5_m28 | FAIL_LEAVE_ONE_OUT_GUARDS | 1.000000 | -4.000000 | 0.000000 | 2.000000 | -1.000000 | 2.000000 | 26.000000 |
| legacy_g6_m17 | FAIL_LEAVE_ONE_OUT_GUARDS | 1.000000 | -5.333333 | 0.000000 | 2.000000 | -1.000000 | 2.000000 | 25.666667 |

## Decision

`LEAVE_ONE_OUT_NO_GUARD_SAFE_SUBSET`

No single train-candidate removal produced a guard-safe subset.

Do not proceed to checkpoint-producing training. Return to data expansion or stronger row-level diagnostics.

## Final note

This review does not authorize checkpoint save, C export, public benchmark, promotion, or current_best overwrite.
