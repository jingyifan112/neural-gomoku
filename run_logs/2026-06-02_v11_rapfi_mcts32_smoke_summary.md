# 15x15 v11 Rapfi mcts32 smoke test

Setup:
- neural checkpoint: v11 / checkpoints/15x15_current_best.pt
- C weights: c_inference/weights/15x15_v11_weights.bin
- neural MCTS sims: 32
- opponent: Rapfi fast
- Rapfi setting: tc=1/1, depth=1
- board size: 15
- games: 2

Result:
- neural_v11_mcts32 vs rapfi_fast: 0-2-0
- both losses were by five connection, not time forfeit

Conclusion:
- mcts32 removes the time-forfeit issue seen with mcts256.
- Rapfi benchmark at mcts32 is now valid for strength comparison.
- Next step: run v10_mcts32 under the same condition, then run 10-game v10/v11 comparison.
