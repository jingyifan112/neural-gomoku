# Policy-only teacher-divergence repair probe setup closeout

## Branch

exp/15x15-policy-only-teacher-divergence-repair-probe

## Base

e45e55f Add teacher divergence signal audit

## Objective

Set up a small policy-only teacher-divergence repair probe using the 25 priority Rapfi teacher rows identified by the signal audit.

## Scope constraints

Included: script audit, probe design, dataset/trainer schema validation, and dry-run validation.

Excluded: value regression, value-head ranking, C export, public benchmark, and promotion.

## Main decision

No new dataset converter is needed for the first probe.

The existing dataset already contains the intended 25 pairwise margin samples and matches scripts/train_rapfi_teacher_policy_margin.py.

Dataset: analysis/public_benchmark_eval/rapfi_teacher_policy_margin_dataset_corpus8_selected.json

Required trainer fields confirmed present: board, current_player, target_rc, suppress_rc, sample_weight.

## Training script decision

Use scripts/train_rapfi_teacher_policy_margin.py with policy-head-only training, pairwise margin objective, current-best checkpoint as init/reference, --ce-weight 0, and small anchor KL only for retention stabilization.

Do not use the regression-gated, mixed-CE, or value-ranking scripts for this first probe.

## Dry-run validation

Dry-run loaded 25 margin samples, 32 anchor samples, and checkpoints/15x15_current_best.pt as both init and reference.

Dry-run printed BEFORE diagnostics and exited before training or saving.

Confirmed checkpoints/15x15_policy_only_teacher_divergence_repair_probe.pt was not written.

## Next possible step

A future step may run the actual policy-only probe training using the same command without --dry-run, still with --ce-weight 0.

That future step should remain a probe only. It should not export C weights, run public benchmark, or promote the checkpoint.
