# v2 tactical checkpoint human play test

## Setup
Branch: tactical-training-data
C weights: c_inference/weights/9x9_tactical_v2_weights.bin
Command:
./play_c weights/9x9_tactical_v2_weights.bin --mcts-sims 256 --debug

## Result
AI won one human test game.

## Notes
This is an improvement compared with earlier checkpoints, where the human could repeatedly win using cross/fork strategies. The v2 tactical checkpoint previously passed the human_play_cross_center_reference comparison in both Python and C:
- direct_policy_top=(4,3)
- raw_mcts_selected=(4,3)
- safety_adjusted_selected=(4,3)
- final_selected=(4,3)

Need more games before claiming the model is stable.
