# b4c64/current-best hardguard-only sanity run3 v2 modefix

## Scope

- Branch: `exp/15x15-rank-topk-nosave-b4c64-hardguard-only-sanity-run3-v2-modefix`
- Hardguard-only sanity no-save run using guarded split v2 after diagnostics mode fix.
- Main CE, pair hinge, worst hinge, and global anchor KL were set to zero.
- No checkpoint save, C export, public benchmark, promotion, or current-best overwrite was performed.

## Run status

- Run status: `PASS_HARD_GUARD_ONLY_SANITY_RUN3_V2_MODEFIX_NO_SAVE`
- Verdict: `PASS_B4C64_CURRENT_BEST_SAFE_NO_SAVE_PROBE`
- Hard guard rows: `2`
- Hard guard objective rows: `2`
- Hard guard failures: `0`
- Checkpoint-like outputs: `[]`

## Hard guard outcomes

| case_id | role | pass | failure reasons | rank before→after | rank>50 before→after | prob Δ | beats-worst before→after | beats-all before→after | required gate |
|---|---|---:|---|---:|---:|---:|---:|---:|---|
| `legacy_g1_m40` | `hard_protected_beats_guard` | `True` | `` | 3.0→3.0 | 0.0→0.0 | 6.0498714447021484e-06 | 0.0→0.0 | 0.0→0.0 | `{"rank_delta_max": 0, "target_prob_delta_min": -0.02, "teacher_beats_all_delta_min": 0, "teacher_beats_worst_delta_min": 0}` |
| `legacy_g1_m8` | `hard_rank_le50_preservation_guard` | `True` | `` | 102.0→102.0 | 1.0→1.0 | 7.203198038041592e-09 | 0.0→0.0 | 0.0→0.0 | `{"rank_delta_max": 0, "rank_gt50_delta_max": 0, "target_prob_delta_min": 0}` |

## Group metrics

| group | top10 Δ | rank>50 Δ | mean rank Δ | target prob Δ | beats-worst Δ | beats-all Δ |
|---|---:|---:|---:|---:|---:|---:|
| `train_main_rank_11_50` | 0.0 | 0.0 | 0.0 | 4.739766673762802e-10 | 0.0 | 0.0 |
| `protected_eval_top10` | 0.0 | 0.0 | 0.0 | 6.217354287657573e-07 | 0.0 | 0.0 |
| `tail_eval_rank_gt50` | 0.0 | 0.0 | 0.0 | 2.4010660126805305e-09 | 0.0 | 0.0 |

## Decision

- Guarded split v2 plus diagnostics mode fix passes the hardguard-only sanity route.
- This is still no-save only.
- Next step: rerun guard-aware objective v1 with diagnostics mode fix and guarded split v2.

## Outputs

- `analysis/integration_eval/rank_topk_nosave_b4c64_hardguard_only_sanity_run3_v2_modefix/group_eval.csv`
- `analysis/integration_eval/rank_topk_nosave_b4c64_hardguard_only_sanity_run3_v2_modefix/group_report.md`
- `analysis/integration_eval/rank_topk_nosave_b4c64_hardguard_only_sanity_run3_v2_modefix/hard_guard_eval.csv`
- `analysis/integration_eval/rank_topk_nosave_b4c64_hardguard_only_sanity_run3_v2_modefix/hardguard_only_sanity_run3_v2_modefix_report.md`
- `analysis/integration_eval/rank_topk_nosave_b4c64_hardguard_only_sanity_run3_v2_modefix/hardguard_only_sanity_run3_v2_modefix_summary.json`
- `analysis/integration_eval/rank_topk_nosave_b4c64_hardguard_only_sanity_run3_v2_modefix/row_trace.csv`
- `analysis/integration_eval/rank_topk_nosave_b4c64_hardguard_only_sanity_run3_v2_modefix/train.log`
