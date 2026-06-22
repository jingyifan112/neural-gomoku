# Policy-only rank/top-k training probe report

## Scope

- Policy-head-only rank/top-k multi-suppress probe.
- No C export, no public benchmark, no promotion.
- dry_run: True
- no_save: False
- saved_checkpoint: False

## Inputs

- dataset: analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_protected_train_11_50_weightcap3.json
- dataset_name: rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_protected_train_11_50_weightcap3
- init_checkpoint: checkpoints/15x15_current_best.pt
- reference_checkpoint: checkpoints/15x15_current_best.pt
- out_checkpoint: checkpoints/15x15_policy_rank_topk_protected_probe.pt
- anchor_snapshots: analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json

## Objective

- margin: 0.25
- ce_weight: 1.0
- pair_weight: 0.0
- worst_weight: 0.0
- anchor_kl_weight: 0.05
- lr: 1e-06
- epochs: 20

## Initial loss terms

| term | value |
|---|---:|
| loss | 7.66362476 |
| ce_loss | 7.65427589 |
| pair_hinge_loss | 4.87708330 |
| worst_hinge_loss | 7.38822079 |
| anchor_kl | 0.18697914 |
| mean_gap | -4.52610779 |
| mean_worst_gap | -6.99209642 |

## Rank/top-k summary

| metric | before | after | delta |
|---|---:|---:|---:|
| top3 | 0 | 0 | 0.0 |
| top5 | 0 | 0 | 0.0 |
| top10 | 1 | 1 | 0.0 |
| rank_gt50 | 0 | 0 | 0.0 |
| mean_rank | 21.142857142857142 | 21.142857142857142 | 0.0 |
| mean_target_prob | 0.0015644194042709256 | 0.0015644194042709256 | 0.0 |
| mean_worst_gap | -7.01457725252424 | -7.01457725252424 | 0.0 |
| mean_pair_hinge_margin_025 | 4.847929872785296 | 4.847929872785296 | 0.0 |
| teacher_beats_worst | 0 | 0 | 0.0 |
| teacher_beats_all | 0 | 0 | 0.0 |

## Decision

Dry-run only. No optimizer step and no checkpoint save.
