# Rapfi Teacher Policy Repair Dataset: corpus8 selected

## Purpose

This JSON dataset converts filtered Rapfi teacher policy candidates into policy-only supervised repair rows.
No training or promotion is performed by this dataset generation step.

## Inputs

- Candidates CSV: `analysis/public_benchmark_eval/rapfi_teacher_policy_candidates_corpus8_selected.csv`
- Board snapshots JSON: `analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json`

## Output

- Repair dataset JSON: `analysis/public_benchmark_eval/rapfi_teacher_policy_repair_dataset_corpus8_selected.json`

## Summary

- rows: 25
- selection rule: `priority_candidate == true`
- policy target: Rapfi re-query best move
- value target: intentionally blank for every row
- intended use: policy-only repair / ranking experiment, not direct value regression

## Bucket counts

| bucket | count |
|---|---:|
| priority_policy_gap_unavailable | 13 |
| priority_policy_numeric_gap | 12 |

## Teacher eval kind counts

| eval kind | count |
|---|---:|
| numeric | 13 |
| mate | 7 |
| NA | 5 |

## Dry-run validation

- `train_rapfi_failure_repair.py --dry-run` loaded all 25 rows.
- Policy repair targets: 25.
- Value repair targets: 0.
- Checkpoint was not written.

## Safety notes

- Mate and NA teacher eval rows are retained as policy targets only.
- Numeric gaps are retained as metadata only.
- `value_target` is blank for all rows, so `train_rapfi_failure_repair.py` applies `value_mask=0` for these samples.
- Actual training should not use `--train-scope value_head` for policy repair; dry-run used it only because dry-run exits before optimization.

