# Retention Family Threshold Smoke Review

## Scope

This review audits the committed threshold train-and-gate smoke artifacts.

It does not run training, does not create a checkpoint, does not export C weights, does not run a public benchmark, and does not promote a model.

Reviewed source directory:

- `analysis/integration_eval/retention_family_threshold_train_gate_smoke`

## Branch lineage

| branch | commit | role |
| --- | --- | --- |
| `exp/15x15-retention-family-threshold-policy-doc-sync` | `a260647` | Documented threshold gate policy. |
| `exp/15x15-retention-family-threshold-train-gate-smoke` | `80c6039` | Ran train-and-gate smoke with threshold gate. |
| `exp/15x15-retention-family-threshold-smoke-review` | current | Reviews smoke artifacts only. |

## Wrapper conclusion

| field | value |
| --- | --- |
| mode | `train-and-gate` |
| overall_status | `gates_passed` |
| gates_passed | `True` |
| setup_errors | `[]` |
| manifest_validation_errors | `[]` |
| checkpoint_action | `gates_passed_no_promotion_requested` |
| candidate_exists | `True` |
| promote_on_pass | `False` |
| final_checkpoint | `` |

## Wrapper command results

| label | returncode | passed | stdout_log | stderr_log |
| --- | --- | --- | --- | --- |
| train | 0 | True | eval_logs/integration_eval/retention_family_threshold_train_gate_smoke/train.stdout.log | eval_logs/integration_eval/retention_family_threshold_train_gate_smoke/train.stderr.log |
| gate_1 | 0 | True | eval_logs/integration_eval/retention_family_threshold_train_gate_smoke/gate_1.stdout.log | eval_logs/integration_eval/retention_family_threshold_train_gate_smoke/gate_1.stderr.log |

## Gate conclusion

| field | value |
| --- | --- |
| decision | `PASS` |
| failures | `[]` |
| eval_prob_epsilon | `0.0005` |
| eval_rank_regressed | `0` |
| eval_prob_regressed | `3` |
| eval_prob_hard_regressed | `0` |
| eval_prob_warnings | `3` |
| train_improved | `1` |

## Training script evaluation rows

| phase | id | split | role | label_type | source_id | side_to_move | policy_target | target_rank | target_prob | target_ce | top_move | top_prob | top_matches_target | value | used_for_training | suggested_weight |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| before | holdout_candidate_d_g2_m15_white_last_8_9_target_live_direct_7_10_over_live_final_8_8 | train_candidate | nonheldout_retention_anchor | nonheldout_retention_anchor | candidate_d_g2_m15_white_last_8_9_target_live_direct_7_10_over_live_final_8_8 | white | 7,10 | 5 | 0.08013161 | 2.52408484 | 4,7 | 0.17489789 | False | -0.67221612 | True | 1.0000 |
| before | holdout_candidate_d_g2_m15_white_last_8_9_target_safe_10_7_over_live_final_8_8 | train_candidate | nonheldout_retention_anchor | nonheldout_retention_anchor | candidate_d_g2_m15_white_last_8_9_target_safe_10_7_over_live_final_8_8 | white | 10,7 | 2 | 0.10073009 | 2.29531070 | 4,7 | 0.17489789 | False | -0.67221612 | True | 1.0000 |
| after | holdout_candidate_d_g2_m15_white_last_8_9_target_live_direct_7_10_over_live_final_8_8 | train_candidate | nonheldout_retention_anchor | nonheldout_retention_anchor | candidate_d_g2_m15_white_last_8_9_target_live_direct_7_10_over_live_final_8_8 | white | 7,10 | 5 | 0.07994794 | 2.52637959 | 4,7 | 0.18134868 | False | -0.67221612 | True | 1.0000 |
| after | holdout_candidate_d_g2_m15_white_last_8_9_target_safe_10_7_over_live_final_8_8 | train_candidate | nonheldout_retention_anchor | nonheldout_retention_anchor | candidate_d_g2_m15_white_last_8_9_target_safe_10_7_over_live_final_8_8 | white | 10,7 | 2 | 0.10455427 | 2.25804898 | 4,7 | 0.18134868 | False | -0.67221612 | True | 1.0000 |

## Probability warning rows

These rows are probability-only eval drops within `--eval-prob-epsilon 0.0005`, so they are warnings rather than hard failures.

| family_id | side | target | before_rank | after_rank | before_prob | after_prob | prob_delta | class |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bd:690e24eaa9cbf978 | eval | 5,11 | 39.0 | 38.0 | 0.00194259 | 0.00182245 | -0.00012013999999999992 | warning_prob_only_within_epsilon |
| bd:fcfbf3a577067568 | eval | 8,10 | 168.0 | 167.0 | 2.02e-06 | 1.64e-06 | -3.8000000000000017e-07 | warning_prob_only_within_epsilon |
| bd:fa22a82f75e4b3c2 | eval | 5,8 | 3.0 | 3.0 | 0.0453654 | 0.04490543 | -0.00045996999999999705 | warning_prob_only_within_epsilon |

## Critical protected family rows

| family_id | side | target | before_rank | after_rank | before_prob | after_prob | prob_delta | class |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bd:ea22cc14729b88fd | train | 7,10 | 5.0 | 5.0 | 0.08013152 | 0.07994807 | -0.00018345000000000167 | non_eval_prob_regression_not_gate_failure |
| bd:ea22cc14729b88fd | train | 10,7 | 2.0 | 2.0 | 0.10073036 | 0.10455413 | 0.0038237699999999902 | not_regressed |
| bd:ea22cc14729b88fd | eval | 7,9 | 4.0 | 4.0 | 0.09005976 | 0.09247528 | 0.0024155200000000043 | not_regressed |

## Interpretation

The smoke demonstrates that the threshold policy works end-to-end through the wrapper path:

- the training command completed,
- the gate command completed,
- the wrapper returned `gates_passed`,
- the gate evaluator returned `PASS`,
- eval probability-only drops were converted to `warning_prob_only_within_epsilon` rows under `--eval-prob-epsilon 0.0005`,
- no hard eval probability regression remained,
- the protected `7,9` eval row did not regress,
- the candidate checkpoint was not promoted.

This should be treated as pipeline validation only. It is not evidence that the candidate checkpoint is stronger in public play, and it is not a promotion decision.

## Recommended next step

Do not promote this smoke checkpoint.

The next meaningful step should be either:

1. run the same gated path on a larger retention/divergence set, still with no promotion, or
2. move back to broader 15x15 strength improvement work where public benchmark score, not this micro-gate alone, determines progress.
