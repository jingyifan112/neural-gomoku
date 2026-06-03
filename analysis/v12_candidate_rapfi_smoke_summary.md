# v12 candidate Rapfi smoke summary

Candidate:
- checkpoints/15x15_v12_candidate.pt
- C weights: c_inference/weights/15x15_v12_candidate_weights.bin
- source: interpolation alpha=0.30 between v11 current_best and v12_stage2 repair specialist

Setup:
- board size: 15
- neural MCTS sims: 32
- move mode: mcts_safe
- opponent: Rapfi fast
- Rapfi setting: depth=1, tc=1/1
- games: 2

Result:
- v12_candidate vs Rapfi depth=1: 0-2
- game 1: White win by five connection
- game 2: Black win by five connection

Interpretation:
- v12_candidate is not ready for promotion based on Rapfi.
- The next question is whether v12_candidate changes the loss pattern compared with v11.
- If v12 and v11 produce identical Rapfi games, then the C MCTS/safety pipeline is still collapsing the repair.
- If v12 produces different games or survives longer, then the failure-set repair affected public benchmark behavior even though it did not yet produce wins.
