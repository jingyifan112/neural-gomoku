# b4c64 guard-aware v2 modefix saved candidate run1

## Scope

- PASS-gated saved candidate route.
- Not promotion.
- No current-best overwrite.
- No C export or public benchmark in this step.

## Status

- Run status: `PASS_SAVED_CANDIDATE_READY_FOR_PUBLIC_BENCHMARK`
- Verdict: `PASS_B4C64_CURRENT_BEST_SAFE_NO_SAVE_PROBE`
- Candidate checkpoint: `checkpoints/probes/15x15_b4c64_guardaware_v2_modefix_candidate_run1.pt`
- Candidate exists: `True`
- Current-best unchanged: `True`
- Hard guard failures: `0`

## Group metrics

| group | top10 Δ | rank>50 Δ | mean rank Δ | target prob Δ | beats-worst Δ | beats-all Δ |
|---|---:|---:|---:|---:|---:|---:|
| `train_main_rank_11_50` | 0.0 | 0.0 | 0.0 | 4.885701595678735e-08 | 0.0 | 0.0 |
| `protected_eval_top10` | 0.0 | 0.0 | 0.0 | 4.847223559964475e-07 | 0.0 | 0.0 |
| `tail_eval_rank_gt50` | 0.0 | 0.0 | 0.0 | 2.5659877185839515e-09 | 0.0 | 0.0 |

## Hard guard outcomes

| case_id | pass | failure reasons | rank before→after | prob Δ | required gate |
|---|---:|---|---:|---:|---|
| `legacy_g1_m40` | `True` | `` | 3.0→3.0 | 5.543231964111328e-06 | `{"rank_delta_max": 0, "target_prob_delta_min": -0.02, "teacher_beats_all_delta_min": 0, "teacher_beats_worst_delta_min": 0}` |
| `legacy_g1_m8` | `True` | `` | 102.0→102.0 | 6.679329089820385e-09 | `{"rank_delta_max": 0, "rank_gt50_delta_max": 0, "target_prob_delta_min": 0}` |

## Decision

- Candidate is ready for public benchmark scoring.

## Outputs

- `analysis/integration_eval/rank_topk_b4c64_guardaware_v2_modefix_saved_candidate_run1/candidate_metadata.json`
- `analysis/integration_eval/rank_topk_b4c64_guardaware_v2_modefix_saved_candidate_run1/candidate_sha256.txt`
- `analysis/integration_eval/rank_topk_b4c64_guardaware_v2_modefix_saved_candidate_run1/current_best_sha256_after.txt`
- `analysis/integration_eval/rank_topk_b4c64_guardaware_v2_modefix_saved_candidate_run1/current_best_sha256_before.txt`
- `analysis/integration_eval/rank_topk_b4c64_guardaware_v2_modefix_saved_candidate_run1/group_eval.csv`
- `analysis/integration_eval/rank_topk_b4c64_guardaware_v2_modefix_saved_candidate_run1/group_report.md`
- `analysis/integration_eval/rank_topk_b4c64_guardaware_v2_modefix_saved_candidate_run1/hard_guard_eval.csv`
- `analysis/integration_eval/rank_topk_b4c64_guardaware_v2_modefix_saved_candidate_run1/row_trace.csv`
- `analysis/integration_eval/rank_topk_b4c64_guardaware_v2_modefix_saved_candidate_run1/saved_candidate_run1_summary.json`
- `analysis/integration_eval/rank_topk_b4c64_guardaware_v2_modefix_saved_candidate_run1/train.log`
- `checkpoints/probes/15x15_b4c64_guardaware_v2_modefix_candidate_run1.pt`
