# Capacity-data pairing training probe authorization

## Branch

`exp/15x15-capacity-data-pairing-training-probe`

## Authorization status

`EXPLICIT_NO_PROMOTION_TRAINING_PROBE_AUTHORIZED`

## Training scope

No-promotion data-supported capacity probe pairing increased multi-suppress teacher-divergence data with the known b4c96 capacity target, only to test whether increased model capacity corresponds to increased training data.

This probe is not promotion and not public benchmark.

## Train dataset

`analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json`

## Gate dataset

`analysis/integration_eval/retention_family_training_consumer_adapter_eval_dataset.json`

## Base checkpoint

`checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`

## Candidate checkpoint output

`checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt`

## Expected output files

- `analysis/integration_eval/capacity_data_pairing_probe/train_report.md`
- `analysis/integration_eval/capacity_data_pairing_probe/train_metrics.csv`
- `analysis/integration_eval/capacity_data_pairing_probe/gate_eval.json`
- `analysis/integration_eval/capacity_data_pairing_probe/gate_eval.md`
- `analysis/integration_eval/capacity_data_pairing_probe/closeout.md`

## Authorized actions

Authorized only for this route:

- read the listed base checkpoint
- execute the no-promotion training probe commands needed for this scope
- write the listed candidate checkpoint output
- write the listed expected output files

## Forbidden actions

Forbidden:

- C export
- public benchmark
- promotion
- overwrite `current_best`
- overwrite current-best aliases
- overwrite manifest
- modify old untracked files
