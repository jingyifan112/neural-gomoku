# b4c96-safe Stage C gate execution closeout

## Branch

`exp/15x15-b4c96-safe-stage-c-gate-execution`

## Scope

Stage C only: no-promotion rank/top-k gate comparing b4c64 Model A against b4c96 Stage B candidate Model B.

## Script

`scripts/evaluate_policy_rank_topk_gate_b4c96.py`

## Inputs

- Model A: `checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`
- Model A architecture: board-size 15, channels 64, blocks 4, win-length 5
- Model B: `checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt`
- Model B architecture: board-size 15, channels 96, blocks 4, win-length 5
- Gate dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json`

## Outputs

- Gate CSV: `analysis/integration_eval/capacity_data_pairing_probe/gate_eval.csv`
- Gate report: `analysis/integration_eval/capacity_data_pairing_probe/gate_eval.md`

## Actions performed

- read authorized Model A checkpoint
- read authorized Model B checkpoint
- executed b4c96-safe Stage C gate/eval
- wrote authorized gate CSV/report

## Actions not performed

- no checkpoint write
- no C export
- no public benchmark
- no promotion
- no overwrite of current_best
- no overwrite of manifests
- no modification of old untracked local artifacts

## Final decision

`B4C96_SAFE_STAGE_C_GATE_EXECUTION_COMPLETE_READY_FOR_CAPACITY_DATA_PAIRING_FINAL_REVIEW`
