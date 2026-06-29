# b4c64/current-best guard-aware objective run2 v2 modefix

## Scope

- Branch: `exp/15x15-rank-topk-nosave-b4c64-guardaware-objective-run2-v2-modefix`
- Full guard-aware objective v1 rerun using guarded split v2 and diagnostics mode fix.
- No checkpoint save, C export, public benchmark, promotion, or current-best overwrite was performed.

## Run status

- Run status: `PASS_GUARDAWARE_OBJECTIVE_RUN2_V2_MODEFIX_NO_SAVE`
- Verdict: `PASS_B4C64_CURRENT_BEST_SAFE_NO_SAVE_PROBE`
- Hard guard rows: `2`
- Hard guard objective rows: `2`
- Hard guard failures: `0`
- Checkpoint-like outputs: `[]`

## Hard guard outcomes

| case_id | role | pass | failure reasons | rank before→after | rank>50 before→after | prob Δ | beats-worst before→after | beats-all before→after | required gate |
|---|---|---:|---|---:|---:|---:|---:|---:|---|
| `legacy_g1_m40` | `hard_protected_beats_guard` | `True` | `` | 3.0→3.0 | 0.0→0.0 | 5.543231964111328e-06 | 0.0→0.0 | 0.0→0.0 | `{"rank_delta_max": 0, "target_prob_delta_min": -0.02, "teacher_beats_all_delta_min": 0, "teacher_beats_worst_delta_min": 0}` |
| `legacy_g1_m8` | `hard_rank_le50_preservation_guard` | `True` | `` | 102.0→102.0 | 1.0→1.0 | 6.679329089820385e-09 | 0.0→0.0 | 0.0→0.0 | `{"rank_delta_max": 0, "rank_gt50_delta_max": 0, "target_prob_delta_min": 0}` |

## Group metrics

| group | top10 Δ | rank>50 Δ | mean rank Δ | target prob Δ | beats-worst Δ | beats-all Δ |
|---|---:|---:|---:|---:|---:|---:|
| `train_main_rank_11_50` | 0.0 | 0.0 | 0.0 | 4.885701595678735e-08 | 0.0 | 0.0 |
| `protected_eval_top10` | 0.0 | 0.0 | 0.0 | 4.847223559964475e-07 | 0.0 | 0.0 |
| `tail_eval_rank_gt50` | 0.0 | 0.0 | 0.0 | 2.5659877185839515e-09 | 0.0 | 0.0 |

## Decision

- Full guard-aware objective v1 rerun passed under guarded split v2 and diagnostics mode fix.
- This is still no-save only.
- Next step: commit this run and enter saved candidate route for public benchmark scoring.

## Outputs

- `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_run2_v2_modefix/group_eval.csv`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_run2_v2_modefix/group_report.md`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_run2_v2_modefix/guardaware_objective_run2_v2_modefix_report.md`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_run2_v2_modefix/guardaware_objective_run2_v2_modefix_summary.json`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_run2_v2_modefix/hard_guard_eval.csv`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_run2_v2_modefix/row_trace.csv`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_run2_v2_modefix/train.log`
