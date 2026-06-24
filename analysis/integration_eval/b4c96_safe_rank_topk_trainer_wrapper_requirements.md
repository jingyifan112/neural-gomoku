# b4c96-safe rank/top-k trainer wrapper requirements

## Branch

`exp/15x15-b4c96-safe-rank-topk-trainer-wrapper`

## Purpose

Add a strict b4c96-safe no-promotion trainer wrapper or patched trainer path for the capacity-data pairing Stage B probe.

This route is code-preparation only.

No checkpoint read, no training, no checkpoint write, no C export, no public benchmark, and no promotion are authorized in this route.

## Background

Stage A successfully initialized a b4c96 warmstart checkpoint:

`checkpoints/probes/15x15_capacity_data_pairing_b4c96_warmstart.pt`

Stage B was blocked because the selected trainer:

`scripts/train_rapfi_teacher_policy_rank_topk_probe.py`

did not expose explicit architecture controls:

- no `--channels`
- no `--blocks`
- no b4c96-specific mention
- no capacity-specific mention

Therefore Stage B cannot be considered a valid capacity-increase training probe until the trainer path explicitly supports b4c96.

## Required new script

Preferred new script:

`scripts/train_rapfi_teacher_policy_rank_topk_b4c96_probe.py`

The new script may reuse code from:

- `scripts/train_rapfi_teacher_policy_rank_topk_probe.py`
- `scripts/train_rapfi_teacher_policy_margin.py`

but it must explicitly expose and use architecture arguments.

## Required CLI arguments

The script must support at least:

- `--dataset`
- `--init-checkpoint`
- `--reference-checkpoint`
- `--out-checkpoint`
- `--out-csv`
- `--out-report`
- `--board-size`, default `15`
- `--channels`, default `96`
- `--blocks`, default `4`
- `--win-length`, default `5`
- `--margin`
- `--ce-weight`
- `--pair-weight`
- `--worst-weight`
- `--anchor-kl-weight`
- `--lr`
- `--epochs`
- `--weight-decay`
- `--seed`
- `--print-every`
- `--dry-run`
- `--no-save`

## Required safety guards

The script must refuse to write to:

- `checkpoints/15x15_current_best.pt`
- `checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`
- any path whose name includes `current_best`

The script must refuse to overwrite an existing output checkpoint unless an explicit allow-existing flag is added. Do not add such a flag unless necessary.

The script must not export C artifacts.

The script must not run public benchmark.

The script must not promote or overwrite current-best.

## Required model behavior

The training model must be instantiated with:

- board size 15
- channels 96
- blocks 4
- win length 5

The init checkpoint must be loaded into this b4c96 model.

The reference checkpoint can remain the base/current b4c64 reference model if the original rank/top-k trainer uses it only for KL/reference policy evaluation. If model architecture mismatch requires a separate reference model path, the implementation must handle this explicitly and safely.

## Required validation

Before any training execution in a later route, this wrapper route must pass:

- `PYTHONPATH=src python scripts/train_rapfi_teacher_policy_rank_topk_b4c96_probe.py --help`
- Python syntax compile
- static check that CLI includes `--channels` and `--blocks`
- static check that current-best overwrite guards exist

## Non-execution scope

Not authorized in this route:

- no checkpoint read
- no training
- no checkpoint write
- no C export
- no public benchmark
- no promotion
