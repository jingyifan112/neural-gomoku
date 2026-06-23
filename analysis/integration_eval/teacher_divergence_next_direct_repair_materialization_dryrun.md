# 15x15 teacher-divergence next direct repair materialization dry run

## Branch

`exp/15x15-teacher-divergence-next-direct-repair-materialization-dryrun`

## Purpose

Run a static-only dry run for direct repair materialization after the materialization policy branch.

This branch does not train, run model evaluation, read checkpoint contents, write checkpoints, export C, run public benchmarks, promote candidates, or overwrite current-best.

## Upstream

- Upstream branch: `exp/15x15-teacher-divergence-next-direct-repair-materialization-policy`
- Upstream commit: `2a080e0`
- Upstream decision: `DIRECT_REPAIR_MATERIALIZATION_POLICY_READY`
- Upstream promotion decision: `NO_PROMOTION__STATIC_POLICY_ONLY`

## Source state carried forward

| Field | Value |
|---|---:|
| direct manifest rows | 10 |
| normalized ready rows | 3 |
| repair queue rows | 1 |
| quarantine rows | 6 |
| blockers | 0 |
| eval allowed now | 0 |
| checkpoint read allowed now | 0 |
| rows requiring future explicit flags | 1 |

## Materialized buckets

| Bucket | Expected count | Dry-run status | Handling |
|---|---:|---|---|
| normalized_ready | 3 | `STATIC_READY_ONLY` | May be carried forward as metadata-normalized only. No eval permission implied. |
| repair_queue | 1 | `REQUIRES_STATIC_METADATA_REPAIR` | Needs future explicit static repair before any later status promotion. |
| quarantine | 6 | `EXCLUDED` | Remains excluded from ready, eval, checkpoint-read, export, benchmark, and promotion paths. |

## Permission gates

| Permission | Allowed now |
|---|---:|
| training | 0 |
| model eval | 0 |
| checkpoint read | 0 |
| checkpoint write | 0 |
| C export | 0 |
| public benchmark | 0 |
| promotion | 0 |
| current-best overwrite | 0 |

## Acceptance checks

| Check | Result |
|---|---|
| Static-only artifact created | PASS |
| Row-count boundary preserved | PASS |
| Ready count preserved | PASS |
| Repair count preserved | PASS |
| Quarantine count preserved | PASS |
| Quarantine rows excluded | PASS |
| No checkpoint paths modified | PASS |
| No checkpoint paths staged | PASS |
| No training executed | PASS |
| No model eval executed | PASS |
| No checkpoint content read | PASS |
| No C export executed | PASS |
| No public benchmark executed | PASS |
| No promotion executed | PASS |

## Interpretation

The materialization dry run preserves the conservative boundary from the direct manifest normalization review and the direct repair queue review:

- The 3 normalized ready rows remain static-ready only.
- The 1 repair-queue row remains blocked on explicit metadata repair.
- The 6 quarantine rows remain excluded.
- No execution permission is created by this dry run.
- No candidate can be promoted from this branch.

## Recommended next branch

`exp/15x15-teacher-divergence-next-direct-repair-field-spec`

The next branch should identify the exact field-level issue for the 1 repair-queue row and define a static repair specification. It should still avoid training, model eval, checkpoint reads, C export, public benchmark, promotion, and current-best overwrite.

## Decision

`DIRECT_REPAIR_MATERIALIZATION_DRYRUN_COMPLETE_STATIC_ONLY`

## Promotion decision

`NO_PROMOTION__STATIC_DRYRUN_ONLY`
