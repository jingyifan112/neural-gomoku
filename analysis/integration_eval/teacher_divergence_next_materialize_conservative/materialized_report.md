# Teacher-divergence next conservative dataset materialization

## Scope

- Dataset materialization only.
- No training.
- No checkpoint read or write.
- No C export, no public benchmark, no promotion.

## Output dataset

`analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_conservative_selection_next.json`

## Counts

- source rows: 25
- train rows: 4
- protected eval rows: 15
- tail eval rows: 3
- quarantine rows: 3

## Train candidates

- `legacy_g4_m13`
- `legacy_g4_m23`
- `legacy_g5_m28`
- `legacy_g6_m17`

## Quarantine rows

- `legacy_g2_m11`
- `legacy_g2_m21`
- `legacy_g5_m14`

## Group counts

| group | rows |
|---|---:|
| protected_eval_samples | 15 |
| quarantine_samples | 3 |
| samples | 4 |
| tail_eval_samples | 3 |

## Interpretation

This dataset is intentionally conservative.

Only the four directionally useful train-candidate rows become ordinary train samples. Protected and tail rows remain held out as guards. Quarantine rows are preserved separately but should not be used for checkpoint-producing training without manual review.

## Decision

`TEACHER_DIVERGENCE_NEXT_CONSERVATIVE_DATASET_MATERIALIZED`

Recommended next step: run a schema/consumer audit before any no-save probe.
