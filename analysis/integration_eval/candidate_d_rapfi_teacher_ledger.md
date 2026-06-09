# Candidate D Rapfi teacher ledger

## Scope

This ledger inspects Candidate D mcts32 game2 critical positions only. It does
not change engine behavior, benchmark settings, rules, draw handling, or result
parsing.

Candidate D source data:

- debug snapshots: `analysis/integration_eval/candidate_d_mcts32_debug_failure_snapshots.json`
- checkpoint: `checkpoints/15x15_current_best_margin_candidate_d_move15_lastmove.pt`
- C weights: `weights/15x15_current_best_margin_candidate_d_move15_lastmove_weights.bin`

Rapfi teacher query:

- engine: Rapfi 0.43.02 through `run_rapfi.sh`
- protocol: Gomocup `START 15`, `INFO rule 0`, `INFO timeout_turn 1000`, `BOARD ... DONE`
- board fields: `X` as black field 1, `O` as white field 2
- side to move is inferred from the reconstructed game2 board counts

Safety check:

- `teacher_safe=yes` means the move is legal and passes the existing
  `safety_move_is_safe` equivalent: after the teacher move, the opponent has no
  immediate win and no one-ply reply that creates multiple immediate wins.
- The one-ply fork score for every listed teacher move is 1.

Top Candidate D policy/MCTS candidates:

- The Candidate D smoke debug logs expose the direct policy top move and final
  MCTS move, but not ranked policy or ranked root-child MCTS candidate lists.
  Those ranked lists are therefore unavailable in this ledger.

## Teacher ledger

| game | move | side | candidate_direct | candidate_mcts | value | rapfi_teacher | teacher_safe | differs_from_candidate | diagnosis |
| --- | ---: | --- | --- | --- | ---: | --- | --- | --- | --- |
| 2 | 13 | white | 8,8 | 8,8 | -0.674789 | 8,8 | yes | no | Rapfi agrees with Candidate D. This is not a local policy or MCTS disagreement; the position already looks strategically dangerous and the one-ply safety score is still only 1. |
| 2 | 15 | white | 7,10 | 7,10 | -0.114186 | 7,9 | yes | yes, differs from direct and MCTS | Rapfi prefers a different safe move while Candidate D value is near neutral despite the subsequent forced-loss line. This is the clearest teacher/data gap and value-blind warning after the move15 repair. |
| 2 | 17 | white | 9,5 | 9,5 | -0.401256 | 9,9 | yes | yes, differs from direct and MCTS | Rapfi chooses a safe central defensive move instead of Candidate D's edge-side move. No immediate fork is visible, so this looks like teacher-guided search/value disagreement rather than a simple fork miss. |
| 2 | 19 | white | 9,9 | 10,11 | -0.587536 | 10,11 | yes | yes, differs from direct; matches MCTS | Candidate D direct policy is unsafe by one-ply scan, but MCTS safety recovers the Rapfi teacher block. This is not a current MCTS failure, though direct policy remains locally wrong. |
| 2 | 21 | white | 9,9 | 8,10 | -0.395404 | 8,10 | yes | yes, differs from direct; matches MCTS | Same pattern as move19: direct policy misses the block, while MCTS final matches Rapfi and passes existing safety. Remaining loss is likely earlier than this move. |

## Reconstructed board positions

Coordinates are zero-based `x,y`, matching the debug logs.

### Game 2 move13, white to move

- black: `4,6`; `5,7`; `6,7`; `7,7`; `6,8`; `7,8`; `9,8`
- white: `3,5`; `5,6`; `6,6`; `7,6`; `8,7`; `5,9`

### Game 2 move15, white to move

- black: `4,6`; `5,7`; `6,7`; `7,7`; `6,8`; `7,8`; `9,8`; `8,9`
- white: `3,5`; `5,6`; `6,6`; `7,6`; `8,7`; `8,8`; `5,9`

### Game 2 move17, white to move

- black: `4,6`; `8,6`; `5,7`; `6,7`; `7,7`; `6,8`; `7,8`; `9,8`; `8,9`
- white: `3,5`; `5,6`; `6,6`; `7,6`; `8,7`; `8,8`; `5,9`; `7,10`

### Game 2 move19, white to move

- black: `4,6`; `8,6`; `5,7`; `6,7`; `7,7`; `6,8`; `7,8`; `9,8`; `8,9`; `9,10`
- white: `3,5`; `9,5`; `5,6`; `6,6`; `7,6`; `8,7`; `8,8`; `5,9`; `7,10`

### Game 2 move21, white to move

- black: `4,6`; `8,6`; `5,7`; `6,7`; `7,7`; `6,8`; `7,8`; `9,8`; `7,9`; `8,9`; `9,10`
- white: `3,5`; `9,5`; `5,6`; `6,6`; `7,6`; `8,7`; `8,8`; `5,9`; `7,10`; `10,11`

## Takeaway

Rapfi's useful disagreement is concentrated at move15 and move17. Move13 is
teacher-aligned, while moves19 and 21 are already recovered by Candidate D MCTS
safety. The next training/diagnostic step should therefore treat move15
teacher `7,9` and move17 teacher `9,9` as candidate teacher-supervised
positions, but only after a separate audit confirms they do not regress the
known Candidate D move15 repair target.
