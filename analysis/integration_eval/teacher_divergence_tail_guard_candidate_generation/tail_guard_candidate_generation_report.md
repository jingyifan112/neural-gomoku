# Teacher-divergence tail guard candidate generation

## Scope

- Candidate source generation only.
- No final dataset materialization.
- No training.
- No checkpoint save.
- No C export, no public benchmark, no promotion.

## Manual schema patch

- snapshot board field: `board_snapshot_before_decision`
- optional after field: `board_snapshot_after_decision`
- side field: `side_to_move`
- game id field: `game_number`
- move id field: `move_count`

## Summary

- snapshots scanned: `32`
- candidate rows: `49`
- P0 tail guard candidates: `17` / `12`
- near-tail review candidates: `3`
- tail rank threshold: `>50`

## Skipped counts

| reason | count |
|---|---:|
| no_candidate_target_extracted | 2 |

## Top tail candidates

| case_id | game | move | side | target_rc | rank | prob | source_field |
|---|---:|---:|---|---|---:|---:|---|
| `tailgen_g2_m7_t0_9_5` | 2 | 7 | white | `[9, 5]` | 200 | 3.91636e-06 | `direct` |
| `tailgen_g1_m6_t0_9_7` | 1 | 6 | black | `[9, 7]` | 172 | 1.09029e-05 | `direct` |
| `tailgen_g2_m9_t0_9_5` | 2 | 9 | white | `[9, 5]` | 170 | 1.34869e-05 | `direct` |
| `tailgen_g4_m23_t2_12_9` | 4 | 23 | white | `[12, 9]` | 166 | 1.2981e-05 | `policy_safety` |
| `tailgen_g5_m28_t1_7_3` | 5 | 28 | black | `[7, 3]` | 161 | 1.44085e-05 | `direct` |
| `tailgen_g5_m30_t1_7_3` | 5 | 30 | black | `[7, 3]` | 152 | 1.50188e-05 | `direct` |
| `tailgen_g5_m16_t0_7_5` | 5 | 16 | black | `[7, 5]` | 140 | 7.15315e-05 | `direct` |
| `tailgen_g5_m10_t0_10_7` | 5 | 10 | black | `[10, 7]` | 116 | 0.000317205 | `direct` |
| `tailgen_g2_m21_t1_2_4` | 2 | 21 | white | `[2, 4]` | 108 | 4.50069e-06 | `direct` |
| `tailgen_g4_m17_t2_10_6` | 4 | 17 | white | `[10, 6]` | 104 | 2.84858e-06 | `policy_safety` |
| `tailgen_g1_m40_t1_12_6` | 1 | 40 | black | `[12, 6]` | 97 | 9.62003e-05 | `policy_safety` |
| `tailgen_g1_m4_t0_7_6` | 1 | 4 | black | `[7, 6]` | 82 | 0.000451137 | `direct` |
| `tailgen_g4_m17_t1_10_8` | 4 | 17 | white | `[10, 8]` | 77 | 6.39163e-06 | `direct` |
| `tailgen_g4_m21_t1_10_8` | 4 | 21 | white | `[10, 8]` | 76 | 8.78085e-06 | `direct` |
| `tailgen_g3_m24_t1_3_7` | 3 | 24 | black | `[3, 7]` | 76 | 1.58585e-05 | `policy_safety` |
| `tailgen_g6_m17_t0_7_9` | 6 | 17 | white | `[7, 9]` | 68 | 0.000165653 | `direct` |
| `tailgen_g2_m21_t0_9_7` | 2 | 21 | white | `[9, 7]` | 51 | 3.36431e-05 | `previous_rapfi_bestline` |

## Decision

`TAIL_GUARD_CANDIDATE_GENERATION_TARGET_MET`

The P0 tail guard candidate target is met at source-review level.

Next step should be review/materialization only. These rows must remain heldout tail guards.

## Final note

This output does not authorize training, checkpoint save, C export, public benchmark, promotion, or current_best overwrite.
