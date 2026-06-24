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

- dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_protected_train_11_50_weightcap3.json`
- dataset_name: `rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_protected_train_11_50_weightcap3`
- init_checkpoint: `checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt`
- reference_checkpoint: `checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt`
- epochs: 3
- lr: 1e-06
- margin: 0.25
- ce_weight: 1.0
- pair_weight: 0.6
- worst_weight: 0.2
- anchor_kl_weight: 0.8

## Group metrics

| group | rows | top3 delta | top5 delta | top10 delta | rank_gt50 delta | mean_rank delta | target_prob delta | mean_worst_gap delta | hinge delta | beats_worst delta | beats_all delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| train_main_rank_11_50 | 7 | 0.000000 | 0.000000 | 1.000000 | -1.000000 | -6.714286 | 0.00312402 | 0.295758 | -0.318614 | 0.000000 | 0.000000 |
| protected_eval_top10 | 15 | 0.000000 | -1.000000 | 2.000000 | 0.000000 | -0.666667 | -0.01157686 | 0.911791 | -0.108834 | -1.000000 | -1.000000 |
| tail_eval_rank_gt50 | 3 | 0.000000 | 0.000000 | -1.000000 | 2.000000 | 23.333333 | -0.00579522 | -1.014530 | 1.280866 | 0.000000 | 0.000000 |

## Final training terms

| term | value |
|---|---:|
| loss | 11.18852234 |
| ce_loss | 7.12062454 |
| pair_hinge_loss | 4.34242392 |
| worst_hinge_loss | 6.79014254 |
| anchor_kl | 0.13051820 |
| mean_gap | -3.69137669 |
| mean_worst_gap | -6.34108067 |

## Verdict

FAIL_B4C96_SAFE_NO_SAVE_PROBE

## Decision

No checkpoint was saved.
If the no-save probe fails, the next step should be another objective/data design change, not a saved run.
