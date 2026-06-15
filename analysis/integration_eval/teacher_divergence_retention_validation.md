# Teacher divergence / retention validation

## Scope

Validate generated dataset rows only. This script does not train, export, or benchmark.

## Summary

- Dataset: `analysis/integration_eval/teacher_divergence_retention_dataset.json`
- Manifest: `analysis/integration_eval/teacher_divergence_retention_manifest.csv`
- Validation CSV: `analysis/integration_eval/teacher_divergence_retention_validation.csv`
- Total rows: 36
- Error rows: 0
- Warning rows: 0

### Split counts

| split | rows | ok | bad |
|---|---:|---:|---:|
| `train_teacher_divergence` | 25 | 25 | 0 |
| `heldout_retention` | 11 | 11 | 0 |

### Board formats

| board_format | rows |
|---|---:|
| `text_grid` | 25 |
| `matrix_list` | 11 |

### Target cell status

| status | rows |
|---|---:|
| `empty` | 36 |

## Errors

No error rows.

## Warnings

No warning rows.
