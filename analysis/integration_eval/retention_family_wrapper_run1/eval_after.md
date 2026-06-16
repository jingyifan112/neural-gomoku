# Retention family adapter probe

Scope: adapter-aware checkpoint probe only. No training, checkpoint save, C export, benchmark, or promotion was run.

## Inputs and outputs

- adapter_json: `analysis/integration_eval/retention_family_training_consumer_adapter_eval_dataset.json`
- checkpoint: `checkpoints/probes/retention_family_wrapper_run1_candidate.pt`
- output_csv: `analysis/integration_eval/retention_family_wrapper_run1/eval_after.csv`
- output_md: `analysis/integration_eval/retention_family_wrapper_run1/eval_after.md`
- plain temporary dataset: `analysis/integration_eval/adapter_probe_tmp/eval_after.plain_dataset.json`
- raw probe csv: `analysis/integration_eval/adapter_probe_tmp/eval_after.raw_probe.csv`
- raw probe md: `analysis/integration_eval/adapter_probe_tmp/eval_after.raw_probe.md`
- stdout log: `analysis/integration_eval/adapter_probe_tmp/eval_after.probe.stdout.log`
- stderr log: `analysis/integration_eval/adapter_probe_tmp/eval_after.probe.stderr.log`

## Summary

- adapter rows: 9
- raw probe rows: 9
- enriched rows: 9
- adapter metadata: `{'adapter_side': 'eval', 'compat_role': 'heldout_retention_gate', 'compat_split': 'heldout_retention', 'critical_family': 'bd:ea22cc14729b88fd', 'generated_at_utc': '2026-06-16T08:04:22.282284+00:00', 'input_dataset_json': 'analysis/integration_eval/teacher_divergence_retention_safety_v3_dataset.json', 'input_eval_manifest': 'analysis/integration_eval/retention_family_training_input_dryrun_eval_manifest.csv', 'input_train_manifest': 'analysis/integration_eval/retention_family_training_input_dryrun_train_manifest.csv', 'row_count': 9, 'scope': 'consumer adapter dataset only; no training/checkpoint/C export/benchmark/promotion'}`

## Critical family rows

| side | target | rank | prob | top1 | gate_scope | only_sibling_gate_ok | risk_flags |
| --- | --- | --- | --- | --- | --- | --- | --- |
| eval | 7,9 | 129 | nan | no | external_or_family_level_only_not_sibling_only | no | critical_sibling_conflict_family;not_only_sibling_family_gate |

## Explicit non-actions

- No model training was run.
- No checkpoint was saved.
- No C weights were exported.
- No benchmark was run.
- No promotion decision was made.
