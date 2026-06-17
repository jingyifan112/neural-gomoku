# Retention family adapter gate evaluation

Scope: adapter-aware gate evaluation only. No training, checkpoint save, C export, benchmark, or promotion was run.

## Decision

- decision: `FAIL`
- failures: `['eval hard prob regressions 3 > 0 (warnings=0)']`
- side counts: `{'eval': 9, 'train': 2}`
- eval rank regressions: 0
- eval prob regressions: 3
- eval hard prob regressions: 3
- eval prob warnings: 0
- eval prob epsilon: 0.0
- train improved rows: 1

## Critical family rows

| side | target | before_rank | after_rank | before_prob | after_prob | prob_delta | gate_scope | rank_regressed | prob_regressed | prob_gate_class |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| train | 7,10 | 5.0 | 5.0 | 0.08013152 | 0.07994807 | -0.00018345000000000167 | not_a_gate | False | True | non_eval_prob_regression_not_gate_failure |
| train | 10,7 | 2.0 | 2.0 | 0.10073036 | 0.10455413 | 0.0038237699999999902 | not_a_gate | False | False | not_regressed |
| eval | 7,9 | 4.0 | 4.0 | 0.09005976 | 0.09247528 | 0.0024155200000000043 | external_or_family_level_only_not_sibling_only | False | False | not_regressed |

## All comparisons

| side | family_id | target | before_rank | after_rank | before_prob | after_prob | prob_delta | rank_regressed | prob_regressed | prob_gate_class | risk_flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| train | bd:ea22cc14729b88fd | 7,10 | 5.0 | 5.0 | 0.08013152 | 0.07994807 | -0.00018345000000000167 | False | True | non_eval_prob_regression_not_gate_failure | critical_sibling_conflict_family |
| train | bd:ea22cc14729b88fd | 10,7 | 2.0 | 2.0 | 0.10073036 | 0.10455413 | 0.0038237699999999902 | False | False | not_regressed | critical_sibling_conflict_family |
| eval | bd:690e24eaa9cbf978 | 5,11 | 39.0 | 38.0 | 0.00194259 | 0.00182245 | -0.00012013999999999992 | False | True | hard_prob_drop_exceeds_epsilon | review_required |
| eval | bd:9af3d20c637fd30d | 8,6 | 1.0 | 1.0 | 0.42844999 | 0.44035241 | 0.011902420000000025 | False | False | not_regressed | review_required |
| eval | bd:a2b4f843dfbb182a | 8,6 | 1.0 | 1.0 | 0.5077036 | 0.51800746 | 0.010303859999999943 | False | False | not_regressed | review_required |
| eval | bd:4e43e8574f31dd70 | 10,7 | 9.0 | 9.0 | 0.01283324 | 0.01283597 | 2.7300000000011343e-06 | False | False | not_regressed | review_required |
| eval | bd:fcfbf3a577067568 | 7,9 | 1.0 | 1.0 | 0.52332556 | 0.53405023 | 0.010724669999999992 | False | False | not_regressed | review_required |
| eval | bd:fcfbf3a577067568 | 10,9 | 7.0 | 7.0 | 0.00526721 | 0.00530354 | 3.6330000000000216e-05 | False | False | not_regressed | review_required |
| eval | bd:fcfbf3a577067568 | 8,10 | 168.0 | 167.0 | 2.02e-06 | 1.64e-06 | -3.8000000000000017e-07 | False | True | hard_prob_drop_exceeds_epsilon | review_required |
| eval | bd:fa22a82f75e4b3c2 | 5,8 | 3.0 | 3.0 | 0.0453654 | 0.04490543 | -0.00045996999999999705 | False | True | hard_prob_drop_exceeds_epsilon | review_required |
| eval | bd:ea22cc14729b88fd | 7,9 | 4.0 | 4.0 | 0.09005976 | 0.09247528 | 0.0024155200000000043 | False | False | not_regressed | critical_sibling_conflict_family;not_only_sibling_family_gate |

## Explicit non-actions

- No model training was run by this evaluator.
- No checkpoint was saved.
- No C weights were exported.
- No benchmark was run.
- No promotion decision was made.
