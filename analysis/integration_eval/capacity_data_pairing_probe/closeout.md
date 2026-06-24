# Capacity-data pairing two-stage training probe closeout

## Branch

`exp/15x15-capacity-data-pairing-two-stage-training-probe`

## Route status

`CLOSED_BLOCKED_BEFORE_STAGE_B_TRAINING`

## Stage A result

Stage A b4c96 warmstart initialization completed successfully.

Input checkpoint:

`checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`

Warmstart checkpoint output:

`checkpoints/probes/15x15_capacity_data_pairing_b4c96_warmstart.pt`

Observed init summary:

- loaded source checkpoint
- wrote warmstart checkpoint
- copied exact tensors: 22
- copied prefix tensors: 50
- skipped tensors: 0

Stage A report:

`analysis/integration_eval/capacity_data_pairing_probe/stage_a_warmstart_report.md`

## Stage B compatibility result

Stage B training was not executed.

Compatibility check:

`analysis/integration_eval/capacity_data_pairing_probe/stage_b_trainer_compatibility.json`

Compatibility decision:

`STAGE_B_NOT_PROVEN_COMPATIBLE_NEEDS_CODEX_OR_WRAPPER_DO_NOT_TRAIN`

## Reason for blocking Stage B

The selected Stage B trainer:

`scripts/train_rapfi_teacher_policy_rank_topk_probe.py`

has the required training/checkpoint interface:

- init checkpoint
- reference checkpoint
- output checkpoint
- train dataset
- output metrics/report

However, compatibility discovery did not prove that it can explicitly run the intended b4c96 architecture:

- `trainer_has_channels_arg`: false
- `trainer_has_blocks_arg`: false
- `trainer_mentions_b4c96`: false
- `trainer_mentions_capacity`: false

Therefore Stage B was blocked before training.

## Actions performed

Performed:

- read authorized base checkpoint for Stage A warmstart initialization
- wrote authorized b4c96 warmstart checkpoint
- wrote Stage A warmstart report
- wrote Stage B trainer compatibility JSON/report

## Actions not performed

Not performed:

- no Stage B training
- no candidate checkpoint write
- no Stage C gate/eval
- no C export
- no public benchmark
- no promotion
- no overwrite of `current_best`
- no overwrite of manifests
- no modification of old untracked local artifacts

## Checkpoint tracking note

The warmstart checkpoint is intentionally not staged for git in this closeout.

Local checkpoint:

`checkpoints/probes/15x15_capacity_data_pairing_b4c96_warmstart.pt`

## Required next route

A small Codex or wrapper/patch route is required before training.

The next route should add or adapt a strict b4c96-safe trainer path that explicitly supports:

- `--channels 96`
- `--blocks 4`
- `--board-size 15`
- `--init-checkpoint checkpoints/probes/15x15_capacity_data_pairing_b4c96_warmstart.pt`
- `--reference-checkpoint checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`
- `--out-checkpoint checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt`
- no save unless authorized
- no current_best overwrite
- no export
- no benchmark
- no promotion

## Final decision

`NONE__TWO_STAGE_ROUTE_BLOCKED_BEFORE_STAGE_B_NEEDS_B4C96_SAFE_TRAINER_WRAPPER`
