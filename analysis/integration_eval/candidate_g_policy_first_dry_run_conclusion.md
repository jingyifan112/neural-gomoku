# Candidate G policy-first distillation dry-run conclusion

## Scope

This was a conservative Candidate G dry run, not a promotion attempt.

The goal was to test whether a small policy-first teacher-seed distillation pass can improve the two seed teacher-divergence targets while preserving the known game2 move15 retention anchor.

No C export was performed.
No formal Rapfi smoke was run.
No current-best or promotion state was changed.

## Inputs

- Dataset: `analysis/integration_eval/candidate_g_teacher_seed_dataset.json`
- Rows: 14
- Role counts:
  - `seed_teacher_divergence`: 2
  - `retention_anchor`: 1
  - `nearby_nondivergent_anchor`: 5
  - `general_teacher_aligned_anchor`: 6
- Base checkpoint: `checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`
- Training script: `scripts/train_candidate_g_policy_first_dry_run.py`
- Report: `analysis/integration_eval/candidate_g_policy_first_dry_run_report.md`

## Result

The dry run passed its conservative checks.

Summary:

- Seed teacher-divergence rows improved: 2 / 2
  - `g1_p22_black`
  - `g2_p17_white`
- All rows improved on the script's monotonic policy-target metric: 14 / 14
- Game2 move15 retention anchor did not regress:
  - row: `g2_p15_white`
  - target: `7,9`
  - target rank improved from 108 to 42
  - target probability improved from 0.0003024530 to 0.0019023796
  - target-vs-model logit gap improved from -4.385743 to -2.360698
- The checkpoint produced by the dry run was intentionally not committed.

## Interpretation

Candidate G shows a positive policy-learning signal.

The two teacher-divergence seed targets both improved, and the retention anchor did not regress under a conservative policy-head-only dry run with BatchNorm and value-head protection.

However, this is not sufficient for promotion. The dataset is intentionally small and focused, and the dry run did not test C inference, formal smoke games, or broader held-out tactical retention.

## Decision

Do not promote Candidate G from this dry run.

Candidate G remains a promising direction for a later, more formal teacher-seed expansion experiment.

## Recommended next action

Before any promotion-oriented Candidate G training, expand the teacher-seed set and add stronger held-out retention checks.

Recommended next step:

1. Add more teacher-divergence rows from additional games or plies.
2. Keep game2 move15 and nearby nondivergent anchors as explicit retention rows.
3. Add held-out retention rows that are not trained on.
4. Run another policy-first dry run.
5. Only if that remains positive, consider a formal Candidate G training run with C export and smoke evaluation.
