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

- dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_conservative_selection_next.json`
- dataset_name: `rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_conservative_selection_next`
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
| train_main_rank_11_50 | 4 | 0.000000 | 0.000000 | 1.000000 | 0.000000 | -4.000000 | 0.00547780 | 0.504478 | -0.366303 | 0.000000 | 0.000000 |
| protected_eval_top10 | 15 | 0.000000 | -1.000000 | 2.000000 | 0.000000 | -0.666667 | -0.01182741 | 0.919337 | -0.121074 | -1.000000 | -1.000000 |
| tail_eval_rank_gt50 | 3 | 0.000000 | 0.000000 | -1.000000 | 2.000000 | 24.666667 | -0.00585572 | -1.021226 | 1.291925 | 0.000000 | 0.000000 |

## Final training terms

| term | value |
|---|---:|
| loss | 7.61483479 |
| ce_loss | 4.93554640 |
| pair_hinge_loss | 2.52162457 |
| worst_hinge_loss | 4.33715105 |
| anchor_kl | 0.11733061 |
| mean_gap | -1.77306867 |
| mean_worst_gap | -4.01807737 |

## Verdict

FAIL_B4C96_SAFE_NO_SAVE_PROBE

## Decision

No checkpoint was saved.
If the no-save probe fails, the next step should be another objective/data design change, not a saved run.
