# b4c96-safe rank/top-k gate wrapper report

## New script path

- `scripts/evaluate_policy_rank_topk_gate_b4c96.py`

## Reused source scripts

- `scripts/evaluate_policy_rank_topk_gate.py`
- `scripts/train_rapfi_teacher_policy_margin.py`

## Architecture args added

- `--board-size`, default `15`
- `--win-length`, default `5`
- `--model-a-channels`, default `64`
- `--model-a-blocks`, default `4`
- `--model-b-channels`, default `96`
- `--model-b-blocks`, default `4`

Model A is instantiated with the CLI board size, Model A channels, Model A blocks, and win length. Model B is instantiated with the CLI board size, Model B channels, Model B blocks, and win length.

## Safety guards / non-write behavior

- Uses compatible checkpoint loading behavior for Model A and Model B.
- Does not add any checkpoint write path.
- Does not add C export, public benchmark, promotion, current-best overwrite, or manifest overwrite behavior.
- Writes only the requested CSV and report outputs when the gate is intentionally executed in a later route.

## Non-execution scope

This route was limited to code preparation and static validation. It did not run the gate/eval, read checkpoint contents, write checkpoints, export C artifacts, run public benchmarks, promote any checkpoint, or overwrite manifests.

## Decision

B4C96_SAFE_RANK_TOPK_GATE_WRAPPER_READY_FOR_STATIC_VALIDATION_NO_GATE
