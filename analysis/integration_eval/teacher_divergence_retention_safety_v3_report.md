# Safety v3 teacher-divergence / retention dataset report

This step builds dataset/manifest/report artifacts only. It does not train, export, benchmark, or modify model weights.

## Summary

- base clean v2 rows: 39
- accepted new safety-block rows: 5
- total v3 dataset rows: 44

## Dataset split counts

| split | count |
|---|---:|
| train_teacher_divergence | 25 |
| heldout_retention | 11 |
| train_candidate | 8 |

## Dataset bucket counts

| bucket | count |
|---|---:|
| priority_policy_gap_unavailable | 13 |
| priority_policy_numeric_gap | 12 |
| safety_block_immediate_threat_candidate | 5 |
| diagnose game2 move17 earlier prevention of y=9 horizontal double threat | 3 |
| game2 move15 earlier fork-prevention repair candidate; true last_move included | 3 |
| candidate_g_seed_teacher_divergence | 3 |
| Black should block/occupy 5,11 before White's lower horizontal threat becomes decisive; B final was 4,12. | 1 |
| CE-only v12k raised target rank/prob but live C final stayed 6,6 | 1 |
| CE-only v12k raised target rank/prob but live C final stayed 9,4 | 1 |
| White should block/occupy 10,7 before Black's diagonal threat becomes decisive; B final was 7,11. | 1 |
| diagnose mcts16 final 5,8 versus mcts32/direct final 8,8 at game2 move13 | 1 |

## Accepted safety-block rows

| source_id | sample | side | target | expected | direct | top | final | snapshot |
|---|---|---|---|---|---|---|---|---|
| `safety_block_current_best_legacy_g1_m44` | `legacy_g1_m44` | black | `2,10` | `2,10` | `10,7` | `10,7` | `2,10` | b_mcts16 |
| `safety_block_current_best_legacy_g1_m46` | `legacy_g1_m46` | black | `4,12` | `4,12` | `2,9` | `10,7` | `4,12` | b_mcts16 |
| `safety_block_current_best_legacy_g1_m48` | `legacy_g1_m48` | black | `8,11` | `3,11 8,11` | `10,7` | `10,7` | `8,11` | b_mcts16 |
| `safety_block_current_best_legacy_g2_m29` | `legacy_g2_m29` | white | `4,9` | `4,9` | `3,4` | `3,4` | `4,9` | candidate_d_mcts32_nearend |
| `safety_block_current_best_legacy_g2_m33` | `legacy_g2_m33` | white | `9,6` | `9,11 9,6` | `10,8` | `7,5` | `9,6` | candidate_d_mcts32_nearend |

## Manifest skip reason counts

| reason | count |
|---|---:|
| not_current_best_eval_family | 24 |
| deduped_lower_priority_snapshot | 7 |
| accepted | 5 |

## Acceptance

- decision: ACCEPT
- safety v3 dataset passes structural validation
- only current_best eval-family safety-block candidates are accepted
- one candidate per sample_id is retained using snapshot priority
- no training/export/benchmark has been run

## Interpretation

- These new rows are immediate-threat safety-block teacher candidates, not capacity or training evidence.
- They are accepted only as a small v3 dataset expansion for future training/probe experiments.
- Held-out retention rows from clean v2 remain held out.
