# Candidate D teacher disagreement census

## Scope

This is a read-only diagnostic census over Candidate D mcts32 Rapfi losses.
It does not train, save, export, promote, or alter smoke/Rapfi settings.

Inputs:

- failure positions: `analysis/integration_eval/candidate_d_mcts32_debug_failure_positions.json`
- replay log: `eval_logs/rapfi_smoke/candidate_d_move15_mcts32_debug_vs_rapfi_fast_g2.log`
- checkpoint: `checkpoints/15x15_current_best_margin_candidate_d_move15_lastmove.pt`
- Rapfi command: `/Users/jing1fan/gomoku_public_benchmark/run_rapfi.sh`

Method:

- Replay the raw smoke protocol log to recover each Candidate D decision board and last-move plane.
- Query Rapfi from the same pre-decision board using `START 15`, `INFO rule 0`, `INFO timeout_turn 1000`, `INFO timeout_match 1000`, `INFO max_depth 1`, and `BOARD ... DONE`.
- Evaluate Candidate D policy rank/probability for the model move and teacher move.
- Force each move once, then evaluate Candidate D value from the mover perspective.
- Query Rapfi after each forced move and mark strong teacher continuation preference when Candidate D's move gives the opponent a mate while the teacher move does not, or when the opponent eval drops by at least the configured threshold.

## Summary

- positions evaluated: 44
- teacher/model divergences: 21
- strong teacher continuation divergences: 2
- teacher top-3 policy among divergences: 3/21
- teacher value-disfavored among divergences: 12/21

## Implementation Plan

1. Replay the Candidate D mcts32 smoke loss log instead of using only the curated five-position ledger, so both Rapfi losses are covered.
2. Recover the exact model-input last-move plane from consecutive board diagrams.
3. Query Rapfi as a same-position teacher for each Candidate D decision.
4. Score the teacher move in Candidate D policy space and compare one-ply Candidate D value after the model move versus after the teacher move.
5. Query Rapfi after each forced first move to identify divergences where the teacher continuation is materially better than Candidate D's continuation.

One important correction from this active census: game2 move17's same-position Rapfi teacher query returns `9,10` with bestline `J11 K12 H10 I11`. Earlier Candidate E notes used `9,9` as a teacher target, but in this log `9,9` is the Rapfi continuation reply after Candidate D's original move, not the same-position teacher move.

## First Major Divergences

| game | ply | side | model_move | teacher_move | teacher_rank | prob_gap | value_original | value_teacher | original_after | teacher_after | diagnosis |
| ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| 1 | 22 | black | 4,7 | 4,8 | 54 | -0.458606 | 0.372578 | 0.804193 | +M7 C8 B8 | 232 D9 | teacher policy/value mixed |
| 2 | 17 | white | 9,5 | 9,10 | 18 | -0.585557 | -0.118350 | -0.509939 | +M9 J11 K12 H10 I11 | 200 G11 | teacher policy-distant and value-disfavored |

## Strong Teacher Divergence Rows

| game | ply | side | model | teacher | teacher_rank | teacher_prob | model_prob | value_original | value_teacher | teacher_eval | after_model | after_teacher |
| ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| 1 | 22 | black | 4,7 | 4,8 | 54 | 0.00005404 | 0.45865965 | 0.372578 | 0.804193 | -127 E9 | +M7 C8 B8 | 232 D9 |
| 2 | 17 | white | 9,5 | 9,10 | 18 | 0.00464902 | 0.59020561 | -0.118350 | -0.509939 | +M9 J11 K12 H10 I11 | +M9 J11 K12 H10 I11 | 200 G11 |

## Conclusions

- Strong divergences with teacher already top-3: 0/2.
- Strong divergences where Candidate D value prefers the original move: 1/2.
- Strong divergences where the teacher is outside top-3: 2/2.
- Dominant observed mode: B. Missing policy knowledge requiring broader teacher distillation.

Recommendation for the next training experiment: do not run another single-position margin repair. The next candidate should be a small teacher-distillation dataset over strong same-position Rapfi divergences and nearby non-divergent anchors, with value/continuation labels added only after the policy target is no longer far outside Candidate D's top policy mass. The first seed targets from this census are game1 ply22 `4,8` and game2 ply17 `9,10`, with Candidate D retention anchors around game2 move15 and the already teacher-aligned/recovered later blocks.

Full row data: `analysis/integration_eval/candidate_d_teacher_disagreement_census.csv`
