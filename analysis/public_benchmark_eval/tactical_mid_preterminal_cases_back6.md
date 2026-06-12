# Tactical-mid Preterminal Case Extractor

- source cases: `analysis/public_benchmark_eval/tactical_mid_must_block_cases.json`
- total source cases: `16`
- max back ply: `6`
- total extracted rows: `96`

## Summary

| Metric | Count | Rate |
|---|---:|---:|
| rows where observed next role is `opponent` | 48/96 | 0.500 |
| rows where observed next role is `neural` | 48/96 | 0.500 |
| opponent moves that create too-late double threat | 16/96 | 0.167 |
| neural rows with opponent double-threat replies after observed neural move | 17/48 | 0.354 |

## Case details

| Case | Back ply | Prefix ply | Role | Observed next | Opp wins before | Opp wins after observed | Opp double-threat replies after observed neural | Neural prevention moves | Observed opponent reply | Reply creates double threat |
|---|---:|---:|---|---|---:|---:|---:|---:|---|---|
| `tactical_mid_g1_block_0_8` | 1 | 172 | `opponent` | `4,12` | 0 | 2 |  |  | `` |  |
| `tactical_mid_g1_block_0_8` | 2 | 171 | `neural` | `0,11` | 1 | 0 | 1 | 0 | `4,12` | True |
| `tactical_mid_g1_block_0_8` | 3 | 170 | `opponent` | `3,11` | 0 | 1 |  |  | `` |  |
| `tactical_mid_g1_block_0_8` | 4 | 169 | `neural` | `0,12` | 1 | 0 | 0 | 1 | `3,11` | False |
| `tactical_mid_g1_block_0_8` | 5 | 168 | `opponent` | `1,11` | 0 | 1 |  |  | `` |  |
| `tactical_mid_g1_block_0_8` | 6 | 167 | `neural` | `2,14` | 1 | 0 | 0 | 3 | `1,11` | False |
| `tactical_mid_g3_block_4_9` | 1 | 24 | `opponent` | `4,6` | 0 | 2 |  |  | `` |  |
| `tactical_mid_g3_block_4_9` | 2 | 23 | `neural` | `3,5` | 1 | 0 | 1 | 1 | `4,6` | True |
| `tactical_mid_g3_block_4_9` | 3 | 22 | `opponent` | `4,5` | 0 | 1 |  |  | `` |  |
| `tactical_mid_g3_block_4_9` | 4 | 21 | `neural` | `8,5` | 0 | 0 | 0 | 2 | `4,5` | False |
| `tactical_mid_g3_block_4_9` | 5 | 20 | `opponent` | `7,5` | 0 | 0 |  |  | `` |  |
| `tactical_mid_g3_block_4_9` | 6 | 19 | `neural` | `2,9` | 1 | 0 | 0 | 206 | `7,5` | False |
| `tactical_mid_g4_block_1_6` | 1 | 29 | `opponent` | `4,9` | 0 | 2 |  |  | `` |  |
| `tactical_mid_g4_block_1_6` | 2 | 28 | `neural` | `2,9` | 0 | 0 | 1 | 0 | `4,9` | True |
| `tactical_mid_g4_block_1_6` | 3 | 27 | `opponent` | `2,7` | 0 | 0 |  |  | `` |  |
| `tactical_mid_g4_block_1_6` | 4 | 26 | `neural` | `5,8` | 0 | 0 | 0 | 199 | `2,7` | False |
| `tactical_mid_g4_block_1_6` | 5 | 25 | `opponent` | `2,6` | 0 | 0 |  |  | `` |  |
| `tactical_mid_g4_block_1_6` | 6 | 24 | `neural` | `3,7` | 0 | 0 | 0 | 3 | `2,6` | False |
| `tactical_mid_g6_block_8_4` | 1 | 39 | `opponent` | `4,8` | 0 | 2 |  |  | `` |  |
| `tactical_mid_g6_block_8_4` | 2 | 38 | `neural` | `5,8` | 1 | 0 | 2 | 0 | `4,8` | True |
| `tactical_mid_g6_block_8_4` | 3 | 37 | `opponent` | `5,7` | 0 | 1 |  |  | `` |  |
| `tactical_mid_g6_block_8_4` | 4 | 36 | `neural` | `5,3` | 0 | 0 | 0 | 2 | `5,7` | False |
| `tactical_mid_g6_block_8_4` | 5 | 35 | `opponent` | `5,5` | 0 | 0 |  |  | `` |  |
| `tactical_mid_g6_block_8_4` | 6 | 34 | `neural` | `7,2` | 1 | 0 | 0 | 191 | `5,5` | False |
| `tactical_mid_g10_block_10_5` | 1 | 51 | `opponent` | `10,1` | 0 | 2 |  |  | `` |  |
| `tactical_mid_g10_block_10_5` | 2 | 50 | `neural` | `12,4` | 1 | 0 | 2 | 0 | `10,1` | True |
| `tactical_mid_g10_block_10_5` | 3 | 49 | `opponent` | `10,4` | 0 | 1 |  |  | `` |  |
| `tactical_mid_g10_block_10_5` | 4 | 48 | `neural` | `9,1` | 0 | 0 | 0 | 177 | `10,4` | False |
| `tactical_mid_g10_block_10_5` | 5 | 47 | `opponent` | `11,4` | 0 | 0 |  |  | `` |  |
| `tactical_mid_g10_block_10_5` | 6 | 46 | `neural` | `11,1` | 1 | 0 | 0 | 179 | `11,4` | False |
| `tactical_mid_g11_block_7_14` | 1 | 86 | `opponent` | `10,11` | 0 | 2 |  |  | `` |  |
| `tactical_mid_g11_block_7_14` | 2 | 85 | `neural` | `8,14` | 1 | 0 | 1 | 1 | `10,11` | True |
| `tactical_mid_g11_block_7_14` | 3 | 84 | `opponent` | `8,13` | 0 | 1 |  |  | `` |  |
| `tactical_mid_g11_block_7_14` | 4 | 83 | `neural` | `12,12` | 1 | 0 | 0 | 3 | `8,13` | False |
| `tactical_mid_g11_block_7_14` | 5 | 82 | `opponent` | `11,12` | 0 | 1 |  |  | `` |  |
| `tactical_mid_g11_block_7_14` | 6 | 81 | `neural` | `10,13` | 1 | 0 | 0 | 1 | `11,12` | False |
| `tactical_mid_g13_block_8_10` | 1 | 22 | `opponent` | `9,10` | 0 | 2 |  |  | `` |  |
| `tactical_mid_g13_block_8_10` | 2 | 21 | `neural` | `9,12` | 0 | 0 | 2 | 0 | `9,10` | True |
| `tactical_mid_g13_block_8_10` | 3 | 20 | `opponent` | `11,10` | 0 | 0 |  |  | `` |  |
| `tactical_mid_g13_block_8_10` | 4 | 19 | `neural` | `14,12` | 1 | 0 | 0 | 3 | `11,10` | False |
| `tactical_mid_g13_block_8_10` | 5 | 18 | `opponent` | `13,11` | 0 | 1 |  |  | `` |  |
| `tactical_mid_g13_block_8_10` | 6 | 17 | `neural` | `9,7` | 0 | 0 | 0 | 2 | `13,11` | False |
| `tactical_mid_g14_block_11_12` | 1 | 23 | `opponent` | `11,8` | 0 | 2 |  |  | `` |  |
| `tactical_mid_g14_block_11_12` | 2 | 22 | `neural` | `7,13` | 1 | 0 | 2 | 0 | `11,8` | True |
| `tactical_mid_g14_block_11_12` | 3 | 21 | `opponent` | `8,12` | 0 | 1 |  |  | `` |  |
| `tactical_mid_g14_block_11_12` | 4 | 20 | `neural` | `12,8` | 0 | 0 | 2 | 0 | `8,12` | False |
| `tactical_mid_g14_block_11_12` | 5 | 19 | `opponent` | `11,9` | 0 | 0 |  |  | `` |  |
| `tactical_mid_g14_block_11_12` | 6 | 18 | `neural` | `13,10` | 1 | 0 | 0 | 207 | `11,9` | False |
| `tactical_mid_g15_block_5_3` | 1 | 34 | `opponent` | `9,7` | 0 | 2 |  |  | `` |  |
| `tactical_mid_g15_block_5_3` | 2 | 33 | `neural` | `7,4` | 0 | 0 | 2 | 0 | `9,7` | True |
| `tactical_mid_g15_block_5_3` | 3 | 32 | `opponent` | `6,4` | 0 | 0 |  |  | `` |  |
| `tactical_mid_g15_block_5_3` | 4 | 31 | `neural` | `5,5` | 0 | 0 | 0 | 194 | `6,4` | False |
| `tactical_mid_g15_block_5_3` | 5 | 30 | `opponent` | `5,4` | 0 | 0 |  |  | `` |  |
| `tactical_mid_g15_block_5_3` | 6 | 29 | `neural` | `10,3` | 0 | 0 | 0 | 196 | `5,4` | False |
| `tactical_mid_g17_block_14_7` | 1 | 42 | `opponent` | `11,10` | 0 | 2 |  |  | `` |  |
| `tactical_mid_g17_block_14_7` | 2 | 41 | `neural` | `9,6` | 0 | 0 | 1 | 0 | `11,10` | True |
| `tactical_mid_g17_block_14_7` | 3 | 40 | `opponent` | `12,9` | 0 | 0 |  |  | `` |  |
| `tactical_mid_g17_block_14_7` | 4 | 39 | `neural` | `8,14` | 1 | 0 | 0 | 3 | `12,9` | False |
| `tactical_mid_g17_block_14_7` | 5 | 38 | `opponent` | `9,13` | 0 | 1 |  |  | `` |  |
| `tactical_mid_g17_block_14_7` | 6 | 37 | `neural` | `13,9` | 0 | 0 | 0 | 3 | `9,13` | False |
| `tactical_mid_g19_block_6_9` | 1 | 22 | `opponent` | `7,8` | 0 | 2 |  |  | `` |  |
| `tactical_mid_g19_block_6_9` | 2 | 21 | `neural` | `9,5` | 1 | 0 | 2 | 0 | `7,8` | True |
| `tactical_mid_g19_block_6_9` | 3 | 20 | `opponent` | `9,6` | 0 | 1 |  |  | `` |  |
| `tactical_mid_g19_block_6_9` | 4 | 19 | `neural` | `9,10` | 0 | 0 | 0 | 2 | `9,6` | False |
| `tactical_mid_g19_block_6_9` | 5 | 18 | `opponent` | `9,9` | 0 | 0 |  |  | `` |  |
| `tactical_mid_g19_block_6_9` | 6 | 17 | `neural` | `10,9` | 1 | 0 | 0 | 208 | `9,9` | False |
| `tactical_mid_g20_block_13_9` | 1 | 25 | `opponent` | `12,8` | 0 | 2 |  |  | `` |  |
| `tactical_mid_g20_block_13_9` | 2 | 24 | `neural` | `10,7` | 0 | 0 | 2 | 0 | `12,8` | True |
| `tactical_mid_g20_block_13_9` | 3 | 23 | `opponent` | `11,7` | 0 | 0 |  |  | `` |  |
| `tactical_mid_g20_block_13_9` | 4 | 22 | `neural` | `11,8` | 0 | 0 | 0 | 203 | `11,7` | False |
| `tactical_mid_g20_block_13_9` | 5 | 21 | `opponent` | `12,7` | 0 | 0 |  |  | `` |  |
| `tactical_mid_g20_block_13_9` | 6 | 20 | `neural` | `7,2` | 0 | 0 | 0 | 205 | `12,7` | False |
| `tactical_mid_g21_block_6_10` | 1 | 32 | `opponent` | `7,10` | 0 | 2 |  |  | `` |  |
| `tactical_mid_g21_block_6_10` | 2 | 31 | `neural` | `8,11` | 1 | 0 | 2 | 0 | `7,10` | True |
| `tactical_mid_g21_block_6_10` | 3 | 30 | `opponent` | `9,10` | 0 | 1 |  |  | `` |  |
| `tactical_mid_g21_block_6_10` | 4 | 29 | `neural` | `13,6` | 0 | 0 | 0 | 2 | `9,10` | False |
| `tactical_mid_g21_block_6_10` | 5 | 28 | `opponent` | `11,8` | 0 | 0 |  |  | `` |  |
| `tactical_mid_g21_block_6_10` | 6 | 27 | `neural` | `12,6` | 0 | 0 | 0 | 198 | `11,8` | False |
| `tactical_mid_g22_block_7_9` | 1 | 43 | `opponent` | `11,5` | 0 | 2 |  |  | `` |  |
| `tactical_mid_g22_block_7_9` | 2 | 42 | `neural` | `11,6` | 1 | 0 | 2 | 0 | `11,5` | True |
| `tactical_mid_g22_block_7_9` | 3 | 41 | `opponent` | `10,6` | 0 | 1 |  |  | `` |  |
| `tactical_mid_g22_block_7_9` | 4 | 40 | `neural` | `10,7` | 1 | 0 | 0 | 1 | `10,6` | False |
| `tactical_mid_g22_block_7_9` | 5 | 39 | `opponent` | `9,6` | 0 | 1 |  |  | `` |  |
| `tactical_mid_g22_block_7_9` | 6 | 38 | `neural` | `6,1` | 1 | 0 | 0 | 1 | `9,6` | False |
| `tactical_mid_g23_block_9_13` | 1 | 52 | `opponent` | `5,9` | 0 | 2 |  |  | `` |  |
| `tactical_mid_g23_block_9_13` | 2 | 51 | `neural` | `6,11` | 0 | 0 | 2 | 0 | `5,9` | True |
| `tactical_mid_g23_block_9_13` | 3 | 50 | `opponent` | `6,10` | 0 | 0 |  |  | `` |  |
| `tactical_mid_g23_block_9_13` | 4 | 49 | `neural` | `5,13` | 1 | 0 | 0 | 176 | `6,10` | False |
| `tactical_mid_g23_block_9_13` | 5 | 48 | `opponent` | `6,12` | 0 | 1 |  |  | `` |  |
| `tactical_mid_g23_block_9_13` | 6 | 47 | `neural` | `11,3` | 0 | 0 | 0 | 178 | `6,12` | False |
| `tactical_mid_g24_block_11_11` | 1 | 49 | `opponent` | `7,11` | 0 | 2 |  |  | `` |  |
| `tactical_mid_g24_block_11_11` | 2 | 48 | `neural` | `10,12` | 0 | 0 | 2 | 0 | `7,11` | True |
| `tactical_mid_g24_block_11_11` | 3 | 47 | `opponent` | `10,11` | 0 | 0 |  |  | `` |  |
| `tactical_mid_g24_block_11_11` | 4 | 46 | `neural` | `8,12` | 1 | 0 | 0 | 179 | `10,11` | False |
| `tactical_mid_g24_block_11_11` | 5 | 45 | `opponent` | `9,11` | 0 | 1 |  |  | `` |  |
| `tactical_mid_g24_block_11_11` | 6 | 44 | `neural` | `13,7` | 0 | 0 | 0 | 2 | `9,11` | False |

## Interpretation

Rows with `back_ply=1` show whether the opponent's previous move created the double-terminal threat. Rows with `back_ply=2` show whether neural's previous move allowed one or more opponent replies that create a double-terminal threat. These are diagnostic/preterminal candidates, not direct training targets yet.
