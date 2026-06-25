# b4c96 tail-aware ablation dataset adapter report

## Scope

- Dataset adapter only.
- No training.
- No checkpoint read or write.
- No C export, no public benchmark, no promotion.

## Inputs

- source_dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_protected_train_11_50_weightcap3.json`
- forensics_csv: `analysis/integration_eval/b4c96_stagec_failure_forensics.csv`
- run1_summary: `analysis/integration_eval/b4c96_nosave_objective_ablation_run1/run1_summary.csv`
- severe_case_ids_loaded: 10

## Output datasets

| dataset | output_train_rows | added_tail_guard_rows | severe_downweighted_rows | weight_sum | path |
|---|---:|---:|---:|---:|---|
| b4c96_tail_aware_ablation_A4_tail_guard_dataset | 10 | 3 | 0 | 21.894943 | `analysis/public_benchmark_eval/b4c96_tail_aware_ablation_A4_tail_guard_dataset.json` |
| b4c96_tail_aware_ablation_A5_tail_guard_downweight_dataset | 10 | 3 | 3 | 17.394943 | `analysis/public_benchmark_eval/b4c96_tail_aware_ablation_A5_tail_guard_downweight_dataset.json` |

## Dataset meanings

- A4 adds compatible tail evaluation rows into the no-save training samples as low-weight tail guards.
- A5 does the same and additionally downweights train rows that overlap severe/core-regression forensics IDs.
- These datasets are no-save ablation inputs only; they are not promotion-valid heldout evidence.

## Decision

`B4C96_TAIL_AWARE_ABLATION_DATASET_ADAPTER_READY`

Next step: run A4/A5 no-save ablations through the b4c96-safe wrapper.
