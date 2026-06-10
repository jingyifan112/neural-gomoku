# Candidate H/I/J local repair close-out

## Scope

This report closes the local Candidate H/I/J repair line for the 15x15 Rapfi
smoke failure investigation. It summarizes the policy-first and value-ranking
work, the live Rapfi smoke outcome, the Candidate I re-query diagnostics, and
the promotion/training decision for Candidate J.

No training, C export, or Rapfi smoke was run for this close-out.

## Candidate Line Summary

| candidate | purpose | result | promote status |
| --- | --- | --- | --- |
| Candidate G | policy-first teacher distillation on known Candidate D teacher gaps | fixed policy visibility on the targeted probe set and passed tactical gates | no promote |
| Candidate H | value-head-only ranking on top of Candidate G | passed fixed policy, value, tactical, pytest, and C-probe checks | no promote |
| Candidate I | smoke failure census plus Rapfi re-query diagnostics | measured live failure and teacher-label coverage only | diagnostics only |
| Candidate J | proposed follow-up local repair | not warranted because validated labels are too sparse | do not train |

## Findings

Candidate G was a successful policy-first repair on the fixed disagreement
positions. The teacher moves became visible in the policy head: ply15 teacher
`7,9` moved to rank 1, ply17 teacher `9,9` moved to rank 1, and the Candidate D
repair anchor `7,10` remained rank 2. The tactical gate passed 7/7 across
direct policy, policy+safety, and MCTS+safety. This made Candidate G useful as
a local probe success, but not a promotion candidate.

Candidate H added value-ranking on top of Candidate G and succeeded in the
fixed probes. Policy gates stayed green, child-value ordering flipped in favor
of the teacher alternatives at the targeted ply15 and ply17 positions, and the
tactical gate remained 7/7. Exported-C probe/parity checks also supported the
fixed-position result.

Candidate H failed the live Rapfi smoke test. In the mcts16 smoke, Candidate H
scored `0-2`, matching the Candidate D baseline and failing to improve the
live match result. The game2 line diverged before the original ply15/ply17
teacher-disagreement boards, so the fixed probe success did not transfer into
the live match trajectory. Candidate H was therefore rejected as a promotion
candidate, and mcts32 smoke was skipped.

Candidate I re-query diagnostics found too little usable teacher signal for a
local Candidate J. The final re-query census attempted 25 positions, got 11
concrete Rapfi moves, left 14 NA/no-move rows, recovered 0 additional concrete
labels with retry/fallback, and produced only 1 valid teacher disagreement
(`game2 ply27`) plus 1 low-policy-visibility agreement (`game1 ply18`). The
remaining NA rows were not terminal, not safety failures, and not stderr/crash
cases; Rapfi returned `OK` plus eval output but no coordinate, including under
depth-1 fallback.

## Decision

Do not train Candidate J from the Candidate I re-query dataset. The validated
label set is too small and too narrow: one disagreement is not enough to justify
another local repair candidate, and NA/no-move rows are not usable teacher
labels.

Promotion status:

- Candidate G: no promote.
- Candidate H: no promote.
- Candidate I: diagnostics only.
- Candidate J: do not train.

## Recommended Next Direction

Move away from repairing one smoke line and build a broader evaluation and
data-generation loop.

Recommended next work:

- Generate a broader self-play and Rapfi-match corpus instead of focusing on a
  single Candidate H smoke trajectory.
- Collect many losses and near-losses before selecting training labels.
- Build a full-game divergence/failure census that records policy rank, child
  value, safety status, live search decision, Rapfi move availability, and
  final outcome.
- Separate label classes: concrete Rapfi teacher disagreements, low-policy
  visibility agreements, value-ranking candidates, and safety/search failures.
- Train only after there are enough validated labels across multiple games and
  failure modes.
- Keep NA/no-move Rapfi rows as diagnostics, not as teacher labels.

The next candidate should come from a corpus-level pattern, not from the
Candidate I single-line census.

## References

- Candidate G report: `analysis/integration_eval/candidate_g_teacher_policy_report.md`
- Candidate H value report: `analysis/integration_eval/candidate_h_value_ranking_report.md`
- Candidate H smoke report: `analysis/integration_eval/candidate_h_rapfi_smoke_report.md`
- Candidate I re-query report: `analysis/integration_eval/candidate_i_rapfi_requery_census.md`
