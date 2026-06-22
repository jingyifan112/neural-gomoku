# Teacher-divergence expanded manifest design

## Branch

exp/15x15-teacher-divergence-expanded-manifest-design

## Scope

Design only.

No training, checkpoint save, C export, public benchmark, or promotion is run on this branch.

## Starting point

The source inventory audit found:

- tracked candidate files: 603
- parsed JSON/CSV files with rows: 110
- total parsed JSON/CSV rows: 3438

The inventory also showed that only a small subset of tracked files have enough schema coverage to serve as direct teacher-divergence manifest inputs.

The next step should not merge all parsed rows. It should define a controlled expanded manifest design with source classes, deduplication keys, join keys, and missing-field statuses.

## Source inventory interpretation

### Fully covered canonical source

Primary canonical source:

- analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json

Coverage:

- rows: 25
- board: yes
- side/current player: yes
- target: yes
- baseline rank: yes
- baseline probability: yes
- suppress candidates: yes
- teacher evaluation: yes
- source trace: yes
- bucket: yes

Role:

- canonical seed source;
- should be included first;
- should define the target schema.

### Derived protected split source

Derived source:

- analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_protected_train_11_50_weightcap3.json

Coverage:

- rows: 25
- full schema coverage

Role:

- should not be counted as new data;
- use only as a split/weighting design reference;
- do not include as independent rows in expanded manifest.

Reason:

- it is derived from the canonical 25-row multi-suppress dataset;
- including it directly would duplicate rows.

### Margin source needing rank/prob refresh

Source:

- analysis/public_benchmark_eval/rapfi_teacher_policy_margin_dataset_corpus8_selected.json

Coverage:

- rows: 25
- board: yes
- side/current player: yes
- target: yes
- suppress: yes
- teacher evaluation: yes
- source trace: yes
- bucket: yes
- rank/prob: missing in inventory

Role:

- useful source, but likely overlaps canonical multi-suppress rows;
- include only for cross-checking and fallback;
- do not duplicate rows already present in canonical source.

Required action:

- deduplicate against canonical source;
- if unique rows exist, run current_best policy probe to fill target rank/prob and suppress metrics.

### Retention-family datasets

Candidate sources:

- analysis/integration_eval/teacher_divergence_retention_dataset.json
- analysis/integration_eval/teacher_divergence_retention_clean_v2_dataset.json
- analysis/integration_eval/teacher_divergence_retention_safety_v3_dataset.json
- analysis/integration_eval/teacher_divergence_retention_manifest.csv
- analysis/integration_eval/teacher_divergence_retention_clean_v2_manifest.csv

Coverage:

- board/side/target/source trace/bucket coverage is generally useful;
- rank/prob coverage is mostly missing;
- suppress coverage is mostly missing;
- teacher_eval coverage exists more in manifests than in datasets.

Role:

- best candidate pool for expansion;
- should feed an expanded candidate manifest;
- not immediately trainable until rank/prob/suppress/current_best diagnostics are filled.

Required action:

- normalize row schema;
- deduplicate across retention versions;
- mark rows as needs_current_best_probe;
- mark rows as needs_suppress_build;
- mark rows as needs_rapfi_requery if teacher_eval is missing or stale.

### Corpus8 candidate CSV and snapshots

Candidate source:

- analysis/public_benchmark_eval/rapfi_teacher_policy_candidates_corpus8_selected.csv

Potential join source:

- analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json

Coverage:

- candidate CSV has side/target/teacher_eval/source_trace/bucket;
- board is missing from CSV;
- board may be joinable from snapshot source by game_number and move_count.

Role:

- useful if join keys are reliable;
- should be included in manifest design as a join candidate, not immediately as final rows.

Required action:

- define join key;
- verify one-to-one join with board snapshots;
- then probe current_best rank/prob and suppress candidates.

### Rank/probe evaluation CSVs

Examples:

- analysis/integration_eval/teacher_divergence_policy_probe_eval.csv
- analysis/integration_eval/teacher_divergence_policy_anchor_probe_eval.csv
- analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_gated_eval.csv
- analysis/integration_eval/teacher_divergence_policy_regression_gated_probe_eval.csv

Coverage:

- rank/prob fields exist;
- side and bucket often exist;
- board/target/source trace may be incomplete.

Role:

- evaluation evidence only;
- should not be used as primary row source unless rows can be linked back to board and target.

Required action:

- use for cross-reference, not as primary manifest source.

## Manifest row statuses

Every candidate row should receive one of these statuses:

### ready_full_schema

Required:

- board
- current_player or side_to_move
- target_rc
- teacher move
- source trace
- baseline target rank
- baseline target probability
- suppress candidates
- teacher evaluation metadata
- bucket assignment

Use:

- can be included in diagnostics immediately;
- may be eligible for future training/eval split.

### needs_current_best_probe

Required missing fields:

- baseline target rank;
- baseline target probability;
- current_best direct move;
- current_best top policy moves.

Use:

- run policy probe before training or dataset build.

### needs_suppress_build

Required missing fields:

- suppress_rcs;
- suppress_candidates;
- primary suppress move;
- worst suppress gap.

Use:

- run suppress builder after current_best probe.

### needs_rapfi_requery

Required missing fields:

- teacher move;
- teacher_eval_before;
- numeric_gap_value;
- reliable teacher_eval_kind.

Use:

- run Rapfi requery/gapfill.

### needs_board_join

Required missing fields:

- board;
- current_player;
- side_to_move.

Use:

- join with board snapshot source before any policy probe.

### duplicate

Definition:

- row duplicates an already selected source row under dedup key.

Use:

- exclude from final manifest;
- keep duplicate_of pointer.

### skipped_invalid

Definition:

- illegal target;
- bad board shape;
- missing unrecoverable fields;
- inconsistent side;
- stale or ambiguous source trace.

Use:

- exclude from manifest build;
- preserve skip reason.

## Deduplication design

Primary dedup key:

- board_hash
- current_player
- target_rc

Secondary source trace key:

- source
- game_number
- move_count
- target_rc

Board hash:

- compute from canonical 15x15 board integer grid;
- include current_player separately;
- do not rely only on case_id because case_id formats differ across sources.

Duplicate handling:

1. Prefer ready_full_schema over incomplete rows.
2. Prefer canonical multi-suppress source over derived protected split.
3. Prefer rows with teacher_eval and numeric_gap over rows without.
4. Prefer rows with suppress_candidates over rows without.
5. Keep all duplicate source references in duplicate_sources.

## Bucket assignment

Assign bucket by current_best baseline target rank after current_best probe.

Buckets:

### protected_top10

Rule:

- before_target_rank <= 10

Initial use:

- eval/protection only.

### trainable_rank_11_50

Rule:

- 11 <= before_target_rank <= 50

Initial use:

- candidate training bucket once enough rows exist.

### tail_rank_gt50

Rule:

- before_target_rank > 50

Initial use:

- diagnostic-only.

### unknown_rank

Rule:

- rank missing or current_best probe not yet run.

Initial use:

- not trainable.

## Minimum manifest fields

The expanded manifest should write one CSV row per candidate with:

- manifest_id
- status
- bucket
- source_priority
- primary_source_path
- duplicate_of
- duplicate_sources
- case_id
- source
- game_number
- move_count
- board_hash
- board_available
- side_available
- target_available
- teacher_eval_available
- rank_prob_available
- suppress_available
- current_player
- side_to_move
- target_rc
- target_xy
- teacher_move
- teacher_eval_kind
- teacher_eval_before
- numeric_gap_available
- numeric_gap_value
- before_target_rank
- before_target_prob
- current_best_direct_rc
- current_best_direct_move
- suppress_count
- suppress_rcs
- validation_notes
- needs_current_best_probe
- needs_suppress_build
- needs_rapfi_requery
- needs_board_join
- skip_reason

## Recommended selected source classes for first manifest

### Include directly

1. analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json

Reason:

- full schema;
- canonical seed source.

### Include as candidate sources needing probe/build

2. analysis/integration_eval/teacher_divergence_retention_safety_v3_dataset.json
3. analysis/integration_eval/teacher_divergence_retention_clean_v2_dataset.json
4. analysis/integration_eval/teacher_divergence_retention_dataset.json

Reason:

- board/side/target/source trace/bucket available;
- useful candidate rows;
- need rank/prob and suppress build.

### Include as metadata/cross-reference

5. analysis/integration_eval/teacher_divergence_retention_clean_v2_manifest.csv
6. analysis/integration_eval/teacher_divergence_retention_manifest.csv
7. analysis/public_benchmark_eval/rapfi_teacher_policy_candidates_corpus8_selected.csv
8. analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json

Reason:

- useful metadata and join support;
- not all are full row sources.

### Exclude from row source for now

- protected train split JSON derived from canonical 25 rows;
- rank/probe evaluation CSVs without board and target linkage;
- reports and logs;
- untracked local artifacts.

## First manifest design target

The next implementation branch should build an inventory-derived manifest, not a training dataset.

Suggested output files:

- analysis/integration_eval/teacher_divergence_expanded_manifest_design_selected_sources.csv
- analysis/integration_eval/teacher_divergence_expanded_manifest_design.md

Suggested later implementation branch:

exp/15x15-teacher-divergence-expanded-manifest-builder

The builder should initially write:

- analysis/integration_eval/teacher_divergence_expanded_candidate_manifest.csv
- analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_report.md

No training should occur until this manifest is reviewed.

## Training gate implication

Do not resume policy training until:

- manifest has enough ready_full_schema rows;
- rank buckets meet minimum size targets;
- protected_top10 and tail_rank_gt50 are eval-only;
- current_best probe and suppress build are complete;
- all duplicates are resolved.

## Decision

Design only.

No training.

No checkpoint.

No C export.

No public benchmark.

No promotion.

Proceed next with expanded manifest builder design or implementation.
