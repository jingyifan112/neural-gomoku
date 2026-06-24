# b4c96 gate-informed objective ablation closeout

## Branch

`exp/15x15-b4c96-gate-informed-objective-ablation`

## Purpose

Plan the next improvement route after b4c96 Stage C gate failure.

This route uses the Stage C failure forensics to define objective/data ablations before any further b4c96 training.

## Source diagnosis

Input forensics:

- `analysis/integration_eval/b4c96_stagec_failure_forensics_summary.json`
- `analysis/integration_eval/b4c96_stagec_failure_forensics.md`
- `analysis/integration_eval/b4c96_stagec_failure_forensics_review.md`

Forensics diagnosis:

`B4C96_STAGEC_FAILED_DUE_TO_PROTECTED_OR_OBJECTIVE_REGRESSION`

Key failure facts:

- top-5 delta was negative
- rank>50 delta was positive
- protected top-10 regression was nonzero
- mean worst suppress gap worsened
- mean multi-pair hinge worsened
- severe core regression rows were nontrivial

## Generated outputs

- `scripts/plan_b4c96_gate_informed_objective_ablation.py`
- `analysis/integration_eval/b4c96_gate_informed_objective_ablation_plan.csv`
- `analysis/integration_eval/b4c96_gate_informed_objective_ablation_plan.json`
- `analysis/integration_eval/b4c96_gate_informed_objective_ablation_plan.md`

## Compatibility finding

Existing rank/top-k training/probe scripts expose no-save and objective weights, including:

- CE weight
- pairwise suppress weight
- worst-suppress weight
- anchor KL weight

However, the current no-save protected probe does not expose b4c96-safe architecture controls.

The b4c96-safe gate wrapper does expose dual architecture controls for Model A and Model B, but the no-save objective ablation path does not yet have equivalent controls.

Therefore direct b4c96 no-save ablation execution is blocked until a b4c96-safe no-save wrapper exists.

## Planned ablations

The plan defines these candidate ablations:

1. `A1_stronger_anchor_balanced_hinge`
2. `A2_light_worst_suppress`
3. `A3_ce_dominant_rank_repair`
4. `A4_tail_capped_training_set`
5. `A5_severe_regression_family_downweight`

The plan also requires explicit gate constraints for:

- protected top-10 regression
- severe core regression separation

## Decision

`ABLATION_PLAN_READY_EXECUTION_BLOCKED_NEEDS_B4C96_SAFE_NOSAVE_WRAPPER`

## Required next route

Open a new implementation route:

`exp/15x15-b4c96-safe-nosave-ablation-wrapper`

That route should implement a no-save wrapper that exposes:

- board size
- win length
- model channels
- model blocks
- init checkpoint
- reference checkpoint
- no-save execution
- CE/pair/worst/anchor-KL weights
- protected/tail group metrics
- no checkpoint write
- no C export
- no public benchmark
- no promotion

## Actions not performed

- no training
- no checkpoint read
- no checkpoint write
- no C export
- no public benchmark
- no promotion
- no overwrite of `current_best`
- no overwrite of manifests
- no modification of old untracked local artifacts

## Final decision

`B4C96_GATE_INFORMED_OBJECTIVE_ABLATION_PLAN_COMPLETE_EXECUTION_BLOCKED`
