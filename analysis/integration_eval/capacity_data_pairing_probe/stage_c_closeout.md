# Stage C gate compatibility closeout

## Branch

`exp/15x15-b4c96-safe-stage-c-gate`

## Route status

`CLOSED_BLOCKED_BEFORE_GATE_EVAL`

## Scope

Stage C no-promotion gate route was authorized to compare the base/reference checkpoint against the b4c96 Stage B candidate checkpoint on the increased multi-suppress teacher-divergence dataset.

This route did not run gate/eval because compatibility was not proven.

## Gate script checked

`scripts/evaluate_policy_rank_topk_gate.py`

## Intended inputs

Model A:

`checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`

Model B:

`checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt`

Gate dataset:

`analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json`

## Compatibility decision

`STAGE_C_GATE_NOT_PROVEN_COMPATIBLE_NEEDS_B4C96_SAFE_GATE_WRAPPER_DO_NOT_GATE`

## Reason for blocking

The selected gate evaluator has basic gate arguments:

- `--model-a`
- `--model-b`
- `--dataset`
- `--out-csv`
- `--out-report`

But it does not expose architecture controls needed to safely compare b4c64 Model A with b4c96 Model B:

- no `--model-a-channels`
- no `--model-b-channels`
- no `--model-a-blocks`
- no `--model-b-blocks`
- no generic `--channels`
- no generic `--blocks`
- no b4c96-specific support signal
- no `load_compatible_checkpoint` signal

Therefore Stage C gate/eval was blocked before checkpoint read or evaluation.

## Actions performed

Performed:

- checked Stage C gate script interface
- wrote Stage C compatibility JSON
- wrote Stage C compatibility report
- blocked gate/eval before execution

## Actions not performed

Not performed:

- no checkpoint read
- no gate/eval
- no checkpoint write
- no C export
- no public benchmark
- no promotion
- no overwrite of `current_best`
- no overwrite of manifests
- no modification of old untracked local artifacts

## Required next route

A b4c96-safe gate wrapper route is required.

The new gate wrapper should explicitly support:

- Model A architecture: board-size 15, channels 64, blocks 4, win-length 5
- Model B architecture: board-size 15, channels 96, blocks 4, win-length 5
- Model A checkpoint: `checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`
- Model B checkpoint: `checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt`
- Gate dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json`
- no C export
- no public benchmark
- no promotion
- no current_best overwrite

## Final decision

`NONE__STAGE_C_GATE_ROUTE_BLOCKED_NEEDS_B4C96_SAFE_GATE_WRAPPER`
