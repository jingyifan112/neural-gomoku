# Mixed-CE heldout blocker position review

## Scope

- read-only review of six repeated heldout blockers
- no training
- no checkpoint
- no C export
- no benchmark
- no promotion

## Executive summary

The six repeated blockers cluster into three source families:

- candidate C / B mcts16 game2 move19 retention target: `10,7`
- candidate D game2 move15 fork-prevention retention targets: `7,10` and `10,7`
- candidate E game2 move13/move17 retention targets: `5,8`, `10,9`, and `8,10`

All six are heldout `policy_target` rows. Filtering only by label_type is therefore not enough.

## Blocker table

| id | game/move | target | source_path | reason/bucket | rank delta by scale | prob delta by scale |
|---|---:|---|---|---|---|---|
| `holdout_b_mcts16_g2_m19_target_10_7_over_7_11` | 2/19 | `10,7` | `analysis/integration_eval/current_best_margin_candidate_c_conservative_anchors.json` | White should block/occupy 10,7 before Black's diagonal threat becomes decisive; B final was 7,11. | `0.10:2;0.05:1;0.025:1` | `0.10:-0.00891487;0.05:-0.00892845;0.025:-0.00893496` |
| `holdout_candidate_d_g2_m15_white_last_8_9_target_live_direct_7_10_over_live_final_8_8` | 2/15 | `7,10` | `analysis/integration_eval/candidate_d_g2_m15_diagnostic_anchors.json` | game2 move15 earlier fork-prevention repair candidate; true last_move included | `0.10:1;0.05:1;0.025:1` | `0.10:-0.03276481;0.05:-0.03185576;0.025:-0.03150625` |
| `holdout_candidate_d_g2_m15_white_last_8_9_target_safe_10_7_over_live_final_8_8` | 2/15 | `10,7` | `analysis/integration_eval/candidate_d_g2_m15_diagnostic_anchors.json` | game2 move15 earlier fork-prevention repair candidate; true last_move included | `0.10:2;0.05:2;0.025:2` | `0.10:-0.02275356;0.05:-0.02212669;0.025:-0.02202318` |
| `holdout_candidate_e_g2_m13_white_target_5_8_over_8_8` | 2/13 | `5,8` | `analysis/integration_eval/candidate_e_g2_m13_diagnostic_anchors.json` | diagnose mcts16 final 5,8 versus mcts32/direct final 8,8 at game2 move13 | `0.10:3;0.05:3;0.025:2` | `0.10:-0.01193557;0.05:-0.01149342;0.025:-0.01131111` |
| `holdout_candidate_e_g2_m17_white_last_9_9_target_block_right_10_9_over_live_final_9_10` | 2/17 | `10,9` | `analysis/integration_eval/candidate_e_g2_m17_diagnostic_anchors.json` | diagnose game2 move17 earlier prevention of y=9 horizontal double threat | `0.10:0;0.05:0;0.025:0` | `0.10:-0.00413944;0.05:-0.00412775;0.025:-0.00411538` |
| `holdout_candidate_e_g2_m17_white_last_9_9_target_future_block_8_10_over_live_final_9_10` | 2/17 | `8,10` | `analysis/integration_eval/candidate_e_g2_m17_diagnostic_anchors.json` | diagnose game2 move17 earlier prevention of y=9 horizontal double threat | `0.10:-7;0.05:-8;0.025:-8` | `0.10:-0.00000192;0.05:-0.00000191;0.025:-0.00000190` |

## Per-position details

### `holdout_b_mcts16_g2_m19_target_10_7_over_7_11`

- source_id: `b_mcts16_g2_m19_target_10_7_over_7_11`
- source_path: `analysis/integration_eval/current_best_margin_candidate_c_conservative_anchors.json`
- game/move: 2 / 19
- side_to_move: `white`
- target: `10,7`
- teacher_move: `10,7`
- current_best_direct_move: `10,7`
- current_best_matches_teacher: `retention_anchor`
- board_digest: `598170c19d674fee`
- bucket: White should block/occupy 10,7 before Black's diagonal threat becomes decisive; B final was 7,11.
- manifest_notes: held-out current-best retention anchor; do not train on this split

| scale | rank before->after | prob before->after | top before->after | top_match before->after |
|---:|---:|---:|---|---|
| 0.10 | 9->11 | 0.01283312->0.00391825 | `9,10`->`9,10` | False->False |
| 0.05 | 9->10 | 0.01283312->0.00390467 | `9,10`->`9,10` | False->False |
| 0.025 | 9->10 | 0.01283312->0.00389816 | `9,10`->`9,10` | False->False |

Board view (`*` marks target; `X/O` are stones as encoded by dataset):

```text
   0 1 2 3 4 5 6 7 8 9 0 1 2 3 4
00 . . . . . . . . . . . . . . .
01 . . . . . . . . . . . . . . .
02 . . . . . . . . . . . . . . .
03 . . . . . . . . . . . . . . .
04 . . . . . . . . . . . . . . .
05 . . . O . . . . . . . . . . .
06 . . . . X O O O . . . . . . .
07 . . . . . X X X O . * . . . .
08 . . . . . O X X O X . . . . .
09 . . . . . O . X X . . . . . .
10 . . . . . . . X O . . . . . .
11 . . . . . . . . . . . . . . .
12 . . . . . . . . . . . . . . .
13 . . . . . . . . . . . . . . .
14 . . . . . . . . . . . . . . .
```

### `holdout_candidate_d_g2_m15_white_last_8_9_target_live_direct_7_10_over_live_final_8_8`

- source_id: `candidate_d_g2_m15_white_last_8_9_target_live_direct_7_10_over_live_final_8_8`
- source_path: `analysis/integration_eval/candidate_d_g2_m15_diagnostic_anchors.json`
- game/move: 2 / 15
- side_to_move: `white`
- target: `7,10`
- teacher_move: `7,10`
- current_best_direct_move: `7,10`
- current_best_matches_teacher: `retention_anchor`
- board_digest: `ea22cc14729b88fd`
- bucket: game2 move15 earlier fork-prevention repair candidate; true last_move included
- manifest_notes: held-out current-best retention anchor; do not train on this split

| scale | rank before->after | prob before->after | top before->after | top_match before->after |
|---:|---:|---:|---|---|
| 0.10 | 5->6 | 0.08013423->0.04736942 | `4,7`->`7,9` | False->False |
| 0.05 | 5->6 | 0.08013423->0.04827847 | `4,7`->`7,9` | False->False |
| 0.025 | 5->6 | 0.08013423->0.04862798 | `4,7`->`7,9` | False->False |

Board view (`*` marks target; `X/O` are stones as encoded by dataset):

```text
   0 1 2 3 4 5 6 7 8 9 0 1 2 3 4
00 . . . . . . . . . . . . . . .
01 . . . . . . . . . . . . . . .
02 . . . . . . . . . . . . . . .
03 . . . . . . . . . . . . . . .
04 . . . . . . . . . . . . . . .
05 . . . O . . . . . . . . . . .
06 . . . . X O O O . . . . . . .
07 . . . . . X X X O . . . . . .
08 . . . . . O X X . X . . . . .
09 . . . . . O . . X . . . . . .
10 . . . . . . . * . . . . . . .
11 . . . . . . . . . . . . . . .
12 . . . . . . . . . . . . . . .
13 . . . . . . . . . . . . . . .
14 . . . . . . . . . . . . . . .
```

### `holdout_candidate_d_g2_m15_white_last_8_9_target_safe_10_7_over_live_final_8_8`

- source_id: `candidate_d_g2_m15_white_last_8_9_target_safe_10_7_over_live_final_8_8`
- source_path: `analysis/integration_eval/candidate_d_g2_m15_diagnostic_anchors.json`
- game/move: 2 / 15
- side_to_move: `white`
- target: `10,7`
- teacher_move: `10,7`
- current_best_direct_move: `10,7`
- current_best_matches_teacher: `retention_anchor`
- board_digest: `ea22cc14729b88fd`
- bucket: game2 move15 earlier fork-prevention repair candidate; true last_move included
- manifest_notes: held-out current-best retention anchor; do not train on this split

| scale | rank before->after | prob before->after | top before->after | top_match before->after |
|---:|---:|---:|---|---|
| 0.10 | 2->4 | 0.10072906->0.07797550 | `4,7`->`7,9` | False->False |
| 0.05 | 2->4 | 0.10072906->0.07860237 | `4,7`->`7,9` | False->False |
| 0.025 | 2->4 | 0.10072906->0.07870588 | `4,7`->`7,9` | False->False |

Board view (`*` marks target; `X/O` are stones as encoded by dataset):

```text
   0 1 2 3 4 5 6 7 8 9 0 1 2 3 4
00 . . . . . . . . . . . . . . .
01 . . . . . . . . . . . . . . .
02 . . . . . . . . . . . . . . .
03 . . . . . . . . . . . . . . .
04 . . . . . . . . . . . . . . .
05 . . . O . . . . . . . . . . .
06 . . . . X O O O . . . . . . .
07 . . . . . X X X O . * . . . .
08 . . . . . O X X . X . . . . .
09 . . . . . O . . X . . . . . .
10 . . . . . . . . . . . . . . .
11 . . . . . . . . . . . . . . .
12 . . . . . . . . . . . . . . .
13 . . . . . . . . . . . . . . .
14 . . . . . . . . . . . . . . .
```

### `holdout_candidate_e_g2_m13_white_target_5_8_over_8_8`

- source_id: `candidate_e_g2_m13_white_target_5_8_over_8_8`
- source_path: `analysis/integration_eval/candidate_e_g2_m13_diagnostic_anchors.json`
- game/move: 2 / 13
- side_to_move: `white`
- target: `5,8`
- teacher_move: `5,8`
- current_best_direct_move: `5,8`
- current_best_matches_teacher: `retention_anchor`
- board_digest: `3edb62648d54c314`
- bucket: diagnose mcts16 final 5,8 versus mcts32/direct final 8,8 at game2 move13
- manifest_notes: held-out current-best retention anchor; do not train on this split

| scale | rank before->after | prob before->after | top before->after | top_match before->after |
|---:|---:|---:|---|---|
| 0.10 | 3->6 | 0.04536510->0.03342953 | `8,8`->`8,8` | False->False |
| 0.05 | 3->6 | 0.04536510->0.03387168 | `8,8`->`8,8` | False->False |
| 0.025 | 3->5 | 0.04536510->0.03405399 | `8,8`->`8,8` | False->False |

Board view (`*` marks target; `X/O` are stones as encoded by dataset):

```text
   0 1 2 3 4 5 6 7 8 9 0 1 2 3 4
00 . . . . . . . . . . . . . . .
01 . . . . . . . . . . . . . . .
02 . . . . . . . . . . . . . . .
03 . . . . . . . . . . . . . . .
04 . . . . . . . . . . . . . . .
05 . . . O . . . . . . . . . . .
06 . . . . X O O O . . . . . . .
07 . . . . . X X X O . . . . . .
08 . . . . . * X X . X . . . . .
09 . . . . . O . . . . . . . . .
10 . . . . . . . . . . . . . . .
11 . . . . . . . . . . . . . . .
12 . . . . . . . . . . . . . . .
13 . . . . . . . . . . . . . . .
14 . . . . . . . . . . . . . . .
```

### `holdout_candidate_e_g2_m17_white_last_9_9_target_block_right_10_9_over_live_final_9_10`

- source_id: `candidate_e_g2_m17_white_last_9_9_target_block_right_10_9_over_live_final_9_10`
- source_path: `analysis/integration_eval/candidate_e_g2_m17_diagnostic_anchors.json`
- game/move: 2 / 17
- side_to_move: `white`
- target: `10,9`
- teacher_move: `10,9`
- current_best_direct_move: `10,9`
- current_best_matches_teacher: `retention_anchor`
- board_digest: `831f9c7e8843d367`
- bucket: diagnose game2 move17 earlier prevention of y=9 horizontal double threat
- manifest_notes: held-out current-best retention anchor; do not train on this split

| scale | rank before->after | prob before->after | top before->after | top_match before->after |
|---:|---:|---:|---|---|
| 0.10 | 7->7 | 0.00526700->0.00112756 | `7,9`->`7,9` | False->False |
| 0.05 | 7->7 | 0.00526700->0.00113925 | `7,9`->`7,9` | False->False |
| 0.025 | 7->7 | 0.00526700->0.00115162 | `7,9`->`7,9` | False->False |

Board view (`*` marks target; `X/O` are stones as encoded by dataset):

```text
   0 1 2 3 4 5 6 7 8 9 0 1 2 3 4
00 . . . . . . . . . . . . . . .
01 . . . . . . . . . . . . . . .
02 . . . . . . . . . . . . . . .
03 . . . . . . . . . . . . . . .
04 . . . . . . . . . . . . . . .
05 . . . O . . . . . . . . . . .
06 . . . . X O O O . . . . . . .
07 . . . . . X X X O . . . . . .
08 . . . . . O X X . X . . . . .
09 . . . . . O . . X X * . . . .
10 . . . . . . . O . . . . . . .
11 . . . . . . . . . . . . . . .
12 . . . . . . . . . . . . . . .
13 . . . . . . . . . . . . . . .
14 . . . . . . . . . . . . . . .
```

### `holdout_candidate_e_g2_m17_white_last_9_9_target_future_block_8_10_over_live_final_9_10`

- source_id: `candidate_e_g2_m17_white_last_9_9_target_future_block_8_10_over_live_final_9_10`
- source_path: `analysis/integration_eval/candidate_e_g2_m17_diagnostic_anchors.json`
- game/move: 2 / 17
- side_to_move: `white`
- target: `8,10`
- teacher_move: `8,10`
- current_best_direct_move: `8,10`
- current_best_matches_teacher: `retention_anchor`
- board_digest: `831f9c7e8843d367`
- bucket: diagnose game2 move17 earlier prevention of y=9 horizontal double threat
- manifest_notes: held-out current-best retention anchor; do not train on this split

| scale | rank before->after | prob before->after | top before->after | top_match before->after |
|---:|---:|---:|---|---|
| 0.10 | 168->161 | 0.00000202->0.00000010 | `7,9`->`7,9` | False->False |
| 0.05 | 168->160 | 0.00000202->0.00000011 | `7,9`->`7,9` | False->False |
| 0.025 | 168->160 | 0.00000202->0.00000012 | `7,9`->`7,9` | False->False |

Board view (`*` marks target; `X/O` are stones as encoded by dataset):

```text
   0 1 2 3 4 5 6 7 8 9 0 1 2 3 4
00 . . . . . . . . . . . . . . .
01 . . . . . . . . . . . . . . .
02 . . . . . . . . . . . . . . .
03 . . . . . . . . . . . . . . .
04 . . . . . . . . . . . . . . .
05 . . . O . . . . . . . . . . .
06 . . . . X O O O . . . . . . .
07 . . . . . X X X O . . . . . .
08 . . . . . O X X . X . . . . .
09 . . . . . O . . X X . . . . .
10 . . . . . . . O * . . . . . .
11 . . . . . . . . . . . . . . .
12 . . . . . . . . . . . . . . .
13 . . . . . . . . . . . . . . .
14 . . . . . . . . . . . . . . .
```

## Interpretation

These blockers are not a single label-type problem. They are concentrated in a few tactical-retention families.

The candidate D move15 rows are especially important because one nearby heldout row gained top-1 under all mixed-CE scales, while two sibling targets regressed. This suggests a local target conflict rather than a global inability to retain the position family.

The candidate E move17 rows have extremely low target probability. One row improves rank while still losing probability, so row-level probability gates are catching a real mass-allocation issue that rank-only metrics would miss.

## Recommendation

Do not train another global mixed-CE scale variant yet.

Next useful experiment should either:

- separate conflicting sibling targets from the same board family, or
- add explicit retention anchors for these blocker families outside the heldout split, or
- make mixed-CE selection conditional on source family instead of label_type alone.

Any such variant must still run through the regression-gated runner before saving a checkpoint.
