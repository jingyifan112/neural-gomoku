# Teacher-divergence round2 trainer dry-run preflight

## Branch

`exp/15x15-teacher-divergence-trainer-ready-preflight`

## Scope

- Prepared a trainer-ready 44-row dataset from the legacy-normalized dry-run dataset.
- Added reconstructed board state to each sample.
- Ran `scripts/train_rapfi_teacher_policy_margin.py` with `--dry-run`.
- Confirmed trainer can load the 44 margin samples and anchor snapshots.
- Confirmed no training was executed.
- Confirmed no checkpoint was saved.
- No C export.
- No public benchmark.
- No promotion.

## Inputs

- dry-run dataset: `analysis/integration_eval/teacher_divergence_round2_trainable_dryrun_dataset_legacy_normalized.json`
- trainer-ready dataset: `analysis/integration_eval/teacher_divergence_round2_trainable_trainer_ready_dataset.json`
- trainer: `scripts/train_rapfi_teacher_policy_margin.py`
- anchor snapshots: `analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json`
- init checkpoint: `checkpoints/15x15_current_best.pt`
- reference checkpoint: `checkpoints/15x15_current_best.pt`

## Output

- trainer-ready dataset: `analysis/integration_eval/teacher_divergence_round2_trainable_trainer_ready_dataset.json`
- adapter report: `analysis/integration_eval/teacher_divergence_round2_trainer_ready_dataset_report.md`
- dry-run log: `analysis/integration_eval/teacher_divergence_round2_trainer_dryrun_preflight.log`

## Decision

Trainer dry-run preflight passed if the log contains:

- `margin samples: 44`
- `dry-run only; not training or saving`

No training.

No checkpoint.

No C export.

No public benchmark.

No promotion.
