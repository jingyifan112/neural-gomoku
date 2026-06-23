# Teacher-divergence run1 fixed-probe / heldout local comparison plan

## Branch

`exp/15x15-teacher-divergence-run1-fixed-probe-heldout-plan`

## Scope

- Plans the next local comparison stage after run1 epsilon review.
- Does not train.
- Does not read or write checkpoints.
- Does not overwrite `checkpoints/15x15_current_best.pt`.
- Does not C export.
- Does not run public benchmark.
- Does not promote.

## Plan decision

`FIXED_PROBE_HELDOUT_PLAN_BLOCKED`

## Upstream decisions

| source | decision |
|---|---|
| wrapper run1 | `EXECUTION_PASS_KEEP_ISOLATED_CANDIDATE` |
| promotion readiness | `NOT_PROMOTION_READY__READY_FOR_EPSILON_GATED_LOCAL_REVIEW` |
| epsilon review | `EPSILON_REVIEW_FAILS__REPAIR_GATE_OR_OBJECTIVE` |

## Key carried-forward evidence

| metric | value |
|---|---:|
| trainable gap improved rows | 44/44 |
| trainable mean gap delta | 0.0086329092 |
| trainable rank regressions | 0 |
| protected rank regressions | 0 |
| anchor top1 changes | 0 |
| anchor max KL | 0.0000060956 |
| epsilon warning rows | 5 |
| epsilon hard concern rows | 4 |
| total raw probability regressions | 19 |
| max probability loss | 0.000997871200 |

## Blockers

- epsilon review does not allow fixed-probe/heldout: EPSILON_REVIEW_FAILS__REPAIR_GATE_OR_OBJECTIVE
- epsilon hard concerns present: 4

## Warnings to carry into next stage

- epsilon warning rows present: 5
- raw probability regressions remain: 19
- protected_top10 raw probability regressions: 11
- tail_rank_gt50 raw probability regressions: 8

## Required next comparison design

The next branch should implement local candidate-vs-current_best evaluation only. It should not export C and should not run a public benchmark.

Required comparisons:

1. Existing fixed probes / tactical probes available in the repository.
2. Heldout retention/protected rows available from the normalized manifest and prior guard outputs.
3. Anchor drift rows already used by the wrapper.
4. Epsilon-aware probability regression classification carried forward from run1.

## Proposed next-stage hard gates

| gate | threshold |
|---|---|
| fixed-probe tactical regression | 0 unreviewed regressions |
| protected_top10 rank regression | 0 |
| anchor top1 changed rows | 0, unless explicitly reviewed |
| heldout severe probability loss | 0 hard_concern rows |
| current_best overwrite | forbidden |
| C export | forbidden in this stage |
| public benchmark | forbidden in this stage |
| promotion | forbidden in this stage |

## Planned outputs for next branch

- fixed_probe_csv: `analysis/integration_eval/teacher_divergence_run1_fixed_probe_candidate_vs_current_best.csv`
- fixed_probe_report: `analysis/integration_eval/teacher_divergence_run1_fixed_probe_candidate_vs_current_best.md`
- heldout_csv: `analysis/integration_eval/teacher_divergence_run1_heldout_candidate_vs_current_best.csv`
- heldout_report: `analysis/integration_eval/teacher_divergence_run1_heldout_candidate_vs_current_best.md`
- decision_csv: `analysis/integration_eval/teacher_divergence_run1_fixed_probe_heldout_decision.csv`
- decision_report: `analysis/integration_eval/teacher_divergence_run1_fixed_probe_heldout_decision.md`

## Summary table

| metric | value | status | notes |
|---|---:|---|---|
| plan_decision | FIXED_PROBE_HELDOUT_PLAN_BLOCKED | INFO | Plan only; not execution. |
| blocker_count | 2 | FAIL | epsilon review does not allow fixed-probe/heldout: EPSILON_REVIEW_FAILS__REPAIR_GATE_OR_OBJECTIVE; epsilon hard concerns present: 4 |
| warning_count | 4 | WARN | epsilon warning rows present: 5; raw probability regressions remain: 19; protected_top10 raw probability regressions: 11; tail_rank_gt50 raw probability regressions: 8 |
| epsilon_decision | EPSILON_REVIEW_FAILS__REPAIR_GATE_OR_OBJECTIVE | FAIL |  |
| promotion_readiness_decision | NOT_PROMOTION_READY__READY_FOR_EPSILON_GATED_LOCAL_REVIEW | INFO |  |
| wrapper_decision | EXECUTION_PASS_KEEP_ISOLATED_CANDIDATE | PASS |  |
| candidate_checkpoint_exists_locally | 1 | PASS | Local artifact only; do not add to git. |
| current_best_exists | 1 | PASS |  |
| hard_concern_rows | 4 | FAIL |  |
| epsilon_warning_rows | 5 | WARN |  |
| total_prob_regressions | 19 | WARN |  |
| protected_top10_prob_regressions | 11 | WARN |  |
| tail_rank_gt50_prob_regressions | 8 | WARN |  |
| total_rank_regressions | 0 | PASS |  |
| max_probability_loss | 0.000997871200 | INFO |  |
| trainable_gap_improved_rows | 44 | PASS |  |
| trainable_mean_gap_delta | 0.0086329092 | PASS |  |
| trainable_rank_regressed_rows | 0 | PASS |  |
| protected_rank_regressed_rows | 0 | PASS |  |
| anchor_top1_changed_rows | 0 | PASS |  |
| anchor_max_kl | 0.0000060956 | PASS |  |

## Recommendation

Do not proceed to fixed-probe/heldout comparison until blockers are resolved.

## Final guardrails

- No current_best overwrite.
- No C export.
- No public benchmark.
- No promotion.
- Do not add local checkpoint artifacts to git.
