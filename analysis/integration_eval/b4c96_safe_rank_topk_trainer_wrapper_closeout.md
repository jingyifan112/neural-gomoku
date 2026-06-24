# b4c96-safe rank/top-k trainer wrapper closeout

## Branch

`exp/15x15-b4c96-safe-rank-topk-trainer-wrapper`

## Commit

`281af3d Add b4c96-safe rank-topk trainer wrapper`

## Purpose

This route added a strict b4c96-safe no-promotion trainer wrapper for the capacity-data pairing Stage B probe.

## New script

`scripts/train_rapfi_teacher_policy_rank_topk_b4c96_probe.py`

## Supporting reports

- `analysis/integration_eval/b4c96_safe_rank_topk_trainer_wrapper_requirements.md`
- `analysis/integration_eval/b4c96_safe_rank_topk_trainer_wrapper_report.md`
- `analysis/integration_eval/b4c96_safe_rank_topk_trainer_wrapper_static_validation.json`

## Static validation result

`B4C96_SAFE_WRAPPER_STATIC_VALIDATION_PASS_READY_FOR_AUTHORIZED_STAGE_B`

## Confirmed wrapper capabilities

Confirmed:

- exposes `--channels`
- exposes `--blocks`
- exposes `--board-size`
- exposes `--win-length`
- exposes `--init-checkpoint`
- exposes `--reference-checkpoint`
- exposes `--out-checkpoint`
- uses `load_compatible_checkpoint`
- includes current-best overwrite guards
- refuses existing output checkpoint
- supports `--dry-run`
- supports `--no-save`
- default channels include 96
- default blocks include 4

## Why this wrapper was required

The previous Stage B candidate trainer did not expose explicit capacity architecture controls:

- no `--channels`
- no `--blocks`
- no b4c96-specific mention
- no capacity-specific mention

Therefore Stage B could not safely prove that the increased-data training probe was also using increased model capacity.

## Actions performed

Performed:

- added b4c96-safe rank/top-k trainer wrapper
- added wrapper requirements/report
- added static validation JSON
- ran `--help`
- ran in-memory syntax compile
- ran static architecture/guard validation
- committed and pushed wrapper route

## Actions not performed

Not performed:

- no checkpoint read
- no checkpoint inspection
- no training
- no checkpoint write
- no C export
- no public benchmark
- no promotion
- no overwrite of `current_best`
- no overwrite of manifests
- no modification of old untracked local artifacts

## Remaining local checkpoint note

The Stage A warmstart checkpoint remains local and intentionally untracked:

`checkpoints/probes/15x15_capacity_data_pairing_b4c96_warmstart.pt`

## Next required route

A separate explicit authorization is required before running Stage B training with:

`scripts/train_rapfi_teacher_policy_rank_topk_b4c96_probe.py`

## Final decision

`B4C96_SAFE_WRAPPER_ROUTE_CLOSED_READY_FOR_EXPLICIT_STAGE_B_TRAINING_AUTHORIZATION`
