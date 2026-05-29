# Tactical checkpoint comparison

## Position
human_play_cross_center_reference

## v2 result
checkpoint: checkpoints/9x9_tactical_v2.pt

sims 16–512:
- direct_policy_top=(4,3)
- raw_mcts_selected=(4,3)
- final_selected=(4,3)

sims 1024:
- final_selected=(7,5)

Conclusion:
v2 is stable for the current play setting of mcts_sims=256.

## v3 result
checkpoint: checkpoints/9x9_tactical_v3.pt

sims 16–128:
- final_selected=(4,3)

sims 256:
- final_selected=(7,1)

sims 512–1024:
- final_selected=(3,4)

Conclusion:
v3 policy head still learns the correct direct move (4,3), but MCTS/value search becomes unstable at higher simulations. v3 is not currently better than v2 for play_c at mcts_sims=256.

## Current best checkpoint
Use checkpoints/9x9_tactical_v2.pt as current best tactical model.
Use C weights: c_inference/weights/9x9_tactical_v2_weights.bin
Recommended play command:
./play_c weights/9x9_tactical_v2_weights.bin --mcts-sims 256 --debug
