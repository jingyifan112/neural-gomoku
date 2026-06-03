# Rapfi failure label summary

Total labeled positions: 7

## Label counts

- direct_policy_missed_immediate_block: 1
- forced_loss_or_double_threat: 2
- pre_double_threat_setup_review: 1
- pre_threat_setup_review: 1
- value_miscalibration_and_direct_policy_missed_immediate_block: 2

## Labeled positions

### Game 1 move_count 38

- failure_type: pre_threat_setup_review
- notes: no immediate win detected, but Rapfi soon creates forcing line; review open-four/double-threat setup
- opponent_immediate_winning_moves: (none)
- preliminary_failure_type: needs_manual_review

### Game 1 move_count 44

- failure_type: value_miscalibration_and_direct_policy_missed_immediate_block
- notes: opponent immediate win at 2,10; direct did not block; final blocked via MCTS/safety while value remained near neutral
- opponent_immediate_winning_moves: 2,10
- preliminary_failure_type: value_miscalibration

### Game 1 move_count 46

- failure_type: value_miscalibration_and_direct_policy_missed_immediate_block
- notes: opponent immediate win at 4,12; direct did not block; final blocked via MCTS/safety while value remained near neutral
- opponent_immediate_winning_moves: 4,12
- preliminary_failure_type: value_miscalibration

### Game 1 move_count 48

- failure_type: forced_loss_or_double_threat
- notes: opponent had two immediate winning moves 3,11 and 8,11; final blocked only one
- opponent_immediate_winning_moves: 3,11 8,11
- preliminary_failure_type: forced_loss_or_double_threat

### Game 2 move_count 29

- failure_type: direct_policy_missed_immediate_block
- notes: opponent immediate win at 4,9; direct did not block; final blocked via MCTS/safety; value was already strongly negative
- opponent_immediate_winning_moves: 4,9
- preliminary_failure_type: needs_manual_review

### Game 2 move_count 31

- failure_type: pre_double_threat_setup_review
- notes: no immediate win detected, but next Rapfi bestline suggests transition into forcing line J8 J12
- opponent_immediate_winning_moves: (none)
- preliminary_failure_type: needs_manual_review

### Game 2 move_count 33

- failure_type: forced_loss_or_double_threat
- notes: opponent had two immediate winning moves 9,6 and 9,11; final blocked only one
- opponent_immediate_winning_moves: 9,6 9,11
- preliminary_failure_type: forced_loss_or_double_threat
