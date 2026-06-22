# Teacher-divergence data expansion design

## Branch

exp/15x15-teacher-divergence-data-expansion-design

## Scope

Design only.

No training, checkpoint save, C export, public benchmark, or promotion is run on this branch.

## Motivation

The policy-only rank/top-k chain is closed.

The 25-row teacher-divergence dataset was useful for probing objective behavior, but it is too small and unstable for policy-head-only repair.

Observed failures:

- single-suppress margin training improved local gaps but left all gaps negative;
- multi-suppress dry-run exposed stronger suppressors but did not justify immediate training;
- rank/top-k full-dataset training failed the candidate gate;
- CE-only and weak-suppress no-save ablations were unstable;
- protected training on rank 11-50 rows improved the train group slightly but damaged protected top10 and tail rows.

Therefore the next useful step is not another objective tweak. The next step is broader, better-bucketed teacher-divergence data construction.

## Design goals

Build a larger teacher-divergence corpus before any new training attempt.

The corpus should support:

1. rank/top-k repair evaluation;
2. protected-row retention checks;
3. tail-row diagnostics;
4. suppress-set construction;
5. separation of training rows from evaluation/protection rows;
6. reproducible source tracing from match logs, board snapshots, and Rapfi teacher queries.

## Required buckets

Every candidate row should be assigned to one primary bucket using baseline current_best policy rank of the teacher target.

### protected_top10

Definition:

- teacher target rank <= 10 under current_best.

Purpose:

- evaluation/protection only at first;
- should not be main training rows;
- must detect target-probability collapse and rank regression.

Required fields:

- baseline target rank;
- baseline target probability;
- baseline direct move;
- teacher target move;
- current_best top-k list;
- suppress candidates;
- teacher-vs-suppress gaps.

### trainable_rank_11_50

Definition:

- 11 <= teacher target rank <= 50 under current_best.

Purpose:

- main initial training candidate bucket;
- most plausible bucket for top-k movement;
- should be large enough before training.

Required fields:

- same fields as protected_top10;
- sample weight;
- hardness score;
- source game and ply;
- teacher query metadata.

### tail_rank_gt50

Definition:

- teacher target rank > 50 under current_best.

Purpose:

- diagnostic-only at first;
- do not mix with main training rows;
- likely requires different objective or more data.

Required fields:

- same fields as trainable rows;
- extra notes explaining whether the teacher target is tactically visible, value-disfavored, or low-policy-visibility.

## Minimum sample targets before training

Do not train again on 25 rows.

Suggested minimums before another policy objective probe:

| bucket | minimum rows | initial use |
|---|---:|---|
| protected_top10 | 50 | eval/protection |
| trainable_rank_11_50 | 100 | training candidate |
| tail_rank_gt50 | 50 | diagnostic-only |
| anchor_retention | 100 | eval/protection |

If these minimums cannot be met, continue data collection instead of training.

## Source candidates

Potential sources to audit and unify:

1. existing corpus8 selected snapshots;
2. baseline mcts16 vs Rapfi depth1 losses;
3. candidate failure snapshots from prior branches;
4. public benchmark fixed openings where current_best differs from Rapfi;
5. near-loss windows from games where current_best collapses tactically;
6. rows with validated Rapfi teacher moves and numeric score gaps;
7. rows where current_best direct move differs from Rapfi best move.

## Required schema

Every row should include:

- case_id
- source
- game_number
- move_count
- board_size
- win_length
- board
- current_player
- side_to_move
- target_rc
- target_xy
- teacher_move
- teacher_eval_kind
- teacher_eval_before
- numeric_gap_available
- numeric_gap_value
- current_best_direct_rc
- current_best_direct_move
- before_target_rank
- before_target_prob
- before_primary_gap
- before_worst_suppress_gap
- suppress_rcs
- suppress_candidates
- bucket
- bucket_reason
- sample_weight
- hardness_weight
- effective_sample_weight
- validation_notes

## Validation rules

A row is valid only if:

1. board shape is 15x15;
2. current_player is either 1 or -1;
3. target_rc is legal;
4. all suppress_rcs are legal;
5. suppress_rcs exclude target_rc;
6. suppress_rcs have no duplicates;
7. before_target_rank is positive;
8. before_target_prob is finite;
9. all gap fields are finite if marked numeric;
10. source trace is available.

Invalid rows should be written to a skipped list with a reason.

## Suppress candidate rule

For each valid row, construct suppress candidates from:

1. current_best direct move;
2. current_best top policy moves excluding target;
3. optionally MCTS-selected move if available;
4. optionally prior known failure move if different.

Recommended suppress count:

- default: 5;
- minimum: 3;
- maximum: 8.

The primary suppress should remain current_best direct move when available.

## Weighting policy

Do not reuse the previous effective weights blindly.

The protected weighting audit showed that high-weight and tail rows can destabilize small probes.

Recommended initial weighting:

- cap effective weight at 3.0;
- protected_top10 rows are eval-only, weight 0 in training;
- tail_rank_gt50 rows are eval-only, weight 0 in training;
- trainable_rank_11_50 rows may use capped weight;
- keep raw sample_weight and hardness_weight for audit, but do not make them decisive before enough data exists.

## Evaluation gate for future training

Before saving any future checkpoint, require a no-save probe to report all buckets separately.

Minimum future gate:

### trainable_rank_11_50

- top10 count improves;
- mean rank improves;
- mean target probability does not decrease;
- mean worst suppress gap improves.

### protected_top10

- no top10 loss;
- no rank_gt50 increase;
- target probability does not collapse;
- teacher_beats_worst does not decrease.

### tail_rank_gt50

- no rank_gt50 increase;
- mean rank does not worsen sharply;
- diagnostic report required before training on tail rows.

### anchor_retention

- no critical tactical anchor regression;
- no broad top-k anchor collapse.

## Recommended implementation sequence

### Step 1: source inventory audit

New branch:

exp/15x15-teacher-divergence-source-inventory-audit

Goal:

- inventory all available teacher-divergence candidate sources;
- do not build final training data yet;
- count rows by source, board availability, teacher label availability, rank bucket availability, and schema completeness.

Suggested output:

- analysis/integration_eval/teacher_divergence_source_inventory_audit.csv
- analysis/integration_eval/teacher_divergence_source_inventory_audit.md

### Step 2: unified candidate manifest

New branch:

exp/15x15-teacher-divergence-expanded-manifest

Goal:

- create a unified manifest of candidate rows;
- deduplicate by board + side_to_move + target;
- label rows as usable, skipped, or needs_requery.

### Step 3: Rapfi teacher requery gap fill

New branch:

exp/15x15-teacher-divergence-rapfi-requery-gapfill

Goal:

- requery missing teacher moves and numeric gaps;
- keep all raw logs;
- do not train.

### Step 4: expanded multi-suppress dataset

New branch:

exp/15x15-teacher-divergence-expanded-multisuppress-dataset

Goal:

- build expanded multi-suppress dataset;
- include bucketed train/protected/tail splits;
- run schema validation and baseline diagnostics;
- still do not train.

### Step 5: training only after data gate

Training should only resume if the expanded dataset meets minimum bucket sizes and passes schema validation.

## Decision

Do not continue training on the 25-row policy-only rank/top-k dataset.

Do not save checkpoints.

Do not export.

Do not public benchmark.

Do not promote.

Proceed next with source inventory audit.
