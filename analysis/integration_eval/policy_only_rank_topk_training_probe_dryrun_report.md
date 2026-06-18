# Policy-only rank/top-k training probe report

## Scope

- Policy-head-only rank/top-k multi-suppress probe.
- No C export, no public benchmark, no promotion.
- dry_run: True
- no_save: False
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
- epochs: 20

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
| top10 | 15 | 15 | 0.0 |
| rank_gt50 | 2 | 2 | 0.0 |
| mean_rank | 15.48 | 15.48 | 0.0 |
| mean_target_prob | 0.029081857770506758 | 0.029081857770506758 | 0.0 |
| mean_worst_gap | -5.781836711764336 | -5.781836711764336 | 0.0 |
| mean_pair_hinge_margin_025 | 3.121083364844322 | 3.121083364844322 | 0.0 |
| teacher_beats_worst | 1 | 1 | 0.0 |
| teacher_beats_all | 1 | 1 | 0.0 |

## Decision

Dry-run only. No optimizer step and no checkpoint save.
