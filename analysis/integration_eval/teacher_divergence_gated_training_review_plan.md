# Teacher-divergence gated training review plan

## Branch

`exp/15x15-teacher-divergence-gated-training-review-plan`

## Scope

- Review-only plan for a later gated training dry run.
- Based on tiny probe closeout and posttrain guard audit.
- Does not train.
- Does not read or write checkpoints.
- Does not overwrite `checkpoints/15x15_current_best.pt`.
- Does not C export.
- Does not run public benchmark.
- Does not promote.

## Source decision

`PASS_TO_GATED_TRAINING_REVIEW_WITH_WARNINGS`

## Plan decision

`READY_TO_DESIGN_GATED_TRAINING_DRYRUN`

## Why a gated review is allowed

| signal | value | interpretation |
|---|---:|---|
| hard failures | 0 | must be zero |
| warnings | 2 | requires explicit gates |
| trainable gap improved rows | 44/44 | positive trainable signal |
| trainable mean gap delta | 0.0025900711 | positive but tiny effect size |
| trainable rank regressions | 0 | must stay zero |
| anchor top1 changes | 0 | must stay zero |
| anchor max KL | 0.0000005536 | very small drift |

## Warning context

| warning source | rows | rank regressions | raw probability regressions | max probability loss |
|---|---:|---:|---:|---:|
| protected_top10 | 23 | 0 | 11 | -0.0002995431 |
| tail_rank_gt50 | 66 | 0 | 8 | -0.0000002012 |

The tiny probe produced raw probability regressions in protected/tail buckets but no rank regression and no anchor top1 change. Therefore the next step may be a gated training dry-run design, not promotion.

## Required next-run architecture

A later gated run must use a wrapper with save-on-pass behavior:

1. Train from `checkpoints/15x15_current_best.pt`, not from a promoted checkpoint.
2. Write only to an isolated candidate path, for example `checkpoints/15x15_teacher_divergence_round2_policy_margin_gated_review.pt`.
3. Run trainable, protected/tail, and anchor guards immediately after training.
4. Keep candidate checkpoint only if all hard gates pass.
5. Quarantine or delete the candidate checkpoint if hard gates fail.
6. Never overwrite `checkpoints/15x15_current_best.pt` in this workflow.

## Proposed hard gates for the later dry run

| gate | threshold | failure action |
|---|---:|---|
| trainable rows evaluated | 44 | fail if not exact |
| trainable gap improved rows | >= 40 | fail run |
| trainable mean gap delta | > 0 | fail run |
| trainable target rank regressions | 0 | fail run |
| protected_top10 target rank regressions | 0 | fail run |
| anchor top1 changed rows | 0 | fail run |
| anchor max KL ref->candidate | <= 0.005 | fail if above hard threshold |

## Proposed warning gates

| warning gate | threshold | action |
|---|---:|---|
| protected_top10 raw target probability regressions | > 0 | report warning; require epsilon-aware review |
| tail_rank_gt50 raw target probability regressions | > 0 | report warning; require epsilon-aware review |
| tail_rank_gt50 target rank regressions | > 0 | block uncontrolled scaling; inspect before continuing |
| anchor max KL ref->candidate | > 0.001 and <= 0.005 | warning only |

## Candidate hyperparameter review, not execution

The tiny run used a very conservative 3-epoch probe and showed positive but small gap movement. A later dry-run may review one conservative configuration first:

| parameter | candidate review value | rationale |
|---|---:|---|
| epochs | 10 | modestly larger than tiny run |
| lr | 1e-6 | same as tiny run to limit protected drift |
| margin | 1.0 | same objective scale |
| anchor_kl_weight | 0.05 | preserve anchor behavior |
| ce_weight | 0.05 | preserve target CE signal |
| weight_decay | 1e-5 | same as tiny run |
| seed | fixed, e.g. 31 | reproducibility |

This is only a review candidate. It is not approved for promotion or public benchmarking.

## Required outputs for the next dry-run branch

- gated train log
- trainable guard CSV
- protected/tail guard CSV
- anchor drift guard CSV
- wrapper decision JSON/CSV
- closeout report
- isolated local checkpoint if and only if hard gates pass

## Summary table

| item | value | gate | rationale |
|---|---:|---|---|
| source_closeout_decision | PASS_TO_GATED_TRAINING_REVIEW_WITH_WARNINGS | INFO | Decision from tiny probe guard closeout. |
| plan_decision | READY_TO_DESIGN_GATED_TRAINING_DRYRUN | INFO | This plan is review-only and does not start training. |
| hard_failure_count | 0 | PASS | Must be zero before any larger run. |
| warning_count | 2 | WARN | Warnings require explicit guard handling. |
| trainable_rows | 44 | PASS | Expected 44 round2 trainable rows. |
| trainable_gap_improved_rows | 44 | PASS | Tiny probe improved all trainable gaps. |
| trainable_mean_gap_delta | 0.0025900711 | PASS | Mean gap delta must remain positive. |
| trainable_min_gap_delta | 0.0010976791 | INFO | Tiny probe min gap delta; useful for calibrating next gate. |
| trainable_target_rank_regressed_rows | 0 | PASS | No trainable target rank regression allowed. |
| protected_top10_rows | 23 | INFO | Protected bucket must be guarded explicitly. |
| protected_top10_rank_regressed_rows | 0 | PASS | Hard fail for any protected rank regression. |
| protected_top10_prob_regressed_rows | 11 | WARN | Raw prob regressions observed; next run needs epsilon-aware guard. |
| protected_top10_max_prob_loss | -0.0002995431 | WARN | Use as warning context, not promotion evidence. |
| tail_rank_gt50_rows | 66 | INFO | Tail bucket is not promotion evidence but should be monitored. |
| tail_rank_gt50_rank_regressed_rows | 0 | PASS | Tail rank regression should block uncontrolled scaling. |
| tail_rank_gt50_prob_regressed_rows | 8 | WARN | Raw prob regressions observed; next run needs epsilon-aware guard. |
| tail_rank_gt50_max_prob_loss | -0.0000002012 | WARN | Use as warning context. |
| anchor_rows | 32 | PASS | Expected corpus8 anchor snapshots. |
| anchor_top1_changed_rows | 0 | PASS | Hard fail for anchor top1 changes. |
| anchor_mean_kl | 0.0000001493 | PASS | Tiny drift was very small. |
| anchor_max_kl | 0.0000005536 | PASS | Use KL as drift gate. |

## Bucket counts from guard audit

| bucket/top1 item | count |
|---|---:|
| bucket:tail_rank_gt50 | 66 |
| bucket:protected_top10 | 23 |
| anchor_top1_changed:0 | 32 |

## Final guardrails

- No current_best overwrite.
- No C export.
- No public benchmark.
- No promotion.
- Do not add local checkpoint artifacts to git.
