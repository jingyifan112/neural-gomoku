# b4c96-safe protected no-save objective ablation wrapper report

## Scope

- b4c96-safe no-save probe only.
- Optimizer runs in memory.
- No checkpoint is saved.
- No C export, no public benchmark, no promotion.

## Architecture

- board_size: 15
- win_length: 5
- channels: 96
- blocks: 4

## Inputs

- dataset: `analysis/integration_eval/teacher_divergence_row_level_guard_review/leave_one_out_datasets/drop_legacy_g5_m28.json`
- dataset_name: `teacher_divergence_leave_one_out_drop_legacy_g5_m28`
- init_checkpoint: `checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt`
- reference_checkpoint: `checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt`
- epochs: 3
- lr: 1e-06
- margin: 0.25
- ce_weight: 1.0
- pair_weight: 0.5
- worst_weight: 0.3
- anchor_kl_weight: 1.0

## Group metrics

| group | rows | top3 delta | top5 delta | top10 delta | rank_gt50 delta | mean_rank delta | target_prob delta | mean_worst_gap delta | hinge delta | beats_worst delta | beats_all delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| train_main_rank_11_50 | 3 | 0.000000 | 0.000000 | 1.000000 | 0.000000 | -4.000000 | 0.00239204 | 0.264272 | -0.197161 | 0.000000 | 0.000000 |
| protected_eval_top10 | 15 | 0.000000 | 0.000000 | 2.000000 | 0.000000 | -0.733333 | -0.01184203 | 0.932582 | -0.130448 | -1.000000 | -1.000000 |
| tail_eval_rank_gt50 | 3 | 0.000000 | 0.000000 | -1.000000 | 2.000000 | 26.000000 | -0.00588665 | -1.039410 | 1.305098 | 0.000000 | 0.000000 |

## Final training terms

| term | value |
|---|---:|
| loss | 8.27482033 |
| ce_loss | 5.28047895 |
| pair_hinge_loss | 2.94408345 |
| worst_hinge_loss | 4.70330191 |
| anchor_kl | 0.11130863 |
| mean_gap | -2.22742605 |
| mean_worst_gap | -4.41089773 |

## Verdict

FAIL_B4C96_SAFE_NO_SAVE_PROBE

## Decision

No checkpoint was saved.
If the no-save probe fails, the next step should be another objective/data design change, not a saved run.
