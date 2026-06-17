# Retention family run2 eval probability regression review

Scope: run2 eval regression review only. No training, checkpoint, C export, benchmark, or promotion was run.

## Gate context

- gate decision: `FAIL`
- gate failures: `['eval prob regressions 3 > 0']`
- gate counts: `{'eval_prob_regressed': 3, 'eval_rank_regressed': 0, 'side_counts': {'eval': 9, 'train': 2}, 'train_improved': 1}`

## Summary

- eval_rows: `9`
- prob_regressions: `3`
- rank_regressions: `0`
- top1_losses: `0`
- critical_7_9_rows: `1`
- missing_before: `0`
- missing_after: `0`
- severity_counts: `{'ok': 6, 'prob_only_regression': 3}`
- prob_regression_family_counts: `{'bd:690e24eaa9cbf978': 1, 'bd:fa22a82f75e4b3c2': 1, 'bd:fcfbf3a577067568': 1}`

## Interpretation

- probability-only regressions: rank/top1 gates stayed stable, but strict probability threshold failed
- critical 7,9 did not have a probability regression

## Probability regression rows

| idx | family | target | gate_scope | before_rank | after_rank | before_prob | after_prob | prob_delta | critical_7_9 | severity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | bd:690e24eaa9cbf978 | 5,11 | review_before_use_as_gate | 39 | 38 | 0.00194259 | 0.00182245 | -0.00012014 | False | prob_only_regression |
| 7 | bd:fcfbf3a577067568 | 8,10 | review_before_use_as_gate | 168 | 167 | 2.02e-06 | 1.64e-06 | -3.8e-07 | False | prob_only_regression |
| 8 | bd:fa22a82f75e4b3c2 | 5,8 | review_before_use_as_gate | 3 | 3 | 0.0453654 | 0.04490543 | -0.00045997 | False | prob_only_regression |

## Critical 7,9 rows

| idx | family | target | gate_scope | before_rank | after_rank | before_prob | after_prob | prob_delta | prob_regressed | rank_regressed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 9 | bd:ea22cc14729b88fd | 7,9 | external_or_family_level_only_not_sibling_only | 4 | 4 | 0.09005976 | 0.09247528 | 0.00241552 | False | False |

## Full eval review

| idx | family | target | before_rank | after_rank | before_prob | after_prob | prob_delta | prob_regressed | severity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | bd:690e24eaa9cbf978 | 5,11 | 39 | 38 | 0.00194259 | 0.00182245 | -0.00012014 | True | prob_only_regression |
| 2 | bd:9af3d20c637fd30d | 8,6 | 1 | 1 | 0.42844999 | 0.44035241 | 0.01190242 | False | ok |
| 3 | bd:a2b4f843dfbb182a | 8,6 | 1 | 1 | 0.5077036 | 0.51800746 | 0.01030386 | False | ok |
| 4 | bd:4e43e8574f31dd70 | 10,7 | 9 | 9 | 0.01283324 | 0.01283597 | 2.73e-06 | False | ok |
| 5 | bd:fcfbf3a577067568 | 7,9 | 1 | 1 | 0.52332556 | 0.53405023 | 0.01072467 | False | ok |
| 6 | bd:fcfbf3a577067568 | 10,9 | 7 | 7 | 0.00526721 | 0.00530354 | 3.633e-05 | False | ok |
| 7 | bd:fcfbf3a577067568 | 8,10 | 168 | 167 | 2.02e-06 | 1.64e-06 | -3.8e-07 | True | prob_only_regression |
| 8 | bd:fa22a82f75e4b3c2 | 5,8 | 3 | 3 | 0.0453654 | 0.04490543 | -0.00045997 | True | prob_only_regression |
| 9 | bd:ea22cc14729b88fd | 7,9 | 4 | 4 | 0.09005976 | 0.09247528 | 0.00241552 | False | ok |

## Explicit non-actions

- No model training was run.
- No checkpoint was saved.
- No C weights were exported.
- No benchmark was run.
- No promotion decision was made.
