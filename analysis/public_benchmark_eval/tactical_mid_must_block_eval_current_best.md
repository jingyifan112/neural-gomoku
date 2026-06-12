# Tactical-mid Must-block Evaluation

- checkpoint: `checkpoints/15x15_current_best.pt`
- cases: `analysis/public_benchmark_eval/tactical_mid_must_block_cases.json`
- total cases: `16`

## Summary

| Metric | Count | Rate |
|---|---:|---:|
| direct selects exact target | 0/16 | 0.000 |
| policy_safety selects exact target | 7/16 | 0.438 |
| direct blocks immediate win | 3/16 | 0.188 |
| policy_safety blocks immediate win | 16/16 | 1.000 |

## Category counts

| Category | Count |
|---|---:|
| `fast_diagonal_loss` | 8 |
| `fast_straight_loss` | 6 |
| `long_diagonal_loss` | 1 |
| `mid_diagonal_loss` | 1 |

## Case details

| Case | Category | Target | Direct | Safety | Target rank | Blunder rank | Direct blocks | Safety blocks |
|---|---|---|---|---|---:|---:|---|---|
| `tactical_mid_g1_block_0_8` | `long_diagonal_loss` | `0,8` | `0,10` | `0,8` | 27 | 19 | False | True |
| `tactical_mid_g3_block_4_9` | `fast_straight_loss` | `4,9` | `2,8` | `4,4` | 36 | 2 | False | True |
| `tactical_mid_g4_block_1_6` | `fast_diagonal_loss` | `1,6` | `4,14` | `1,6` | 126 | 4 | False | True |
| `tactical_mid_g6_block_8_4` | `fast_diagonal_loss` | `8,4` | `6,8` | `8,4` | 34 | 21 | False | True |
| `tactical_mid_g10_block_10_5` | `fast_straight_loss` | `10,5` | `10,0` | `10,0` | 41 | 1 | True | True |
| `tactical_mid_g11_block_7_14` | `mid_diagonal_loss` | `7,14` | `7,2` | `12,9` | 117 | 38 | False | True |
| `tactical_mid_g13_block_8_10` | `fast_straight_loss` | `8,10` | `9,6` | `8,10` | 85 | 70 | False | True |
| `tactical_mid_g14_block_11_12` | `fast_straight_loss` | `11,12` | `14,10` | `11,7` | 96 | 2 | False | True |
| `tactical_mid_g15_block_5_3` | `fast_diagonal_loss` | `5,3` | `10,8` | `5,3` | 146 | 1 | True | True |
| `tactical_mid_g17_block_14_7` | `fast_diagonal_loss` | `14,7` | `6,7` | `14,7` | 21 | 18 | False | True |
| `tactical_mid_g19_block_6_9` | `fast_diagonal_loss` | `6,9` | `11,4` | `11,4` | 6 | 1 | True | True |
| `tactical_mid_g20_block_13_9` | `fast_diagonal_loss` | `13,9` | `6,1` | `8,4` | 55 | 8 | False | True |
| `tactical_mid_g21_block_6_10` | `fast_straight_loss` | `6,10` | `11,6` | `6,10` | 87 | 67 | False | True |
| `tactical_mid_g22_block_7_9` | `fast_diagonal_loss` | `7,9` | `8,3` | `12,4` | 112 | 12 | False | True |
| `tactical_mid_g23_block_9_13` | `fast_diagonal_loss` | `9,13` | `9,3` | `4,8` | 134 | 5 | False | True |
| `tactical_mid_g24_block_11_11` | `fast_straight_loss` | `11,11` | `5,12` | `6,11` | 97 | 20 | False | True |
