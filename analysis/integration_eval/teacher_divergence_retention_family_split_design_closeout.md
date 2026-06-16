# Retention family split design closeout

## Scope

This closeout records a read-only split-design audit over heldout retention families.

This branch did not run training and did not create a checkpoint.

Boundaries:

- no checkpoint
- no C export
- no benchmark
- no promotion
- no current-best overwrite
- no model-capacity conclusion

## Inputs

Primary inputs:

- `analysis/integration_eval/teacher_divergence_retention_safety_v3_dataset.json`
- `analysis/integration_eval/teacher_divergence_retention_manifest.csv`
- `analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_regression_audit_summary.csv`
- `analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_blocker_position_review.csv`

Generated artifacts:

- `scripts/design_retention_family_splits.py`
- `analysis/integration_eval/teacher_divergence_retention_family_split_design_rows.csv`
- `analysis/integration_eval/teacher_divergence_retention_family_split_design_families.csv`
- `analysis/integration_eval/teacher_divergence_retention_family_split_design_report.md`

## Summary

The audit reviewed 11 heldout rows grouped into 7 board/source families.

Key counts:

- heldout rows reviewed: 11
- heldout families: 7
- families with repeated blockers: 4
- families with sibling target conflict: 2
- families with mixed signal conflict: 1

## High-priority families

### `bd:ea22cc14729b88fd`

Family:

- source: `analysis/integration_eval/candidate_d_g2_m15_diagnostic_anchors.json`
- game/move: g2/m15
- targets: `10,7`, `7,10`, `7,9`

Finding:

- `7,10` and `10,7` are repeated blockers.
- `7,9` gains top-1 under all corrected mixed-CE scales.

Decision implication:

This is a sibling-target conflict. A future split must not train one sibling target while using another sibling target from the same board digest as the only heldout check.

Recommendation:

- `split_sibling_targets_and_add_nonheldout_retention_anchor`

### `bd:831f9c7e8843d367`

Family:

- source: `analysis/integration_eval/candidate_e_g2_m17_diagnostic_anchors.json`
- game/move: g2/m17
- targets: `10,9`, `7,9`, `8,10`

Finding:

- `10,9` and `8,10` are repeated blockers.
- `7,9` remains top-1 and gains probability.
- `8,10` improves rank but loses probability under all corrected scales.

Decision implication:

Rank-only gates are insufficient for this family. Probability regression catches real target-mass loss.

Recommendation:

- `split_sibling_targets_by_board_family`

### `bd:3edb62648d54c314`

Family:

- source: `analysis/integration_eval/candidate_e_g2_m13_diagnostic_anchors.json`
- game/move: g2/m13
- target: `5,8`

Finding:

- Single-target family with repeated blocker behavior.
- Target remains below competing top move `8,8`.

Recommendation:

- `add_family_specific_retention_anchor_or_exclude_from_mixed_ce`

### `bd:598170c19d674fee`

Family:

- source: `analysis/integration_eval/current_best_margin_candidate_c_conservative_anchors.json`
- game/move: g2/m19
- target: `10,7`

Finding:

- Single-target family with repeated blocker behavior.
- Target remains below competing top move `9,10`.

Recommendation:

- `add_family_specific_retention_anchor_or_exclude_from_mixed_ce`

## Proposed split rules

1. Do not use a sibling target from the same board digest as the only heldout check while training another sibling target in mixed CE.
2. For board families with repeated blockers, create a small non-heldout retention-anchor subset and keep a separate family-level heldout subset.
3. Preserve probability regression gates; rank-only gates miss low-probability future-block mass loss.
4. Condition mixed-CE row selection by board family/source family, not by label_type alone.
5. Any future training variant must use the regression-gated runner and must not save unless gates pass.

## Decision

Close this branch as a design/audit branch.

No model artifact should be promoted from this branch.

## Recommended next step

The next branch may implement a new dataset split builder that separates retention families by board digest and prevents sibling-target leakage between training and heldout checks.

That next branch should still be measurement-first. Training should only happen after the new split manifest is reviewed.
