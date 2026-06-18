# Policy-only multi-suppress dry-run closeout

## Branch

`exp/15x15-policy-only-multisuppress-dryrun`

## Scope

This branch implemented and validated a dry-run path for a policy-only multi-suppress teacher-divergence objective.

Included artifacts:

- `scripts/build_rapfi_teacher_policy_multisuppress_dataset.py`
- `scripts/train_rapfi_teacher_policy_multisuppress_margin.py`
- `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json`
- `analysis/integration_eval/policy_only_multisuppress_dataset_build.log`
- `analysis/integration_eval/policy_only_multisuppress_dryrun.log`
- `analysis/integration_eval/policy_only_multisuppress_dryrun_metrics.csv`
- `analysis/integration_eval/policy_only_multisuppress_dryrun_report.md`

## Dataset build result

- Source rows: 25
- Written rows: 25
- Skipped rows: 0
- Suppress count min/mean/max: 5 / 5.0 / 5
- Target rank > 10: 10
- Target rank > 50: 3
- Mean worst suppress gap: -4.954128
- Median worst suppress gap: -5.318236

## Dry-run diagnostic result

- Rows: 25
- Anchor rows: 32
- Target rank top3: 5
- Target rank top5: 11
- Target rank top10: 15
- Target rank > 10: 10
- Target rank > 50: 3
- Mean worst suppress gap: -4.954128
- Median worst suppress gap: -5.318236
- Mean multi-pair hinge: 3.524615

## Interpretation

The dry-run validates the multi-suppress schema and scoring path. Every source row produced five legal suppress moves and the dry-run trainer reloaded and scored all rows successfully.

However, the primary current_best direct move remains the worst suppress move in aggregate: the mean primary gap and mean worst suppress gap are both -4.954128. This means the added top-policy suppress moves do not currently expose a harder pair than the original direct-move suppress pair.

Conclusion: the multi-suppress path is useful for future rank/top-k oriented gates, but this dry-run alone does not justify immediate training, export, benchmark, or promotion.

## Next recommendation

If training is attempted, it should explicitly target rank/top-k movement, not just a larger version of the old primary-pair objective. The gate should require improved top3/top5/top10 visibility, reduced high-rank tail, zero rank regressions, small anchor KL, and no C export or public benchmark unless those local gates pass.

## Status

Closeout only. No training, no checkpoint, no C export, no public benchmark, no promotion.
