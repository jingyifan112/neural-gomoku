# Rapfi Teacher Score-Gap Benchmark

## Scope

- positions: `analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json`
- model eval: `analysis/public_benchmark_eval/candidate_h_corpus8_selected_eval.csv`
- Rapfi binary: `/Users/jing1fan/gomoku_public_benchmark/rapfi-master/Rapfi/build/pbrain-rapfi`
- retry spec: `2:3000,1:2000`
- rows: 32

## Summary

- Rapfi concrete best move before model move: 32 / 32
- Rapfi concrete reply after model direct move: 32 / 32
- model direct move matches Rapfi best-before move: 6 / 32
- numeric provisional root-pov gaps: 13 / 32

## Important interpretation note

Rapfi `Eval` sign convention is treated conservatively here. The CSV includes raw before/after scores and a provisional root-perspective gap.
The provisional gap assumes Rapfi eval is side-to-move-relative, so after the model move the returned score is from the opponent's perspective.
This should be sanity-checked before using the gap as a training or promotion metric.

## Rows

| sample | side | type | model | Rapfi best | agree | Eval before | Eval after model | provisional gap | PV before |
|---|---|---|---:|---:|---|---:|---:|---:|---|
| legacy_g1_m4 | black | neighbor | 7,6 | 7,5 | False | 120 | 431 | 551 | H6 J8 |
| legacy_g1_m6 | black | first_direct_vs_mcts_divergence | 9,7 | 7,8 | False | 87 | 61 | 148 | H9 H6 |
| legacy_g1_m8 | black | neighbor | 9,7 | 8,5 | False | 319 | 155 | 474 | I6 K6 |
| legacy_g1_m38 | black | late_loss_window | 9,7 | 12,8 | False | NA | NA | NA | NA |
| legacy_g1_m40 | black | late_loss_window | 9,7 | 12,6 | False | NA | NA | NA | NA |
| legacy_g2_m5 | white | neighbor | 8,6 | 8,6 | True | 440 | 172 | 612 | I7 F7 |
| legacy_g2_m7 | white | first_direct_vs_mcts_divergence;neighbor | 9,5 | 5,6 | False | +M3 | +M3 | NA | F7 |
| legacy_g2_m9 | white | first_losing_value;neighbor | 9,5 | 10,5 | False | 63 | 212 | 275 | K6 L5 G9 E7 F7 |
| legacy_g2_m11 | white | neighbor | 7,4 | 9,7 | False | -92 | 186 | 94 | J8 J5 |
| legacy_g2_m19 | white | late_loss_window | 5,6 | 5,6 | True | -M4 | +M3 | NA | F7 |
| legacy_g2_m21 | white | late_loss_window | 2,4 | 7,9 | False | -M2 | 294 | NA | H10 |
| legacy_g3_m2 | black | first_direct_vs_mcts_divergence | 7,6 | 7,6 | True | 84 | -27 | 57 | H7 I6 |
| legacy_g3_m4 | black | neighbor | 8,8 | 5,6 | False | 134 | 24 | 158 | F7 H9 |
| legacy_g3_m24 | black | late_loss_window | 4,6 | 3,7 | False | -M4 | -M4 | NA | D8 |
| legacy_g3_m26 | black | late_loss_window | 7,6 | 6,3 | False | -M2 | NA | NA | G4 |
| legacy_g4_m13 | white | neighbor | 6,4 | 9,6 | False | -42 | 117 | 75 | J7 H5 H4 |
| legacy_g4_m15 | white | first_direct_vs_mcts_divergence | 9,9 | 6,4 | False | 2 | +M3 | NA | G5 H5 H4 |
| legacy_g4_m17 | white | neighbor | 9,9 | 10,6 | False | 353 | NA | NA | K7 H4 H5 J5 |
| legacy_g4_m21 | white | late_loss_window | 5,9 | 10,8 | False | NA | NA | NA | NA |
| legacy_g4_m23 | white | late_loss_window | 7,4 | 7,9 | False | NA | NA | NA | NA |
| legacy_g5_m6 | black | neighbor | 8,6 | 8,6 | True | 1 | +M7 | NA | I7 G9 |
| legacy_g5_m8 | black | first_direct_vs_mcts_divergence | 6,6 | 8,5 | False | +M3 | +M3 | NA | I6 |
| legacy_g5_m10 | black | neighbor | 10,7 | 10,7 | True | 236 | -135 | 101 | K8 F9 |
| legacy_g5_m12 | black | neighbor | 5,9 | 8,9 | False | 198 | 83 | 281 | I10 I11 H10 |
| legacy_g5_m14 | black | first_losing_value | 5,9 | 7,9 | False | 410 | 307 | 717 | H10 J5 K4 |
| legacy_g5_m16 | black | neighbor | 6,8 | 7,5 | False | +M3 | +M3 | NA | H6 |
| legacy_g5_m28 | black | late_loss_window | 5,4 | 5,11 | False | NA | NA | NA | NA |
| legacy_g5_m30 | black | late_loss_window | 5,4 | 4,9 | False | NA | NA | NA | NA |
| legacy_g6_m5 | white | first_losing_value | 8,8 | 6,8 | False | 440 | 361 | 801 | G9 G6 |
| legacy_g6_m15 | white | neighbor | 4,8 | 4,8 | True | NA | +M5 | NA | NA |
| legacy_g6_m17 | white | first_direct_vs_mcts_divergence;late_loss_window | 4,9 | 8,6 | False | +M3 | +M3 | NA | I7 |
| legacy_g6_m19 | white | neighbor;late_loss_window | 7,9 | 9,5 | False | NA | NA | NA | NA |
