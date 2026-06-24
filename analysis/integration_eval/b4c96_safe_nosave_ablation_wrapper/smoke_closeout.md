# b4c96-safe no-save ablation wrapper smoke closeout

## Branch

`exp/15x15-b4c96-safe-nosave-ablation-wrapper`

## Purpose

Validate that the new b4c96-safe no-save objective ablation wrapper can load the b4c96 checkpoint with explicit architecture parameters and run an in-memory optimizer probe without saving a checkpoint.

## Script

`scripts/probe_policy_rank_topk_protected_nosave_b4c96.py`

## Scope

Smoke execution only.

No checkpoint was saved. No C export, public benchmark, promotion, or current_best overwrite was performed.

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

## Objective smoke config

- epochs: 1
- lr: 1e-6
- margin: 0.25
- ce_weight: 1.0
- pair_weight: 0.0
- worst_weight: 0.0
- anchor_kl_weight: 0.05

## Execution result

The wrapper loaded the b4c96 checkpoint successfully twice:

- init model
- reference model

The in-memory optimizer ran for 1 epoch.

Policy-head trainable parameters:

`101671`

Final loss terms:

| term | value |
|---|---:|
| loss | 7.12899780 |
| ce_loss | 7.12246752 |
| pair_hinge_loss | 4.34403467 |
| worst_hinge_loss | 6.79207420 |
| anchor_kl | 0.13060468 |
| mean_gap | -3.69300938 |
| mean_worst_gap | -6.34299994 |

## Group metrics

| group | rows | top10 delta | rank_gt50 delta | mean_rank delta | target_prob delta | mean_worst_gap delta | hinge delta |
|---|---:|---:|---:|---:|---:|---:|---:|
| train_main_rank_11_50 | 7 | +1 | -1 | -6.571429 | +0.00311335 | +0.293837 | -0.317029 |
| protected_eval_top10 | 15 | +2 | 0 | -0.666667 | -0.01157200 | +0.911482 | -0.108855 |
| tail_eval_rank_gt50 | 3 | -1 | +2 | +23.000000 | -0.00579487 | -1.014286 | +1.280641 |

## Verdict

`FAIL_B4C96_SAFE_NO_SAVE_PROBE`

## Interpretation

The wrapper itself passed execution smoke:

- architecture-controlled b4c96 load works
- no-save execution works
- group metrics are written
- no checkpoint is saved

The objective smoke configuration failed. The main train group improved, but the tail group regressed severely and protected target probability regressed.

This confirms that the next step should be objective ablation, not checkpoint-producing training.

## Outputs

- `analysis/integration_eval/b4c96_safe_nosave_ablation_wrapper/static_validation.md`
- `analysis/integration_eval/b4c96_safe_nosave_ablation_wrapper/smoke_e1_group_metrics.csv`
- `analysis/integration_eval/b4c96_safe_nosave_ablation_wrapper/smoke_e1_report.md`
- `analysis/integration_eval/b4c96_safe_nosave_ablation_wrapper/smoke_closeout.md`

## Recommended next route

`exp/15x15-b4c96-nosave-objective-ablation-run1`

That route should run no-save variants from the prior ablation plan, especially:

- stronger anchor balanced hinge
- light worst-suppress
- CE-dominant rank repair
- tail-capped or tail-aware configuration

## Actions not performed

- no checkpoint save
- no C export
- no public benchmark
- no promotion
- no overwrite of `current_best`
- no overwrite of manifests
- no modification of old untracked local artifacts

## Final decision

`B4C96_SAFE_NOSAVE_ABLATION_WRAPPER_SMOKE_COMPLETE_OBJECTIVE_FAILED_NO_CHECKPOINT`
