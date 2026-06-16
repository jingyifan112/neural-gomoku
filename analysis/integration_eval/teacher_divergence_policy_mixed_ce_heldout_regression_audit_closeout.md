# Mixed-CE heldout regression audit closeout

## Scope

This closeout records a read-only heldout regression audit over the corrected mixed-CE scale sweep.

This audit did not run training and did not create a checkpoint.

Boundaries:

- no checkpoint
- no C export
- no benchmark
- no promotion
- no current-best overwrite
- no model-capacity conclusion

## Inputs

Audited corrected mixed-CE scale sweep eval CSVs:

- scale 0.10: `analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_gated_eval.csv`
- scale 0.05: `analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_w005_gated_eval.csv`
- scale 0.025: `analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_w0025_gated_eval.csv`

Audit outputs:

- detail CSV: `analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_regression_audit.csv`
- summary CSV: `analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_regression_audit_summary.csv`
- report: `analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_regression_audit.md`

## Per-scale heldout summary

| scale | rows | rank improved/same/regressed | prob improved/same/regressed | top match gained/lost |
|---:|---:|---:|---:|---:|
| 0.10 | 11 | 3/4/4 | 5/0/6 | 1/0 |
| 0.05 | 11 | 3/4/4 | 4/0/7 | 1/0 |
| 0.025 | 11 | 3/4/4 | 4/0/7 | 1/0 |

## Repeated blockers

Six heldout rows regress by rank or probability under all three corrected scale settings.

Four rows regress on both rank and probability under every scale:

- `holdout_b_mcts16_g2_m19_target_10_7_over_7_11`
- `holdout_candidate_d_g2_m15_white_last_8_9_target_live_direct_7_10_over_live_final_8_8`
- `holdout_candidate_d_g2_m15_white_last_8_9_target_safe_10_7_over_live_final_8_8`
- `holdout_candidate_e_g2_m13_white_target_5_8_over_8_8`

Two rows regress by probability under every scale, even though rank is stable or improved:

- `holdout_candidate_e_g2_m17_white_last_9_9_target_block_right_10_9_over_live_final_9_10`
- `holdout_candidate_e_g2_m17_white_last_9_9_target_future_block_8_10_over_live_final_9_10`

## Stable top-1 gain

One heldout row gains target top-1 under all three scales:

- `holdout_candidate_d_g2_m15_white_last_8_9_target_safe_7_9_over_live_final_8_8`

This means the mixed-CE signal is not uniformly harmful to heldout retention. The failure is concentrated in a small set of repeated blockers.

## Interpretation

The corrected scale sweep failed gates because a small fixed cluster of heldout rows regressed repeatedly.

Simple global mixed-CE scale tuning is unlikely to solve this, because lowering the scale from 0.10 to 0.05 and 0.025 did not remove the repeated heldout regressions.

All repeated blockers are `policy_target` rows, so filtering by label_type alone is not sufficient.

## Decision

Close this branch as a read-only diagnosis of heldout-retention regressions.

No model artifact should be promoted from this audit.

## Recommended next step

Inspect the repeated blocker source positions directly before adding more training signal.

The next useful branch should compare the repeated blocker positions against:

- their original board snapshots or source artifacts
- target rationale
- neighboring teacher-divergence rows
- whether the heldout target is tactical, defensive, live-final, or local-shape retention

Only after that should another gated training variant be attempted.
