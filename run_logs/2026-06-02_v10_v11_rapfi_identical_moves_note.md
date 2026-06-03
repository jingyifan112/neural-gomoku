# v10/v11 Rapfi mcts32 identical-log finding

Setup:
- v10_mcts32 vs Rapfi depth=1: 0-10
- v11_mcts32 vs Rapfi depth=1: 0-10
- all games ended by five connection, not time forfeit
- v10 and v11 C weight files are different by SHA-256 and cmp

Normalized diff:
- After normalizing engine names, wrapper paths, Speed, and Time fields, the v10 and v11 Rapfi benchmark logs produced no diff.

Conclusion:
- v10 and v11 appear to make the same moves in the C pbrain + MCTS32 + safety benchmark.
- The external Rapfi benchmark is currently insensitive to the internal v10 -> v11 improvement.
- The likely issue is not checkpoint export, but the C inference / MCTS / safety decision pipeline selecting the same moves despite different weights.

Next diagnostic:
- Compare direct policy / safe policy / raw MCTS / safe MCTS decisions for v10 and v11 on fixed boards.
- Determine whether the network outputs differ but safety/MCTS collapses them to the same final move.
