# b4c64/current-best guard-aware objective run1

## Scope

- Branch: `exp/15x15-rank-topk-nosave-b4c64-guardaware-objective-run1`
- Guard-aware objective v1 no-save run.
- No checkpoint save, C export, public benchmark, promotion, or current-best overwrite was performed.

## Run status

- Run status: `FAIL_HARD_GUARD_DAMAGE_REMAINS`
- Verdict: `FAIL_HARD_GUARD_ROW_DAMAGE`
- Hard guard rows: `2`
- Hard guard objective rows: `2`
- Hard guard failures: `2`
- Checkpoint-like outputs: `[]`

## Hard guard outcomes

| case_id | role | pass | failure reasons | rank before→after | rank>50 before→after | prob Δ | beats-worst before→after | beats-all before→after |
|---|---|---:|---|---:|---:|---:|---:|---:|
| `legacy_g1_m40` | `hard_protected_beats_guard` | `False` | `rank_delta=2.0 > 0.0;target_prob_delta=-0.2768222987651825 < -0.02;teacher_beats_all_delta=-1.0 < 0.0;teacher_beats_worst_delta=-1.0 < 0.0` | 1.0→3.0 | 0.0→0.0 | -0.2768222987651825 | 1.0→0.0 | 1.0→0.0 |
| `legacy_g1_m8` | `hard_rank_le50_preservation_guard` | `False` | `rank_after=107.0 > 50.0;rank_delta=88.0 > 0.0;rank_gt50_delta=1.0 > 0.0;target_prob_delta=-0.0005092088904348202 < 0.0` | 19.0→107.0 | 0.0→1.0 | -0.0005092088904348202 | 0.0→0.0 | 0.0→0.0 |

## Group metrics

| group | top10 Δ | rank>50 Δ | mean rank Δ | target prob Δ | beats-worst Δ | beats-all Δ |
|---|---:|---:|---:|---:|---:|---:|
| `train_main_rank_11_50` | 0.0 | 0.0 | -2.1428571428571423 | 0.0004786293814374534 | 0.0 | 0.0 |
| `protected_eval_top10` | 1.0 | 0.0 | -0.40000000000000036 | -0.012815377958274136 | -1.0 | -1.0 |
| `tail_eval_rank_gt50` | 0.0 | 1.0 | 36.33333333333333 | -0.00010760186705738306 | 0.0 | 0.0 |

## Decision

- Do not save a candidate from this run.
- Do not run C export, public benchmark, promotion, or current-best overwrite.
- Next route should adjust guard-aware weights/data and rerun no-save only.

## Outputs

- `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_run1/group_eval.csv`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_run1/group_report.md`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_run1/guardaware_run_report.md`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_run1/guardaware_run_summary.json`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_run1/hard_guard_eval.csv`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_run1/row_trace.csv`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_run1/train.log`
