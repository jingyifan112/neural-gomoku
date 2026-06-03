# v11 to v12 failure summary

The Rapfi losses are no longer just unexplained 0-10 results. The current analysis identifies three concrete failure modes.

## 1. Direct policy misses immediate blocks

In several positions, the opponent has an immediate winning move, but the direct policy does not choose the blocking point. MCTS/safety often fixes this by selecting the block.

Examples:
- Game 1 move 44: opponent immediate win at 2,10; direct did not block; final blocked.
- Game 1 move 46: opponent immediate win at 4,12; direct did not block; final blocked.
- Game 2 move 29: opponent immediate win at 4,9; direct did not block; final blocked.

Conclusion:
v12 should include targeted immediate-win/block policy training.

## 2. Value head misses forced lines

In Game 1, the value remains near neutral or positive even when the opponent has immediate threats or is close to a forced win.

Examples:
- Game 1 move 44: value = 0.059948 despite opponent immediate win.
- Game 1 move 46: value = 0.037243 despite opponent immediate win.
- Game 1 move 48: value = 0.018474 despite opponent double immediate threat.

Conclusion:
v12 should include value targets for forced-loss / double-threat positions.

## 3. Some positions are already forced loss / double threat

At some late positions, the opponent has two immediate winning moves. The final move can block one but not both.

Examples:
- Game 1 move 48: opponent immediate wins = 3,11 and 8,11.
- Game 2 move 33: opponent immediate wins = 9,6 and 9,11.

Conclusion:
The model needs to avoid the earlier pre-threat setup, not just block at the final move.

## v12 direction

Do not continue plain self-play as the next step.

Recommended v12 direction:
- build targeted training data from immediate block positions
- add forced-loss / double-threat value examples
- add pre-double-threat avoidance examples
- keep internal gates against greedy, random, mixed_v5, and v10
- add a new Rapfi failure-position accuracy gate
