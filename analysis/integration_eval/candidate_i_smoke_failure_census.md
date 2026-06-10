# Candidate I smoke failure census

## Scope

- input log: `eval_logs/integration_eval/candidate_h_mcts16_vs_rapfi_depth1_15x15_smoke.engine_io.log`
- C weights probed: `weights/15x15_candidate_h_value_ranking_weights.bin`
- measurement only; no Candidate I training was run.
- teacher move source: second move of Rapfi's previous PV when available.

## Summary

- Candidate H loss decisions audited: 25
- decisions with Rapfi teacher continuation available: 10
- comparable Candidate D divergence rows: 5
- divergences from available Rapfi teacher continuation: 0
- teacher moves with low policy visibility rank > 10: 1
- teacher child-value greater than Candidate H child-value: 0

## Focus Window

| game | ply | Candidate H | Candidate D baseline | Rapfi teacher | teacher rank | policy gap | child-value gap | safety H/teacher | classification |
|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 2 | 13 | 2,6 | 5,8 | 2,6 | 1 | 0.000000 | 0.000000 | True/True | diverges_from_candidate_d_baseline;matches_rapfi_teacher;already_losing_value |
| 2 | 15 | 2,8 | 7,10 | 2,8 | 5 | 0.000000 | 0.000000 | True/True | diverges_from_candidate_d_baseline;matches_rapfi_teacher;already_losing_value |
| 2 | 17 | 4,10 | 9,10 | 4,10 | 4 | 0.000000 | 0.000000 | True/True | diverges_from_candidate_d_baseline;matches_rapfi_teacher;already_losing_value |

Candidate H follows the available Rapfi PV continuation at game2 plies 13, 15, and 17. The new live divergence from Candidate D at ply13 is therefore not a simple missing-policy problem under the available shallow teacher continuation; it is a changed line that still collapses later.

## Game 1 Late Failure Context

| game | ply | Candidate H | Rapfi teacher | teacher rank | root value | child value | next result | classification |
|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | 14 | 8,5 | NA | NA | 0.416917 | 0.831770 | White win by five connection | context |
| 1 | 16 | 4,5 | 4,5 | 1 | -0.201069 | 0.843044 | White win by five connection | matches_rapfi_teacher |
| 1 | 18 | 5,2 | 5,2 | 37 | -0.227468 | 0.801930 | White win by five connection | matches_rapfi_teacher;teacher_low_policy_visibility |
| 1 | 20 | 7,1 | 7,1 | 1 | -0.223367 | 0.879718 | White win by five connection | matches_rapfi_teacher |

## Interpretation

- The old fixed-position Candidate H improvements did not transfer because the live game2 trajectory changed before the old ply15/ply17 boards.
- In the new game2 focus window, Candidate H is not ignoring the available Rapfi continuation; it matches the PV continuation at ply13, ply15, and ply17.
- The logged/root values are already strongly negative through much of game2, so the model appears to be navigating a bad line rather than merely suppressing a visible local teacher move.
- Game1 has fewer teacher-continuation labels available from the log, so it needs fresh teacher probing before it can support targeted value-ranking pairs.

## Recommendation

Recommendation D: reject this line and return to broader data generation, with a small supporting A component. The next useful measurement/training loop should generate stronger teacher labels from live Candidate H failure positions, not just reuse shallow prior-PV continuations. Expand the teacher policy dataset only after re-querying a stronger teacher on the reconstructed game1 and game2 positions; defer value-ranking pairs until those teacher choices are stable and demonstrably improve continuations.

Do not train Candidate I yet; this report is a measurement artifact.
