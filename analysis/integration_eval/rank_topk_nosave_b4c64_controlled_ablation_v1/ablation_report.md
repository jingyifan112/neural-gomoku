# b4c64/current-best rank/top-k controlled no-save ablation v1

## Scope

- Branch: `exp/15x15-rank-topk-nosave-b4c64-controlled-ablation-v1`
- Controlled no-save ablation only.
- No checkpoint save, C export, public benchmark, promotion, or current-best overwrite was performed.

## Config summary

| config | verdict | selection | train prob Δ | protected beats-worst Δ | tail rank>50 Δ | tail mean-rank Δ |
|---|---|---|---:|---:|---:|---:|
| `baseline_lr1e7_anchor035` | `FAIL_B4C64_CURRENT_BEST_SAFE_NO_SAVE_PROBE` | `train_improves_but_gate_regresses` | 0.0004910827413238752 | -1.0 | 1.0 | 37.33333333333333 |
| `lowlr_anchor100` | `FAIL_B4C64_CURRENT_BEST_SAFE_NO_SAVE_PROBE` | `train_improves_but_gate_regresses` | 0.0004910153966193322 | -1.0 | 1.0 | 37.33333333333333 |
| `pair_focus_lowlr_anchor100` | `FAIL_B4C64_CURRENT_BEST_SAFE_NO_SAVE_PROBE` | `train_improves_but_gate_regresses` | 0.0004910151305271679 | -1.0 | 1.0 | 37.33333333333333 |

## Decision policy

- Do not save any checkpoint from this ablation.
- A follow-up no-save probe is allowed only if a config improves train rows while preserving protected and tail gates.
- If all configs still regress protected/tail gates, change the objective/data split rather than increasing epochs.

## Outputs

- `analysis/integration_eval/rank_topk_nosave_b4c64_controlled_ablation_v1/ablation_report.md`
- `analysis/integration_eval/rank_topk_nosave_b4c64_controlled_ablation_v1/ablation_summary.csv`
- `analysis/integration_eval/rank_topk_nosave_b4c64_controlled_ablation_v1/ablation_summary.json`
- `analysis/integration_eval/rank_topk_nosave_b4c64_controlled_ablation_v1/baseline_lr1e7_anchor035/eval.csv`
- `analysis/integration_eval/rank_topk_nosave_b4c64_controlled_ablation_v1/baseline_lr1e7_anchor035/report.md`
- `analysis/integration_eval/rank_topk_nosave_b4c64_controlled_ablation_v1/baseline_lr1e7_anchor035/train.log`
- `analysis/integration_eval/rank_topk_nosave_b4c64_controlled_ablation_v1/lowlr_anchor100/eval.csv`
- `analysis/integration_eval/rank_topk_nosave_b4c64_controlled_ablation_v1/lowlr_anchor100/report.md`
- `analysis/integration_eval/rank_topk_nosave_b4c64_controlled_ablation_v1/lowlr_anchor100/train.log`
- `analysis/integration_eval/rank_topk_nosave_b4c64_controlled_ablation_v1/pair_focus_lowlr_anchor100/eval.csv`
- `analysis/integration_eval/rank_topk_nosave_b4c64_controlled_ablation_v1/pair_focus_lowlr_anchor100/report.md`
- `analysis/integration_eval/rank_topk_nosave_b4c64_controlled_ablation_v1/pair_focus_lowlr_anchor100/train.log`
