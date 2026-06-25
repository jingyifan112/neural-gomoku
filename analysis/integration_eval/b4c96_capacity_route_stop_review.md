# b4c96 capacity route stop review

## Branch

`exp/15x15-b4c96-capacity-route-stop-review`

## Purpose

Close the current b4c96 capacity route with a conservative stop decision.

This review answers whether the current b4c96 capacity increase, paired with the increased multi-suppress teacher-divergence data route, should proceed to checkpoint-producing training, C export, public benchmark, promotion, or `current_best` overwrite.

## Decision

`STOP_B4C96_CAPACITY_ROUTE_CURRENT_OBJECTIVE_DATA_INSUFFICIENT`

Do not continue this b4c96 route into checkpoint-producing training.

Do not export, public benchmark, promote, or overwrite `current_best` from this route.

## Evidence chain

| order | branch | commit | result |
|---:|---|---|---|
| 1 | `exp/15x15-capacity-data-pairing-final-review` | `3cdedaa` | Capacity-data pairing completed; b4c96 + increased multi-suppress data was actually evaluated. |
| 2 | `exp/15x15-b4c96-stagec-failure-forensics` | `056b473` | Stage C failure attributed to protected/objective regressions. |
| 3 | `exp/15x15-b4c96-gate-informed-objective-ablation` | `d47957c` | Ablation plan created; b4c96-safe no-save wrapper required before execution. |
| 4 | `exp/15x15-b4c96-safe-nosave-ablation-wrapper` | `ecfcf62` | b4c96-safe no-save wrapper implemented and smoke-tested; no checkpoint saved. |
| 5 | `exp/15x15-b4c96-nosave-objective-ablation-run1` | `bde54c7` | A1/A2/A3 objective reweighting all failed. |
| 6 | `exp/15x15-b4c96-tail-aware-ablation-dataset-adapter` | `a0dd5f7` | A4/A5 tail-aware datasets built. |
| 7 | `exp/15x15-b4c96-tail-aware-nosave-ablation-run2` | `d007944` | A4/A5 tail-aware no-save ablations both failed. |

## Capacity-data pairing result

The mentor requirement that model capacity increase and training data increase should correspond was satisfied at the process level:

- capacity increase: b4c96
- data increase: increased multi-suppress teacher-divergence dataset
- evaluation: b4c96-safe Stage C gate

However, the paired route failed the gate and therefore cannot be promoted.

## Stage C gate failure summary

The b4c96 Stage C candidate failed against the b4c64 base/reference.

Key failure pattern:

- target top-3 rows did not improve
- target top-5 rows regressed
- rank>50 rows increased
- mean target rank worsened
- mean worst suppress gap worsened
- mean multi-pair hinge worsened
- protected top-10 regression was nonzero
- teacher beats worst/all suppressors stayed at zero

Gate verdict:

`FAIL_CANDIDATE_GATE`

## Failure forensics summary

Forensics diagnosis:

`B4C96_STAGEC_FAILED_DUE_TO_PROTECTED_OR_OBJECTIVE_REGRESSION`

Hard failure reasons included:

- protected top-10 regression
- negative top-5 delta
- increased rank>50 tail failures
- worse mean worst-suppress gap
- worse mean multi-pair hinge

Forensics found the candidate had a mixture of localized improvement and severe regression:

- directionally useful rows existed
- severe core regression rows were nontrivial
- protected/tail regressions were not acceptable

## No-save objective ablation run1

Run1 tested simple objective reweighting:

| variant | result |
|---|---|
| A1 stronger anchor balanced hinge | FAIL |
| A2 light worst suppress | FAIL |
| A3 CE-dominant rank repair | FAIL |

Run1 pattern:

- train group improved
- protected group lost top-5 coverage and target probability
- tail group regressed severely

Run1 decision:

`B4C96_NOSAVE_OBJECTIVE_ABLATION_RUN1_ALL_FAIL_NO_CHECKPOINT`

## Tail-aware dataset adapter

The adapter built A4/A5 datasets:

| dataset | output train rows | added tail guard rows | severe downweighted rows |
|---|---:|---:|---:|
| A4 tail guard | 10 | 3 | 0 |
| A5 tail guard downweight | 10 | 3 | 3 |

The adapter was valid as a no-save ablation input, but not promotion-valid evidence.

Adapter decision:

`B4C96_TAIL_AWARE_ABLATION_DATASET_ADAPTER_COMPLETE`

## Tail-aware no-save ablation run2

Run2 tested A4/A5:

| variant | result |
|---|---|
| A4 tail guard | FAIL |
| A5 tail guard + severe downweight | FAIL |

Run2 pattern:

- protected group still lost top-5 coverage
- protected target probability still regressed
- tail group still lost top-10 coverage
- tail group still increased rank>50 failures by +2
- tail mean rank still worsened by about +22.33
- train group also began showing rank>50 regression

Run2 decision:

`B4C96_TAIL_AWARE_NOSAVE_ABLATION_RUN2_ALL_FAIL_NO_CHECKPOINT`

## Conservative interpretation

The current b4c96 route is not blocked by missing pairing anymore. Pairing was done.

The problem is that the current data/objective combination does not support stable b4c96 improvement:

1. The Stage C gate failed.
2. The failure was not a single metric artifact; it appeared across rank, top-k, suppress-gap, and protected/tail diagnostics.
3. Simple objective reweighting did not solve the failure.
4. Tail-aware guard rows and severe-regression downweighting did not solve the failure.
5. The no-save route repeatedly showed train/protected/tail tradeoffs that are not safe enough for checkpoint-producing training.

## What should not happen next

Do not:

- save a new b4c96 checkpoint from this route
- export a C model
- run public benchmark
- promote this candidate
- overwrite `current_best`
- rerun the same A1/A2/A3/A4/A5 variants as checkpoint-producing training
- treat no-save train-group improvement as sufficient promotion evidence

## Recommended next direction

Return to data construction and selection before any further b4c96 capacity training.

Recommended next route:

`exp/15x15-teacher-divergence-data-selection-next`

Possible goals:

- expand teacher-divergence corpus beyond the current small protected/tail split
- separate trainable divergence rows from protected/tail guard rows more carefully
- add more diverse tail/protected examples before another capacity probe
- build a gate-first selection rule that rejects rows causing protected/tail instability
- only revisit b4c96 after the data route produces stable no-save behavior

## Final decision

`B4C96_CAPACITY_ROUTE_STOPPED_RETURN_TO_DATA_SELECTION`

## Actions not performed in this stop review

- no training
- no checkpoint read
- no checkpoint write
- no C export
- no public benchmark
- no promotion
- no overwrite of `current_best`
- no modification of old untracked local artifacts
