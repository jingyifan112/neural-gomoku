# Teacher-divergence tail schema recovery

## Scope

- Schema recovery only.
- No dataset build.
- No training.
- No checkpoint read or write.
- No C export, no public benchmark, no promotion.

## Upstream

- source audit decision: `EXPANSION_SOURCE_AUDIT_HAS_PARTIAL_CANDIDATES`
- tail plan decision: `TAIL_SOURCE_GENERATION_PLAN_REQUIRED`
- tail gap: `12`
- protected gap: `0`
- train gap: `5`

## Recovery summary

- unclassified rows reviewed: `602`
- unique tail recovered: `0`
- unique materializable tail recovered: `0`

## Bucket counts

| bucket | rows | materializable rows |
|---|---:|---:|
| P0_protected_guard_candidate_recovered | 104 | 0 |
| schema_partially_recovered | 498 | 0 |

## Source summary

| source | unclassified | recovered_tail | materializable_tail | recovered_train | still_unclassified |
|---|---:|---:|---:|---:|---:|
| `analysis/integration_eval/teacher_divergence_data_inventory_manifest.csv` | 274 | 0 | 0 | 0 | 0 |
| `analysis/integration_eval/teacher_divergence_expansion_source_audit.csv` | 36 | 0 | 0 | 0 | 0 |
| `analysis/integration_eval/teacher_divergence_retention_expanded_manifest.csv` | 231 | 0 | 0 | 0 | 0 |
| `analysis/integration_eval/teacher_divergence_retention_expanded_dataset.json` | 58 | 0 | 0 | 0 | 0 |
| `analysis/integration_eval/teacher_divergence_source_schema_audit.json` | 3 | 0 | 0 | 0 | 0 |

## Decision

`TAIL_SCHEMA_RECOVERY_NO_TAIL_FOUND`

Schema recovery did not recover tail guard candidates from the unclassified rows.

Next step should generate or collect new tail source rows before any dataset materialization.

## Final note

This recovery does not authorize training, checkpoint save, C export, public benchmark, promotion, or current_best overwrite.
