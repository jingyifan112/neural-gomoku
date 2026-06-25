# b4c96-safe protected no-save objective ablation wrapper report

## Scope

- b4c96-safe no-save probe only.
- Optimizer runs in memory.
- No checkpoint is saved.
- No C export, no public benchmark, no promotion.

## Architecture

- board_size: 15
- win_length: 5
- channels: 64
- blocks: 4

## Inputs

- dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_conservative_plus_generated_tail_guards_plus_generated_train_candidates_dryrun.json`
- dataset_name: `rapfi_teacher_policy_multisuppress_conservative_plus_generated_tail_guards_plus_generated_train_candidates_dryrun`
- init_checkpoint: `checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`
- reference_checkpoint: `checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`
- epochs: 3
- lr: 1e-06
- margin: 0.25
- ce_weight: 1.0
- pair_weight: 0.0
- worst_weight: 0.0
- anchor_kl_weight: 0.05

## Group metrics

| group | rows | top3 delta | top5 delta | top10 delta | rank_gt50 delta | mean_rank delta | target_prob delta | mean_worst_gap delta | hinge delta | beats_worst delta | beats_all delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| train_main_rank_11_50 | 12 | 0.000000 | 0.000000 | 1.000000 | -1.000000 | -1.333333 | 0.00126085 | -0.041617 | -0.232748 | 0.000000 | 0.000000 |
| protected_eval_top10 | 15 | 1.000000 | 0.000000 | 0.000000 | 0.000000 | -0.133333 | -0.00861646 | 0.782891 | -0.156378 | -1.000000 | -1.000000 |
| tail_eval_rank_gt50 | 15 | 0.000000 | 0.000000 | 0.000000 | 3.000000 | 15.600000 | -0.00000786 | 0.582859 | 0.161464 | 0.000000 | 0.000000 |

## Final training terms

| term | value |
|---|---:|
| loss | 6.82248688 |
| ce_loss | 6.81382418 |
| pair_hinge_loss | 4.28170967 |
| worst_hinge_loss | 6.37040138 |
| anchor_kl | 0.17325372 |
| mean_gap | -4.36046410 |
| mean_worst_gap | -6.50375605 |

## Verdict

FAIL_B4C96_SAFE_NO_SAVE_PROBE

## Decision

No checkpoint was saved.
If the no-save probe fails, the next step should be another objective/data design change, not a saved run.
