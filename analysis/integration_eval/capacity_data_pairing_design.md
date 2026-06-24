# Capacity-data pairing design

## Branch

`exp/15x15-capacity-data-pairing-design`

## Purpose

This route turns the capacity-data pairing audit into a concrete design for satisfying the mentor requirement:

> model capacity increase and training data increase must correspond to each other.

This is a design route only.

## Non-execution scope

Not performed:

- no checkpoint read
- no checkpoint inspection
- no training
- no checkpoint write
- no C export
- no public benchmark
- no promotion
- no overwrite of `current_best`
- no overwrite of manifests
- no modification of old untracked local artifacts

## Input audit

`analysis/integration_eval/capacity_data_pairing_audit.json`

Audit decision:

`CAPACITY_DATA_PAIRING_AUDIT_COMPLETE_READY_FOR_DESIGN_NO_TRAINING`

## Primary increased-data candidate

| Field | Value |
|---|---|
| path | `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json` |
| role | primary increased-data policy repair training candidate |
| row count | `25` |
| reason | This is the most direct increased-data candidate for teacher-divergence repair: it upgrades the earlier single-suppress formulation to multi-suppress rows. |

## Supporting data evidence

| Path | Role | Count | Exists |
|---|---|---:|---:|
| `analysis/integration_eval/policy_only_multisuppress_dryrun_metrics.csv` | multi-suppress readiness/gate metrics | 25 | `True` |
| `analysis/integration_eval/policy_only_rank_topk_gate_run1_metrics.csv` | rank/top-k gate evidence | 25 | `True` |
| `analysis/integration_eval/policy_only_rank_topk_protected_nosave_probe_group_metrics.csv` | protected group evidence for rank/top-k route | 3 | `True` |
| `analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_with_fills.csv` | expanded teacher-divergence candidate pool / future scaling source | 362 | `True` |

## Retention / gate data

| Path | Role | Count | Exists |
|---|---|---:|---:|
| `analysis/integration_eval/retention_family_training_consumer_adapter_eval_dataset.json` | retention-family eval/gate set | 9 | `True` |
| `analysis/integration_eval/retention_family_training_consumer_adapter_train_weighted_dataset.json` | small weighted adapter train/control set; not sufficient alone for capacity increase | 2 | `True` |
| `analysis/integration_eval/retention_family_materialized_split_manifest.csv` | heldout / family split manifest for gate design | 11 | `True` |

## Capacity target

`capacity_B_b4c96_data_supported_probe_candidate`

Type:

width-increase candidate, data-supported rerun only

Rationale:

Capacity B is preferred for a minimal data-supported revisit because it is a known capacity-upgrade path with prior reports. It previously did not justify promotion, but those runs should not be treated as satisfying the mentor requirement because they were not cleanly paired with the current increased-data policy/multi-suppress route.

Prior history files:

- `analysis/integration_eval/capacity_candidate_b_b4c96_init_report.md`
- `analysis/integration_eval/capacity_candidate_b_b4c96_train_v1_fixed_probe.md`
- `analysis/integration_eval/capacity_candidate_b_b4c96_train_v2_fixed_probe.md`
- `analysis/integration_eval/capacity_sweep_a_b_conclusion.md`

## Design pairing

The minimum viable capacity-data pairing is:

1. Data side: use the multi-suppress teacher-divergence dataset as the primary increased-data candidate.
2. Gate side: use retention-family eval/gate data to prevent regression.
3. Capacity side: revisit the known b4c96 capacity path only as a data-supported probe, not as promotion.
4. Output side: any future checkpoint must go under a probe/quarantine path and must not overwrite `current_best`.
5. Evaluation side: future gates must measure improvement on teacher-divergence rows and retention preservation.

## Mentor alignment

Requirement:

model capacity increase must correspond to increased training data

Design response:

Do not run a capacity probe unless it is explicitly paired with the increased multi-suppress / teacher-divergence data side and a retention gate.

Status:

`design_ready_but_training_not_authorized`

## What is not authorized yet

- training
- checkpoint reading
- checkpoint writing
- export
- public benchmark
- promotion
- current_best overwrite
- manifest overwrite

## Recommended next route

`exp/15x15-capacity-data-pairing-preflight`

Purpose:

Discover the exact trainer/evaluator command class and verify input/output paths for a later explicitly authorized no-promotion training probe.

Preflight must check:

- exact trainer script
- exact dataset argument name
- exact gate/eval script or static evaluator
- whether capacity B initialization exists as code path
- new output checkpoint path under checkpoints/probes/ only
- new eval output paths under analysis/integration_eval/capacity_data_pairing_probe_preflight or similar
- guards against current_best overwrite

Codex needed now:

`False`

Codex note:

Codex is not needed for this design. Codex may be useful after preflight if the existing training wrapper cannot express the intended capacity/data pairing safely.

## Decision

`CAPACITY_DATA_PAIRING_DESIGN_COMPLETE_READY_FOR_PREFLIGHT_NO_TRAINING`
