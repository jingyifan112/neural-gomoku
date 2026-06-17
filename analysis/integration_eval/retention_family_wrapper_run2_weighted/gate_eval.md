# Retention family adapter gate evaluation

Scope: adapter-aware gate evaluation only. No training, checkpoint save, C export, benchmark, or promotion was run.

## Decision

- decision: `FAIL`
- failures: `['eval prob regressions 3 > 0']`
- side counts: `{'eval': 9, 'train': 2}`
- eval rank regressions: 0
- eval prob regressions: 3
- train improved rows: 1

## Critical family rows

| side | target | before_rank | after_rank | before_prob | after_prob | gate_scope | rank_regressed | prob_regressed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| train | 7,10 | 5.0 | 5.0 | 0.08013152 | 0.07994807 | not_a_gate | False | True |
| train | 10,7 | 2.0 | 2.0 | 0.10073036 | 0.10455413 | not_a_gate | False | False |
| eval | 7,9 | 4.0 | 4.0 | 0.09005976 | 0.09247528 | external_or_family_level_only_not_sibling_only | False | False |

## All comparisons

| side | family_id | target | before_rank | after_rank | before_prob | after_prob | rank_regressed | prob_regressed | risk_flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| train | bd:ea22cc14729b88fd | 7,10 | 5.0 | 5.0 | 0.08013152 | 0.07994807 | False | True | critical_sibling_conflict_family |
| train | bd:ea22cc14729b88fd | 10,7 | 2.0 | 2.0 | 0.10073036 | 0.10455413 | False | False | critical_sibling_conflict_family |
| eval | bd:690e24eaa9cbf978 | 5,11 | 39.0 | 38.0 | 0.00194259 | 0.00182245 | False | True | review_required |
| eval | bd:9af3d20c637fd30d | 8,6 | 1.0 | 1.0 | 0.42844999 | 0.44035241 | False | False | review_required |
| eval | bd:a2b4f843dfbb182a | 8,6 | 1.0 | 1.0 | 0.5077036 | 0.51800746 | False | False | review_required |
| eval | bd:4e43e8574f31dd70 | 10,7 | 9.0 | 9.0 | 0.01283324 | 0.01283597 | False | False | review_required |
| eval | bd:fcfbf3a577067568 | 7,9 | 1.0 | 1.0 | 0.52332556 | 0.53405023 | False | False | review_required |
| eval | bd:fcfbf3a577067568 | 10,9 | 7.0 | 7.0 | 0.00526721 | 0.00530354 | False | False | review_required |
| eval | bd:fcfbf3a577067568 | 8,10 | 168.0 | 167.0 | 2.02e-06 | 1.64e-06 | False | True | review_required |
| eval | bd:fa22a82f75e4b3c2 | 5,8 | 3.0 | 3.0 | 0.0453654 | 0.04490543 | False | True | review_required |
| eval | bd:ea22cc14729b88fd | 7,9 | 4.0 | 4.0 | 0.09005976 | 0.09247528 | False | False | critical_sibling_conflict_family;not_only_sibling_family_gate |

## Explicit non-actions

- No model training was run by this evaluator.
- No checkpoint was saved.
- No C weights were exported.
- No benchmark was run.
- No promotion decision was made.
