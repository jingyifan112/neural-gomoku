# C Neural MCTS Migration

Goal: migrate the Python play-time neural MCTS path to C/CPU inference.

Previous completed milestones:
- PyTorch checkpoint export to C-readable weights
- C CNN policy/value forward pass
- Python/C consistency test
- C terminal safety layer
- C direct policy and safety play

This stage adds C neural MCTS.

Implemented files:
- c_inference/mcts_c.c
- c_inference/mcts_c.h

Updated files:
- c_inference/play_c.c
- c_inference/benchmark_c.c
- c_inference/Makefile
- c_inference/README.md

The C play path now supports:
- direct CNN policy inference
- CNN policy + terminal safety
- CNN policy/value + neural MCTS + terminal safety

Validation commands:
- make clean
- make
- ./test_infer
- ./benchmark_c weights/9x9_weights.bin
- ./play_c weights/9x9_weights.bin --mcts-sims 64

Conclusion:
The full play-time C/CPU inference path now includes CNN policy-value inference, terminal safety, and neural MCTS. This completes the full migration target at the inference/play level. Training and self-play are still Python/PyTorch based.
