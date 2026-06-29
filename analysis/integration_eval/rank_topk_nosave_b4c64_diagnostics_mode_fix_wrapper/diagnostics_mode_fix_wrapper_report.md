# b4c64 diagnostics mode fix wrapper

## Scope

- Branch: `exp/15x15-rank-topk-nosave-b4c64-diagnostics-mode-fix-wrapper`
- Wrapper diagnostics mode fix only.
- No training, checkpoint save, C export, public benchmark, promotion, or current-best overwrite was performed.

## Rationale

- BN/mode audit showed full `train()` changes hard-guard outputs, while `set_policy_head_training_mode()` matches eval outputs.
- Corrected gradient audit v2 showed hard-guard gradients are safe under policy-head training mode.
- This patch forces policy-head/eval-consistent mode before both before and after diagnostics.

## Static checks

| check | value |
|---|---:|
| `contains_diagnostics_mode_fix_marker` | `True` |
| `contains_train_guardaware` | `True` |
| `call_path_uses_train_guardaware` | `True` |
| `contains_hard_guard_args` | `True` |
| `contains_torch_save` | `False` |
| `contains_out_checkpoint` | `False` |
| `set_policy_head_training_mode_call_count` | `3` |

## Decision

- Next step: rerun hardguard-only sanity no-save probe with this diagnostics mode fix.

## Outputs

- `analysis/integration_eval/rank_topk_nosave_b4c64_diagnostics_mode_fix_wrapper/diagnostics_mode_fix_wrapper_summary.json`
- `analysis/integration_eval/rank_topk_nosave_b4c64_diagnostics_mode_fix_wrapper/wrapper_help.txt`
