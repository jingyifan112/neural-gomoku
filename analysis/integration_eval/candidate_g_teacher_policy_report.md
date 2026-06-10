# Candidate G teacher policy-distillation report

## Setup

- dataset: `analysis/integration_eval/candidate_g_teacher_policy_dataset.json`
- before checkpoint: `/Users/jing1fan/Documents/Codex/2026-05-21/files-mentioned-by-the-user-400/neural-gomoku/checkpoints/15x15_v12l_margin_candidate.pt`
- after checkpoint: `checkpoints/15x15_candidate_g_teacher_policy.pt`
- training phase: policy-focused; no C export and no Rapfi smoke.

## Teacher Rank Comparison

| ply | target | before rank | after rank | gate |
| ---: | --- | ---: | ---: | --- |
| 15 | 7,9 | 6 | 1 | PASS top-3 |
| 17 | 9,9 | 70 | 1 | PASS top-10 |
| 15 | 7,10 Candidate D repair anchor | NA | 2 | PASS top-3 |

## Tactical Gate

| metric | before | after | gate |
| --- | ---: | ---: | --- |
| direct policy | 6/7 | 7/7 | PASS |
| policy plus safety | 6/7 | 7/7 | PASS |
| MCTS plus safety | 6/7 | 7/7 | PASS |

## Gate Decision

Candidate G passes the policy-rank and no-regression gates. Proceed to value tuning next; do not export to C until the value-tuned candidate also passes these gates.

## Recommendation

Use this checkpoint as the policy-visible base for a small value-ranking/counterfactual phase focused on the same two divergences.
