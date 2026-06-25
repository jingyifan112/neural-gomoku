# b4c96 tail-aware no-save ablation run2 closeout

## Branch

`exp/15x15-b4c96-tail-aware-nosave-ablation-run2`

## Purpose

Run A4/A5 tail-aware no-save ablations after A1/A2/A3 objective-only reweighting failed.

This route tests whether adding tail guard rows and severe-regression downweighting can prevent the protected/tail regressions observed in run1.

## Scope

No-save ablation only.

No checkpoint was saved. No C export, public benchmark, promotion, or `current_best` overwrite was performed.

## Inputs

- Wrapper: `scripts/probe_policy_rank_topk_protected_nosave_b4c96.py`
- A4 dataset: `analysis/public_benchmark_eval/b4c96_tail_aware_ablation_A4_tail_guard_dataset.json`
- A5 dataset: `analysis/public_benchmark_eval/b4c96_tail_aware_ablation_A5_tail_guard_downweight_dataset.json`
- Anchor snapshots: `analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json`
- Init checkpoint: `checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt`
- Reference checkpoint: `checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt`

## Architecture

- board size: 15
- win length: 5
- channels: 96
- blocks: 4

## Variants run

| variant | dataset | ce | pair | worst | anchor_kl | verdict |
|---|---|---:|---:|---:|---:|---|
| A4_tail_guard | `analysis/public_benchmark_eval/b4c96_tail_aware_ablation_A4_tail_guard_dataset.json` | 1.0 | 0.5 | 0.3 | 1.0 | FAIL_B4C96_SAFE_NO_SAVE_PROBE |
| A5_tail_guard_downweight | `analysis/public_benchmark_eval/b4c96_tail_aware_ablation_A5_tail_guard_downweight_dataset.json` | 1.0 | 0.5 | 0.3 | 1.0 | FAIL_B4C96_SAFE_NO_SAVE_PROBE |

## Key metrics

| variant | group | top5 delta | top10 delta | rank>50 delta | mean_rank delta | target_prob delta | worst_gap delta | hinge delta |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| A4 | train_main_rank_11_50 | 0 | 0 | +1 | +2.300000 | +0.00037343 | -0.115352 | +0.157952 |
| A4 | protected_eval_top10 | -1 | +2 | 0 | -0.666667 | -0.01150738 | +0.890207 | -0.098539 |
| A4 | tail_eval_rank_gt50 | 0 | -1 | +2 | +22.333333 | -0.00576096 | -1.041146 | +1.266028 |
| A5 | train_main_rank_11_50 | 0 | 0 | +1 | +2.300000 | +0.00037362 | -0.115340 | +0.157958 |
| A5 | protected_eval_top10 | -1 | +2 | 0 | -0.666667 | -0.01150805 | +0.890158 | -0.098536 |
| A5 | tail_eval_rank_gt50 | 0 | -1 | +2 | +22.333333 | -0.00576089 | -1.041126 | +1.266004 |

## Interpretation

A4/A5 both failed.

The tail-aware adapter did not solve the core failure mode:

- protected group still loses top-5 coverage
- protected target probability still regresses by about `-0.0115`
- tail group still loses top-10 coverage
- tail group still increases rank>50 failures by `+2`
- tail mean rank still worsens by about `+22.33`

Additionally, both A4/A5 now regress the train group:

- train rank>50 delta: `+1`
- train mean rank delta: `+2.3`
- train worst gap worsens

Therefore neither A4 nor A5 should proceed to checkpoint-producing training.

## Decision

`B4C96_TAIL_AWARE_NOSAVE_ABLATION_RUN2_ALL_FAIL_NO_CHECKPOINT`

## Recommended next route

Open:

`exp/15x15-b4c96-capacity-route-stop-review`

Purpose:

Close the current b4c96 capacity route with a conservative stop decision:

- capacity-data pairing was attempted
- Stage C failed
- failure forensics identified protected/objective regressions
- no-save objective ablation run1 failed
- tail-aware no-save ablation run2 failed
- no b4c96 checkpoint should be saved, exported, benchmarked, promoted, or used as current_best from this route

Further b4c96 work should return to data selection or teacher-divergence corpus construction before any capacity retraining.

## Actions not performed

- no checkpoint save
- no C export
- no public benchmark
- no promotion
- no overwrite of `current_best`
- no overwrite of manifests
- no modification of old untracked local artifacts

## Final decision

`RUN2_CLOSED_TAIL_AWARE_ABLATION_INSUFFICIENT_STOP_B4C96_CAPACITY_ROUTE`
