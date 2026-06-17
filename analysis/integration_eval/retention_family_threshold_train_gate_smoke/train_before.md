# Retention family adapter probe

Scope: adapter-aware checkpoint probe only. No training, checkpoint save, C export, benchmark, or promotion was run.

## Inputs and outputs

- adapter_json: `analysis/integration_eval/retention_family_training_consumer_adapter_train_weighted_dataset.json`
- checkpoint: `checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`
- output_csv: `analysis/integration_eval/retention_family_threshold_train_gate_smoke/train_before.csv`
- output_md: `analysis/integration_eval/retention_family_threshold_train_gate_smoke/train_before.md`
- plain temporary dataset: `analysis/integration_eval/adapter_probe_tmp/train_before.plain_dataset.json`
- raw probe csv: `analysis/integration_eval/adapter_probe_tmp/train_before.raw_probe.csv`
- raw probe md: `analysis/integration_eval/adapter_probe_tmp/train_before.raw_probe.md`
- stdout log: `analysis/integration_eval/adapter_probe_tmp/train_before.probe.stdout.log`
- stderr log: `analysis/integration_eval/adapter_probe_tmp/train_before.probe.stderr.log`

## Summary

- adapter rows: 2
- raw probe rows: 2
- enriched rows: 2
- adapter metadata: `{'adapter_side': 'train', 'adapter_train_weight_policy': {'changed_rows': 2, 'default_train_weight': 1.0, 'non_actions': ['no training', 'no checkpoint', 'no C export', 'no benchmark', 'no promotion'], 'purpose': 'ensure adapter train rows have positive finite suggested_weight before guarded training', 'skipped_rows': 0, 'unchanged_positive_rows': 0}, 'compat_role': 'nonheldout_retention_anchor', 'compat_split': 'train_candidate', 'critical_family': 'bd:ea22cc14729b88fd', 'generated_at_utc': '2026-06-16T08:04:22.282284+00:00', 'input_dataset_json': 'analysis/integration_eval/teacher_divergence_retention_safety_v3_dataset.json', 'input_eval_manifest': 'analysis/integration_eval/retention_family_training_input_dryrun_eval_manifest.csv', 'input_train_manifest': 'analysis/integration_eval/retention_family_training_input_dryrun_train_manifest.csv', 'row_count': 2, 'scope': 'consumer adapter dataset only; no training/checkpoint/C export/benchmark/promotion', 'source': 'analysis/integration_eval/retention_family_training_consumer_adapter_train_dataset.json'}`

## Critical family rows

| side | target | rank | prob | top1 | gate_scope | only_sibling_gate_ok | risk_flags |
| --- | --- | --- | --- | --- | --- | --- | --- |
| train | 7,10 | 5 | 0.08013152 | no | not_a_gate | no | critical_sibling_conflict_family |
| train | 10,7 | 2 | 0.10073036 | no | not_a_gate | no | critical_sibling_conflict_family |

## Explicit non-actions

- No model training was run.
- No checkpoint was saved.
- No C weights were exported.
- No benchmark was run.
- No promotion decision was made.
