# Retention Family Threshold Gate Policy Sync

## Scope

This document synchronizes the final retention-family gate policy after the evaluator threshold-policy branch and wrapper gates-only dry-run branch.

Explicit non-actions:

- No training.
- No checkpoint creation.
- No checkpoint promotion.
- No C export.
- No public benchmark.
- No model promotion.

## Branch lineage

| branch | commit | purpose |
| --- | --- | --- |
| `exp/15x15-retention-family-gate-threshold-policy-review` | `c07628a` | Reviewed whether probability-only micro regressions should remain hard failures. |
| `exp/15x15-retention-family-gate-evaluator-threshold-policy` | `da4091e` | Added evaluator support for `--eval-prob-epsilon`. |
| `exp/15x15-retention-family-wrapper-threshold-gate-dryrun` | `33bbf70` | Verified wrapper-level `gates-only` can pass `--eval-prob-epsilon 0.0005` through `--gate-cmd`. |

## Final gate policy

The retention-family gate policy is:

1. Missing before/after probe rows are hard failures.
2. Eval rank regressions are hard failures.
3. Eval top-1 losses are hard failures.
4. Critical protected row regressions are hard failures.
5. Eval probability-only drops larger than `--eval-prob-epsilon` are hard failures.
6. Eval probability-only drops within `--eval-prob-epsilon` are warnings when:
   - rank is not regressed,
   - top-1 is not lost,
   - the row is not the protected critical row,
   - before/after probabilities are available.
7. Train-side probability drops are reported but are not eval gate failures.
8. If `--require-train-improvement` is enabled, at least one train-side row must improve by rank or probability.

## Protected critical family rule

The critical protected family remains:

- family: `bd:ea22cc14729b88fd`
- protected eval target: `7,9`
- required gate scope: `external_or_family_level_only_not_sibling_only`
- `allowed_as_only_sibling_family_gate` must not be `yes`

The protected `7,9` row must not regress by rank, probability, or top-1 status.

## Recommended evaluator invocation

Future threshold gate runs should include:

```bash
--max-eval-rank-regressed 0 \
--max-eval-prob-regressed 0 \
--eval-prob-epsilon 0.0005 \
--require-train-improvement
```

Strict behavior remains available by setting:

```bash
--eval-prob-epsilon 0
```

## Evaluator dry-run evidence

The evaluator threshold-policy branch produced two dry-runs on existing run2 before/after probe files.

### Strict policy

Input setting:

- `--eval-prob-epsilon 0`

Result:

- decision: `FAIL`
- eval rows: `9`
- train rows: `2`
- eval rank regressions: `0`
- eval probability regressions: `3`
- eval hard probability regressions: `3`
- eval probability warnings: `0`
- train improved rows: `1`

This reproduces the original strict probability-gate failure.

### Threshold policy

Input setting:

- `--eval-prob-epsilon 0.0005`

Result:

- decision: `PASS`
- failures: `[]`
- eval rows: `9`
- train rows: `2`
- eval rank regressions: `0`
- eval probability regressions: `3`
- eval hard probability regressions: `0`
- eval probability warnings: `3`
- train improved rows: `1`

The three eval probability regressions are warning-only under the threshold policy.

## Wrapper gates-only evidence

The wrapper threshold-gate dry-run used:

- wrapper mode: `gates-only`
- gate command: evaluator invocation with `--eval-prob-epsilon 0.0005`
- promote on pass: `False`
- quarantine on fail: `False`

Result:

- wrapper overall status: `gates_passed`
- wrapper gates passed: `True`
- setup errors: `[]`
- manifest validation errors: `[]`
- gate command returncode: `0`
- gate command passed: `True`
- checkpoint action: `gates_passed_no_promotion_requested`

The wrapper can pass the threshold-policy flag through `--gate-cmd` without code changes.

## Warning rows under threshold policy

| family_id | target | rank before->after | prob before->after | prob delta | class |
| --- | --- | --- | --- | --- | --- |
| `bd:690e24eaa9cbf978` | `5,11` | `39 -> 38` | `0.00194259 -> 0.00182245` | `-0.00012014` | `warning_prob_only_within_epsilon` |
| `bd:fcfbf3a577067568` | `8,10` | `168 -> 167` | `0.00000202 -> 0.00000164` | `-0.00000038` | `warning_prob_only_within_epsilon` |
| `bd:fa22a82f75e4b3c2` | `5,8` | `3 -> 3` | `0.04536540 -> 0.04490543` | `-0.00045997` | `warning_prob_only_within_epsilon` |

## Protected row outcome

The protected eval row was not harmed:

- family: `bd:ea22cc14729b88fd`
- target: `7,9`
- rank: `4 -> 4`
- probability: `0.09005976 -> 0.09247528`
- probability delta: `+0.00241552`
- class: `not_regressed`

## Operational interpretation

The threshold policy should be used as a retention-family gate rule, not as a model promotion rule.

A threshold-policy PASS means:

- the specific retention-family gate conditions passed,
- probability-only micro drops were downgraded to warnings,
- no hard rank/top1/critical protected failure was observed.

A threshold-policy PASS does not mean:

- the candidate should be promoted,
- the checkpoint should be saved as final,
- C weights should be exported,
- public benchmarks should be skipped,
- broader model quality has been established.

## Current recommendation

Use `--eval-prob-epsilon 0.0005` for future retention-family evaluator and wrapper gate runs.

Keep the warning rows visible in reports so that probability-only micro drops remain auditable, even when they do not block the gate.
