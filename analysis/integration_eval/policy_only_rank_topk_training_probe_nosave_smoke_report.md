# Policy-only rank/top-k training probe report

## Scope

- Policy-head-only rank/top-k multi-suppress probe.
- No C export, no public benchmark, no promotion.
- dry_run: False
- no_save: True
- saved_checkpoint: False

## Inputs

- dataset: analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json
- dataset_name: rapfi_teacher_policy_multisuppress_dataset_corpus8_selected
- init_checkpoint: checkpoints/15x15_current_best.pt
- reference_checkpoint: checkpoints/15x15_current_best.pt
- out_checkpoint: checkpoints/15x15_policy_rank_topk_probe.pt
- anchor_snapshots: analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json

## Objective

- margin: 0.25
- ce_weight: 1.0
- pair_weight: 0.25
- worst_weight: 0.5
- anchor_kl_weight: 0.05
- lr: 3e-06
- epochs: 3

## Initial loss terms

| term | value |
|---|---:|
| loss | 9.98456860 |
| ce_loss | 6.15531540 |
| pair_hinge_loss | 3.36247849 |
| worst_hinge_loss | 5.95856953 |
| anchor_kl | 0.18697914 |
| mean_gap | -2.54067230 |
| mean_worst_gap | -5.50288868 |

## Rank/top-k summary

| metric | before | after | delta |
|---|---:|---:|---:|
| top3 | 7 | 7 | 0.0 |
| top5 | 11 | 11 | 0.0 |
| top10 | 15 | 16 | 1.0 |
| rank_gt50 | 2 | 3 | 1.0 |
| mean_rank | 15.48 | 19.36 | 3.879999999999999 |
| mean_target_prob | 0.029081857770506758 | 0.022074080884485738 | -0.007007776886021021 |
| mean_worst_gap | -5.781836711764336 | -5.284619159698487 | 0.49721755206584906 |
| mean_pair_hinge_margin_025 | 3.121083364844322 | 3.0470229682922367 | -0.07406039655208518 |
| teacher_beats_worst | 1 | 0 | -1.0 |
| teacher_beats_all | 1 | 0 | -1.0 |

## Final training terms

| term | value |
|---|---:|
| loss | 9.69472790 |
| ce_loss | 5.98642969 |
| pair_hinge_loss | 3.29097581 |
| worst_hinge_loss | 5.75615644 |
| anchor_kl | 0.14952497 |
| mean_gap | -2.50320458 |
| mean_worst_gap | -5.28681040 |

## Decision

Training ran in-process, but no checkpoint was saved because --no-save was set.
