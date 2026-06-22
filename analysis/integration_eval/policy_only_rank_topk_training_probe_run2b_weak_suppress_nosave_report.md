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
- out_checkpoint: checkpoints/15x15_policy_rank_topk_probe_run2b.pt
- anchor_snapshots: analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json

## Objective

- margin: 0.25
- ce_weight: 1.0
- pair_weight: 0.05
- worst_weight: 0.1
- anchor_kl_weight: 0.05
- lr: 3e-06
- epochs: 20

## Initial loss terms

| term | value |
|---|---:|
| loss | 6.92864513 |
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
| mean_rank | 15.48 | 19.12 | 3.6400000000000006 |
| mean_target_prob | 0.029081857770506758 | 0.02272485507390229 | -0.006357002696604469 |
| mean_worst_gap | -5.781836711764336 | -5.2475705814361575 | 0.5342661303281782 |
| mean_pair_hinge_margin_025 | 3.121083364844322 | 3.0207215900421147 | -0.1003617748022072 |
| teacher_beats_worst | 1 | 0 | -1.0 |
| teacher_beats_all | 1 | 0 | -1.0 |

## Final training terms

| term | value |
|---|---:|
| loss | 6.69386435 |
| ce_loss | 5.95126915 |
| pair_hinge_loss | 3.26424074 |
| worst_hinge_loss | 5.71903658 |
| anchor_kl | 0.14959207 |
| mean_gap | -2.47123337 |
| mean_worst_gap | -5.24975204 |

## Decision

Training ran in-process, but no checkpoint was saved because --no-save was set.
