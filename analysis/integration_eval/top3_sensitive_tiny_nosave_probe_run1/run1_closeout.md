# Top3-sensitive tiny no-save probe run1 closeout

## Scope

- Branch: `exp/15x15-top3-sensitive-tiny-nosave-probe-run1`
- Tiny positive-CE no-save probe only.
- No checkpoint save, C export, public benchmark, promotion, or current-best overwrite was performed.

## Decision

- Decision: `FAIL_NO_SAVE_OBJECTIVE_MOVED_WRONG_DIRECTION`
- Checkpoint exists: `False`

## Movement summary

- paired rows: `3`
- rank improved/same/regressed: `0/1/2`
- prob improved/regressed: `0/3`
- CE improved/regressed: `0/3`

## Row movement

| id | target | rank before | rank after | prob before | prob after | ce before | ce after | top before | top after |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| `legacy_g2_m11` | `9,7` | 12 | 12 | 0.00032455 | 0.00018413 | 8.033082 | 8.599865 | `6,5` | `6,5` |
| `legacy_g2_m21` | `7,9` | 47 | 48 | 0.00014416 | 0.00006372 | 8.844576 | 9.660978 | `2,4` | `2,4` |
| `legacy_g5_m14` | `7,9` | 17 | 18 | 0.00194023 | 0.00131850 | 6.244950 | 6.631262 | `6,6` | `6,6` |

## Interpretation

The tiny no-save CE-only route moved the selected targets in the wrong direction or failed to improve them. Do not save a candidate from this route. The next safe option is not to increase epochs blindly; instead inspect objective/target semantics and consider whether these rows should remain gate/forensics rows rather than positive CE training rows.

## Outputs

- `analysis/integration_eval/top3_sensitive_tiny_nosave_probe_run1/run1_closeout.md`
- `analysis/integration_eval/top3_sensitive_tiny_nosave_probe_run1/run1_summary.json`
- `analysis/integration_eval/top3_sensitive_tiny_nosave_probe_run1/tiny_nosave_eval.csv`
- `analysis/integration_eval/top3_sensitive_tiny_nosave_probe_run1/tiny_nosave_report.md`
- `analysis/integration_eval/top3_sensitive_tiny_nosave_probe_run1/tiny_nosave_train.log`
- `analysis/integration_eval/top3_sensitive_tiny_nosave_probe_run1/tiny_primary_positive_ce_train_candidate_dataset.json`
