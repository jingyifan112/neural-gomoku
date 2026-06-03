# 15x15 v10/v11 Rapfi depth=1 benchmark

Setup:
- engine wrapper: Gomocup pbrain C inference
- opponent: Rapfi fast
- Rapfi setting: tc=1/1, depth=1
- board size: 15
- rule: 0
- games: 10
- drawafter: 225
- neural MCTS sims: 256

C weight check:
- v10 and v11 exported C weights have different SHA-256 hashes.
- cmp returned 1, confirming the C weight files are different.

Results:
- v11 vs rapfi_fast: 0-10-0
- v10 vs rapfi_fast: 0-10-0

Important finding:
- All games were lost by time forfeit, not by normal five-in-a-row losses.
- Therefore this benchmark is not a valid playing-strength comparison yet.

Interpretation:
- The C/Gomocup wrapper and exported weights work.
- However, NEURAL_GOMOKU_MCTS_SIMS=256 is too slow for this Rapfi/c-gomoku-cli time-control setup.
- Next step is to reduce neural MCTS simulations and rerun the benchmark until games finish normally.
