# Teacher-divergence next conservative no-save probe closeout

## Branch

`exp/15x15-teacher-divergence-next-nosave-probe`

## Purpose

Run a no-save probe on the conservative teacher-divergence dataset after:

- b4c96 capacity route stop review
- data selection audit
- conservative dataset materialization
- consumer/schema audit PASS

## Scope

No-save probe only.

No checkpoint was saved. No C export, public benchmark, promotion, or `current_best` overwrite was performed.

## Input dataset

`analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_conservative_selection_next.json`

Dataset composition:

- train rows: 4
- protected eval rows: 15
- tail eval rows: 3
- quarantine rows: 3

## Architecture/checkpoint

- architecture: b4c96
- board size: 15
- win length: 5
- init/reference checkpoint: `checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt`

## Variant

| variant | epochs | lr | ce | pair | worst | anchor_kl | verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| conservative_selection_next | 3 | 1e-6 | 1.0 | 0.5 | 0.3 | 1.0 | FAIL_B4C96_SAFE_NO_SAVE_PROBE |

## Metrics

| group | top5 delta | top10 delta | rank>50 delta | mean_rank delta | target_prob delta | worst_gap delta | hinge delta |
|---|---:|---:|---:|---:|---:|---:|---:|
| train_main_rank_11_50 | 0 | +1 | 0 | -4.000000 | +0.00547780 | +0.504478 | -0.366303 |
| protected_eval_top10 | -1 | +2 | 0 | -0.666667 | -0.01182741 | +0.919337 | -0.121074 |
| tail_eval_rank_gt50 | 0 | -1 | +2 | +24.666667 | -0.00585572 | -1.021226 | +1.291925 |

## Interpretation

The conservative dataset improved the train group but did not protect the guard groups.

Failure pattern:

- protected group lost top-5 coverage
- protected target probability regressed
- tail group lost top-10 coverage
- tail group rank>50 failures increased by +2
- tail mean rank worsened by about +24.67
- tail worst suppress gap and hinge regressed

Therefore the conservative dataset should not proceed to checkpoint-producing training.

## Decision

`CONSERVATIVE_NOSAVE_PROBE_FAILED_GUARDS`

## Recommended next route

Open:

`exp/15x15-teacher-divergence-row-level-guard-review`

Purpose:

Review row-level deltas for protected/tail guard failures and identify which train candidate(s) are causing guard instability.

Recommended approach:

- compare before/after per-row metrics from the no-save probe report/CSV
- isolate protected top5 loss row(s)
- isolate tail top10 loss / rank>50 regression row(s)
- test leave-one-train-candidate-out no-save probes only if needed
- do not save checkpoint

## Actions not performed

- no checkpoint save
- no C export
- no public benchmark
- no promotion
- no overwrite of `current_best`
- no modification of old untracked local artifacts

## Final decision

`NO_SAVE_PROBE_CLOSED_RETURN_TO_ROW_LEVEL_GUARD_REVIEW`
