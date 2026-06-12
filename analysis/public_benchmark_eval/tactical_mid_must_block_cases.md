# Tactical-mid Must-block Cases

- source run: `analysis/public_benchmark_eval/local_runs/neural_mcts16_vs_tactical_mid_20260612_104648`
- source categories: `analysis/public_benchmark_eval/tactical_mid_failure_categories.csv`
- total cases: `16`

Each case is the position before neural's final defensive blunder in a tactical_mid loss.

| Case | Game | Neural color | Category | Ply before blunder | Target block | Actual neural move | Threat line after blunder |
|---|---:|---|---|---:|---|---|---|
| `tactical_mid_g1_block_0_8` | 1 | W | `long_diagonal_loss` | 173 | `0,8` | `5,13` | `0,8 1,9 2,10 3,11 4,12` |
| `tactical_mid_g3_block_4_9` | 3 | W | `fast_straight_loss` | 25 | `4,9` | `4,4` | `4,5 4,6 4,7 4,8 4,9` |
| `tactical_mid_g4_block_1_6` | 4 | B | `fast_diagonal_loss` | 30 | `1,6` | `6,11` | `1,6 2,7 3,8 4,9 5,10` |
| `tactical_mid_g6_block_8_4` | 6 | B | `fast_diagonal_loss` | 40 | `8,4` | `3,9` | `4,8 5,7 6,6 7,5 8,4` |
| `tactical_mid_g10_block_10_5` | 10 | B | `fast_straight_loss` | 52 | `10,5` | `10,0` | `10,1 10,2 10,3 10,4 10,5` |
| `tactical_mid_g11_block_7_14` | 11 | W | `mid_diagonal_loss` | 87 | `7,14` | `12,9` | `7,14 8,13 9,12 10,11 11,10` |
| `tactical_mid_g13_block_8_10` | 13 | W | `fast_straight_loss` | 23 | `8,10` | `13,10` | `8,10 9,10 10,10 11,10 12,10` |
| `tactical_mid_g14_block_11_12` | 14 | B | `fast_straight_loss` | 24 | `11,12` | `11,7` | `11,8 11,9 11,10 11,11 11,12` |
| `tactical_mid_g15_block_5_3` | 15 | W | `fast_diagonal_loss` | 35 | `5,3` | `10,8` | `5,3 6,4 7,5 8,6 9,7` |
| `tactical_mid_g17_block_14_7` | 17 | W | `fast_diagonal_loss` | 43 | `14,7` | `11,9` | `10,11 11,10 12,9 13,8 14,7` |
| `tactical_mid_g19_block_6_9` | 19 | W | `fast_diagonal_loss` | 23 | `6,9` | `11,4` | `6,9 7,8 8,7 9,6 10,5` |
| `tactical_mid_g20_block_13_9` | 20 | B | `fast_diagonal_loss` | 26 | `13,9` | `8,4` | `9,5 10,6 11,7 12,8 13,9` |
| `tactical_mid_g21_block_6_10` | 21 | W | `fast_straight_loss` | 33 | `6,10` | `11,10` | `6,10 7,10 8,10 9,10 10,10` |
| `tactical_mid_g22_block_7_9` | 22 | B | `fast_diagonal_loss` | 44 | `7,9` | `12,4` | `7,9 8,8 9,7 10,6 11,5` |
| `tactical_mid_g23_block_9_13` | 23 | W | `fast_diagonal_loss` | 53 | `9,13` | `4,8` | `5,9 6,10 7,11 8,12 9,13` |
| `tactical_mid_g24_block_11_11` | 24 | B | `fast_straight_loss` | 50 | `11,11` | `6,11` | `7,11 8,11 9,11 10,11 11,11` |

## Use

These cases should be used first as a fixed regression test. A candidate model should select the target block move, or at minimum avoid allowing the opponent's immediate five-completion move.
