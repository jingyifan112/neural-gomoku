# Teacher-divergence gated wrapper controlled execution review

## Branch

`exp/15x15-teacher-divergence-gated-wrapper-controlled-exec-review`

## Scope

- Upgrades the wrapper to support controlled execution mode.
- Default mode remains dry-run.
- Controlled execution requires both `--execute` and the exact confirm token.
- This branch only runs dry-run validation.
- Does not train in this run.
- Does not write checkpoints in this run.
- Does not move or delete checkpoints in this run.
- Does not overwrite `checkpoints/15x15_current_best.pt`.
- Does not C export.
- Does not run public benchmark.
- Does not promote.

## Executor decision

`EXECUTION_PASS_KEEP_ISOLATED_CANDIDATE`

## Safety flags for this run

| flag | value |
|---|---:|
| mode | execute |
| execute_requested | 1 |
| confirm_execute_valid | 1 |
| executed_training | 1 |
| executed_guard | 1 |
| moved_to_quarantine | 0 |

## Preconditions

| item | value |
|---|---:|
| source closeout decision | PASS_TO_GATED_TRAINING_REVIEW_WITH_WARNINGS |
| plan decision | READY_TO_DESIGN_GATED_TRAINING_DRYRUN |
| preflight blockers | 0 |
| preflight warnings | 0 |
| final hard failures | 0 |
| final warnings | 2 |

## Hard gates for execution mode

| gate | threshold |
|---|---|
| trainable_rows | == 44 |
| trainable_gap_improved | >= 40 |
| trainable_mean_gap_delta | > 0 |
| trainable_rank_regressed | == 0 |
| protected_top10_rank_regressed | == 0 |
| anchor_top1_changed | == 0 |
| anchor_max_kl | <= 0.005 |

## Warning gates

| gate | action |
|---|---|
| protected_top10_raw_probability_regressions | warn if > 0 |
| tail_rank_gt50_raw_probability_regressions | warn if > 0 |
| tail_rank_gt50_rank_regressions | warn/block uncontrolled scaling if > 0 |

## Planned training command

```bash
env PYTHONPATH=src python scripts/train_rapfi_teacher_policy_margin.py --dataset analysis/integration_eval/teacher_divergence_round2_trainable_trainer_ready_dataset.json --anchor-snapshots analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json --init-checkpoint checkpoints/15x15_current_best.pt --reference-checkpoint checkpoints/15x15_current_best.pt --out-checkpoint checkpoints/15x15_teacher_divergence_round2_policy_margin_gated_run1_e10.pt --epochs 10 --margin 1.0 --lr 1e-6 --anchor-kl-weight 0.05 --ce-weight 0.05 --weight-decay 1e-5 --seed 31 --print-every 1 | tee analysis/integration_eval/teacher_divergence_gated_training_run1_e10_train.log
```

## Planned guard command

```bash
env PYTHONPATH=src python scripts/audit_teacher_divergence_tiny_posttrain_guards.py --baseline-checkpoint checkpoints/15x15_current_best.pt --candidate-checkpoint checkpoints/15x15_teacher_divergence_round2_policy_margin_gated_run1_e10.pt --trainer-ready-dataset analysis/integration_eval/teacher_divergence_round2_trainable_trainer_ready_dataset.json --manifest analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_legacy_suppress_normalized.csv --anchor-snapshots analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json --out-trainable-csv analysis/integration_eval/teacher_divergence_gated_training_run1_e10_trainable_gap_guard.csv --out-bucket-csv analysis/integration_eval/teacher_divergence_gated_training_run1_e10_manifest_bucket_guard.csv --out-anchor-csv analysis/integration_eval/teacher_divergence_gated_training_run1_e10_anchor_drift_guard.csv --out-report analysis/integration_eval/teacher_divergence_gated_training_run1_e10_guard_audit.md --expected-trainable 44
```

## Checkpoint policy

- Baseline checkpoint: `checkpoints/15x15_current_best.pt`
- Candidate checkpoint: `checkpoints/15x15_teacher_divergence_round2_policy_margin_gated_run1_e10.pt`
- Quarantine checkpoint: `checkpoints/quarantine/15x15_teacher_divergence_round2_policy_margin_gated_run1_e10_FAILED.pt`
- Pass action: keep isolated candidate checkpoint only.
- Fail action: quarantine candidate checkpoint if it exists.
- Never overwrite `checkpoints/15x15_current_best.pt`.
- Never add checkpoint artifacts to git.

## Preflight blockers

- None.

## Warnings

- protected_top10 raw probability regressions 11
- tail_rank_gt50 raw probability regressions 8

## Outputs

- decision JSON: `analysis/integration_eval/teacher_divergence_gated_training_run1_e10_wrapper_decision.json`
- decision CSV: `analysis/integration_eval/teacher_divergence_gated_training_run1_e10_wrapper_decision.csv`
- command plan: `analysis/integration_eval/teacher_divergence_gated_training_run1_e10_wrapper_commands.txt`
- report: `analysis/integration_eval/teacher_divergence_gated_training_run1_e10_wrapper_report.md`

## Next step

A later branch may run controlled execution by passing `--execute --confirm-execute TEACHER_DIVERGENCE_GATED_TRAINING`.

This branch remains a review/dry-run branch only.

## Final guardrails

- No current_best overwrite.
- No C export.
- No public benchmark.
- No promotion.
- Do not add local checkpoint artifacts to git.
