# b4c64/current-best-safe protected no-save objective ablation wrapper report

## Scope

- b4c64/current-best-safe no-save probe only.
- Optimizer runs in memory.
- No checkpoint is saved.
- No C export, no public benchmark, no promotion.

## Architecture

- board_size: 15
- win_length: 5
- channels: 64
- blocks: 4

## Inputs

- dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_guarded_split_v1.json`
- dataset_name: `rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_guarded_split_v1`
- init_checkpoint: `checkpoints/15x15_current_best.pt`
- reference_checkpoint: `checkpoints/15x15_current_best.pt`
- epochs: 1
- lr: 5e-08
- margin: 1.0
- ce_weight: 0.5
- pair_weight: 0.5
- worst_weight: 0.25
- anchor_kl_weight: 1.0
- hard_guard_reference_kl_weight: 4.0
- hard_guard_target_ce_weight: 1.0
- hard_guard_beats_weight: 4.0
- hard_guard_beats_margin: 0.0

## Group metrics

| group | rows | top3 delta | top5 delta | top10 delta | rank_gt50 delta | mean_rank delta | target_prob delta | mean_worst_gap delta | hinge delta | beats_worst delta | beats_all delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| train_main_rank_11_50 | 7 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | -2.142857 | 0.00047863 | -0.083512 | -0.235495 | 0.000000 | 0.000000 |
| protected_eval_top10 | 15 | 0.000000 | 0.000000 | 1.000000 | 0.000000 | -0.400000 | -0.01281538 | 0.675007 | -0.162315 | -1.000000 | -1.000000 |
| tail_eval_rank_gt50 | 3 | 0.000000 | 0.000000 | 0.000000 | 1.000000 | 36.333333 | -0.00010760 | 0.354533 | 0.613684 | 0.000000 | 0.000000 |

## Final training terms

| term | value |
|---|---:|
| loss | 23.76394653 |
| ce_loss | 7.68278265 |
| pair_hinge_loss | 5.47614765 |
| worst_hinge_loss | 8.24426460 |
| anchor_kl | 0.20587209 |
| hard_guard_reference_kl | 0.29295695 |
| hard_guard_target_ce | 6.95573330 |
| hard_guard_beats_hinge | 1.69749534 |
| mean_gap | -4.36246157 |
| mean_worst_gap | -7.24426460 |

## Hard guard row verdicts

| case_id | role | pass | failure reasons | rank before→after | rank>50 before→after | beats-worst before→after | beats-all before→after |
|---|---|---:|---|---:|---:|---:|---:|
| legacy_g1_m40 | hard_protected_beats_guard | False | rank_delta=2.0 > 0.0;target_prob_delta=-0.2768222987651825 < -0.02;teacher_beats_all_delta=-1.0 < 0.0;teacher_beats_worst_delta=-1.0 < 0.0 | 1.0→3.0 | 0→0 | 1→0 | 1→0 |
| legacy_g1_m8 | hard_rank_le50_preservation_guard | False | rank_after=107.0 > 50.0;rank_delta=88.0 > 0.0;rank_gt50_delta=1.0 > 0.0;target_prob_delta=-0.0005092088904348202 < 0.0 | 19.0→107.0 | 0→1 | 0→0 | 0→0 |

## Verdict

FAIL_HARD_GUARD_ROW_DAMAGE

## Decision

No checkpoint was saved.
If the no-save probe fails, the next step should be another objective/data design change, not a saved run.
