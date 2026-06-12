# Candidate G policy-first distillation dry run

## Scope

- Conservative dry run only.
- Trains policy target behavior on the Candidate G board-state dataset.
- Freezes BatchNorm and value head.
- Does not export C weights.
- Does not run formal Rapfi smoke.
- Does not mark any checkpoint as promoted/current-best.

## Inputs

- dataset: `analysis/integration_eval/candidate_g_teacher_seed_dataset.json`
- base_checkpoint: `checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`
- out_checkpoint: `checkpoints/15x15_candidate_g_policy_first_dry_run.pt`
- rows: 14
- model_meta: `{"blocks": 4, "board_size": 15, "channels": 64, "win_length": 5}`
- epochs: 80
- lr: 3e-05
- kl_anchor: 0.25
- policy_head_only: True

## Summary

- rows: 14
- role_counts: {'general_teacher_aligned_anchor': 6, 'nearby_nondivergent_anchor': 5, 'seed_teacher_divergence': 2, 'retention_anchor': 1}
- seed_rows: 2
- seed_improved: 2
- seed_improved_ids: ['g1_p22_black', 'g2_p17_white']
- all_improved: 14
- g2_move15_no_regression: True
- g2_move15_details: [{'row_id': 'g2_p15_white', 'target': '7,9', 'before_top': '10,7', 'after_top': '10,7', 'before_rank': 108, 'after_rank': 42, 'before_prob': 0.00030245300149545074, 'after_prob': 0.0019023795612156391, 'before_gap': -4.385743141174316, 'after_gap': -2.3606977462768555, 'rank_ok': True, 'prob_ok': True, 'logit_ok': True, 'gap_ok': True, 'ok': True}]
- saved_checkpoint: True

## Row metrics

| row_id | role | target | before_top | before_rank | before_prob | before_gap | after_top | after_rank | after_prob | after_gap | improved |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| g1_p0_black | general_teacher_aligned_anchor | 7,7 | 7,7 | 1 | 0.977090 | 0.000000 | 7,7 | 1 | 0.988305 | 0.000000 | True |
| g1_p6_black | general_teacher_aligned_anchor | 3,3 | 3,3 | 1 | 0.201014 | 0.000000 | 3,3 | 1 | 0.432600 | 0.000000 | True |
| g1_p16_black | general_teacher_aligned_anchor | 5,6 | 6,5 | 7 | 0.013797 | 0.000000 | 6,5 | 3 | 0.055914 | 0.000000 | True |
| g1_p18_black | general_teacher_aligned_anchor | 5,8 | 5,8 | 1 | 0.597344 | 0.000000 | 5,8 | 1 | 0.753647 | 0.000000 | True |
| g1_p18_black | nearby_nondivergent_anchor | 5,8 | 5,8 | 1 | 0.597344 | 0.000000 | 5,8 | 1 | 0.753647 | 0.000000 | True |
| g1_p22_black | seed_teacher_divergence | 4,8 | 9,7 | 129 | 0.000023 | -3.818490 | 9,7 | 64 | 0.000161 | -1.978081 | True |
| g1_p24_black | nearby_nondivergent_anchor | 5,7 | 8,6 | 5 | 0.012527 | 6.322269 | 8,6 | 4 | 0.054723 | 7.483844 | True |
| g1_p28_black | general_teacher_aligned_anchor | 6,6 | 8,6 | 3 | 0.074679 | 0.000000 | 8,6 | 2 | 0.299985 | 0.000000 | True |
| g1_p40_black | general_teacher_aligned_anchor | 8,12 | 7,8 | 65 | 0.000388 | 0.000000 | 7,8 | 23 | 0.002873 | 0.000000 | True |
| g2_p13_white | nearby_nondivergent_anchor | 8,8 | 8,8 | 1 | 0.378104 | 0.000000 | 8,8 | 1 | 0.638852 | 0.000000 | True |
| g2_p15_white | retention_anchor | 7,9 | 10,7 | 108 | 0.000302 | -4.385743 | 10,7 | 42 | 0.001902 | -2.360698 | True |
| g2_p17_white | seed_teacher_divergence | 9,10 | 5,9 | 67 | 0.001173 | 0.840252 | 5,9 | 24 | 0.007817 | 2.680592 | True |
| g2_p19_white | nearby_nondivergent_anchor | 10,11 | 9,9 | 127 | 0.000505 | 0.000000 | 9,9 | 73 | 0.002100 | 0.000000 | True |
| g2_p21_white | nearby_nondivergent_anchor | 8,10 | 9,9 | 10 | 0.015595 | 0.000000 | 9,9 | 3 | 0.052632 | 0.000000 | True |
