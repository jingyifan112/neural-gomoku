# Explicit eval authorization request / readiness policy

## Branch

`exp/15x15-eval-authorization-readiness-policy`

## Base route

Previous closed route:

`exp/15x15-teacher-divergence-next-direct-repair-route-final-closeout`

Previous final commit:

`b5a8632 Add direct repair route final closeout`

Previous final decision:

`DIRECT_REPAIR_ROUTE_FINAL_CLOSEOUT_COMPLETE_NO_EXECUTION_NO_AUTHORIZATION_GRANTED`

Previous route status:

`NONE__ROUTE_CLOSED_SEPARATE_EXPLICIT_AUTHORIZATION_REQUIRED_FOR_EVAL`

## Purpose

This route starts a new independent readiness/policy step for explicit eval authorization.

The purpose is only to define what must be true before any future eval command may be run.

This document is not an eval run, not an implicit authorization, not a checkpoint inspection, not a training plan, and not a promotion plan.

## Current route status

`EVAL_AUTHORIZATION_READINESS_POLICY_ONLY_NO_EXECUTION`

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
- overwrite the original manifest
- mutate any prior route artifact except by adding this new standalone policy document

## Authorization principle

No eval is authorized unless the user provides a separate, explicit, future instruction that satisfies all of the following:

1. The instruction names the exact eval scope.
2. The instruction names the exact input artifact or manifest.
3. The instruction names the exact checkpoint path, if checkpoint access is required.
4. The instruction explicitly says checkpoint reading is allowed, if checkpoint reading is required.
5. The instruction explicitly says eval execution is allowed.
6. The instruction confirms that no training, export, benchmark, promotion, or current_best overwrite is allowed unless separately authorized.

## Required future authorization wording

A future eval route should require wording equivalent to:

> I explicitly authorize a readiness-only eval for [specific artifact/scope].
> You may read checkpoint [exact checkpoint path] only for this eval.
> You may run the eval command needed for this scope.
> Do not train, write checkpoint, export C, run public benchmark, promote, or overwrite current_best.

Without equivalent wording, the only valid next action is to produce another non-execution readiness note or request clarification.

## Readiness checklist before any future eval

Before any future eval command is run, a separate route must record:

- branch name
- base commit
- exact eval purpose
- exact artifact or manifest path
- exact checkpoint path, if needed
- whether checkpoint reading is explicitly allowed
- whether eval execution is explicitly allowed
- list of forbidden actions still in force
- expected output files, if any
- confirmation that outputs do not overwrite prior artifacts

## Forbidden by default

The following remain forbidden by default even after eval authorization, unless separately authorized:

- training
- checkpoint writing
- C export
- public benchmark
- promotion
- overwrite of `checkpoints/15x15_current_best.pt`
- overwrite of any current-best alias
- overwrite of original manifests
- mutation of previous route closeout files

## Allowed in this route

This route may only add this policy/readiness document and commit it.

## Decision

`EVAL_AUTHORIZATION_READINESS_POLICY_RECORDED_NO_EVAL_NO_CHECKPOINT_READ_NO_TRAINING_NO_EXPORT_NO_BENCHMARK_NO_PROMOTION`
