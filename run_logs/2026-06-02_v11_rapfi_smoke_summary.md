# 15x15 v11 Rapfi smoke test

Checkpoint:
- v11: checkpoints/15x15_current_best.pt
- C weights: c_inference/weights/15x15_v11_weights.bin
- wrapper: ~/gomoku_public_benchmark/run_neural_v11_15x15.sh
- MCTS sims: 256

Opponent:
- Rapfi fast
- tc=1/1
- depth=1
- board size: 15
- rule: 0
- games: 2
- drawafter: 225

Result:
- neural_v11 vs rapfi_fast: 0 - 2 - 0

Interpretation:
- The C/Gomocup wrapper works for 15x15 v11.
- v11 lost the 2-game smoke test against Rapfi depth=1.
- This does not invalidate v11 promotion, because v11 was promoted based on internal checkpoint robustness.
- Next step is to run a same-condition v10 control benchmark and then compare v10 vs v11 against Rapfi.
