# b4c96-safe rank/top-k trainer wrapper report

## New script path

- `scripts/train_rapfi_teacher_policy_rank_topk_b4c96_probe.py`

## Reused source scripts

- `scripts/train_rapfi_teacher_policy_rank_topk_probe.py`
- `scripts/train_rapfi_teacher_policy_margin.py`

## Architecture args added

- `--board-size`, default `15`
- `--channels`, default `96`
- `--blocks`, default `4`
- `--win-length`, default `5`

The train model is instantiated with the CLI board size, channels, and blocks, and the CLI win length is recorded on the model object and checkpoint metadata.

## Safety guards added

- Refuses any `--out-checkpoint` path containing `current_best`.
- Refuses `checkpoints/15x15_current_best.pt`.
- Refuses `checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`.
- Refuses to overwrite an existing `--out-checkpoint`.
- Keeps the route as no-promotion: no C export, no public benchmark, and no current-best overwrite behavior was added.

## Non-execution scope

This route was limited to code preparation and static validation. It did not run training, read checkpoint contents, write checkpoints, export C artifacts, run public benchmarks, or promote any checkpoint.

## Decision

B4C96_SAFE_RANK_TOPK_TRAINER_WRAPPER_READY_FOR_STATIC_VALIDATION_NO_TRAINING
