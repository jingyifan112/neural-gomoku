# Teacher-divergence next consumer/schema audit

## Scope

- Consumer/schema audit only.
- No training.
- No checkpoint read or write.
- No C export, no public benchmark, no promotion.

## Dataset

`analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_conservative_selection_next.json`

## Group counts

| group | expected | actual |
|---|---:|---:|
| samples | 4 | 4 |
| protected_eval_samples | 15 | 15 |
| tail_eval_samples | 3 | 3 |
| quarantine_samples | 3 | 3 |

## Static consumer scan

| check | value |
|---|---|
| wrapper_exists | `True` |
| trainer_exists | `True` |
| wrapper_mentions_protected_eval_samples | `True` |
| wrapper_mentions_tail_eval_samples | `True` |
| wrapper_mentions_quarantine_samples | `False` |
| trainer_mentions_effective_sample_weight | `True` |
| trainer_mentions_suppress_rcs | `True` |
| forbidden_save_in_wrapper | `False` |
| forbidden_save_in_this_audit | `False` |
| consumer_static_status | `PASS_STATIC_COMPATIBILITY_SCAN` |

## Case IDs

### Train samples
- `legacy_g4_m13`
- `legacy_g4_m23`
- `legacy_g5_m28`
- `legacy_g6_m17`

### Quarantine samples
- `legacy_g2_m11`
- `legacy_g2_m21`
- `legacy_g5_m14`

## Decision

`PASS_CONSUMER_SCHEMA_AUDIT`

The conservative dataset is schema-compatible for a separate no-save probe route.

Next route may run a no-save probe only. It must not save a checkpoint unless a later gate explicitly authorizes checkpoint-producing training.
