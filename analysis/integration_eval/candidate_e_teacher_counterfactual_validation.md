# Candidate E teacher counterfactual validation

## Scope

This report validates only Candidate D mcts32 game2 move15 and move17
counterfactual first moves. It does not train, save, or promote any checkpoint;
does not change engine behavior; and does not change smoke settings, Rapfi
settings, board size, rule, time control, draw settings, or result parsing.

Inputs:

- `analysis/integration_eval/candidate_d_rapfi_teacher_ledger.md`
- `analysis/integration_eval/candidate_e_teacher_repair_dryrun.md`
- `analysis/integration_eval/candidate_d_mcts32_debug_failure_snapshots.json`
- `checkpoints/15x15_current_best_margin_candidate_d_move15_lastmove.pt`

Method:

- Reconstructed the move15 and move17 boards from Candidate D mcts32 debug
  snapshots.
- For each forced first move, checked legality and the current safety/fork
  predicate.
- Applied the forced white move, then evaluated the resulting black-to-move
  board with Candidate D. The reported value is from black's perspective after
  the forced move.
- Queried Rapfi diagnostically from the resulting black-to-move position using
  `START 15`, `INFO rule 0`, `INFO timeout_turn 1000`, and `BOARD ... DONE`.
  This is not a smoke run and does not alter benchmark settings.

## Counterfactual ledger

| game | move | forced source | forced first move | legal | safety check | Candidate D value after move, black POV | immediate/fork risk after move | Rapfi black continuation | appears better than Candidate D original |
| --- | ---: | --- | --- | --- | --- | ---: | --- | --- | --- |
| 2 | 15 | Candidate D direct | 7,10 | yes | safe | 0.604780 | no immediate black win; max black immediate wins after one reply = 1 | `7,9`; bestline `H10 I11 J11 K12 J10 J7 I7`; eval `+M11` | baseline |
| 2 | 15 | Candidate D MCTS final | 7,10 | yes | safe | 0.604780 | no immediate black win; max black immediate wins after one reply = 1 | `7,9`; bestline `H10 I11 J11 K12 J10 J7 I7`; eval `+M11` | baseline |
| 2 | 15 | Rapfi teacher | 7,9 | yes | safe | 0.691393 | no immediate black win; max black immediate wins after one reply = 1 | `3,8`; bestline `D9 J11 K12 G11 G12 E8 D8 D7 E10`; eval `51` | yes by Rapfi continuation, no by Candidate D value |
| 2 | 17 | Candidate D direct | 9,5 | yes | safe | 0.118350 | no immediate black win; max black immediate wins after one reply = 1 | `9,9`; bestline `J10 J11`; eval `+M7` | baseline |
| 2 | 17 | Candidate D MCTS final | 9,5 | yes | safe | 0.118350 | no immediate black win; max black immediate wins after one reply = 1 | `9,9`; bestline `J10 J11`; eval `+M7` | baseline |
| 2 | 17 | Rapfi teacher | 9,9 | yes | safe | 0.530931 | no immediate black win; max black immediate wins after one reply = 1 | `4,7`; bestline `E8 D8 E9 E6 D9 F9`; eval `139` | yes by Rapfi continuation, no by Candidate D value |

## Move15 diagnosis

Candidate D direct and MCTS both force `7,10`. That move is legal and passes
the current safety/fork check, but Rapfi's black reply reports `+M11` after
`7,10`, with black reply `7,9`.

The Rapfi teacher first move `7,9` is also legal and safe under the same current
checks. It does not reduce the one-ply fork score below Candidate D's move; both
remain at max 1 immediate black win after a black reply. The difference appears
only in continuation diagnostics: Rapfi no longer reports a mate, instead
returning eval `51` with black reply `3,8`.

Candidate D's own value head disagrees with Rapfi here: after teacher `7,9`,
the black-perspective value is higher (`0.691393`) than after Candidate D
`7,10` (`0.604780`). This reinforces the dry-run finding that move15 is a
teacher/value disagreement, not a simple safety-filter miss.

Verdict: `7,9` appears better than Candidate D's original move by Rapfi
counterfactual continuation, but it remains risky as a direct Candidate E repair
target because it conflicts with the Candidate D move15 repair behavior and is
not supported by Candidate D's value head.

## Move17 diagnosis

Candidate D direct and MCTS both force `9,5`. That move is legal and passes the
current safety/fork check, but Rapfi reports `+M7` after black reply `9,9`.

The Rapfi teacher first move `9,9` is legal and safe. The immediate tactical
summary again does not distinguish it from Candidate D's move: no immediate
black win and max one black immediate win after a reply. Rapfi continuation,
however, changes from a forced mate report to non-mate eval `139`, with black
reply `4,7`.

Candidate D's value head again disagrees with Rapfi: after teacher `9,9`, the
black-perspective value is `0.530931`, much higher than the `0.118350` after
Candidate D `9,5`. This matches the dry-run policy gap: the teacher was rank 40
with probability `0.00163610`.

Verdict: `9,9` appears better than Candidate D's original move by Rapfi
counterfactual continuation, but it is not suitable as a small single-step
margin repair target. It is too far from Candidate D's policy manifold and is
also contradicted by Candidate D's value head.

## Conclusion

The counterfactual validation supports the teacher ledger's diagnosis:

- Existing legality and safety/fork checks cannot separate Candidate D's moves
  from Rapfi teacher moves at move15 or move17.
- Rapfi continuation diagnostics favor the teacher moves: Candidate D moves lead
  to short mate reports for black (`+M11` at move15 and `+M7` at move17), while
  teacher moves reduce those to non-mate evaluations.
- Candidate D's own value head points the opposite way after both teacher moves,
  so these are value/search/teacher-data disagreements rather than immediate
  tactical misses.

Neither move should be promoted into training yet as a narrow Candidate E repair
without a separate retention audit. Move15 is the more plausible teacher-data
candidate, but it conflicts with the just-fixed Candidate D move15 behavior.
Move17 is useful diagnostic evidence but remains too policy-distant for a small
explainable margin repair.
