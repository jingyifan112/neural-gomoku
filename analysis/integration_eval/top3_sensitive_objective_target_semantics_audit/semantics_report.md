# Top3-sensitive objective/target semantics audit

## Scope

- Branch: `exp/15x15-top3-sensitive-objective-target-semantics-audit`
- Read-only audit after run1 no-save failure.
- No training, checkpoint save, C export, public benchmark, promotion, or current-best overwrite was performed.

## Question

Run1 showed a small printed `train_ce` decrease, but eval target probability regressed on all 3 selected rows. This audit checks whether the issue is caused by row identity, coordinate semantics, or target selection.

## Summary

- rows audited: `3`
- all `teacher_move` match `target_rc` converted to x,y: `True`
- all `policy_target` match `teacher_move`: `True`
- prob improved/regressed: `0/3`
- CE improved/regressed: `0/3`
- rank improved/regressed: `0/2`

## Row semantics

| id | target_rc | target_rc as xy | teacher_move | policy_target | coordinate ok | rank before | rank after | prob before | prob after | CE before | CE after |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| `legacy_g2_m11` | `[7, 9]` | `9,7` | `9,7` | `9,7` | True | 12 | 12 | 0.00032455 | 0.00018413 | 8.033082 | 8.599865 |
| `legacy_g2_m21` | `[9, 7]` | `7,9` | `7,9` | `7,9` | True | 47 | 48 | 0.00014416 | 0.00006372 | 8.844576 | 9.660978 |
| `legacy_g5_m14` | `[9, 7]` | `7,9` | `7,9` | `7,9` | True | 17 | 18 | 0.00194023 | 0.00131850 | 6.244950 | 6.631262 |

## Interpretation

- Row identity and coordinate semantics are consistent.
- The run1 failure should not be explained as an x/y vs row/col target bug.
- Since all 3 target probabilities regressed, this tiny CE no-save route remains closed.
- Next safe audit should inspect objective weighting/update direction or use a dedicated rank/top-k wrapper rather than this legacy CE trainer.

## Outputs

- `analysis/integration_eval/top3_sensitive_objective_target_semantics_audit/semantics_report.md`
- `analysis/integration_eval/top3_sensitive_objective_target_semantics_audit/row_semantics_audit.csv`
- `analysis/integration_eval/top3_sensitive_objective_target_semantics_audit/run1_train_log_excerpt.txt`
- `analysis/integration_eval/top3_sensitive_objective_target_semantics_audit/semantics_summary.json`
- `analysis/integration_eval/top3_sensitive_objective_target_semantics_audit/trainer_script_extracts.json`
