# v2 tactical checkpoint human play win

## Setup
C weights:
c_inference/weights/9x9_tactical_v2_weights.bin

Command:
./play_c weights/9x9_tactical_v2_weights.bin --mcts-sims 256 --debug

## Result
model wins

## Notes
This was a human-vs-C-AI test using the v2 tactical checkpoint. Compared with earlier checkpoints, the model showed improved stability after tactical training.

Previous key verification:
- Python v2 checkpoint selected (4,3) on human_play_cross_center_reference.
- C exported v2 weights also selected (4,3) on the same position.
- v2 was stable on the cross-center reference for mcts_sims 16–512.
- v3 was less stable because MCTS/value search overrode the correct policy move at higher sims.

Current best model:
checkpoints/9x9_tactical_v2.pt
c_inference/weights/9x9_tactical_v2_weights.bin
