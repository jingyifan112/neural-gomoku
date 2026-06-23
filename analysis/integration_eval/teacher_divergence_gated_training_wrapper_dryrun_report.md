# Teacher-divergence gated training wrapper dry-run report

## Branch

`exp/15x15-teacher-divergence-gated-training-wrapper-dryrun`

## Scope

- Implements a dry-run executor frame for later gated training.
- Validates wrapper preconditions, commands, hard gates, warning gates, and checkpoint policy.
- Does not train.
- Does not write checkpoints.
- Does not move or delete checkpoints.
- Does not overwrite `checkpoints/15x15_current_best.pt`.
- Does not C export.
- Does not run public benchmark.
- Does not promote.

## Executor decision

`DRY_RUN_READY_FOR_CONTROLLED_EXECUTION`

## Dry-run safety flags

| flag | value |
|---|---:|
| execute_requested | 0 |
| would_train | 0 |
| would_write_checkpoint | 0 |
| would_move_checkpoint | 0 |
| would_delete_checkpoint | 0 |

## Preconditions

| item | value |
|---|---:|
| source closeout decision | PASS_TO_GATED_TRAINING_REVIEW_WITH_WARNINGS |
| plan decision | READY_TO_DESIGN_GATED_TRAINING_DRYRUN |
| missing required paths | 0 |
| blockers | 0 |
| warnings | 0 |
| candidate checkpoint preexisting | 0 |
| quarantine checkpoint preexisting | 0 |

## Planned training command

```bash
env PYTHONPATH=src python scripts/train_rapfi_teacher_policy_margin.py --dataset analysis/integration_eval/teacher_divergence_round2_trainable_trainer_ready_dataset.json --anchor-snapshots analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json --init-checkpoint checkpoints/15x15_current_best.pt --reference-checkpoint checkpoints/15x15_current_best.pt --out-checkpoint checkpoints/15x15_teacher_divergence_round2_policy_margin_gated_review_e10.pt --epochs 10 --margin 1.0 --lr 1e-6 --anchor-kl-weight 0.05 --ce-weight 0.05 --weight-decay 1e-5 --seed 31 --print-every 1 | tee analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_train.log
```

## Planned guard command

```bash
env PYTHONPATH=src python scripts/audit_teacher_divergence_tiny_posttrain_guards.py --baseline-checkpoint checkpoints/15x15_current_best.pt --candidate-checkpoint checkpoints/15x15_teacher_divergence_round2_policy_margin_gated_review_e10.pt --trainer-ready-dataset analysis/integration_eval/teacher_divergence_round2_trainable_trainer_ready_dataset.json --manifest analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_legacy_suppress_normalized.csv --anchor-snapshots analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json --out-trainable-csv analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_trainable_gap_guard.csv --out-bucket-csv analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_manifest_bucket_guard.csv --out-anchor-csv analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_anchor_drift_guard.csv --out-report analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_guard_audit.md --expected-trainable 44
```

## Hard gates

| gate | threshold |
|---|---|
| trainable_rows_evaluated | == 44 |
| trainable_gap_improved_rows | >= 40 |
| trainable_mean_gap_delta | > 0 |
| trainable_target_rank_regressions | == 0 |
| protected_top10_target_rank_regressions | == 0 |
| anchor_top1_changed_rows | == 0 |
| anchor_max_kl_ref_to_candidate | <= 0.005 |

## Warning gates

| gate | action |
|---|---|
| protected_top10_raw_probability_regressions | warn if > 0; require epsilon-aware review |
| tail_rank_gt50_raw_probability_regressions | warn if > 0; require epsilon-aware review |
| tail_rank_gt50_rank_regressions | block uncontrolled scaling and inspect if > 0 |
| anchor_max_kl_ref_to_candidate | warn if > 0.001 and <= 0.005 |

## Checkpoint policy

- Baseline checkpoint: `checkpoints/15x15_current_best.pt`
- Candidate checkpoint: `checkpoints/15x15_teacher_divergence_round2_policy_margin_gated_review_e10.pt`
- Quarantine checkpoint: `checkpoints/quarantine/15x15_teacher_divergence_round2_policy_margin_gated_review_e10_FAILED.pt`
- Pass action: keep candidate checkpoint isolated only.
- Fail action: quarantine candidate checkpoint if it exists.
- Never overwrite `checkpoints/15x15_current_best.pt`.
- Never add checkpoint artifacts to git.

## Blockers

- None.

## Warnings

- None.

## Outputs

- decision JSON: `analysis/integration_eval/teacher_divergence_gated_training_wrapper_dryrun_decision.json`
- decision CSV: `analysis/integration_eval/teacher_divergence_gated_training_wrapper_dryrun_decision.csv`
- command plan: `analysis/integration_eval/teacher_divergence_gated_training_wrapper_dryrun_commands.txt`
- report: `analysis/integration_eval/teacher_divergence_gated_training_wrapper_dryrun_report.md`

## Next step

A later branch may add controlled execution mode. This branch remains dry-run only.

## Final guardrails

- No current_best overwrite.
- No C export.
- No public benchmark.
- No promotion.
- Do not add local checkpoint artifacts to git.
