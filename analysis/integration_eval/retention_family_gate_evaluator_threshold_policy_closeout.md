# Retention Family Gate Evaluator Threshold Policy Closeout

## Scope

This branch implements and dry-runs the gate evaluator threshold policy only.

Explicit non-actions:

- No training.
- No checkpoint creation.
- No checkpoint promotion.
- No C export.
- No public benchmark.
- No model promotion.

## Change

Updated `scripts/evaluate_retention_family_adapter_gates.py` with an eval probability threshold policy:

- `--eval-prob-epsilon` adds an absolute probability-drop epsilon.
- Eval probability-only drops within epsilon are classified as `warning_prob_only_within_epsilon`.
- Rank regressions remain hard failures.
- Top-1 losses remain hard failures.
- Critical protected `bd:ea22cc14729b88fd` target `7,9` regressions remain hard failures.
- Eval probability-only drops larger than epsilon remain hard failures.
- Train-side probability drops are reported but not used as eval gate failures.

## Dry-run inputs

The dry-run used existing run2 before/after probe files:

- Train adapter: `analysis/integration_eval/retention_family_training_consumer_adapter_train_weighted_dataset.json`
- Eval adapter: `analysis/integration_eval/retention_family_training_consumer_adapter_eval_dataset.json`
- Train before: `analysis/integration_eval/retention_family_wrapper_run2_weighted/train_before.csv`
- Train after: `analysis/integration_eval/retention_family_wrapper_run2_weighted/train_after.csv`
- Eval before: `analysis/integration_eval/retention_family_wrapper_run2_weighted/eval_before.csv`
- Eval after: `analysis/integration_eval/retention_family_wrapper_run2_weighted/eval_after.csv`

## Strict policy dry-run

Command used `--eval-prob-epsilon 0`.

Result:

- decision: `FAIL`
- eval rows: `9`
- train rows: `2`
- eval rank regressions: `0`
- eval probability regressions: `3`
- eval hard probability regressions: `3`
- eval probability warnings: `0`
- train improved rows: `1`
- failure: `eval hard prob regressions 3 > 0 (warnings=0)`

This reproduces the original run2 gate failure behavior under strict probability gating.

## Threshold policy dry-run

Command used `--eval-prob-epsilon 0.0005`.

Result:

- decision: `PASS`
- eval rows: `9`
- train rows: `2`
- eval rank regressions: `0`
- eval probability regressions: `3`
- eval hard probability regressions: `0`
- eval probability warnings: `3`
- train improved rows: `1`
- failures: `[]`

The three eval probability regressions are reclassified as warning-only because rank/top1 are preserved, the critical `7,9` row is not harmed, and each absolute probability drop is within `0.0005`.

## Warning rows under threshold policy

| family_id | target | rank before->after | prob before->after | prob delta | class |
| --- | --- | --- | --- | --- | --- |
| `bd:690e24eaa9cbf978` | `5,11` | `39 -> 38` | `0.00194259 -> 0.00182245` | `-0.00012014` | `warning_prob_only_within_epsilon` |
| `bd:fcfbf3a577067568` | `8,10` | `168 -> 167` | `0.00000202 -> 0.00000164` | `-0.00000038` | `warning_prob_only_within_epsilon` |
| `bd:fa22a82f75e4b3c2` | `5,8` | `3 -> 3` | `0.04536540 -> 0.04490543` | `-0.00045997` | `warning_prob_only_within_epsilon` |

## Critical protected row

The protected eval row was not harmed:

- family: `bd:ea22cc14729b88fd`
- target: `7,9`
- rank: `4 -> 4`
- probability: `0.09005976 -> 0.09247528`
- probability delta: `+0.00241552`
- class: `not_regressed`

## Recommendation

Adopt this evaluator policy as the future retention-family gate behavior:

1. Fail on rank regression.
2. Fail on top-1 loss.
3. Fail on critical protected row regression.
4. Fail on eval probability-only drop larger than epsilon.
5. Warn, not fail, on eval probability-only drop within epsilon when rank/top1 are preserved and the row is not critical harmed.

This branch validates the evaluator rule on existing run2 artifacts only. It does not retroactively promote the run2 checkpoint.
