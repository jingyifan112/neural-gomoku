# Tactical-mid Too-late Double-threat C Engine Evaluation

- engine: `c_inference/pbrain-neural-gomoku`
- weights: `weights/15x15_current_best_weights.bin`
- move mode: `mcts_safe`
- mcts sims: `16`
- cases: `analysis/public_benchmark_eval/tactical_mid_must_block_cases.json`
- total cases: `16`
- diagnostic: `too_late_double_threat` means the opponent already has at least two immediate winning moves before the recorded neural move.
- interpretation: C final repeating the match blunder confirms engine parity with the public match, but these cases are too late for single-target block training.

## Summary

| Metric | Count | Rate |
|---|---:|---:|
| debug line found | 16/16 | 1.000 |
| too_late_double_threat positions | 16/16 | 1.000 |
| single-terminal must-block positions | 0/16 | 0.000 |
| C final selects exact target endpoint | 0/16 | 0.000 |
| C final repeats match blunder | 16/16 | 1.000 |

## Case details

| Case | Label | Opp win count | Opponent immediate wins | Target | Match blunder | C direct | C safety | C mcts_raw | C mcts_safety | C final/stdout | Exact target | Same blunder |
|---|---|---:|---|---|---|---|---|---|---|---|---|---|
| `tactical_mid_g1_block_0_8` | `too_late_double_threat` | 2 | `0,8 5,13` | `0,8` | `5,13` | `0,10` | `5,13` | `0,10` | `5,13` | `5,13` | False | True |
| `tactical_mid_g3_block_4_9` | `too_late_double_threat` | 2 | `4,4 4,9` | `4,9` | `4,4` | `2,8` | `4,4` | `2,8` | `4,4` | `4,4` | False | True |
| `tactical_mid_g4_block_1_6` | `too_late_double_threat` | 2 | `1,6 6,11` | `1,6` | `6,11` | `4,14` | `6,11` | `4,14` | `6,11` | `6,11` | False | True |
| `tactical_mid_g6_block_8_4` | `too_late_double_threat` | 2 | `8,4 3,9` | `8,4` | `3,9` | `6,8` | `3,9` | `6,8` | `3,9` | `3,9` | False | True |
| `tactical_mid_g10_block_10_5` | `too_late_double_threat` | 2 | `10,0 10,5` | `10,5` | `10,0` | `10,0` | `10,0` | `10,0` | `10,0` | `10,0` | False | True |
| `tactical_mid_g11_block_7_14` | `too_late_double_threat` | 2 | `12,9 7,14` | `7,14` | `12,9` | `7,2` | `12,9` | `7,2` | `12,9` | `12,9` | False | True |
| `tactical_mid_g13_block_8_10` | `too_late_double_threat` | 2 | `8,10 13,10` | `8,10` | `13,10` | `9,6` | `13,10` | `9,6` | `13,10` | `13,10` | False | True |
| `tactical_mid_g14_block_11_12` | `too_late_double_threat` | 2 | `11,7 11,12` | `11,12` | `11,7` | `14,10` | `11,7` | `14,10` | `11,7` | `11,7` | False | True |
| `tactical_mid_g15_block_5_3` | `too_late_double_threat` | 2 | `5,3 10,8` | `5,3` | `10,8` | `10,8` | `10,8` | `10,8` | `10,8` | `10,8` | False | True |
| `tactical_mid_g17_block_14_7` | `too_late_double_threat` | 2 | `14,7 11,9` | `14,7` | `11,9` | `6,7` | `11,9` | `6,7` | `11,9` | `11,9` | False | True |
| `tactical_mid_g19_block_6_9` | `too_late_double_threat` | 2 | `11,4 6,9` | `6,9` | `11,4` | `11,4` | `11,4` | `11,4` | `11,4` | `11,4` | False | True |
| `tactical_mid_g20_block_13_9` | `too_late_double_threat` | 2 | `8,4 13,9` | `13,9` | `8,4` | `6,1` | `8,4` | `6,1` | `8,4` | `8,4` | False | True |
| `tactical_mid_g21_block_6_10` | `too_late_double_threat` | 2 | `6,10 11,10` | `6,10` | `11,10` | `11,6` | `11,10` | `11,6` | `11,10` | `11,10` | False | True |
| `tactical_mid_g22_block_7_9` | `too_late_double_threat` | 2 | `12,4 7,9` | `7,9` | `12,4` | `8,3` | `12,4` | `8,3` | `12,4` | `12,4` | False | True |
| `tactical_mid_g23_block_9_13` | `too_late_double_threat` | 2 | `4,8 9,13` | `9,13` | `4,8` | `9,3` | `4,8` | `9,3` | `4,8` | `4,8` | False | True |
| `tactical_mid_g24_block_11_11` | `too_late_double_threat` | 2 | `6,11 11,11` | `11,11` | `6,11` | `5,12` | `6,11` | `5,12` | `6,11` | `6,11` | False | True |
