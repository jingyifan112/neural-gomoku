# 15x15 v10/v11 Rapfi depth=1 mcts32 benchmark

Setup:
- board size: 15
- rule: 0
- drawafter: 225
- opponent: Rapfi fast
- Rapfi setting: tc=1/1, depth=1
- neural engine: C pbrain wrapper
- neural MCTS sims: 32

Why mcts32:
- Earlier mcts256 benchmark caused time forfeits.
- mcts32 removed the time-forfeit issue.
- Games now finish by five connection, so this is a valid external benchmark.

Results:
- v11_mcts32 vs rapfi_fast: 0-10-0
- v10_mcts32 vs rapfi_fast: 0-10-0
- All losses were by five connection.

Interpretation:
- v11 remains the internal current best because it consistently beats v10_frozen 20-0 and preserves greedy/random/mixed_v5 performance.
- However, v11 does not yet show external win-rate improvement against Rapfi depth=1.
- Since v10 and v11 have identical external scores, the next step is to compare move sequences and identify whether both versions are making the same losing moves.
