# b4c96-safe Stage B training closeout

## Branch

`exp/15x15-b4c96-safe-stage-b-training-probe`

## Scope

Stage B only: no-promotion capacity-data pairing training using the b4c96-safe rank/top-k trainer wrapper.

## Script

`scripts/train_rapfi_teacher_policy_rank_topk_b4c96_probe.py`

## Authorized architecture

- board size: 15
- channels: 96
- blocks: 4
- win length: 5

## Inputs

- train dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json`
- init checkpoint: `checkpoints/probes/15x15_capacity_data_pairing_b4c96_warmstart.pt`
- reference checkpoint: `checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`

## Outputs

- candidate checkpoint: `checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt`
- train metrics: `analysis/integration_eval/capacity_data_pairing_probe/train_metrics.csv`
- train report: `analysis/integration_eval/capacity_data_pairing_probe/train_report.md`

## Actions performed

- read authorized init checkpoint
- read authorized reference checkpoint
- trained b4c96 Stage B candidate
- wrote authorized candidate checkpoint
- wrote authorized train metrics and report

## Actions not performed

- no Stage C gate
- no C export
- no public benchmark
- no promotion
- no overwrite of current_best
- no overwrite of manifests
- no modification of old untracked local artifacts

## Checkpoint tracking note

The warmstart and candidate checkpoints are intentionally not staged for git.

## Final decision

`B4C96_SAFE_STAGE_B_TRAINING_COMPLETE_READY_FOR_STAGE_C_GATE_AUTHORIZATION`
