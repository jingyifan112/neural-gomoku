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

- dataset: `analysis/public_benchmark_eval/b4c96_tail_aware_ablation_A4_tail_guard_dataset.json`
- dataset_name: `b4c96_tail_aware_ablation_A4_tail_guard_dataset`
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
| train_main_rank_11_50 | 10 | 0.000000 | 0.000000 | 0.000000 | 1.000000 | 2.300000 | 0.00037343 | -0.115352 | 0.157952 | 0.000000 | 0.000000 |
| protected_eval_top10 | 15 | 0.000000 | -1.000000 | 2.000000 | 0.000000 | -0.666667 | -0.01150738 | 0.890207 | -0.098539 | -1.000000 | -1.000000 |
| tail_eval_rank_gt50 | 3 | 0.000000 | 0.000000 | -1.000000 | 2.000000 | 22.333333 | -0.00576096 | -1.041146 | 1.266028 | 0.000000 | 0.000000 |

## Final training terms

| term | value |
|---|---:|
| loss | 11.61468792 |
| ce_loss | 7.20117044 |
| pair_hinge_loss | 4.45208025 |
| worst_hinge_loss | 6.77952147 |
| anchor_kl | 0.15362054 |
| mean_gap | -4.11531019 |
| mean_worst_gap | -6.33544064 |

## Verdict

FAIL_B4C96_SAFE_NO_SAVE_PROBE

## Decision

No checkpoint was saved.
If the no-save probe fails, the next step should be another objective/data design change, not a saved run.
