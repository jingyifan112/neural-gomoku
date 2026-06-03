# Rapfi failure set preliminary review

This is a preliminary review of the 7 selected Rapfi failure positions. These labels are not final because the current failure set does not yet include board snapshots.

## Game 1

Game 1 appears to show value miscalibration. The model eventually loses by five connection, but late-game values remain near neutral or positive.

### move_count 38
- value = 0.210098
- direct = 7,11
- mcts_raw = 8,6
- mcts_safety/final = 3,8
- next Rapfi bestline = H12 I13
- preliminary type: value_miscalibration + safety_override_review

### move_count 44
- value = 0.059948
- direct = 10,7
- final = 2,10
- next Rapfi bestline = E12 E13
- preliminary type: value_miscalibration + tactical_defense_review

### move_count 46
- value = 0.037243
- direct = 2,9
- final = 4,12
- next Rapfi bestline = F12 I12
- preliminary type: value_miscalibration + tactical_defense_review

### move_count 48
- value = 0.018474
- direct/mcts_raw = 10,7
- mcts_safety/final = 8,11
- preliminary type: value_miscalibration + safety_override_review

## Game 2

Game 2 appears to show tactical defense failure. The value is already strongly negative, so the model knows the position is bad, but it still fails to find a saving move.

### move_count 29
- value = -0.759072
- direct = 3,4
- final = 4,9
- next Rapfi bestline = J10
- preliminary type: tactical_defense_failure

### move_count 31
- value = -0.745447
- direct/mcts_raw = 3,4
- mcts_safety/final = 10,9
- next Rapfi bestline = J8 J12
- preliminary type: safety_override_review + tactical_defense_failure

### move_count 33
- value = -0.741298
- direct/mcts_raw = 10,8
- mcts_safety/final = 9,6
- Rapfi wins after this phase
- preliminary type: safety_override_review + tactical_defense_failure

## Next step

Extract board snapshots for these 7 positions before assigning final labels. The current CSV is enough to identify suspicious positions, but not enough to decide the correct move.
