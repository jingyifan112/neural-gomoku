# v12l next direction: fork/value/deeper-search diagnostics

## Baseline

Starting point:

- branch: exp/15x15-current-best-v12l-integration
- baseline commit: 76fb747
- latest candidate: Candidate D
- Candidate D checkpoint:
  - checkpoints/15x15_current_best_margin_candidate_d_move15_lastmove.pt
- Candidate D C weights:
  - weights/15x15_current_best_margin_candidate_d_move15_lastmove_weights.bin

## Current conclusion

Candidate D fixed the local game2 move15 last-move-aware repair target:

- previous mcts16 game2 move15: 8,8
- Candidate D mcts16/mcts32 game2 move15: 7,10

However, Candidate D still failed Rapfi smoke:

- mcts16: 0-2
- mcts32: 0-2
- mcts64: changed the path but timed out in game2

Therefore Candidate D should not be promoted to 15x15_current_best.pt.

## Decision

Stop single-position margin repair for this failure path.

The next improvement should diagnose and attack deeper failure causes:

1. value mis-evaluation on failed trajectories,
2. missing fork / multi-threat tactical awareness,
3. insufficient MCTS depth or rollout behavior for multi-ply threats.

## Immediate next experiment

Run a no-training diagnostic first.

For each Candidate D Rapfi smoke loss, inspect the critical midgame white moves after move13 and compare:

- live final move,
- direct policy top move,
- MCTS top candidates,
- one-ply fork score,
- two-ply fork risk if available,
- value estimate before and after the move,
- whether the move allows black to create multiple immediate wins.

The goal is to classify each failure as one of:

- POLICY_MARGIN_LOCAL: direct policy prefers bad move, but local target is obvious.
- FORK_MISSED: move allows opponent multi-threat / double immediate-win structure.
- VALUE_BLIND: value is high or neutral in a position that is strategically losing.
- SEARCH_TOO_SHALLOW: better move appears only at higher sims/depth.
- DATA_GAP: failure shape is absent from tactical/value training data.

## Promotion rule

Do not promote any new checkpoint unless it improves Rapfi smoke over Candidate D and does not regress the existing move15 fix.
