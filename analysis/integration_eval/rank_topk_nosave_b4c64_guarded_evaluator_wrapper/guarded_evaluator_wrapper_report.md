# b4c64/current-best guarded evaluator wrapper patch

## Scope

- Branch: `exp/15x15-rank-topk-nosave-b4c64-guarded-evaluator-wrapper`
- Wrapper patch only.
- Added hard-guard row evaluation when dataset provides `hard_guard_samples`.
- No training, checkpoint save, C export, public benchmark, promotion, or current-best overwrite was performed.

## Static checks

| check | value |
|---|---:|
| `contains_out_hard_guard_csv` | `True` |
| `help_contains_out_hard_guard_csv` | `True` |
| `contains_evaluate_hard_guards` | `True` |
| `contains_apply_hard_guard_verdict` | `True` |
| `contains_fail_hard_guard_verdict` | `True` |
| `contains_write_hard_guard_csv` | `True` |
| `contains_torch_save` | `False` |
| `contains_out_checkpoint` | `False` |

## Behavior

- If no `hard_guard_samples` are present, wrapper behavior remains group-gate based.
- If hard guards are present and any guard fails, final verdict becomes `FAIL_HARD_GUARD_ROW_DAMAGE`.
- Optional `--out-hard-guard-csv` writes hard-guard row outcomes.

## Outputs

- `analysis/integration_eval/rank_topk_nosave_b4c64_guarded_evaluator_wrapper/guarded_evaluator_wrapper_summary.json`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guarded_evaluator_wrapper/wrapper_help_with_hard_guard.txt`
