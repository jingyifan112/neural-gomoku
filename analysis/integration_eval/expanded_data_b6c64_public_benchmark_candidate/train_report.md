# b4c96-safe rank/top-k trainer wrapper report

## Scope

- No-promotion b4c96-safe rank/top-k multi-suppress trainer wrapper.
- No C export, no public benchmark, no promotion, no current-best overwrite.
- dry_run: False
- no_save: False
- saved_checkpoint: True

## Inputs

- dataset: analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_conservative_plus_generated_tail_guards_plus_generated_train_candidates_dryrun.json
- dataset_name: rapfi_teacher_policy_multisuppress_conservative_plus_generated_tail_guards_plus_generated_train_candidates_dryrun
- init_checkpoint: checkpoints/15x15_capacity_a_b6c64_train_v2.pt
- reference_checkpoint: checkpoints/15x15_capacity_a_b6c64_train_v2.pt
- out_checkpoint: checkpoints/probes/15x15_expanded_data_b6c64_public_benchmark_candidate.pt
- out_csv: analysis/integration_eval/expanded_data_b6c64_public_benchmark_candidate/train_group_metrics.csv
- anchor_snapshots: analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json

## Architecture

- board_size: 15
- channels: 64
- blocks: 6
- win_length: 5

## Objective

- margin: 0.25
- ce_weight: 1.0
- pair_weight: 0.0
- worst_weight: 0.0
- anchor_kl_weight: 0.05
- lr: 1e-06
- epochs: 3

## Safety Guards

- Refuses any out-checkpoint path containing `current_best`.
- Refuses `checkpoints/15x15_current_best.pt`.
- Refuses `checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`.
- Refuses to overwrite an existing out-checkpoint.

## Initial loss terms

| term | value |
|---|---:|
| loss | 5.32858133 |
| ce_loss | 5.32786179 |
| pair_hinge_loss | 0.28410447 |
| worst_hinge_loss | 0.52511430 |
| anchor_kl | 0.01439053 |
| mean_gap | 0.07419837 |
| mean_worst_gap | -0.26501215 |

## Rank/top-k summary

| metric | before | after | delta |
|---|---:|---:|---:|
| top3 | 0 | 0 | 0.0 |
| top5 | 0 | 0 | 0.0 |
| top10 | 1 | 1 | 0.0 |
| rank_gt50 | 6 | 9 | 3.0 |
| mean_rank | 91.83333333333333 | 97.91666666666667 | 6.083333333333343 |
| mean_target_prob | 0.005185543617699295 | 0.0050043217100513475 | -0.00018122190764794776 |
| mean_worst_gap | -0.2332342006266117 | -0.2681661086777846 | -0.03493190805117291 |
| mean_pair_hinge_margin_025 | 0.2592299152786533 | 0.27420171871781346 | 0.014971803439160158 |
| teacher_beats_worst | 2 | 2 | 0.0 |
| teacher_beats_all | 2 | 2 | 0.0 |

## Final training terms

| term | value |
|---|---:|
| loss | 5.33936501 |
| ce_loss | 5.33905029 |
| pair_hinge_loss | 0.28212112 |
| worst_hinge_loss | 0.53568059 |
| anchor_kl | 0.00629073 |
| mean_gap | 0.08613253 |
| mean_worst_gap | -0.26840457 |

## Decision

Checkpoint saved as a no-promotion probe candidate only.
