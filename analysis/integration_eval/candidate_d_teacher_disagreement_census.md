# Candidate D teacher disagreement census

## Implementation plan

1. Use the audited Candidate D mcts32 game2 teacher ledger as the seed set.
2. Reconstruct each board with side-to-move and last-move channel.
3. Probe Candidate D direct policy for teacher rank, teacher/model probabilities, and top-k moves.
4. Probe child-state value after the model move and after the teacher move, negating the child value back to the mover's perspective.
5. Summarize whether teacher disagreements are already known to policy or require larger distillation.

## Scope

- checkpoint: `/Users/jing1fan/Documents/Codex/2026-05-21/files-mentioned-by-the-user-400/neural-gomoku/checkpoints/15x15_v12l_margin_candidate.pt`
- coordinate convention: `x,y` with zero-based `x=col,y=row`.
- audited loss coverage in this checkout: Candidate D mcts32 game2 critical positions from the existing Rapfi teacher ledger.

## Census table

| game | ply | model | teacher | teacher rank | policy gap | value(model) | value(teacher) | teacher top-3 | value-disfavored | teacher continuation |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| 2 | 13 | 8,8 | 8,8 | 1 | 0.000000 | -0.072565 | -0.072565 | True | False | teacher_aligned |
| 2 | 15 | 7,10 | 7,9 | 6 | -0.819871 | -0.049808 | -0.110933 | False | True | strong_teacher_preference |
| 2 | 17 | 9,5 | 9,9 | 70 | -0.504395 | 0.387090 | 0.004199 | False | True | strong_teacher_preference |
| 2 | 19 | 10,11 | 10,11 | 44 | 0.000000 | 0.409687 | 0.409687 | False | False | teacher_aligned |
| 2 | 21 | 8,10 | 8,10 | 49 | 0.000000 | 0.074011 | 0.074011 | False | False | teacher_aligned |

## Summary

- positions audited: 5
- model/teacher divergences: 2
- strong teacher-continuation preferences: 2
- strong_teacher_preference: 2
- teacher_aligned: 3
- divergent teacher moves already top-3 policy: 0/2
- divergent teacher moves value-disfavored: 2/2

## Conclusions

The dominant failure mode is B: at least one strong teacher move is outside top-3 policy, so the model is missing policy knowledge rather than merely undervaluing an already available option.

## Recommendation

Run larger teacher distillation on the first-divergence positions and nearby teacher continuations, then gate on teacher rank/probability before value tuning.
