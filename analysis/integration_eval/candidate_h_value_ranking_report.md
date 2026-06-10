# Candidate H value-ranking report

## Setup

- dataset: `analysis/integration_eval/candidate_g_teacher_policy_dataset.json`
- before checkpoint: `checkpoints/15x15_candidate_g_teacher_policy.pt`
- after checkpoint: `checkpoints/15x15_candidate_h_value_ranking.pt`
- training phase: value-head-only pairwise child-value ranking.
- no C export and no Rapfi smoke.

## Policy Gates

| gate | after | status |
| --- | ---: | --- |
| ply15 teacher 7,9 rank <= 3 | 1 | PASS |
| ply17 teacher 9,9 rank <= 10 | 1 | PASS |
| Candidate D repair 7,10 rank <= 3 | 2 | PASS |

## Child Value Gates

| ply | before teacher-original | after teacher-original | status |
| ---: | ---: | ---: | --- |
| 15 | -0.061126 | 0.111610 | PASS |
| 17 | -0.382891 | 0.052105 | PASS |

## Tactical Gate

| metric | before | after | status |
| --- | ---: | ---: | --- |
| direct policy | 7/7 | 7/7 | PASS |
| policy plus safety | 7/7 | 7/7 | PASS |
| MCTS plus safety | 7/7 | 7/7 | PASS |

## Gate Decision

Candidate H passes the policy, value, tactical, and pytest gates. It is eligible for a cautious C export check, but Rapfi smoke should still wait until exported-C parity is verified.

## Recommendation

Proceed to exported-C parity/tactical verification next. Keep this checkpoint separate from current best until C parity passes.
