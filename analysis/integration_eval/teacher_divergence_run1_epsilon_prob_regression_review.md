# Teacher-divergence run1 epsilon-aware probability regression review

## Branch

`exp/15x15-teacher-divergence-run1-epsilon-prob-regression-review`

## Scope

- Reviews raw probability regressions from run1 protected/tail guard.
- Classifies probability loss by epsilon bands.
- Does not train.
- Does not read or write checkpoints.
- Does not overwrite `checkpoints/15x15_current_best.pt`.
- Does not C export.
- Does not run public benchmark.
- Does not promote.

## Epsilon bands

| band | condition | interpretation |
|---|---:|---|
| numerical_noise | loss <= 1e-06 | likely numerical noise |
| tiny_acceptable_drift | loss <= 1e-05 | tiny drift, acceptable for local review |
| warning | loss <= 0.0001 | warning; requires local fixed-probe/heldout before any export |
| hard_concern | loss > 0.0001 | repair gate/objective before continuing |

## Decision

`EPSILON_REVIEW_FAILS__REPAIR_GATE_OR_OBJECTIVE`

## Summary

| metric | value | status | notes |
|---|---:|---|---|
| epsilon_decision | EPSILON_REVIEW_FAILS__REPAIR_GATE_OR_OBJECTIVE | INFO | Local epsilon review decision; not promotion. |
| evaluated_rows | 89 | PASS |  |
| protected_top10_rows | 23 | PASS |  |
| tail_rank_gt50_rows | 66 | PASS |  |
| total_prob_regressions | 19 | WARN |  |
| protected_top10_prob_regressions | 11 | WARN |  |
| tail_rank_gt50_prob_regressions | 8 | WARN |  |
| total_rank_regressions | 0 | PASS |  |
| no_regression_rows | 70 | INFO |  |
| numerical_noise_rows | 9 | INFO |  |
| tiny_acceptable_drift_rows | 1 | INFO |  |
| warning_rows | 5 | WARN |  |
| hard_concern_rows | 4 | FAIL |  |
| protected_top10_warning_rows | 5 | WARN |  |
| tail_rank_gt50_warning_rows | 0 | PASS |  |
| protected_top10_hard_concern_rows | 4 | FAIL |  |
| tail_rank_gt50_hard_concern_rows | 0 | PASS |  |
| max_probability_loss | 0.000997871200 | FAIL |  |
| mean_probability_loss_among_regressions | 0.000122302142 | INFO |  |
| noise_eps | 1e-06 | INFO |  |
| tiny_eps | 1e-05 | INFO |  |
| warn_eps | 0.0001 | INFO |  |
| promotion_readiness_decision | NOT_PROMOTION_READY__READY_FOR_EPSILON_GATED_LOCAL_REVIEW | INFO |  |

## Severity counts

| severity | rows |
|---|---:|
| no_regression | 70 |
| numerical_noise | 9 |
| tiny_acceptable_drift | 1 |
| warning | 5 |
| hard_concern | 4 |

## Bucket × severity counts

| bucket | severity | rows |
|---|---|---:|
| protected_top10 | no_regression | 12 |
| protected_top10 | numerical_noise | 1 |
| protected_top10 | tiny_acceptable_drift | 1 |
| protected_top10 | warning | 5 |
| protected_top10 | hard_concern | 4 |
| tail_rank_gt50 | no_regression | 58 |
| tail_rank_gt50 | numerical_noise | 8 |
| tail_rank_gt50 | tiny_acceptable_drift | 0 |
| tail_rank_gt50 | warning | 0 |
| tail_rank_gt50 | hard_concern | 0 |

## Worst raw probability regressions

| bucket | manifest_id | case_id | prob_before | prob_after | prob_delta | loss | severity | rank_delta |
|---|---|---|---:|---:|---:|---:|---|---:|
| protected_top10 | td_exp_00056 | holdout_candidate_e_g2_m17_white_last_9_9_target_block_right_10_9_over_live_final_9_10 | 0.3702892363 | 0.3692913651 | -0.000997871200 | 0.000997871200 | hard_concern | 0 |
| protected_top10 | td_exp_00004 | legacy_g1_m40 | 0.1502913237 | 0.1496061236 | -0.000685200100 | 0.000685200100 | hard_concern | 0 |
| protected_top10 | td_exp_00059 | holdout_candidate_d_g2_m15_white_last_8_9_target_live_direct_7_10_over_live_final_8_8 | 0.1522409171 | 0.1519690007 | -0.000271916400 | 0.000271916400 | hard_concern | 0 |
| protected_top10 | td_exp_00025 | legacy_g6_m19 | 0.0262563098 | 0.0261367112 | -0.000119598600 | 0.000119598600 | hard_concern | 0 |
| protected_top10 | td_exp_00060 | holdout_candidate_d_g2_m15_white_last_8_9_target_safe_10_7_over_live_final_8_8 | 0.0551292226 | 0.0550493412 | -0.000079881400 | 0.000079881400 | warning | 0 |
| protected_top10 | td_exp_00006 | legacy_g2_m7 | 0.0157086700 | 0.0156530160 | -0.000055654000 | 0.000055654000 | warning | 0 |
| protected_top10 | td_exp_00007 | legacy_g2_m9 | 0.0652434900 | 0.0651895627 | -0.000053927300 | 0.000053927300 | warning | 0 |
| protected_top10 | td_exp_00002 | legacy_g1_m6 | 0.0208760891 | 0.0208346099 | -0.000041479200 | 0.000041479200 | warning | 0 |
| protected_top10 | td_exp_00020 | legacy_g5_m16 | 0.1067679003 | 0.1067553982 | -0.000012502100 | 0.000012502100 | warning | 0 |
| protected_top10 | td_exp_00001 | legacy_g1_m4 | 0.0135820787 | 0.0135779474 | -0.000004131300 | 0.000004131300 | tiny_acceptable_drift | 0 |
| tail_rank_gt50 | td_exp_00064 | tdiv_candidate_g_g2_p17_white | 0.0014207098 | 0.0014200488 | -0.000000661000 | 0.000000661000 | numerical_noise | 0 |
| protected_top10 | td_exp_00023 | legacy_g6_m5 | 0.0036299117 | 0.0036295862 | -0.000000325500 | 0.000000325500 | numerical_noise | 0 |
| tail_rank_gt50 | td_exp_00070 | tdiv_legacy_g1_m40 | 0.0000873986 | 0.0000872973 | -0.000000101300 | 0.000000101300 | numerical_noise | 0 |
| tail_rank_gt50 | td_exp_00110 | tdiv_legacy_g1_m40 | 0.0000873986 | 0.0000872973 | -0.000000101300 | 0.000000101300 | numerical_noise | 0 |
| tail_rank_gt50 | td_exp_00137 | tdiv_legacy_g1_m40 | 0.0000873986 | 0.0000872973 | -0.000000101300 | 0.000000101300 | numerical_noise | 0 |
| tail_rank_gt50 | td_exp_00249 |  | 0.0000873986 | 0.0000872973 | -0.000000101300 | 0.000000101300 | numerical_noise | 0 |
| tail_rank_gt50 | td_exp_00335 |  | 0.0000873986 | 0.0000872973 | -0.000000101300 | 0.000000101300 | numerical_noise | 0 |
| tail_rank_gt50 | td_exp_00057 | holdout_candidate_e_g2_m17_white_last_9_9_target_future_block_8_10_over_live_final_9_10 | 0.0000745192 | 0.0000744341 | -0.000000085100 | 0.000000085100 | numerical_noise | 0 |
| tail_rank_gt50 | td_exp_00062 | tdiv_candidate_g_g1_p22_black | 0.0000046183 | 0.0000046173 | -0.000000001000 | 0.000000001000 | numerical_noise | 0 |

## Interpretation

At least one hard concern or rank regression exists. Do not continue toward export or benchmark.

Repair the gate/objective first, then rerun controlled training or guard audit.

## Outputs

- detail CSV: `analysis/integration_eval/teacher_divergence_run1_epsilon_prob_regression_review.csv`
- summary CSV: `analysis/integration_eval/teacher_divergence_run1_epsilon_prob_regression_summary.csv`
- report: `analysis/integration_eval/teacher_divergence_run1_epsilon_prob_regression_review.md`

## Final guardrails

- No current_best overwrite.
- No C export.
- No public benchmark.
- No promotion.
- Do not add local checkpoint artifacts to git.
