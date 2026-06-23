# Teacher-divergence gated training dry-run wrapper design

## Branch

`exp/15x15-teacher-divergence-gated-training-dryrun-wrapper-design`

## Scope

- Designs the wrapper for a later gated training dry run.
- Generates command plan and save-on-pass policy.
- Does not train.
- Does not read or write candidate checkpoints.
- Does not overwrite `checkpoints/15x15_current_best.pt`.
- Does not C export.
- Does not run public benchmark.
- Does not promote.

## Source plan state

| item | value |
|---|---:|
| source closeout decision | PASS_TO_GATED_TRAINING_REVIEW_WITH_WARNINGS |
| plan decision | READY_TO_DESIGN_GATED_TRAINING_DRYRUN |
| hard failures | 0 |
| warnings | 2 |
| allowed to design wrapper | 1 |
| missing required paths | 0 |

## Proposed training command

```bash
PYTHONPATH=src python scripts/train_rapfi_teacher_policy_margin.py --dataset analysis/integration_eval/teacher_divergence_round2_trainable_trainer_ready_dataset.json --anchor-snapshots analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json --init-checkpoint checkpoints/15x15_current_best.pt --reference-checkpoint checkpoints/15x15_current_best.pt --out-checkpoint checkpoints/15x15_teacher_divergence_round2_policy_margin_gated_review_e10.pt --epochs 10 --margin 1.0 --lr 1e-6 --anchor-kl-weight 0.05 --ce-weight 0.05 --weight-decay 1e-5 --seed 31 --print-every 1 | tee analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_train.log
```

## Proposed guard command

```bash
PYTHONPATH=src python scripts/audit_teacher_divergence_tiny_posttrain_guards.py --baseline-checkpoint checkpoints/15x15_current_best.pt --candidate-checkpoint checkpoints/15x15_teacher_divergence_round2_policy_margin_gated_review_e10.pt --trainer-ready-dataset analysis/integration_eval/teacher_divergence_round2_trainable_trainer_ready_dataset.json --manifest analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_legacy_suppress_normalized.csv --anchor-snapshots analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json --out-trainable-csv analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_trainable_gap_guard.csv --out-bucket-csv analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_manifest_bucket_guard.csv --out-anchor-csv analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_anchor_drift_guard.csv --out-report analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_guard_audit.md --expected-trainable 44
```

## Save-on-pass wrapper policy

| gate | threshold | failure action |
|---|---|---|
| trainable rows evaluated | exactly 44 | fail + quarantine candidate |
| trainable gap improved rows | >= 40 | fail + quarantine candidate |
| trainable mean gap delta | > 0 | fail + quarantine candidate |
| trainable target rank regressions | 0 | fail + quarantine candidate |
| protected_top10 target rank regressions | 0 | fail + quarantine candidate |
| anchor top1 changed rows | 0 | fail + quarantine candidate |
| anchor max KL ref->candidate | <= 0.005 | fail + quarantine candidate |

## Warning policy

| warning | action |
|---|---|
| protected_top10 raw probability regressions | report, require epsilon-aware review |
| tail_rank_gt50 raw probability regressions | report, require epsilon-aware review |
| tail_rank_gt50 rank regression | block uncontrolled scaling and inspect |
| anchor max KL > 0.001 and <= 0.005 | warning only |

## Candidate paths

- baseline checkpoint: `checkpoints/15x15_current_best.pt`
- isolated candidate checkpoint: `checkpoints/15x15_teacher_divergence_round2_policy_margin_gated_review_e10.pt`
- quarantine checkpoint path: `checkpoints/quarantine/15x15_teacher_divergence_round2_policy_margin_gated_review_e10_FAILED.pt`

## Planned outputs for later execution

- training log: `analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_train.log`
- trainable guard CSV: `analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_trainable_gap_guard.csv`
- manifest bucket guard CSV: `analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_manifest_bucket_guard.csv`
- anchor drift guard CSV: `analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_anchor_drift_guard.csv`
- guard report: `analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_guard_audit.md`
- wrapper decision JSON: `analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_wrapper_decision.json`
- wrapper decision CSV: `analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_wrapper_decision.csv`
- wrapper closeout report: `analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_wrapper_closeout.md`

## Summary table

| item | value | status | notes |
|---|---:|---|---|
| source_closeout_decision | PASS_TO_GATED_TRAINING_REVIEW_WITH_WARNINGS | INFO |  |
| plan_decision | READY_TO_DESIGN_GATED_TRAINING_DRYRUN | INFO |  |
| allowed_to_design_wrapper | 1 | PASS |  |
| hard_failure_count | 0 | PASS |  |
| warning_count | 2 | WARN |  |
| missing_required_paths | 0 | PASS |  |
| baseline_checkpoint | checkpoints/15x15_current_best.pt | INFO | must never be overwritten |
| candidate_checkpoint | checkpoints/15x15_teacher_divergence_round2_policy_margin_gated_review_e10.pt | INFO | isolated output path |
| quarantine_checkpoint | checkpoints/quarantine/15x15_teacher_divergence_round2_policy_margin_gated_review_e10_FAILED.pt | INFO | failure path only |
| epochs | 10 | INFO |  |
| lr | 1e-6 | INFO |  |
| margin | 1.0 | INFO |  |
| anchor_kl_weight | 0.05 | INFO |  |
| ce_weight | 0.05 | INFO |  |
| weight_decay | 1e-5 | INFO |  |
| seed | 31 | INFO |  |
| train_log | analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_train.log | INFO |  |
| trainable_guard_csv | analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_trainable_gap_guard.csv | INFO |  |
| bucket_guard_csv | analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_manifest_bucket_guard.csv | INFO |  |
| anchor_guard_csv | analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_anchor_drift_guard.csv | INFO |  |
| guard_report | analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_guard_audit.md | INFO |  |
| wrapper_decision_json | analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_wrapper_decision.json | INFO |  |
| wrapper_decision_csv | analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_wrapper_decision.csv | INFO |  |
| wrapper_closeout | analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_wrapper_closeout.md | INFO |  |

## Missing required paths

- None.

## Decision

`WRAPPER_DESIGN_READY_FOR_IMPLEMENTATION`

This branch is design-only. The next branch may implement the actual wrapper executor, still with dry-run defaults.

## Final guardrails

- No current_best overwrite.
- No C export.
- No public benchmark.
- No promotion.
- Do not add local checkpoint artifacts to git.
