# b4c96 no-save objective ablation run1 closeout

## Branch

`exp/15x15-b4c96-nosave-objective-ablation-run1`

## Purpose

Run b4c96-safe no-save objective ablations after the capacity-data paired b4c96 candidate failed Stage C due to protected/objective regressions.

This route uses the b4c96-safe no-save wrapper created in:

`exp/15x15-b4c96-safe-nosave-ablation-wrapper`

## Scope

No-save ablation only.

No checkpoint was saved. No C export, public benchmark, promotion, or `current_best` overwrite was performed.

## Inputs

- Dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_protected_train_11_50_weightcap3.json`
- Anchor snapshots: `analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json`
- Init checkpoint: `checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt`
- Reference checkpoint: `checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt`

## Architecture

- board size: 15
- win length: 5
- channels: 96
- blocks: 4

## Variants run

| variant | ce | pair | worst | anchor_kl | verdict |
|---|---:|---:|---:|---:|---|
| A1_stronger_anchor_balanced_hinge | 1.0 | 0.6 | 0.6 | 1.0 | FAIL_B4C96_SAFE_NO_SAVE_PROBE |
| A2_light_worst_suppress | 1.0 | 0.6 | 0.2 | 0.8 | FAIL_B4C96_SAFE_NO_SAVE_PROBE |
| A3_ce_dominant_rank_repair | 1.5 | 0.3 | 0.1 | 0.8 | FAIL_B4C96_SAFE_NO_SAVE_PROBE |

## Result summary

All three variants showed the same high-level pattern:

- train group improved
- protected group lost top-5 coverage and target probability
- tail group regressed severely

The train group improvement was not sufficient to justify checkpoint-producing training.

## Key metrics

| variant | group | top5 delta | top10 delta | rank>50 delta | mean_rank delta | target_prob delta | worst_gap delta | hinge delta |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| A1 | train_main_rank_11_50 | 0 | +1 | -1 | -6.714286 | +0.00312396 | +0.295766 | -0.318609 |
| A1 | protected_eval_top10 | -1 | +2 | 0 | -0.666667 | -0.01157658 | +0.911788 | -0.108818 |
| A1 | tail_eval_rank_gt50 | 0 | -1 | +2 | +23.333333 | -0.00579524 | -1.014543 | +1.280915 |
| A2 | train_main_rank_11_50 | 0 | +1 | -1 | -6.714286 | +0.00312402 | +0.295758 | -0.318614 |
| A2 | protected_eval_top10 | -1 | +2 | 0 | -0.666667 | -0.01157686 | +0.911791 | -0.108834 |
| A2 | tail_eval_rank_gt50 | 0 | -1 | +2 | +23.333333 | -0.00579522 | -1.014530 | +1.280866 |
| A3 | train_main_rank_11_50 | 0 | +1 | -1 | -6.714286 | +0.00312409 | +0.295759 | -0.318613 |
| A3 | protected_eval_top10 | -1 | +2 | 0 | -0.666667 | -0.01157822 | +0.911739 | -0.108866 |
| A3 | tail_eval_rank_gt50 | 0 | -1 | +2 | +23.333333 | -0.00579517 | -1.014528 | +1.280806 |

## Interpretation

The unlocked b4c96-safe no-save wrapper works, but simple objective reweighting is not enough.

A1/A2/A3 are rejected because all variants violate the directional safety rule:

- protected group should not lose top-5/top-10 coverage
- tail group should not increase rank>50 failures
- no variant should proceed if train improvement is bought by tail collapse

The strongest regression is consistent across all three variants:

- tail top10 delta: `-1`
- tail rank>50 delta: `+2`
- tail mean_rank delta: about `+23.333333`

## Decision

`B4C96_NOSAVE_OBJECTIVE_ABLATION_RUN1_ALL_FAIL_NO_CHECKPOINT`

## Recommended next route

Open:

`exp/15x15-b4c96-tail-aware-ablation-dataset-adapter`

Purpose:

Build an adapter for A4/A5-style ablations before further no-save training:

- tail-capped training set
- tail-aware guard rows
- severe regression family downweight
- protected/tail hard-guard reporting

## Actions not performed

- no checkpoint save
- no C export
- no public benchmark
- no promotion
- no overwrite of `current_best`
- no overwrite of manifests
- no modification of old untracked local artifacts

## Final decision

`RUN1_CLOSED_OBJECTIVE_REWEIGHTING_INSUFFICIENT_NEEDS_TAIL_AWARE_DATA_ADAPTER`
