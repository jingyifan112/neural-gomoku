# Eval authorization route ledger

## Branch

`exp/15x15-eval-authorization-route-ledger`

## Purpose

This route records the current authorization state across the recent eval-readiness routes.

This document is an index and state ledger only.

It does not authorize eval.

It does not authorize checkpoint reading.

It does not authorize training, checkpoint writing, C export, public benchmark, promotion, or current-best overwrite.

## Current global authorization state

`NO_EVAL_AUTHORIZED`

`NO_CHECKPOINT_READ_AUTHORIZED`

`NO_TRAINING_AUTHORIZED`

`NO_EXPORT_AUTHORIZED`

`NO_BENCHMARK_AUTHORIZED`

`NO_PROMOTION_AUTHORIZED`

`NO_CURRENT_BEST_OVERWRITE_AUTHORIZED`

## Route history

### 1. Direct repair final closeout

Branch:

`exp/15x15-teacher-divergence-next-direct-repair-route-final-closeout`

Final commit:

`b5a8632 Add direct repair route final closeout`

Final decision:

`DIRECT_REPAIR_ROUTE_FINAL_CLOSEOUT_COMPLETE_NO_EXECUTION_NO_AUTHORIZATION_GRANTED`

Route status:

`NONE__ROUTE_CLOSED_SEPARATE_EXPLICIT_AUTHORIZATION_REQUIRED_FOR_EVAL`

Recorded constraints:

- no eval
- no checkpoint read
- no training
- no checkpoint write
- no C export
- no public benchmark
- no promotion
- no overwrite current_best
- no overwrite original manifest

### 2. Eval authorization readiness policy

Branch:

`exp/15x15-eval-authorization-readiness-policy`

Commits:

- `ce00870 Add eval authorization readiness policy`
- `b888801 Add eval authorization readiness policy closeout`

Final decision:

`NONE__READINESS_POLICY_ROUTE_CLOSED_SEPARATE_EXPLICIT_AUTHORIZATION_REQUIRED_FOR_ANY_EVAL`

Meaning:

The route defined the requirements for future explicit eval authorization.

It did not authorize eval.

It did not authorize checkpoint reading.

### 3. Eval authorization request template

Branch:

`exp/15x15-eval-authorization-request-template`

Commits:

- `21d2a00 Add eval authorization request template`
- `5196b7a Add eval authorization request template closeout`

Final decision:

`NONE__REQUEST_TEMPLATE_ROUTE_CLOSED_SEPARATE_EXPLICIT_AUTHORIZATION_REQUIRED_FOR_ANY_EVAL`

Meaning:

The route created a reusable template for a future authorization request.

The template file is not an authorization.

The closeout confirms that no eval, checkpoint read, training, export, benchmark, or promotion occurred.

## Current allowed action class

Only documentation/index/readiness routes are allowed unless the user provides a separate explicit authorization.

Allowed without further authorization:

- add route ledger documents
- add closeout documents
- add non-execution policy documents
- add non-execution authorization templates

Not allowed without separate explicit authorization:

- run eval
- read checkpoint
- inspect checkpoint contents
- train
- write checkpoint
- export C
- run public benchmark
- promote model
- overwrite `checkpoints/15x15_current_best.pt`
- overwrite any current-best alias
- overwrite original manifests
- mutate prior route closeout artifacts
- modify old untracked local artifacts

## Future eval authorization minimum standard

A future eval route must explicitly record all of the following before any command is run:

1. exact branch name
2. exact base commit
3. exact eval purpose
4. exact input artifact or manifest path
5. exact checkpoint path, if checkpoint access is required
6. explicit checkpoint-read permission, if checkpoint access is required
7. explicit eval-execution permission
8. forbidden actions still in force
9. exact output paths
10. confirmation that outputs are new files only
11. confirmation that no prior artifacts are overwritten

## Invalid next-step wording

The following remain insufficient:

- "continue"
- "next"
- "run it"
- "do eval"
- "check checkpoint"
- "try the command"
- "use current_best"
- "go ahead"

These do not satisfy the explicit authorization standard.

## Valid future authorization shape

A valid future authorization must be equivalent to:

> I explicitly authorize a readiness-only eval for [exact scope].
> Input artifact or manifest: [exact path].
> Checkpoint path: [exact path, or NOT REQUIRED].
> Checkpoint reading is authorized only for this eval: [yes/no].
> Eval execution is authorized only for this scope: [yes/no].
> Expected output files: [exact new output paths].
> Do not train, write checkpoint, export C, run public benchmark, promote, overwrite current_best, overwrite manifests, or mutate prior closeouts.

## Ledger decision

`EVAL_AUTHORIZATION_ROUTE_LEDGER_RECORDED_NO_EVAL_NO_CHECKPOINT_READ_NO_TRAINING_NO_EXPORT_NO_BENCHMARK_NO_PROMOTION`

## Current final state

`NONE__NO_EVAL_AUTHORIZED_SEPARATE_EXPLICIT_AUTHORIZATION_REQUIRED`
