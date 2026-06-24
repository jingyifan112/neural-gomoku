# b4c96-safe rank/top-k gate wrapper static validation review

## Branch

`exp/15x15-b4c96-safe-rank-topk-gate-wrapper`

## Reviewed commit

`e403aae Add b4c96-safe rank-topk gate wrapper`

## Original static validation decision

`B4C96_SAFE_GATE_WRAPPER_STATIC_VALIDATION_FAIL_REVIEW_REQUIRED`

## Reason for review

The static validation failed because the text-level checks required:

- `does_not_mention_export`
- `does_not_mention_benchmark`
- `does_not_mention_promotion`

to be true.

Those checks are overly conservative if the terms appear only in comments, docstrings, help text, report text, or explicit non-execution guard language.

The meaningful safety question is whether the wrapper contains executable behavior that exports C artifacts, runs public benchmark, promotes, writes checkpoints, overwrites current_best, or overwrites manifests.

## Review scope

Reviewed script:

`scripts/evaluate_policy_rank_topk_gate_b4c96.py`

This review is static only.

No checkpoint read, no gate/eval, no checkpoint write, no C export, no public benchmark, and no promotion were performed.

## Required architecture support

The wrapper exposes:

- `--model-a-channels`
- `--model-b-channels`
- `--model-a-blocks`
- `--model-b-blocks`
- `--board-size`
- `--win-length`
- `--model-a`
- `--model-b`
- `--dataset`
- `--out-csv`
- `--out-report`

Expected Model A architecture:

- board-size 15
- channels 64
- blocks 4
- win-length 5

Expected Model B architecture:

- board-size 15
- channels 96
- blocks 4
- win-length 5

## Review decision

`B4C96_SAFE_GATE_WRAPPER_STATIC_REVIEW_NEEDED`

## Precise static review result

`B4C96_SAFE_GATE_WRAPPER_STATIC_REVIEW_FAIL_REQUIRES_PATCH`

## Checks

| Check | Result |
|---|---:|
| `script_exists` | `True` |
| `has_model_a_channels_arg` | `True` |
| `has_model_b_channels_arg` | `True` |
| `has_model_a_blocks_arg` | `True` |
| `has_model_b_blocks_arg` | `True` |
| `has_model_a_arg` | `True` |
| `has_model_b_arg` | `True` |
| `has_dataset_arg` | `True` |
| `has_out_csv` | `True` |
| `has_out_report` | `True` |
| `uses_load_compatible_checkpoint` | `True` |
| `no_torch_save` | `True` |
| `no_out_checkpoint_arg` | `True` |
| `no_subprocess_calls` | `True` |
| `no_os_system_calls` | `True` |
| `no_export_command_refs` | `True` |
| `no_current_best_write_refs` | `True` |
| `no_manifest_write_refs` | `False` |

## Danger hits

### `calls_torch_save`

- none

### `defines_out_checkpoint_arg`

- none

### `calls_subprocess`

- none

### `calls_os_system`

- none

### `mentions_pbrain_export_command`

- none

### `writes_current_best`

- none

### `writes_manifest`

- `472: out += ["- No C export, no public benchmark, no promotion, no manifest overwrite."]`
- `547: out.append("Evaluation only. Do not train, export, public benchmark, promote, or overwrite manifests from this wrapper.")`
- `634: print("evaluation only; no training/checkpoint/export/benchmark/promotion/manifest overwrite")`

## Final review decision

`B4C96_SAFE_GATE_WRAPPER_STATIC_REVIEW_FAIL_REQUIRES_PATCH`
