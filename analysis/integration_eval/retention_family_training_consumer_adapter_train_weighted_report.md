# Retention family adapter train weight policy

Scope: adapter train-weight materialization only. No training, checkpoint, C export, benchmark, or promotion was run.

## Summary

- input_json: `analysis/integration_eval/retention_family_training_consumer_adapter_train_dataset.json`
- out_json: `analysis/integration_eval/retention_family_training_consumer_adapter_train_weighted_dataset.json`
- default_train_weight: `1.0`
- rows: `2`
- changed_rows: `2`
- unchanged_positive_rows: `0`
- skipped_rows: `0`
- split_counts: `{'train_candidate': 2}`
- label_type_counts: `{'nonheldout_retention_anchor': 2}`
- action_counts: `{'set_default_positive_weight': 2}`

## Row manifest

| idx | family | target | split | label_type | before_weight | before_status | after_weight | action | risk_flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | bd:ea22cc14729b88fd | 7,10 | train_candidate | nonheldout_retention_anchor | 0.0 | finite | 1.0 | set_default_positive_weight | critical_sibling_conflict_family |
| 2 | bd:ea22cc14729b88fd | 10,7 | train_candidate | nonheldout_retention_anchor | 0.0 | finite | 1.0 | set_default_positive_weight | critical_sibling_conflict_family |

## Interpretation

The wrapper run1 failure showed that adapter train rows with zero suggested_weight make the legacy trainer's weighted CE/KL denominator invalid. This materialized dataset gives those train rows positive finite weights so future guarded dry-runs or probes can proceed without entering the zero-weight NaN path.

## Explicit non-actions

- No model training was run.
- No checkpoint was saved.
- No C weights were exported.
- No benchmark was run.
- No promotion decision was made.
