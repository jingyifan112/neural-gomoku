# b4c96-safe rank/top-k gate wrapper requirements

## Branch

`exp/15x15-b4c96-safe-rank-topk-gate-wrapper`

## Purpose

Add a strict b4c96-safe no-promotion gate wrapper for Stage C of the capacity-data pairing route.

This route is code-preparation only.

No checkpoint read, no gate/eval execution, no checkpoint write, no C export, no public benchmark, and no promotion are authorized in this route.

## Background

Stage C using the existing evaluator was blocked because:

`scripts/evaluate_policy_rank_topk_gate.py`

did not expose architecture controls needed to safely compare b4c64 Model A against b4c96 Model B:

- no `--model-a-channels`
- no `--model-b-channels`
- no `--model-a-blocks`
- no `--model-b-blocks`
- no generic `--channels`
- no generic `--blocks`
- no b4c96 support signal
- no `load_compatible_checkpoint` signal

## Required new script

Preferred new script:

`scripts/evaluate_policy_rank_topk_gate_b4c96.py`

The new script may reuse logic from:

- `scripts/evaluate_policy_rank_topk_gate.py`
- `scripts/train_rapfi_teacher_policy_margin.py`

## Required CLI arguments

The script must support at least:

- `--dataset`
- `--model-a`
- `--model-b`
- `--out-csv`
- `--out-report`
- `--margin`
- `--board-size`, default `15`
- `--win-length`, default `5`
- `--model-a-channels`, default `64`
- `--model-a-blocks`, default `4`
- `--model-b-channels`, default `96`
- `--model-b-blocks`, default `4`

## Required model behavior

The script must instantiate Model A with:

- board size 15
- channels 64
- blocks 4
- win length 5

The script must instantiate Model B with:

- board size 15
- channels 96
- blocks 4
- win length 5

The script must load Model A from:

`checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`

The script must load Model B from:

`checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt`

The script must use compatible checkpoint loading behavior where appropriate.

## Required safety guards

The script must not:

- write checkpoints
- export C artifacts
- run public benchmark
- promote
- overwrite current_best
- overwrite manifests

The script must write only CSV/report paths passed via CLI.

## Required validation

Before any gate execution in a later route, this wrapper route must pass:

- `PYTHONPATH=src python scripts/evaluate_policy_rank_topk_gate_b4c96.py --help`
- in-memory syntax compile
- static check that model-a/model-b architecture args exist
- static check that no checkpoint write / export / benchmark / promotion behavior exists

## Non-execution scope

Not authorized in this route:

- no checkpoint read
- no gate/eval execution
- no checkpoint write
- no C export
- no public benchmark
- no promotion
