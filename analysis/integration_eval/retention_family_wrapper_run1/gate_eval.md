# Retention family adapter gate evaluation

Scope: adapter-aware gate evaluation only. No training, checkpoint save, C export, benchmark, or promotion was run.

## Decision

- decision: `FAIL`
- failures: `['eval rank regressions 8 > 0', 'eval top1 losses: 3', 'critical 7,9 eval gate regressed', 'no train-side row improved']`
- side counts: `{'eval': 9, 'train': 2}`
- eval rank regressions: 8
- eval prob regressions: 0
- train improved rows: 0

## Critical family rows

| side | target | before_rank | after_rank | before_prob | after_prob | gate_scope | rank_regressed | prob_regressed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| train | 7,10 | 5.0 | 143.0 | 0.08013152 | None | not_a_gate | True | False |
| train | 10,7 | 2.0 | 107.0 | 0.10073036 | None | not_a_gate | True | False |
| eval | 7,9 | 4.0 | 129.0 | 0.09005976 | None | external_or_family_level_only_not_sibling_only | True | False |

## All comparisons

| side | family_id | target | before_rank | after_rank | before_prob | after_prob | rank_regressed | prob_regressed | risk_flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| train | bd:ea22cc14729b88fd | 7,10 | 5.0 | 143.0 | 0.08013152 | None | True | False | critical_sibling_conflict_family |
| train | bd:ea22cc14729b88fd | 10,7 | 2.0 | 107.0 | 0.10073036 | None | True | False | critical_sibling_conflict_family |
| eval | bd:690e24eaa9cbf978 | 5,11 | 39.0 | 128.0 | 0.00194259 | None | True | False | review_required |
| eval | bd:9af3d20c637fd30d | 8,6 | 1.0 | 93.0 | 0.42844999 | None | True | False | review_required |
| eval | bd:a2b4f843dfbb182a | 8,6 | 1.0 | 95.0 | 0.5077036 | None | True | False | review_required |
| eval | bd:4e43e8574f31dd70 | 10,7 | 9.0 | 107.0 | 0.01283324 | None | True | False | review_required |
| eval | bd:fcfbf3a577067568 | 7,9 | 1.0 | 129.0 | 0.52332556 | None | True | False | review_required |
| eval | bd:fcfbf3a577067568 | 10,9 | 7.0 | 130.0 | 0.00526721 | None | True | False | review_required |
| eval | bd:fcfbf3a577067568 | 8,10 | 168.0 | 142.0 | 2.02e-06 | None | False | False | review_required |
| eval | bd:fa22a82f75e4b3c2 | 5,8 | 3.0 | 117.0 | 0.0453654 | None | True | False | review_required |
| eval | bd:ea22cc14729b88fd | 7,9 | 4.0 | 129.0 | 0.09005976 | None | True | False | critical_sibling_conflict_family;not_only_sibling_family_gate |

## Explicit non-actions

- No model training was run by this evaluator.
- No checkpoint was saved.
- No C weights were exported.
- No benchmark was run.
- No promotion decision was made.
