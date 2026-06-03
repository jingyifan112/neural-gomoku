# Rapfi failure board review notes

## Main finding

The current Rapfi losses should be analyzed as failure positions, not just as win/loss benchmark results.

The selected 7 positions show two different failure patterns:

## Game 1: value miscalibration

Game 1 positions have values near zero or positive even though the model later loses by five connection.

Positions:
- move_count 38: value = 0.210098
- move_count 44: value = 0.059948
- move_count 46: value = 0.037243
- move_count 48: value = 0.018474

Preliminary label:
- value_miscalibration
- forced_line_not_detected

Interpretation:
The model does not recognize Rapfi's forced winning line early enough.

## Game 2: tactical defense failure

Game 2 positions have strongly negative values, so the model knows the position is bad.

Positions:
- move_count 29: value = -0.759072
- move_count 31: value = -0.745447
- move_count 33: value = -0.741298

Preliminary label:
- tactical_defense_failure
- possible_forced_loss_already

Important positions:
- move_count 31:
  - direct/mcts_raw = 3,4
  - mcts_safety/final = 10,9
  - next Rapfi bestline = J8 J12
- move_count 33:
  - direct/mcts_raw = 10,8
  - mcts_safety/final = 9,6
  - previous Rapfi bestline = J8 J12

Interpretation:
The model may already be in a forced-loss or double-threat position. The correct improvement may need to happen before move_count 31.

## Next step

Add threat-level analysis:
- detect opponent immediate winning moves
- detect whether direct / mcts_raw / mcts_safety / final blocks the threat
- classify whether each position is missed block, forced loss, value miscalibration, or safety/MCTS override failure
