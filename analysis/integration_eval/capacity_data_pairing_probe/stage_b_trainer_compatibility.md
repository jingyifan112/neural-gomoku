# Stage B trainer compatibility check

## Route

`exp/15x15-capacity-data-pairing-two-stage-training-probe`

## Purpose

Check whether the selected Stage B trainer can safely execute the b4c96 capacity-data pairing training probe.

This check does not train and does not read checkpoint contents.

## Trainer

`scripts/train_rapfi_teacher_policy_rank_topk_probe.py`

## Warmstart checkpoint

`checkpoints/probes/15x15_capacity_data_pairing_b4c96_warmstart.pt`

## Signals

| Signal | Value |
|---|---:|
| `trainer_has_channels_arg` | `False` |
| `trainer_has_blocks_arg` | `False` |
| `trainer_mentions_b4c96` | `False` |
| `trainer_mentions_capacity` | `False` |
| `trainer_uses_policy_value_net` | `True` |
| `trainer_loads_compatible_checkpoint` | `True` |
| `trainer_has_out_checkpoint` | `True` |
| `trainer_has_init_checkpoint` | `True` |
| `trainer_has_reference_checkpoint` | `True` |

## Conservative decision

`STAGE_B_NOT_PROVEN_COMPATIBLE_NEEDS_CODEX_OR_WRAPPER_DO_NOT_TRAIN`

## Interpretation

If the trainer does not expose architecture controls such as `--channels 96` and `--blocks 4`, this route must not execute Stage B as a capacity probe. In that case, use Codex or a small wrapper/patch route to add strict b4c96 support before training.

## Non-execution scope

Not performed:

- no checkpoint content read
- no training
- no checkpoint write
- no C export
- no public benchmark
- no promotion
