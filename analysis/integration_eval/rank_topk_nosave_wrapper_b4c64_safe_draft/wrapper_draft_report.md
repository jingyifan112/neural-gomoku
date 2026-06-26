# b4c64/current-best rank/top-k no-save wrapper draft

## Scope

- Branch: `exp/15x15-rank-topk-nosave-wrapper-b4c64-safe-draft`
- Drafts a b4c64/current-best-safe no-save wrapper from the existing b4c96 reference wrapper.
- No training, checkpoint save, C export, public benchmark, promotion, or current-best overwrite was performed.

## Generated wrapper

- Source: `scripts/probe_policy_rank_topk_protected_nosave_b4c96.py`
- Destination: `scripts/probe_policy_rank_topk_protected_nosave_b4c64_current_best.py`

## Static checks

| check | value |
|---|---:|
| `contains_torch_save` | `False` |
| `contains_save_checkpoint_text` | `False` |
| `contains_out_checkpoint_arg` | `False` |
| `contains_b4c96_literal` | `False` |
| `contains_channels_arg` | `True` |
| `contains_init_checkpoint_arg` | `True` |
| `contains_reference_checkpoint_arg` | `True` |
| `contains_no_save_text` | `True` |
| `line_count` | `421` |

## Safety interpretation

- Static safety status: `DRAFT_STATIC_SAFE_FOR_HELP_ONLY`
- Next step may run `--help` and a zero/one-epoch smoke only after reviewing CLI defaults.

## Outputs

- `analysis/integration_eval/rank_topk_nosave_wrapper_b4c64_safe_draft/wrapper_draft_report.md`
- `analysis/integration_eval/rank_topk_nosave_wrapper_b4c64_safe_draft/wrapper_help.txt`
- `analysis/integration_eval/rank_topk_nosave_wrapper_b4c64_safe_draft/wrapper_help_after_default_patch.txt`
- `analysis/integration_eval/rank_topk_nosave_wrapper_b4c64_safe_draft/wrapper_static_checks.json`
- `analysis/integration_eval/rank_topk_nosave_wrapper_b4c64_safe_draft/wrapper_static_checks_after_default_patch.json`
