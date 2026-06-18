# Policy-only teacher-divergence repair probe training closeout

## Branch

exp/15x15-policy-only-teacher-divergence-repair-train

## Training run

- Trainer: scripts/train_rapfi_teacher_policy_margin.py
- Dataset: analysis/public_benchmark_eval/rapfi_teacher_policy_margin_dataset_corpus8_selected.json
- Init/reference checkpoint: checkpoints/15x15_current_best.pt
- Output checkpoint: checkpoints/15x15_policy_only_teacher_divergence_repair_probe.pt
- Objective: policy-head-only pairwise margin, with --ce-weight 0
- Epochs: 40

## Local probe result

- Cases parsed: 25
- Target probability improved: 24 / 25
- Suppress probability decreased: 24 / 25
- Target rank improved: 8 / 25
- Target rank regressed: 0 / 25
- Target-vs-suppress logit gap improved: 24 / 25
- Mean delta gap: +0.148287
- Non-improved case: legacy_g6_m19

## Interpretation

The probe moved the direct supervised pairwise margin in the intended direction on almost all training rows. However, the absolute margin remains negative for every row, rank improvement is limited, and this was trained directly on the 25 supervised priority rows.

Conclusion: treat this as a local signal probe only. It is not a candidate for C export, public benchmark, or promotion.

## Next recommendation

Do not promote this checkpoint. The next useful experiment should either strengthen the policy-only objective/gate design or collect broader validated teacher-divergence rows before considering export or benchmark evaluation.
