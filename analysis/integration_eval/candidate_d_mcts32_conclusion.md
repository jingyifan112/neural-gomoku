# Candidate D mcts16/mcts32 integration conclusion

## Context

Candidate D checkpoint:

- `checkpoints/15x15_current_best_margin_candidate_d_move15_lastmove.pt`
- exported C weights:
  - `weights/15x15_current_best_margin_candidate_d_move15_lastmove_weights.bin`

Candidate D was trained from Candidate C with the corrected last-move-aware repair setup.

The main added repair sample was:

- game2 move15
- side to move: white
- true last move: xy=(8,9)
- target: xy=(7,10)
- suppress: xy=(8,8)

The previously considered game2 move19 target `10,7 over 7,11` was rejected because last-move-aware analysis showed `7,11` was the correct immediate block.

## Result summary

Candidate D successfully fixed the local game2 move15 issue:

- Candidate C mcts16 game2 move15 final: `8,8`
- Candidate D mcts16/mcts32 game2 move15 final: `7,10`

However, Candidate D still lost both games in Rapfi smoke tests:

- mcts16: `0-2`
- mcts32: `0-2`
- mcts64: changed the path but timed out in game2

Therefore Candidate D should not be promoted to `15x15_current_best.pt`.

## mcts16 vs mcts32 path difference

mcts16 game2 early path:

- move13 final: `5,8`
- move15 final: `7,10`
- move17 final: `9,10`
- move19 final: `8,10`
- move21 final: `11,9`

mcts32 game2 early path:

- move13 final: `8,8`
- move15 final: `7,10`
- move17 final: `9,5`
- move19 final: `10,11`
- move21 final: `8,10`

mcts32 did not timeout, but it still lost by five connection.

## Single-step repair investigation

Several possible Candidate E repair points were investigated.

### game2 move17

mcts32 move17:

- live final: `9,5`
- direct: `9,5`

One-ply fork scan showed `9,5` had score 1, and the top safe candidates also had score 1.
No clear better single-step target was found.

Conclusion: do not use move17 as a margin-repair target.

### game2 move25

mcts32 move25:

- direct: `5,8`
- final: `4,5`

One-ply fork scan showed:

- `final=4,5` gives max black immediate wins after one reply = 1
- `direct=5,8` gives max black immediate wins after one reply = 2

Conclusion: move25 is a good safety correction, not a failure target.

### game2 move31

mcts32 move31:

- final: `9,7`

One-ply fork scan showed multiple candidates still allowed black to create two immediate wins after one reply.
This position appears too late or too complex for simple single-step repair.

Conclusion: do not use move31 as a margin-repair target.

### game2 move13

mcts32 move13:

- live final: `8,8`
- mcts16 alternative: `5,8`

One-ply fork score:

- `8,8`: score 1
- `5,8`: score 1

Dry-run logits for `target 5,8 over suppress 8,8`:

- target probability: `0.01476191`
- suppress probability: `0.72105098`
- target rank: `6`
- suppress rank: `1`
- logit gap: `-3.888659`

Conclusion: `5,8` is not a safe Candidate E margin-repair target. The gap is too large and the one-ply scan does not show a clear safety advantage.

## Final conclusion

Candidate D produced a valid local fix, but it did not improve the public Rapfi smoke result.

No Candidate E single-step policy-margin repair target is currently justified.

Recommended next direction:

1. Do not promote Candidate D.
2. Stop single-position margin repair for this failure path.
3. Move to deeper improvement:
   - value training on failed/forced-loss trajectories,
   - stronger tactical/fork data,
   - or MCTS search improvements for multi-ply fork detection.
