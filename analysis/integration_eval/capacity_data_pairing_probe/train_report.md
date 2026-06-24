# b4c96-safe rank/top-k trainer wrapper report

## Scope

- No-promotion b4c96-safe rank/top-k multi-suppress trainer wrapper.
- No C export, no public benchmark, no promotion, no current-best overwrite.
- dry_run: False
- no_save: False
- saved_checkpoint: True

## Inputs

- dataset: analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json
- dataset_name: rapfi_teacher_policy_multisuppress_dataset_corpus8_selected
- init_checkpoint: checkpoints/probes/15x15_capacity_data_pairing_b4c96_warmstart.pt
- reference_checkpoint: checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt
- out_checkpoint: checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt
- out_csv: analysis/integration_eval/capacity_data_pairing_probe/train_metrics.csv
- anchor_snapshots: analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json

## Architecture

- board_size: 15
- channels: 96
- blocks: 4
- win_length: 5

## Objective

- margin: 0.25
- ce_weight: 1.0
- pair_weight: 0.25
- worst_weight: 0.5
- anchor_kl_weight: 0.05
- lr: 3e-06
- epochs: 20

## Safety Guards

- Refuses any out-checkpoint path containing `current_best`.
- Refuses `checkpoints/15x15_current_best.pt`.
- Refuses `checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`.
- Refuses to overwrite an existing out-checkpoint.

## Initial loss terms

| term | value |
|---|---:|
| loss | 10.12306786 |
| ce_loss | 6.31177521 |
| pair_hinge_loss | 3.21624899 |
| worst_hinge_loss | 5.93738413 |
| anchor_kl | 0.77075595 |
| mean_gap | -2.28635025 |
| mean_worst_gap | -5.56897163 |

## Rank/top-k summary

| metric | before | after | delta |
|---|---:|---:|---:|
| top3 | 6 | 7 | 1.0 |
| top5 | 8 | 9 | 1.0 |
| top10 | 12 | 15 | 3.0 |
| rank_gt50 | 2 | 4 | 2.0 |
| mean_rank | 17.6 | 19.52 | 1.9199999999999982 |
| mean_target_prob | 0.025773488223203456 | 0.018964999554591487 | -0.006808488668611969 |
| mean_worst_gap | -5.863985748291015 | -4.915171098709107 | 0.9488146495819088 |
| mean_pair_hinge_margin_025 | 2.990903438568115 | 2.769512586593627 | -0.22139085197448782 |
| teacher_beats_worst | 1 | 0 | -1.0 |
| teacher_beats_all | 1 | 0 | -1.0 |

## Final training terms

| term | value |
|---|---:|
| loss | 9.21083450 |
| ce_loss | 5.74839592 |
| pair_hinge_loss | 3.02325535 |
| worst_hinge_loss | 5.38522482 |
| anchor_kl | 0.28025240 |
| mean_gap | -2.29359579 |
| mean_worst_gap | -4.91728783 |

## Decision

Checkpoint saved as a no-promotion probe candidate only.
