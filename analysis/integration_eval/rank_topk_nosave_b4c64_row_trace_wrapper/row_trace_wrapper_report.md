# b4c64/current-best no-save row trace wrapper patch

## Scope

- Branch: `exp/15x15-rank-topk-nosave-b4c64-row-trace-wrapper`
- Wrapper patch only.
- Added optional `--out-row-csv` per-row before/after diagnostics.
- No training, checkpoint save, C export, public benchmark, promotion, or current-best overwrite was performed.

## Static checks

| check | value |
|---|---:|
| `contains_out_row_csv` | `True` |
| `help_contains_out_row_csv` | `True` |
| `contains_torch_save` | `False` |
| `contains_out_checkpoint` | `False` |
| `contains_row_trace_helper` | `True` |
| `contains_write_row_csv` | `True` |
| `contains_row_trace_call` | `True` |

## Implementation notes

- Per-row trace reuses existing `diagnose_summary(model, [sample], device)` on one-row slices.
- This avoids adding a separate scoring implementation.
- The wrapper still writes only CSV/report diagnostics and does not save model artifacts.

## Outputs

- `analysis/integration_eval/rank_topk_nosave_b4c64_row_trace_wrapper/row_trace_wrapper_summary.json`
- `analysis/integration_eval/rank_topk_nosave_b4c64_row_trace_wrapper/wrapper_help_with_row_csv.txt`
