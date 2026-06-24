# b4c96-safe no-save ablation wrapper static validation

## Branch

`exp/15x15-b4c96-safe-nosave-ablation-wrapper`

## Scope

Static validation only.

No training was run. No checkpoint was read or written. No C export, public benchmark, or promotion was performed.

## Script

`scripts/probe_policy_rank_topk_protected_nosave_b4c96.py`

## Purpose

Add a b4c96-safe no-save objective ablation wrapper after Stage C failure forensics showed protected/objective regressions.

The wrapper is intended to execute in-memory objective ablations only, with no checkpoint save.

## Architecture controls

The wrapper exposes:

- `--board-size`
- `--win-length`
- `--channels`
- `--blocks`

Default architecture:

- board size: 15
- win length: 5
- channels: 96
- blocks: 4

## Objective controls

The wrapper exposes:

- `--ce-weight`
- `--pair-weight`
- `--worst-weight`
- `--anchor-kl-weight`
- `--margin`
- `--lr`
- `--epochs`
- `--weight-decay`
- `--seed`

## Safety controls

The wrapper:

- uses `load_compatible_checkpoint`
- builds `PolicyValueNet` with explicit channels/blocks
- refuses `15x15_current_best.pt` as b4c96 init/reference checkpoint
- does not contain `torch.save`
- does not expose `out_checkpoint`
- writes only CSV/report metrics
- does not export C
- does not run public benchmark
- does not promote

## Static validation result

`PASS_STATIC_VALIDATION`

## Next step

Run a very small no-save smoke probe only after confirming the protected dataset exists and the b4c96 checkpoint loads with explicit architecture.

## Final decision

`B4C96_SAFE_NOSAVE_ABLATION_WRAPPER_STATIC_READY`
