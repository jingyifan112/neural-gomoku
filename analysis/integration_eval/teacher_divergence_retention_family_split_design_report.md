# Retention family split design

## Scope

- read-only split-design audit over heldout retention families
- no training
- no checkpoint
- no C export
- no benchmark
- no promotion

## Outputs

- row detail: `analysis/integration_eval/teacher_divergence_retention_family_split_design_rows.csv`
- family summary: `analysis/integration_eval/teacher_divergence_retention_family_split_design_families.csv`

## Summary

- heldout rows reviewed: 11
- heldout families: 7
- families with repeated blockers: 4
- families with sibling target conflict: 2
- families with mixed signal conflict: 1

## High-priority families

| family | rows | targets | blockers | prob-mass-loss | stable top1 gains | recommendation |
|---|---:|---|---:|---:|---:|---|
| `bd:ea22cc14729b88fd` | 3 | `10,7;7,10;7,9` | 2 | 0 | 1 | `split_sibling_targets_and_add_nonheldout_retention_anchor` |
| `bd:831f9c7e8843d367` | 3 | `10,9;7,9;8,10` | 2 | 2 | 0 | `split_sibling_targets_by_board_family` |
| `bd:3edb62648d54c314` | 1 | `5,8` | 1 | 0 | 0 | `add_family_specific_retention_anchor_or_exclude_from_mixed_ce` |
| `bd:598170c19d674fee` | 1 | `10,7` | 1 | 0 | 0 | `add_family_specific_retention_anchor_or_exclude_from_mixed_ce` |

## High-priority row details

### `bd:ea22cc14729b88fd`

- targets: `10,7;7,10;7,9`
- source_paths: `analysis/integration_eval/candidate_d_g2_m15_diagnostic_anchors.json`
- game_moves: `g2_m15`
- recommendation: `split_sibling_targets_and_add_nonheldout_retention_anchor`

| id | target | blocker | prob-mass-loss | stable top1 gain | rank delta | prob delta | top match |
|---|---|---:|---:|---:|---|---|---|
| `holdout_candidate_d_g2_m15_white_last_8_9_target_live_direct_7_10_over_live_final_8_8` | `7,10` | True | False | False | `0.10:1;0.05:1;0.025:1` | `0.10:-0.03276481;0.05:-0.03185576;0.025:-0.03150625` | `0.10:0->0;0.05:0->0;0.025:0->0` |
| `holdout_candidate_d_g2_m15_white_last_8_9_target_safe_10_7_over_live_final_8_8` | `10,7` | True | False | False | `0.10:2;0.05:2;0.025:2` | `0.10:-0.02275356;0.05:-0.02212669;0.025:-0.02202318` | `0.10:0->0;0.05:0->0;0.025:0->0` |
| `holdout_candidate_d_g2_m15_white_last_8_9_target_safe_7_9_over_live_final_8_8` | `7,9` | False | False | True | `0.10:-3;0.05:-3;0.025:-3` | `0.10:0.20446586;0.05:0.20080071;0.025:0.19859716` | `0.10:0->1;0.05:0->1;0.025:0->1` |

### `bd:831f9c7e8843d367`

- targets: `10,9;7,9;8,10`
- source_paths: `analysis/integration_eval/candidate_e_g2_m17_diagnostic_anchors.json`
- game_moves: `g2_m17`
- recommendation: `split_sibling_targets_by_board_family`

| id | target | blocker | prob-mass-loss | stable top1 gain | rank delta | prob delta | top match |
|---|---|---:|---:|---:|---|---|---|
| `holdout_candidate_e_g2_m17_white_last_9_9_target_block_right_10_9_over_live_final_9_10` | `10,9` | True | True | False | `0.10:0;0.05:0;0.025:0` | `0.10:-0.00413944;0.05:-0.00412775;0.025:-0.00411538` | `0.10:0->0;0.05:0->0;0.025:0->0` |
| `holdout_candidate_e_g2_m17_white_last_9_9_target_future_block_8_10_over_live_final_9_10` | `8,10` | True | True | False | `0.10:-7;0.05:-8;0.025:-8` | `0.10:-0.00000192;0.05:-0.00000191;0.025:-0.00000190` | `0.10:0->0;0.05:0->0;0.025:0->0` |
| `holdout_candidate_e_g2_m17_white_last_9_9_target_block_left_7_9_over_live_final_9_10` | `7,9` | False | False | False | `0.10:0;0.05:0;0.025:0` | `0.10:0.02783764;0.05:0.02321560;0.025:0.01949698` | `0.10:1->1;0.05:1->1;0.025:1->1` |

### `bd:3edb62648d54c314`

- targets: `5,8`
- source_paths: `analysis/integration_eval/candidate_e_g2_m13_diagnostic_anchors.json`
- game_moves: `g2_m13`
- recommendation: `add_family_specific_retention_anchor_or_exclude_from_mixed_ce`

| id | target | blocker | prob-mass-loss | stable top1 gain | rank delta | prob delta | top match |
|---|---|---:|---:|---:|---|---|---|
| `holdout_candidate_e_g2_m13_white_target_5_8_over_8_8` | `5,8` | True | False | False | `0.10:3;0.05:3;0.025:2` | `0.10:-0.01193557;0.05:-0.01149342;0.025:-0.01131111` | `0.10:0->0;0.05:0->0;0.025:0->0` |

### `bd:598170c19d674fee`

- targets: `10,7`
- source_paths: `analysis/integration_eval/current_best_margin_candidate_c_conservative_anchors.json`
- game_moves: `g2_m19`
- recommendation: `add_family_specific_retention_anchor_or_exclude_from_mixed_ce`

| id | target | blocker | prob-mass-loss | stable top1 gain | rank delta | prob delta | top match |
|---|---|---:|---:|---:|---|---|---|
| `holdout_b_mcts16_g2_m19_target_10_7_over_7_11` | `10,7` | True | False | False | `0.10:2;0.05:1;0.025:1` | `0.10:-0.00891487;0.05:-0.00892845;0.025:-0.00893496` | `0.10:0->0;0.05:0->0;0.025:0->0` |

## Proposed split rules

1. Do not use a sibling target from the same board digest as the only heldout check while training another sibling target in mixed CE.
2. For board families with repeated blockers, create a small non-heldout retention-anchor subset and keep a separate family-level heldout subset.
3. Preserve probability regression gates; rank-only gates miss low-probability future-block mass loss.
4. Condition mixed-CE row selection by board family/source family, not by label_type alone.
5. Any future training variant must use the regression-gated runner and must not save unless gates pass.

## Decision

This branch should remain a design/audit branch. It should not promote any model artifact.
