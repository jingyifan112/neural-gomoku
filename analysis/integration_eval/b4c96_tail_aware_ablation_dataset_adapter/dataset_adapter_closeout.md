# b4c96 tail-aware ablation dataset adapter closeout

## Branch

`exp/15x15-b4c96-tail-aware-ablation-dataset-adapter`

## Purpose

Create tail-aware no-save ablation datasets for A4/A5 after A1/A2/A3 objective reweighting failed.

Prior run1 showed that simple objective reweighting improved the train group but caused protected/tail regressions. This adapter therefore prepares tail-aware training inputs before further b4c96 no-save ablations.

## Scope

Dataset adapter only.

No training was run. No checkpoint was read or written. No C export, public benchmark, promotion, or `current_best` overwrite was performed.

## Script

`scripts/build_b4c96_tail_aware_ablation_datasets.py`

## Inputs

- Source dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_protected_train_11_50_weightcap3.json`
- Forensics CSV: `analysis/integration_eval/b4c96_stagec_failure_forensics.csv`
- Run1 summary: `analysis/integration_eval/b4c96_nosave_objective_ablation_run1/run1_summary.csv`

## Outputs

- `analysis/public_benchmark_eval/b4c96_tail_aware_ablation_A4_tail_guard_dataset.json`
- `analysis/public_benchmark_eval/b4c96_tail_aware_ablation_A5_tail_guard_downweight_dataset.json`
- `analysis/integration_eval/b4c96_tail_aware_ablation_dataset_adapter/dataset_manifest.csv`
- `analysis/integration_eval/b4c96_tail_aware_ablation_dataset_adapter/dataset_adapter_summary.json`
- `analysis/integration_eval/b4c96_tail_aware_ablation_dataset_adapter/dataset_adapter_report.md`
- `analysis/integration_eval/b4c96_tail_aware_ablation_dataset_adapter/dataset_adapter_closeout.md`

## Adapter results

| dataset | source train rows | output train rows | added tail guard rows | severe downweighted rows | suppress count |
|---|---:|---:|---:|---:|---:|
| A4 tail guard | 7 | 10 | 3 | 0 | 5 |
| A5 tail guard downweight | 7 | 10 | 3 | 3 | 5 |

Both datasets preserve fixed suppress count:

`{5: 10}`

Both datasets keep protected/tail eval groups unchanged:

- protected eval rows: 15
- tail eval rows: 3

## Dataset meanings

A4:

- adds compatible tail evaluation rows into train samples as low-weight tail guards
- does not downweight severe/core-regression train rows

A5:

- adds the same compatible tail guard rows
- additionally downweights train rows overlapping severe/core-regression forensics IDs

## Validation

Validation passed:

- output datasets exist
- all train rows have fixed suppress count 5
- tail guard rows were added
- adapter metadata exists
- no checkpoint-producing action was performed

## Decision

`B4C96_TAIL_AWARE_ABLATION_DATASET_ADAPTER_COMPLETE`

## Recommended next route

Open:

`exp/15x15-b4c96-tail-aware-nosave-ablation-run2`

Purpose:

Run A4/A5 through the b4c96-safe no-save wrapper:

- A4 tail guard dataset
- A5 tail guard + severe downweight dataset

The next route must remain no-save only unless a later gate explicitly authorizes checkpoint-producing training.

## Actions not performed

- no training
- no checkpoint read
- no checkpoint write
- no C export
- no public benchmark
- no promotion
- no overwrite of `current_best`
- no overwrite of manifests
- no modification of old untracked local artifacts

## Final decision

`ADAPTER_READY_FOR_A4_A5_NOSAVE_RUN2`
