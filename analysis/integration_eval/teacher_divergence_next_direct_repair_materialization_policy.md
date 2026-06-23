# 15x15 teacher-divergence next direct repair materialization policy

## Branch

`exp/15x15-teacher-divergence-next-direct-repair-materialization-policy`

## Purpose

Define a conservative static-only policy for the next direct adapter repair queue materialization step.

This document follows the completed branch:

`exp/15x15-teacher-divergence-next-direct-repair-queue-review`

The goal is to make the repair queue actionable without allowing training, model evaluation, checkpoint reading, C export, public benchmark, promotion, or current-best overwrite.

## Prior state

### Run1 conservative core-reuse final closeout

- `final_decision = RUN1_CORE_REUSE_FINAL_CLOSEOUT_COMPLETE_WITH_WARNINGS`
- `promotion_decision = NO_PROMOTION__KEEP_RUN1_CANDIDATE_ISOLATED`
- No training.
- No model evaluation.
- No C export.
- No public benchmark.
- No promotion.

### Direct adapter blocker inspection

- `inspection_decision = DIRECT_ADAPTER_BLOCKER_INSPECTION_READY_FOR_NORMALIZATION_REVIEW`
- `manifest_rows = 10`
- `ready_rows = 3`
- `needs_repair_rows = 1`
- `not_ready_rows = 6`
- `quarantine_rows = 6`
- `blockers = []`

### Direct manifest normalization review

- Normalized ready rows: 3.
- Repair queue rows: 1.
- Quarantine rows: 6.
- `eval_allowed_now = 0`
- `checkpoint_read_allowed_now = 0`
- Rows requiring future explicit flags: 1.

### Direct repair queue review

The repair queue review branch is complete and pushed:

`exp/15x15-teacher-divergence-next-direct-repair-queue-review`

This policy treats that review as the authoritative immediate predecessor.

## Scope of this policy

This policy allows only static manifest-level materialization work.

Allowed:

1. Read tracked text, markdown, CSV, or JSON artifacts under `analysis/integration_eval`.
2. Create a derived static materialization plan.
3. Create a derived static acceptance checklist.
4. Commit only newly created analysis/report files.
5. Keep the 1 repair-queue row isolated from ready rows unless its metadata repair is fully explained.

Forbidden:

1. No training.
2. No model evaluation.
3. No checkpoint content read.
4. No checkpoint artifact creation or staging.
5. No C export.
6. No public benchmark.
7. No promotion.
8. No current-best overwrite.
9. No implicit inclusion of quarantine rows.
10. No use of broad `git add -A`.

## Materialization policy

The next materialization step should produce a static artifact with three buckets:

| Bucket | Expected count | Allowed handling |
|---|---:|---|
| normalized_ready | 3 | May be listed as static-ready only. No eval permission implied. |
| repair_queue | 1 | May be described with required metadata repair. No eval permission implied. |
| quarantine | 6 | Must remain excluded. No eval, no checkpoint read, no promotion path. |

The materialized output must preserve the conservative boundary from the normalization review:

- Ready means metadata-normalized only.
- Ready does not mean eval-ready.
- Ready does not mean checkpoint-readable.
- Repair queue means the row needs explicit future metadata repair before any later status promotion.
- Quarantine rows remain excluded from all follow-on execution.

## Acceptance checklist for the next branch

A future materialization branch may pass only if all checks below are true.

### Static-only checks

- The branch creates only analysis/report artifacts.
- No checkpoint paths are modified or staged.
- No training scripts are executed.
- No model eval scripts are executed.
- No checkpoint-loading command is executed.
- No C export command is executed.
- No benchmark command is executed.

### Manifest checks

- Total direct manifest rows remain 10.
- Normalized ready rows remain 3 unless a static reason is documented.
- Repair queue rows remain 1 unless a static repair is documented.
- Quarantine rows remain 6 unless a later branch explicitly reopens them.
- Quarantine rows are not included in any ready/eval materialization output.

### Permission checks

The materialized artifact must carry these permissions:

- `eval_allowed_now = 0`
- `checkpoint_read_allowed_now = 0`
- `training_allowed_now = 0`
- `c_export_allowed_now = 0`
- `public_benchmark_allowed_now = 0`
- `promotion_allowed_now = 0`

### Future flag checks

The one repair-queue row may only move forward in a later branch if all are true:

1. The exact missing or inconsistent metadata field is named.
2. The static source used for the repair is named.
3. The repaired value is shown before and after.
4. The branch states that the repair does not read checkpoint content.
5. The branch states that the repair does not run model evaluation.
6. The branch keeps promotion disabled.

## Recommended next branch after this policy

If this policy is accepted, the next safe branch should be:

`exp/15x15-teacher-divergence-next-direct-repair-materialization-dryrun`

That branch should only create a static dry-run materialization artifact. It should not train, evaluate, read checkpoints, export C, benchmark, promote, or overwrite current-best.

## Decision

`DIRECT_REPAIR_MATERIALIZATION_POLICY_READY`

This policy is ready for a static materialization dry run.

## Promotion decision

`NO_PROMOTION__STATIC_POLICY_ONLY`

The direct adapter path remains isolated. No candidate should be promoted from this step.
