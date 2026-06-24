# Capacity-data pairing final review

## Branch

`exp/15x15-capacity-data-pairing-final-review`

## Purpose

Final review for the data-supported capacity probe chain.

This route records whether the project satisfied the mentor requirement that model capacity increases and training data increases should correspond to each other.

## Chain summary

The chain executed the paired capacity/data probe:

- capacity side: b4c96 capacity path
- data side: increased multi-suppress teacher-divergence dataset
- training side: b4c96-safe Stage B training wrapper
- gate side: b4c96-safe Stage C rank/top-k gate wrapper

## Key commits

- Stage B training: `f1bfec9 Add b4c96-safe Stage B training probe results`
- Stage C gate execution: `82a0fad Add b4c96-safe Stage C gate execution results`
- Gate wrapper static review pass: `800df53 Patch b4c96-safe gate wrapper static review`

## Mentor alignment

The mentor requirement is satisfied at the experimental-process level:

- increased model capacity was used: b4c96
- increased training data was used: multi-suppress teacher-divergence dataset
- the capacity increase and data increase were paired in an actual Stage B training probe
- the result was evaluated with a b4c96-safe Stage C gate

## Gate verdict

`FAIL_CANDIDATE_GATE`

## Gate summary

| Metric | Model A | Model B | Delta |
|---|---:|---:|---:|
| target top-3 rows | 7 | 7 | 0 |
| target top-5 rows | 11 | 9 | -2 |
| target top-10 rows | 14 | 15 | 1 |
| target rank > 50 rows | 3 | 4 | 1 |
| mean target rank | 17.32 | 19.52 | 2.20 |
| mean worst suppress gap | -4.430053 | -4.915171 | -0.485118 |
| mean multi-pair hinge | 3.120448 | 3.394243 | 0.273795 |
| teacher beats worst suppress rows | 0 | 0 | 0 |
| teacher beats all suppressors rows | 0 | 0 | 0 |

Protected top-10 regressions:

`1`

## Interpretation

The paired capacity/data experiment ran successfully, but the candidate did not improve enough to pass gate.

Observed regressions include:

- target top-5 rows decreased
- target rank > 50 rows increased
- mean target rank worsened
- mean worst suppress gap worsened
- mean multi-pair hinge worsened
- protected top-10 regression count was nonzero

Therefore the candidate is not eligible for promotion.

## Actions not performed

Not performed:

- no C export
- no public benchmark
- no promotion
- no overwrite of `current_best`
- no overwrite of manifests
- no modification of old untracked local artifacts

## Checkpoint tracking note

The local warmstart and candidate checkpoints remain intentionally untracked unless a separate checkpoint-tracking policy authorizes them.

## Final decision

`CAPACITY_DATA_PAIRING_FINAL_REVIEW_COMPLETE_GATE_FAILED_NO_PROMOTION`
