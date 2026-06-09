# candidate_c g2 m19 last_move diagnosis

Finding:
- Python dry-run without true last_move made target xy=10,7 look strong.
- Exact C probe shows last_move channel changes policy strongly.

Exact C probe result:
- black_last_none:
  - target xy=10,7 rank=2
  - target over live_final xy=7,11 gap=+0.981065
- black_last_7_10:
  - target xy=10,7 rank=2
  - live_final xy=7,11 becomes rank=1
  - target over live_final xy=7,11 gap=-2.735304
- white_last_7_10:
  - direct xy=6,11
  - mcts_safety xy=7,11

Interpretation:
- The current margin repair/dry-run dataset likely does not preserve last_move.
- Because model input includes [current_player_stones, opponent_stones, last_move], repair evaluation/training without last_move is not faithful to live C pbrain behavior.
- Do not train candidate D until repair scripts support last_move in samples.

Next candidate direction:
- game2 move15 is the likely earlier repair point.
- live final xy=8,8 has deeper fork score (1,2,1).
- safer candidates:
  - xy=7,10 score (0,1,0)
  - xy=10,7 score (0,1,0)
  - xy=7,9 score (0,1,0)
- However xy=7,10 was already direct policy, while MCTS selected xy=8,8.
- This suggests value/MCTS miscalibration, not just direct policy failure.
- Any candidate D repair must include the true last_move channel for move15.

Candidate D result:
- Candidate D trained target xy=7,10 over xy=8,8 on game2 move15 with true last_move xy=8,9.
- Local repair succeeded in live C smoke:
  - candidate C move15 final was xy=8,8.
  - candidate D move15 final became xy=7,10.
  - direct/policy_safety/mcts_raw/mcts_safety/final all selected xy=7,10 at move15.
- However 2-game Rapfi smoke still ended 0-2.
- D changed the game2 path; new failure snapshots must be extracted from candidate D log.
