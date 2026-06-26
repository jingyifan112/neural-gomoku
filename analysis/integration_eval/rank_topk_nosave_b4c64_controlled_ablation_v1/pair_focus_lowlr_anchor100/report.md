# b4c64/current-best-safe protected no-save objective ablation wrapper report

## Scope

- b4c64/current-best-safe no-save probe only.
- Optimizer runs in memory.
- No checkpoint is saved.
- No C export, no public benchmark, no promotion.

## Architecture

- board_size: 15
- win_length: 5
- channels: 64
- blocks: 4

## Inputs

- dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_protected_train_11_50_weightcap3.json`
- dataset_name: `rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_protected_train_11_50_weightcap3`
- init_checkpoint: `checkpoints/15x15_current_best.pt`
- reference_checkpoint: `checkpoints/15x15_current_best.pt`
- epochs: 1
- lr: 5e-08
- margin: 1.0
- ce_weight: 1.0
- pair_weight: 1.0
- worst_weight: 0.25
- anchor_kl_weight: 1.0

## Group metrics

| group | rows | top3 delta | top5 delta | top10 delta | rank_gt50 delta | mean_rank delta | target_prob delta | mean_worst_gap delta | hinge delta | beats_worst delta | beats_all delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| train_main_rank_11_50 | 7 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | -1.857143 | 0.00049102 | 0.039125 | -0.236212 | 0.000000 | 0.000000 |
| protected_eval_top10 | 15 | 0.000000 | 0.000000 | 1.000000 | 0.000000 | -0.466667 | -0.01281688 | 0.734939 | -0.185709 | -1.000000 | -1.000000 |
| tail_eval_rank_gt50 | 3 | 0.000000 | 0.000000 | 0.000000 | 1.000000 | 37.333333 | -0.00009596 | 0.496984 | 0.558214 | 0.000000 | 0.000000 |

## Final training terms

| term | value |
|---|---:|
| loss | 15.25589180 |
| ce_loss | 7.58634520 |
| pair_hinge_loss | 5.46949673 |
| worst_hinge_loss | 8.11739826 |
| anchor_kl | 0.17070143 |
| mean_gap | -4.36175966 |
| mean_worst_gap | -6.97549534 |

## Verdict

FAIL_B4C64_CURRENT_BEST_SAFE_NO_SAVE_PROBE

## Decision

No checkpoint was saved.
If the no-save probe fails, the next step should be another objective/data design change, not a saved run.
