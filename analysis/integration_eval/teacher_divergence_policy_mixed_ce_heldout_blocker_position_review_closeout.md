# Mixed-CE heldout blocker position review closeout

## Scope

This closeout records a read-only position review of the six repeated heldout blockers found in the mixed-CE heldout regression audit.

This branch did not run training and did not create a checkpoint.

Boundaries:

- no checkpoint
- no C export
- no benchmark
- no promotion
- no current-best overwrite
- no model-capacity conclusion

## Inputs

Reviewed blockers came from:

- `analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_regression_audit_summary.csv`
- `analysis/integration_eval/teacher_divergence_retention_safety_v3_dataset.json`
- `analysis/integration_eval/teacher_divergence_retention_manifest.csv`
- `analysis/integration_eval/teacher_divergence_retention_probe.csv`
- corrected mixed-CE scale sweep eval CSVs

Generated artifacts:

- `scripts/review_mixed_ce_heldout_blocker_positions.py`
- `analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_blocker_position_review.csv`
- `analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_blocker_position_review.md`

## Main finding

The repeated heldout blockers are not random and not a simple label-type issue.

All six blockers are `policy_target` rows, but they cluster into three tactical-retention source families:

1. candidate C / B mcts16 game2 move19 retention target
2. candidate D game2 move15 fork-prevention retention targets
3. candidate E game2 move13/move17 retention targets

Therefore, filtering mixed CE by label_type alone is not sufficient.

## Source-family findings

### candidate C / B mcts16 game2 move19

Blocker:

- `holdout_b_mcts16_g2_m19_target_10_7_over_7_11`

Target:

- `10,7`

Observation:

- The target remains non-top under all scales.
- The top move remains `9,10`.
- Target probability drops under every corrected scale.

Interpretation:

This is a retention position where mixed CE pushes more mass toward a competing tactical move family instead of preserving the heldout target.

### candidate D game2 move15

Blockers:

- `holdout_candidate_d_g2_m15_white_last_8_9_target_live_direct_7_10_over_live_final_8_8`
- `holdout_candidate_d_g2_m15_white_last_8_9_target_safe_10_7_over_live_final_8_8`

Targets:

- `7,10`
- `10,7`

Observation:

- Both blockers share the same board digest.
- Both shift their top move from `4,7` to `7,9`.
- The previous heldout regression audit found that a sibling target `7,9` gains top-1 under all mixed-CE scales.

Interpretation:

This is likely a local sibling-target conflict, not a global retention failure. Mixed CE improves one target in the family while damaging nearby retention alternatives.

### candidate E game2 move13/move17

Blockers:

- `holdout_candidate_e_g2_m13_white_target_5_8_over_8_8`
- `holdout_candidate_e_g2_m17_white_last_9_9_target_block_right_10_9_over_live_final_9_10`
- `holdout_candidate_e_g2_m17_white_last_9_9_target_future_block_8_10_over_live_final_9_10`

Targets:

- `5,8`
- `10,9`
- `8,10`

Observation:

- g2m13 target `5,8` remains below competing top move `8,8`.
- g2m17 targets `10,9` and `8,10` remain below competing top move `7,9`.
- The `8,10` row improves rank but still loses probability under all scales.

Interpretation:

Rank-only metrics would miss part of the regression. The heldout probability gate is catching real target-mass loss, especially for very low-probability future-block targets.

## Decision

Close this branch as a read-only blocker position review.

No model artifact should be promoted from this branch.

## Recommended next step

Do not continue global mixed-CE scale tuning.

The next training branch should change the data selection or split design. The most useful next options are:

1. create a small non-heldout retention-anchor training split for the repeated blocker families, then keep a separate heldout set for final gating;
2. separate sibling targets from the same board digest so mixed CE does not train one local target while using its sibling as the only heldout check;
3. condition mixed-CE selection by source family or board digest rather than label_type alone.

Any future training variant must still use the regression-gated runner and must not save a checkpoint unless gates pass.
