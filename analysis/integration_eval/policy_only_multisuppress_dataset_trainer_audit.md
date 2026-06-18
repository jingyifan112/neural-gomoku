# Policy-only multi-suppress dataset/trainer audit

## Branch

`exp/15x15-policy-only-multisuppress-audit`

## Purpose

Audit whether the existing policy-only teacher-divergence margin dataset and trainer can support a multi-suppress objective: teacher move ranked above several high-probability model alternatives.

## Inputs reviewed

- Existing trainer: `scripts/train_rapfi_teacher_policy_margin.py`
- Existing margin dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_margin_dataset_corpus8_selected.json`
- Prior design: `analysis/integration_eval/policy_only_objective_gate_next_design.md`
- Prior train metrics: `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_train_metrics.csv`

## Findings

### Existing trainer is single-suppress only

- `load_margin_samples()` reads a top-level `samples` list.
- `make_margin_tensors()` expects `target_rc` and one `suppress_rc` per sample.
- The trainer computes one target action and one suppress action per row.
- The margin loss is a single pairwise term: teacher target logit minus one suppress logit.
- The current implementation does not accept `suppress_rcs`, `suppress_candidates`, or top-k suppress actions.

### Existing dataset is single-suppress only

- Dataset row count: 25 samples.
- Current row schema includes `target_rc`, `suppress_rc`, `sample_weight`, `target_xy`, and `suppress_xy`.
- Current row schema does not include a list of suppress candidates.
- The current notes explicitly describe one suppress move: current_best direct move.

### Existing gate scripts can inform reporting, not training

- `evaluate_teacher_divergence_policy_probe_gates.py` contains useful rank/prob regression gate logic.
- It is not a multi-suppress data builder or trainer.
- The next implementation should reuse gate ideas, not directly repurpose this script as the trainer.

## Recommended next implementation

Use a new narrow implementation rather than mutating the old single-suppress trainer in place.

### Proposed new dataset builder

Create `scripts/build_rapfi_teacher_policy_multisuppress_dataset.py`.

Output path:

`analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json`

Proposed row fields:

- `case_id`
- `board`
- `current_player`
- `target_rc`
- `primary_suppress_rc`
- `suppress_rcs`
- `suppress_actions_source`
- `sample_weight`
- `hardness_weight`
- `before_target_rank`
- `before_gap`
- `validation_notes`

### Proposed new trainer

Create `scripts/train_rapfi_teacher_policy_multisuppress_margin.py`.

The trainer should:

- keep policy-head-only training;
- keep `--ce-weight 0` by default;
- rank the teacher target above every suppress action in `suppress_rcs`;
- use a per-row multi-pair loss, such as the mean or max of pairwise hinge losses;
- retain anchor KL against current_best anchor positions;
- print BEFORE/AFTER diagnostics for target rank, target probability, primary suppress gap, and worst suppress gap;
- refuse to overwrite `checkpoints/15x15_current_best.pt`.

## Gate before any future export or benchmark

- Mean delta gap should materially exceed the previous +0.148287 baseline.
- Target rank improvements should exceed the previous 8 / 25 baseline.
- Target rank regressions must remain 0 / 25.
- High-rank tail should shrink: rows with target rank > 50 should decrease from 3.
- At least some teacher targets should enter top-3 or top-5.
- Anchor KL should remain small.

## Decision

Do not train from this audit branch. The next branch should implement a dedicated multi-suppress dataset builder and trainer dry-run.

## Status

Audit/design only. No dataset generated, no training, no checkpoint, no C export, no public benchmark, no promotion.
