# Rapfi Teacher Policy Margin Dataset: corpus8 selected

## Purpose

This dataset converts policy-only teacher repair rows into pairwise policy-logit margin rows.

Each sample asks the model to satisfy:

`teacher_move_logit > current_best_direct_move_logit + margin`

## Inputs

- Source repair dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_repair_dataset_corpus8_selected.json`

## Output

- Margin dataset JSON: `analysis/public_benchmark_eval/rapfi_teacher_policy_margin_dataset_corpus8_selected.json`

## Summary

- source rows: 25
- margin samples: 25
- skipped rows: 0
- target move: Rapfi teacher move
- suppress move: current_best direct move
- value targets: none

## Bucket counts

| bucket | count |
|---|---:|
| priority_policy_gap_unavailable | 13 |
| priority_policy_numeric_gap | 12 |

## Sample weight summary

- min: 1.000
- max: 3.000
- mean: 1.419

## Safety notes

- Numeric gap is used only as a capped sample-weight heuristic.
- Numeric gap is not used as a value target.
- This dataset should be dry-run diagnosed before training.
- Existing full-model margin scripts should not be used for final training without a conservative train scope.

