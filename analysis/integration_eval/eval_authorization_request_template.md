# Eval authorization request template

## Branch

`exp/15x15-eval-authorization-request-template`

## Base route

Previous readiness policy route:

`exp/15x15-eval-authorization-readiness-policy`

Previous readiness policy closeout commit:

`b888801 Add eval authorization readiness policy closeout`

Previous readiness policy decision:

`NONE__READINESS_POLICY_ROUTE_CLOSED_SEPARATE_EXPLICIT_AUTHORIZATION_REQUIRED_FOR_ANY_EVAL`

## Purpose

This route creates a template for a future explicit eval authorization request.

This document is not an eval run.

This document is not an authorization by itself.

This document does not permit checkpoint reading, eval execution, training, export, benchmark, promotion, or current-best overwrite.

## Current route status

`EVAL_AUTHORIZATION_REQUEST_TEMPLATE_ONLY_NO_EXECUTION`

## Hard non-execution scope

This route must not:

- run eval
- read any checkpoint
- inspect checkpoint contents
- train
- write checkpoint
- export C
- run public benchmark
- promote any model
- overwrite `current_best`
- overwrite any current-best alias
- overwrite the original manifest
- mutate prior route closeout artifacts
- touch old untracked local artifacts

## Required future authorization fields

A future authorization request must explicitly fill all fields below.

### 1. Eval scope

Status: `UNFILLED`

Required value:

- exact eval purpose
- exact route name
- exact reason this eval is needed

Placeholder:

`[FILL_EXACT_EVAL_SCOPE_HERE]`

### 2. Input artifact or manifest

Status: `UNFILLED`

Required value:

- exact artifact path or manifest path
- whether the artifact is read-only
- confirmation that the original artifact must not be overwritten

Placeholder:

`[FILL_EXACT_INPUT_ARTIFACT_OR_MANIFEST_PATH_HERE]`

### 3. Checkpoint path

Status: `UNFILLED`

Required value if checkpoint access is needed:

- exact checkpoint path
- explicit permission to read this checkpoint
- confirmation that the checkpoint must not be modified

Placeholder:

`[FILL_EXACT_CHECKPOINT_PATH_HERE_OR_MARK_NOT_REQUIRED]`

### 4. Checkpoint read authorization

Status: `UNFILLED`

Required value:

`AUTHORIZED` or `NOT_AUTHORIZED`

Placeholder:

`[FILL_CHECKPOINT_READ_AUTHORIZATION_HERE]`

### 5. Eval execution authorization

Status: `UNFILLED`

Required value:

`AUTHORIZED` or `NOT_AUTHORIZED`

Placeholder:

`[FILL_EVAL_EXECUTION_AUTHORIZATION_HERE]`

### 6. Forbidden actions still in force

The following must remain forbidden unless separately and explicitly authorized:

- training
- checkpoint writing
- C export
- public benchmark
- promotion
- overwrite of `checkpoints/15x15_current_best.pt`
- overwrite of any current-best alias
- overwrite of original manifests
- mutation of prior route closeout files
- cleanup or modification of old untracked local artifacts

### 7. Expected output files

Status: `UNFILLED`

Required value:

- exact output file paths
- confirmation that outputs are new files only
- confirmation that outputs do not overwrite prior artifacts

Placeholder:

`[FILL_EXPECTED_OUTPUT_FILES_HERE]`

### 8. Exact command class

Status: `UNFILLED`

Required value:

- command category only, before execution
- no concrete command may be run until all authorization fields are filled

Placeholder:

`[FILL_COMMAND_CLASS_HERE]`

## Valid future authorization wording

A future user instruction must be equivalent to:

> I explicitly authorize a readiness-only eval for [specific artifact/scope].
> You may read checkpoint [exact checkpoint path] only for this eval.
> You may run the eval command needed for this scope.
> Do not train, write checkpoint, export C, run public benchmark, promote, or overwrite current_best.

## Invalid authorization examples

The following are not sufficient:

- "continue"
- "go ahead"
- "run the next step"
- "do the eval"
- "use the checkpoint"
- "check it"
- "try it"

These do not specify the required scope, artifact, checkpoint path, checkpoint-read permission, eval-execution permission, forbidden actions, and output paths.

## Decision

`EVAL_AUTHORIZATION_REQUEST_TEMPLATE_RECORDED_NO_EVAL_NO_CHECKPOINT_READ_NO_TRAINING_NO_EXPORT_NO_BENCHMARK_NO_PROMOTION`

## Route status

This route only records the authorization request template.

No future eval is authorized by this file alone.
