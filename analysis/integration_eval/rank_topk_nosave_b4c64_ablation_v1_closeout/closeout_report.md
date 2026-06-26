# b4c64/current-best rank/top-k no-save ablation v1 closeout

## Scope

- Branch: `exp/15x15-rank-topk-nosave-b4c64-ablation-v1-closeout`
- Closeout only.
- No training, checkpoint save, C export, public benchmark, promotion, or current-best overwrite was performed.

## Source

- Source ablation summary: `analysis/integration_eval/rank_topk_nosave_b4c64_controlled_ablation_v1/ablation_summary.json`

## Findings

- Config count: `3`
- All configs failed wrapper gate: `True`
- All configs improved train target probability: `True`
- All configs regressed protected beats-worst gate: `True`
- All configs regressed tail rank>50 gate: `True`
- No checkpoint-like outputs: `True`

## Config table

| config | verdict | selection | train prob Δ | protected beats-worst Δ | tail rank>50 Δ | tail mean-rank Δ |
|---|---|---|---:|---:|---:|---:|
| `baseline_lr1e7_anchor035` | `FAIL_B4C64_CURRENT_BEST_SAFE_NO_SAVE_PROBE` | `train_improves_but_gate_regresses` | 0.0004910827413238752 | -1.0 | 1.0 | 37.33333333333333 |
| `lowlr_anchor100` | `FAIL_B4C64_CURRENT_BEST_SAFE_NO_SAVE_PROBE` | `train_improves_but_gate_regresses` | 0.0004910153966193322 | -1.0 | 1.0 | 37.33333333333333 |
| `pair_focus_lowlr_anchor100` | `FAIL_B4C64_CURRENT_BEST_SAFE_NO_SAVE_PROBE` | `train_improves_but_gate_regresses` | 0.0004910151305271679 | -1.0 | 1.0 | 37.33333333333333 |

## Decision

- Final decision: `CLOSE_ABLATION_V1_NO_SAVE`
- Do not save a candidate from this route.
- Do not run C export, public benchmark, promotion, or current-best overwrite.
- Do not continue this route by increasing epochs.

## Next route

- Add row-level gate tracing before changing objective weights again.
- The trace should identify which protected row lost `teacher_beats_worst/all` and which tail row crossed into `rank_gt50`.
- After row-level diagnosis, decide whether to change objective terms, split rows differently, or exclude/anchor specific rows.

## Outputs

- `analysis/integration_eval/rank_topk_nosave_b4c64_ablation_v1_closeout/closeout_summary.json`
