# Teacher-divergence tail guard consumer/gate dry-run audit

## Scope

- Consumer/gate dry-run audit only.
- No training.
- No optimizer step.
- No checkpoint save.
- No C export, no public benchmark, no promotion.

## Inputs

- dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_conservative_plus_generated_tail_guards_dryrun.json`
- wrapper: `scripts/probe_policy_rank_topk_protected_nosave_b4c96.py`

## Wrapper compatibility

- wrapper load ok: `True`
- wrapper load error: ``
- wrapper forbidden checkpoint save token present: `False`

## Counts

| group | count | expected |
|---|---:|---:|
| samples | 4 | 4 |
| protected_eval_samples | 15 | 15 |
| tail_eval_samples | 15 | 15 |
| quarantine_samples | 3 | 3 |
| generated_tail_rows | 12 | 12 |

## Row audit

| status | count |
|---|---:|
| PASS | 37 |

## Hard failures

- none

## Decision

`TAIL_GUARD_CONSUMER_GATE_DRYRUN_AUDIT_PASS`

## Final note

This audit does not authorize training, checkpoint save, C export, public benchmark, promotion, or current_best overwrite.
