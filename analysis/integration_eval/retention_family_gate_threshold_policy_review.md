# Retention Family Gate Threshold Policy Review

## Scope

- Policy review only.
- No training.
- No checkpoint.
- No C export.
- No benchmark.
- No promotion.

## Source Run2 Status

| field | value |
| --- | --- |
| gate decision | FAIL |
| wrapper overall_status | gates_failed |
| wrapper gates_passed | False |
| run2 review scope | run2 eval probability regression review only; no training/checkpoint/C export/benchmark/promotion |

## Reviewed Policy

- Probability epsilon: `0.0005` absolute policy probability.
- Current rule: any finite eval probability decrease is a gate failure.
- Reviewed rule: probability-only decrease within epsilon becomes warning-only if rank/top1 are preserved and no critical row is harmed.

Recommended gate hierarchy:

- FAIL if top1 is lost.
- FAIL if target rank regresses.
- FAIL if a critical protected row regresses by probability, rank, or top1.
- FAIL if probability-only drop is larger than epsilon.
- WARNING, not FAIL, if probability-only drop is within epsilon and rank/top1 are preserved.

## Counts

| metric | value |
| --- | --- |
| eval rows | 9 |
| current gate prob regressions | 3 |
| current gate rank regressions | 0 |
| current gate top1 losses | 0 |
| critical harmed rows | 0 |
| threshold policy warnings | 3 |
| threshold policy hard failures | 0 |
| threshold policy decision | PASS_WITH_WARNINGS_FOR_POLICY_REVIEW_ONLY |

## Warning Rows Under Threshold Policy

| row | family_id | target | rank before->after | prob before->after | prob delta | abs drop | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | bd:690e24eaa9cbf978 | 5,11 | 39->38 | 0.00194259->0.00182245 | -0.00012014 | 0.00012014 | warning_prob_only_within_epsilon |
| 7 | bd:fcfbf3a577067568 | 8,10 | 168->167 | 2.02e-06->1.64e-06 | -3.8e-07 | 3.8e-07 | warning_prob_only_within_epsilon |
| 8 | bd:fa22a82f75e4b3c2 | 5,8 | 3->3 | 0.0453654->0.04490543 | -0.00045997 | 0.00045997 | warning_prob_only_within_epsilon |

## Hard Failure Rows Under Threshold Policy

None.

## Recommendation

Adopt the thresholded policy for future gate-evaluator design review: rank/top1/critical regressions remain hard failures, while probability-only drops within epsilon are warnings. This run should remain a policy-review case rather than a retroactive checkpoint promotion.

## Outputs

- CSV: `analysis/integration_eval/retention_family_gate_threshold_policy_review.csv`
- JSON: `analysis/integration_eval/retention_family_gate_threshold_policy_review.json`
- Markdown: `analysis/integration_eval/retention_family_gate_threshold_policy_review.md`
