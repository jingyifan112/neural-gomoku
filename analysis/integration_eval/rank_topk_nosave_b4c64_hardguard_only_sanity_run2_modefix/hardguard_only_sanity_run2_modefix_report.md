# b4c64/current-best hardguard-only sanity run2 modefix

## Scope

- Branch: `exp/15x15-rank-topk-nosave-b4c64-hardguard-only-sanity-run2-modefix`
- Hardguard-only sanity no-save run after diagnostics mode fix.
- Main CE, pair hinge, worst hinge, and global anchor KL were set to zero.
- No checkpoint save, C export, public benchmark, promotion, or current-best overwrite was performed.

## Run status

- Run status: `FAIL_HARD_GUARD_ONLY_SANITY_MODEFIX`
- Verdict: `FAIL_HARD_GUARD_ROW_DAMAGE`
- Hard guard rows: `2`
- Hard guard objective rows: `2`
- Hard guard failures: `1`
- Checkpoint-like outputs: `[]`

## Hard guard outcomes

| case_id | role | pass | failure reasons | rank before→after | rank>50 before→after | prob Δ | beats-worst before→after | beats-all before→after |
|---|---|---:|---|---:|---:|---:|---:|---:|
| `legacy_g1_m40` | `hard_protected_beats_guard` | `True` | `` | 3.0→3.0 | 0.0→0.0 | 6.0498714447021484e-06 | 0.0→0.0 | 0.0→0.0 |
| `legacy_g1_m8` | `hard_rank_le50_preservation_guard` | `False` | `rank_after=102.0 > 50.0` | 102.0→102.0 | 1.0→1.0 | 7.203198038041592e-09 | 0.0→0.0 | 0.0→0.0 |

## Group metrics

| group | top10 Δ | rank>50 Δ | mean rank Δ | target prob Δ | beats-worst Δ | beats-all Δ |
|---|---:|---:|---:|---:|---:|---:|
| `train_main_rank_11_50` | 0.0 | 0.0 | 0.0 | 4.739766673762802e-10 | 0.0 | 0.0 |
| `protected_eval_top10` | 0.0 | 0.0 | 0.0 | 6.217354287657573e-07 | 0.0 | 0.0 |
| `tail_eval_rank_gt50` | 0.0 | 0.0 | 0.0 | 2.4010660126805305e-09 | 0.0 | 0.0 |

## Decision

- Hard guards still fail even after diagnostics mode fix.
- Do not save a candidate from this run.
- Next step: inspect wrapper train/eval sequencing or optimizer step implementation directly.

## Outputs

- `analysis/integration_eval/rank_topk_nosave_b4c64_hardguard_only_sanity_run2_modefix/group_eval.csv`
- `analysis/integration_eval/rank_topk_nosave_b4c64_hardguard_only_sanity_run2_modefix/group_report.md`
- `analysis/integration_eval/rank_topk_nosave_b4c64_hardguard_only_sanity_run2_modefix/hard_guard_eval.csv`
- `analysis/integration_eval/rank_topk_nosave_b4c64_hardguard_only_sanity_run2_modefix/hardguard_only_sanity_run2_modefix_report.md`
- `analysis/integration_eval/rank_topk_nosave_b4c64_hardguard_only_sanity_run2_modefix/hardguard_only_sanity_run2_modefix_summary.json`
- `analysis/integration_eval/rank_topk_nosave_b4c64_hardguard_only_sanity_run2_modefix/row_trace.csv`
- `analysis/integration_eval/rank_topk_nosave_b4c64_hardguard_only_sanity_run2_modefix/train.log`
