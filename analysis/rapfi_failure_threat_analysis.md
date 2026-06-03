# Rapfi failure threat analysis

## Game 1 move_count 38

- side_to_move: black
- opponent: white
- value: 0.210098
- direct: 7,11 blocks=False
- policy_safety: 3,8
- mcts_raw: 8,6 blocks=False
- mcts_safety: 3,8 blocks=False
- final: 3,8 blocks=False
- current_player_immediate_winning_moves: (none)
- opponent_immediate_winning_moves: (none)
- preliminary_failure_type: needs_manual_review

## Game 1 move_count 44

- side_to_move: black
- opponent: white
- value: 0.059948
- direct: 10,7 blocks=False
- policy_safety: 2,10
- mcts_raw: 2,10 blocks=True
- mcts_safety: 2,10 blocks=True
- final: 2,10 blocks=True
- current_player_immediate_winning_moves: (none)
- opponent_immediate_winning_moves: 2,10
- preliminary_failure_type: value_miscalibration

## Game 1 move_count 46

- side_to_move: black
- opponent: white
- value: 0.037243
- direct: 2,9 blocks=False
- policy_safety: 4,12
- mcts_raw: 4,12 blocks=True
- mcts_safety: 4,12 blocks=True
- final: 4,12 blocks=True
- current_player_immediate_winning_moves: (none)
- opponent_immediate_winning_moves: 4,12
- preliminary_failure_type: value_miscalibration

## Game 1 move_count 48

- side_to_move: black
- opponent: white
- value: 0.018474
- direct: 10,7 blocks=False
- policy_safety: 8,11
- mcts_raw: 10,7 blocks=False
- mcts_safety: 8,11 blocks=True
- final: 8,11 blocks=True
- current_player_immediate_winning_moves: (none)
- opponent_immediate_winning_moves: 3,11 8,11
- preliminary_failure_type: forced_loss_or_double_threat

## Game 2 move_count 29

- side_to_move: white
- opponent: black
- value: -0.759072
- direct: 3,4 blocks=False
- policy_safety: 4,9
- mcts_raw: 4,9 blocks=True
- mcts_safety: 4,9 blocks=True
- final: 4,9 blocks=True
- current_player_immediate_winning_moves: (none)
- opponent_immediate_winning_moves: 4,9
- preliminary_failure_type: needs_manual_review

## Game 2 move_count 31

- side_to_move: white
- opponent: black
- value: -0.745447
- direct: 3,4 blocks=False
- policy_safety: 10,9
- mcts_raw: 3,4 blocks=False
- mcts_safety: 10,9 blocks=False
- final: 10,9 blocks=False
- current_player_immediate_winning_moves: (none)
- opponent_immediate_winning_moves: (none)
- preliminary_failure_type: needs_manual_review

## Game 2 move_count 33

- side_to_move: white
- opponent: black
- value: -0.741298
- direct: 10,8 blocks=False
- policy_safety: 9,6
- mcts_raw: 10,8 blocks=False
- mcts_safety: 9,6 blocks=True
- final: 9,6 blocks=True
- current_player_immediate_winning_moves: (none)
- opponent_immediate_winning_moves: 9,6 9,11
- preliminary_failure_type: forced_loss_or_double_threat
