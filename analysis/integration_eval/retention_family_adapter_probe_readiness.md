# Retention family adapter probe readiness

Scope: adapter probe implementation/readiness only. No training, checkpoint save, C export, benchmark, or promotion was run.

## Added probe emitter

Added:

- `scripts/probe_retention_family_adapter_dataset.py`

The probe emitter wraps the existing `scripts/probe_teacher_divergence_retention_dataset.py` and enriches the resulting probe CSV with retention-family adapter metadata.

## Purpose

Future wrapper-controlled run1 needs four CSVs:

- train before CSV
- train after CSV
- eval before CSV
- eval after CSV

The new probe emitter produces adapter-aware CSVs containing:

- `family_id`
- `source`
- `policy_target`
- `target_rank`
- `target_prob`
- `top1`
- `gate_scope`
- `allowed_as_only_sibling_family_gate`
- `train_use_policy`
- `eval_use_policy`
- `risk_flags`

These fields are consumed by:

- `scripts/evaluate_retention_family_adapter_gates.py`

## Critical family contract

For `bd:ea22cc14729b88fd`, the run1 probe outputs must preserve:

- `7,10` on train side
- `10,7` on train side
- `7,9` on eval side
- restricted gate scope for `7,9`

## Explicit non-actions

- No model training was run.
- No checkpoint was saved.
- No C weights were exported.
- No benchmark was run.
- No promotion decision was made.
