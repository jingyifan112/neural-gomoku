# Top3-sensitive tiny no-save probe preflight

## Scope

- Branch: `exp/15x15-top3-sensitive-tiny-nosave-probe-preflight`
- Purpose: materialize tiny probe inputs from the manual decision audit.
- No training, checkpoint save, C export, public benchmark, promotion, or current-best overwrite was performed.

## Primary positive CE rows

| row_id | target | rank | source found | source json | section |
|---|---|---:|---:|---|---|
| `legacy_g2_m11` | `7,9` | 12 | True | `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json` | `samples` |
| `legacy_g2_m21` | `9,7` | 47 | True | `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json` | `samples` |
| `legacy_g5_m14` | `9,7` | 17 | True | `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json` | `samples` |

## Materialization summary

| dataset | requested | materialized | missing ids |
|---|---:|---:|---|
| `primary_positive_ce` | 3 | 3 | `` |
| `backup_positive_ce` | 4 | 4 | `` |
| `protected_anchor_gate` | 15 | 15 | `` |
| `tail_eval_guard` | 3 | 3 | `` |

## Decision

- Preflight status: `READY_FOR_TINY_NO_SAVE_PROBE`
- The next step may run a no-save training/eval probe using `primary_positive_ce_dataset.json` as the tiny train input.

## Outputs

- `analysis/integration_eval/top3_sensitive_tiny_nosave_probe_preflight/backup_positive_ce_dataset.json`
- `analysis/integration_eval/top3_sensitive_tiny_nosave_probe_preflight/backup_positive_ce_manifest.csv`
- `analysis/integration_eval/top3_sensitive_tiny_nosave_probe_preflight/preflight_report.md`
- `analysis/integration_eval/top3_sensitive_tiny_nosave_probe_preflight/preflight_summary.json`
- `analysis/integration_eval/top3_sensitive_tiny_nosave_probe_preflight/primary_positive_ce_dataset.json`
- `analysis/integration_eval/top3_sensitive_tiny_nosave_probe_preflight/primary_positive_ce_manifest.csv`
- `analysis/integration_eval/top3_sensitive_tiny_nosave_probe_preflight/protected_anchor_gate_dataset.json`
- `analysis/integration_eval/top3_sensitive_tiny_nosave_probe_preflight/protected_anchor_gate_manifest.csv`
- `analysis/integration_eval/top3_sensitive_tiny_nosave_probe_preflight/script_help_surfaces.txt`
- `analysis/integration_eval/top3_sensitive_tiny_nosave_probe_preflight/tail_eval_guard_dataset.json`
- `analysis/integration_eval/top3_sensitive_tiny_nosave_probe_preflight/tail_eval_guard_manifest.csv`
