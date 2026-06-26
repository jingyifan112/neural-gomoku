# b4c64/current-best guarded split baseline run1

## Scope

- Branch: `exp/15x15-rank-topk-nosave-b4c64-guarded-split-baseline-run1`
- Guarded split baseline no-save run.
- No checkpoint save, C export, public benchmark, promotion, or current-best overwrite was performed.

## Run status

- Run status: `PASS_GUARDED_EVALUATOR_CAUGHT_HARD_GUARD_DAMAGE`
- Verdict: `FAIL_HARD_GUARD_ROW_DAMAGE`
- Hard guard rows: `2`
- Hard guard failures: `2`
- Checkpoint-like outputs: `[]`

## Hard guard failures

| case_id | role | pass | failure reasons | rank before→after | rank>50 before→after | prob Δ | beats-worst before→after | beats-all before→after |
|---|---|---:|---|---:|---:|---:|---:|---:|
| `legacy_g1_m40` | `hard_protected_beats_guard` | `False` | `rank_delta=2.0 > 0.0;target_prob_delta=-0.27682457119226456 < -0.02;teacher_beats_all_delta=-1.0 < 0.0;teacher_beats_worst_delta=-1.0 < 0.0` | 1.0→3.0 | 0.0→0.0 | -0.27682457119226456 | 1.0→0.0 | 1.0→0.0 |
| `legacy_g1_m8` | `hard_rank_le50_preservation_guard` | `False` | `rank_after=107.0 > 50.0;rank_delta=88.0 > 0.0;rank_gt50_delta=1.0 > 0.0;target_prob_delta=-0.0005092114006401971 < 0.0` | 19.0→107.0 | 0.0→1.0 | -0.0005092114006401971 | 0.0→0.0 | 0.0→0.0 |

## Group metrics

| group | top10 Δ | rank>50 Δ | mean rank Δ | target prob Δ | beats-worst Δ | beats-all Δ |
|---|---:|---:|---:|---:|---:|---:|
| `train_main_rank_11_50` | 0.0 | 0.0 | -2.1428571428571423 | 0.00047871205424598906 | 0.0 | 0.0 |
| `protected_eval_top10` | 1.0 | 0.0 | -0.40000000000000036 | -0.012815646351858355 | -1.0 | -1.0 |
| `tail_eval_rank_gt50` | 0.0 | 1.0 | 36.33333333333333 | -0.00010760363026444489 | 0.0 | 0.0 |

## Decision

- Do not save a candidate from this run.
- Do not run C export, public benchmark, promotion, or current-best overwrite.
- The guarded evaluator works if this run status is `PASS_GUARDED_EVALUATOR_CAUGHT_HARD_GUARD_DAMAGE`.
- Next route should change objective/data so hard guards survive before any saved candidate is considered.

## Outputs

- `analysis/integration_eval/rank_topk_nosave_b4c64_guarded_split_baseline_run1/group_eval.csv`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guarded_split_baseline_run1/group_report.md`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guarded_split_baseline_run1/guarded_run_report.md`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guarded_split_baseline_run1/guarded_run_summary.json`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guarded_split_baseline_run1/hard_guard_eval.csv`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guarded_split_baseline_run1/row_trace.csv`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guarded_split_baseline_run1/train.log`
