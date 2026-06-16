# Mixed-CE heldout regression audit

## Scope

- audited split: `heldout_retention`
- source runs: corrected mixed-CE scale sweep
- no training
- no checkpoint
- no C export
- no benchmark
- no promotion

## Per-scale summary

| variant | scale | rows | rank improved/same/regressed | prob improved/same/regressed | top match gained/lost |
|---|---:|---:|---:|---:|---:|
| w010 | 0.10 | 11 | 3/4/4 | 5/0/6 | 1/0 |
| w005 | 0.05 | 11 | 3/4/4 | 4/0/7 | 1/0 |
| w0025 | 0.025 | 11 | 3/4/4 | 4/0/7 | 1/0 |

## Repeated regression rows

| id | target | rank regression count | prob regression count | rank delta by scale | prob delta by scale | top match by scale |
|---|---|---:|---:|---|---|---|
| `holdout_b_mcts16_g2_m19_target_10_7_over_7_11` | `10,7` | 3 | 3 | `0.10:2;0.05:1;0.025:1` | `0.10:-0.00891487;0.05:-0.00892845;0.025:-0.00893496` | `0.10:0->0;0.05:0->0;0.025:0->0` |
| `holdout_candidate_d_g2_m15_white_last_8_9_target_live_direct_7_10_over_live_final_8_8` | `7,10` | 3 | 3 | `0.10:1;0.05:1;0.025:1` | `0.10:-0.03276481;0.05:-0.03185576;0.025:-0.03150625` | `0.10:0->0;0.05:0->0;0.025:0->0` |
| `holdout_candidate_d_g2_m15_white_last_8_9_target_safe_10_7_over_live_final_8_8` | `10,7` | 3 | 3 | `0.10:2;0.05:2;0.025:2` | `0.10:-0.02275356;0.05:-0.02212669;0.025:-0.02202318` | `0.10:0->0;0.05:0->0;0.025:0->0` |
| `holdout_candidate_e_g2_m13_white_target_5_8_over_8_8` | `5,8` | 3 | 3 | `0.10:3;0.05:3;0.025:2` | `0.10:-0.01193557;0.05:-0.01149342;0.025:-0.01131111` | `0.10:0->0;0.05:0->0;0.025:0->0` |
| `holdout_candidate_e_g2_m17_white_last_9_9_target_block_right_10_9_over_live_final_9_10` | `10,9` | 0 | 3 | `0.10:0;0.05:0;0.025:0` | `0.10:-0.00413944;0.05:-0.00412775;0.025:-0.00411538` | `0.10:0->0;0.05:0->0;0.025:0->0` |
| `holdout_candidate_e_g2_m17_white_last_9_9_target_future_block_8_10_over_live_final_9_10` | `8,10` | 0 | 3 | `0.10:-7;0.05:-8;0.025:-8` | `0.10:-0.00000192;0.05:-0.00000191;0.025:-0.00000190` | `0.10:0->0;0.05:0->0;0.025:0->0` |

## Top-match gains

| id | target | gained count | top match by scale |
|---|---|---:|---|
| `holdout_candidate_d_g2_m15_white_last_8_9_target_safe_7_9_over_live_final_8_8` | `7,9` | 3 | `0.10:0->1;0.05:0->1;0.025:0->1` |

## Interpretation

Rows that regress under all scales are the most important blockers for any future mixed-CE selection strategy.
The next step should inspect these repeated regression rows before adding more training signal.
