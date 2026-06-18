# Policy-only objective and gate next design

## Branch

`exp/15x15-policy-only-objective-gate-design`

## Inputs

- Previous branch: `exp/15x15-policy-only-teacher-divergence-repair-train`
- Metrics source: `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_train_metrics.csv`
- Previous objective: policy-head-only pairwise margin, `--ce-weight 0`, margin `1.0`, lr `5e-6`, epochs `40`.

## Previous probe summary

| metric | value |
|---|---:|
| cases | 25 |
| target probability improved | 24 / 25 |
| target-vs-suppress gap improved | 24 / 25 |
| target rank improved | 8 / 25 |
| target rank regressed | 0 / 25 |
| after gaps still negative | 25 / 25 |
| mean delta gap | 0.148287 |
| mean after gap | -4.805841 |
| median after gap | -5.146485 |
| after target rank > 10 | 10 |
| after target rank > 50 | 3 |

## Diagnosis

The previous probe is a valid local signal probe, but it is too weak for promotion. It moved probability and pairwise gap in the intended direction on most training rows, but all final teacher-vs-suppress gaps remain negative and only 8 of 25 target ranks improved.

The next experiment should therefore strengthen the policy-only objective and gate before any new export or benchmark work.

## Hard cases: worst final gaps

| case_id | after_gap | delta_gap | before_rank | after_rank |
|---|---:|---:|---:|---:|
| legacy_g2_m21 | -8.571234 | 0.171221 | 47 | 44 |
| legacy_g1_m8 | -7.708438 | 0.180011 | 102 | 101 |
| legacy_g4_m13 | -7.439025 | 0.162790 | 21 | 19 |
| legacy_g5_m30 | -7.385575 | 0.122039 | 73 | 73 |
| legacy_g2_m11 | -6.990972 | 0.179782 | 12 | 12 |
| legacy_g5_m12 | -6.934880 | 0.159864 | 69 | 66 |
| legacy_g4_m23 | -5.500234 | 0.169173 | 23 | 21 |
| legacy_g3_m24 | -5.486225 | 0.215282 | 7 | 7 |
| legacy_g6_m5 | -5.309093 | 0.152413 | 6 | 6 |
| legacy_g5_m14 | -5.304506 | 0.188320 | 17 | 15 |

## Hard cases: high final target rank

| case_id | after_rank | before_rank | after_gap | delta_gap |
|---|---:|---:|---:|---:|
| legacy_g1_m8 | 101 | 102 | -7.708438 | 0.180011 |
| legacy_g5_m30 | 73 | 73 | -7.385575 | 0.122039 |
| legacy_g5_m12 | 66 | 69 | -6.934880 | 0.159864 |
| legacy_g2_m21 | 44 | 47 | -8.571234 | 0.171221 |
| legacy_g4_m23 | 21 | 23 | -5.500234 | 0.169173 |
| legacy_g4_m13 | 19 | 21 | -7.439025 | 0.162790 |
| legacy_g5_m28 | 17 | 17 | -4.519498 | 0.131438 |
| legacy_g5_m14 | 15 | 17 | -5.304506 | 0.188320 |
| legacy_g6_m17 | 15 | 15 | -5.140766 | 0.118665 |
| legacy_g2_m11 | 12 | 12 | -6.990972 | 0.179782 |

## Non-improved rows

| case_id | delta_target_prob | delta_gap | after_rank | after_gap |
|---|---:|---:|---:|---:|
| legacy_g6_m19 | -0.00045912 | -0.032483 | 7 | -3.066855 |

## Next objective candidates

### O1: stronger weighted pairwise margin

- Keep policy-head-only training.
- Keep `--ce-weight 0`.
- Increase one controlled axis at a time: learning rate, epochs, or hard-row weighting.
- Reweight by policy difficulty, such as gap deficit or target rank, not by treating Rapfi numeric score as a value label.

### O2: multi-suppress pairwise margin

- Current dataset suppresses only the current-best direct move.
- A stronger dataset can rank the teacher move above several high-probability model alternatives.
- This targets rank improvement more directly than a single target-vs-current pair.

### O3: top-k visibility gate

- Add a gate requiring teacher targets to move into top-k bands, not merely improve by a small logit amount.
- Track rows with target rank greater than 10 and greater than 50 as hard-tail diagnostics.

### O4: broader validated teacher-divergence collection

- Collect more rows only after the stronger gate is defined.
- Required fields should include board, side/current_player, teacher move, suppress/model move, legality, source trace, split, and validation status.
- Do not mix held-out retention rows into training.

## Proposed next gate

A future stronger policy-only probe should satisfy:

1. gap improves on at least 24 / 25 rows;
2. mean delta gap materially exceeds the prior +0.148287 baseline;
3. target rank improves on more than 8 / 25 rows;
4. target rank regression remains 0 / 25;
5. high-rank tail shrinks, especially target rank > 50;
6. some teacher targets become top-3 or top-5;
7. anchor KL remains small;
8. no value regression, no C export, no public benchmark, no promotion.

## Recommendation

Do not promote the local checkpoint. The next step should be an auditable design/implementation of either hard-row weighted pairwise margin or multi-suppress pairwise margin. Keep it local and policy-only until the strengthened gate passes.

## Status

Design only. No training, no checkpoint, no C export, no public benchmark, no promotion.
