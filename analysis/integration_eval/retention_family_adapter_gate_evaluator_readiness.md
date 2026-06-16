# Retention family adapter gate evaluator readiness

Scope: evaluator implementation/readiness only. No training, checkpoint save, C export, benchmark, or promotion was run.

## Added evaluator

Added:

- `scripts/evaluate_retention_family_adapter_gates.py`

The evaluator compares before/after probe CSVs for:

- train adapter dataset rows
- eval adapter dataset rows

It is adapter-aware and reads metadata from retention-family consumer adapter fields, including family id, policy target, gate scope, sibling-gate permission, and risk flags.

## Intended run1 usage

A future actual run1 should produce four probe CSVs:

- train before CSV
- train after CSV
- eval before CSV
- eval after CSV

Then run `scripts/evaluate_retention_family_adapter_gates.py` on those four CSVs plus the train/eval adapter JSONs.

## Critical family rule

For `bd:ea22cc14729b88fd`, the evaluator enforces:

- `7,10` must appear on train side.
- `10,7` must appear on train side.
- `7,9` must appear on eval side.
- `7,9` must have `gate_scope=external_or_family_level_only_not_sibling_only`.
- `7,9` must not have `allowed_as_only_sibling_family_gate=yes`.
- `7,9` must not regress on eval-side rank/prob/top1 checks.

## Readiness decision

Decision: READY for actual wrapper-controlled run1, provided the run1 command first generates before/after probe CSVs for both train and eval adapter datasets.

Actual checkpoint save/promotion must still be controlled by:

- `scripts/run_retention_family_gated_training_probe.py`

## Explicit non-actions

- No model training was run.
- No checkpoint was saved.
- No C weights were exported.
- No benchmark was run.
- No promotion decision was made.
