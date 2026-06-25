# Teacher-divergence expansion targets

## Scope

- Expansion target planning only.
- No training.
- No checkpoint read or write.
- No C export, no public benchmark, no promotion.

## Why expansion is required

The conservative 4-train-row no-save probe improved the train group but still failed protected/tail guards.

Leave-one-train-candidate-out review showed that removing any single train candidate did not produce a guard-safe subset.

Therefore the current 25-row corpus is insufficient for stable b4c96 capacity work. The next safe step is targeted data expansion, not more training.

## Current findings

- selection_base_rows: `25`
- strict_train_candidate_rows: `4`
- materialized_train_rows: `4`
- materialized_protected_eval_rows: `15`
- materialized_tail_eval_rows: `3`
- materialized_quarantine_rows: `3`
- row_level_decision: `LEAVE_ONE_OUT_NO_GUARD_SAFE_SUBSET`
- tail_failure: `True`
- protected_failure: `True`
- train_improved: `True`

## Expansion targets

| priority | target_area | minimum_new_rows | do_not_use_as |
|---|---|---:|---|
| P0 | tail_guard_expansion | 12 | ordinary_train_rows |
| P0 | protected_guard_expansion | 12 | ordinary_train_rows |
| P1 | train_candidate_expansion | 20 | checkpoint_producing_train_until_guard_safe |
| P1 | quarantine_review | 0 | ordinary_train_rows |
| P2 | family_diversity | 20 | unbalanced_single_family_expansion |

## Detailed rules

### P0 tail_guard_expansion

- current evidence: tail_eval_rank_gt50 failed in full conservative probe and every leave-one-out variant
- minimum new rows: 12
- selection rule: Collect rank>50 or near-tail teacher-divergence rows, especially cases where training tends to lose top10 or create rank>50 regressions.
- acceptance rule: Rows must remain held out as tail_guard until a no-save probe shows rank_gt50_delta <= 0 and mean_rank_delta <= 0.
- do not use as: `ordinary_train_rows`

### P0 protected_guard_expansion

- current evidence: protected_eval_top10 lost top5 coverage or target probability across probes
- minimum new rows: 12
- selection rule: Collect top3/top5/top10 teacher rows where target is already relatively good and must not regress.
- acceptance rule: Rows must remain held out as protected_guard until top5_delta >= 0, top10_delta >= 0, and no teacher-beats regression appears.
- do not use as: `ordinary_train_rows`

### P1 train_candidate_expansion

- current evidence: Only 4 strict train candidates survived selection audit, and no leave-one-out subset became guard-safe.
- minimum new rows: 20
- selection rule: Collect rank 11-50 directionally useful teacher-divergence rows with no severe/core regression tags and no overlap with protected/tail instability.
- acceptance rule: Candidate rows may be trainable only after no-save checks show train improvement without protected/tail guard failure.
- do not use as: `checkpoint_producing_train_until_guard_safe`

### P1 quarantine_review

- current evidence: 3 prior train rows became quarantine: legacy_g2_m11, legacy_g2_m21, legacy_g5_m14
- minimum new rows: 0
- selection rule: Do not expand from severe/core-regression families unless explicitly reviewed as negative examples.
- acceptance rule: Quarantine rows remain excluded from ordinary training.
- do not use as: `ordinary_train_rows`

### P2 family_diversity

- current evidence: Current corpus is small and concentrated; no 25-row subset was guard-safe for b4c96.
- minimum new rows: 20
- selection rule: Prefer more games/families rather than multiple near-duplicates from the same local pattern.
- acceptance rule: Expansion manifest should include game/family balancing and duplicate-family flags.
- do not use as: `unbalanced_single_family_expansion`

## Decision

`TEACHER_DIVERGENCE_EXPANSION_TARGETS_READY`

Recommended next branch:

`exp/15x15-teacher-divergence-expansion-source-audit-next`

The next branch should audit available source artifacts for rows matching these targets. It should not train.
