# Teacher-divergence train candidate generation

## Scope

- Candidate source generation only.
- No final dataset materialization.
- No training.
- No checkpoint save.
- No C export, no public benchmark, no promotion.

## Inputs

- board snapshots: `analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json`
- reference dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_conservative_plus_generated_tail_guards_dryrun.json`
- model checkpoint: `checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`
- model arch: `b4c64`

## Rank policy

- train candidate rank band: `11` to `50`
- protected reference: `<= 10`
- tail reference: `> 50`
- min train target: `12`

## Summary

- snapshots scanned: `32`
- candidate rows: `30`
- P1 train candidates: `8` / `12`
- protected reference candidates: `17`
- tail reference candidates: `5`
- gap reference candidates: `0`

## Skipped counts

| reason | count |
|---|---:|
| board_target_identity_already_exists | 19 |
| no_candidate_target_extracted | 2 |

## Top train candidates

| case_id | game | move | side | target_rc | rank | prob | source_field |
|---|---:|---:|---|---|---:|---:|---|
| `traingen_g5_m30_t2_4_9` | 5 | 30 | black | `[4, 9]` | 48 | 0.00082598 | `policy_safety` |
| `traingen_g6_m17_t0_7_9` | 6 | 17 | white | `[7, 9]` | 47 | 0.000386197 | `direct` |
| `traingen_g1_m38_t1_12_8` | 1 | 38 | black | `[12, 8]` | 46 | 0.000913961 | `direct` |
| `traingen_g4_m21_t1_10_8` | 4 | 21 | white | `[10, 8]` | 44 | 0.00013093 | `direct` |
| `traingen_g4_m13_t0_8_4` | 4 | 13 | white | `[8, 4]` | 23 | 0.000450608 | `direct` |
| `traingen_g5_m8_t1_8_5` | 5 | 8 | black | `[8, 5]` | 20 | 0.00317801 | `policy_safety` |
| `traingen_g5_m28_t2_5_11` | 5 | 28 | black | `[5, 11]` | 18 | 0.00423876 | `policy_safety` |
| `traingen_g5_m30_t0_9_9` | 5 | 30 | black | `[9, 9]` | 17 | 0.00433257 | `previous_rapfi_bestline` |

## Decision

`TRAIN_CANDIDATE_GENERATION_PARTIAL`

## Final note

This output does not authorize training, checkpoint save, C export, public benchmark, promotion, or current_best overwrite.
