# 15x15 Teacher-Divergence Signal Audit

## Scope

This audit reviews the existing teacher-divergence and Rapfi-teacher supervision artifacts after the capacity-upgrade audit.

It does not run training.
It does not create a checkpoint.
It does not export C weights.
It does not run a public benchmark.
It does not promote any model.

## Motivation

The capacity-upgrade audit concluded that isolated capacity increases are not the right next move.

The next improvement attempt should focus on better training signal:

- validated Rapfi teacher disagreement rows,
- policy-only repair targets,
- explicit held-out retention checks,
- no blind value regression from mixed Rapfi score formats.

## Existing Rapfi teacher candidate set

Primary candidate source:

- `analysis/public_benchmark_eval/rapfi_teacher_policy_candidates_corpus8_selected.csv`
- report: `analysis/public_benchmark_eval/rapfi_teacher_policy_candidates_corpus8_selected_report.md`

Summary:

- total rows: `32`
- concrete teacher rows: `32`
- stable teacher move rows: `32`
- current_best already matches teacher: `7`
- current_best mismatches teacher: `25`
- priority candidates: `25`
- priority numeric-gap candidates: `12`
- priority gap-unavailable candidates: `13`
- low-priority already-matched rows: `7`
- numeric eval rows: `16`
- mate eval rows: `8`
- NA eval rows: `8`
- value regression candidates: `0`

## Recommended supervision interpretation

The Rapfi teacher rows should be treated as policy supervision, not direct value regression.

Reason:

- all 32 rows have concrete and stable teacher moves,
- 25 rows are priority policy candidates because current_best disagrees with the teacher,
- numeric gaps exist for only part of the set,
- mate and NA rows should not be coerced into numeric value targets,
- `value_regression_candidate` is false for every row in this pass.

## Current candidate datasets

### Policy repair dataset

File:

- `analysis/public_benchmark_eval/rapfi_teacher_policy_repair_dataset_corpus8_selected.json`

Summary:

- rows: `25`
- selection rule: `priority_candidate == true`
- bucket split:
  - `priority_policy_numeric_gap`: `12`
  - `priority_policy_gap_unavailable`: `13`
- intended use: policy-only repair or ranking experiment
- value targets: blank / masked out

### Pairwise margin dataset

File:

- `analysis/public_benchmark_eval/rapfi_teacher_policy_margin_dataset_corpus8_selected.json`

Summary:

- rows: `25`
- skipped rows: `0`
- bucket split:
  - `priority_policy_numeric_gap`: `12`
  - `priority_policy_gap_unavailable`: `13`

Interpretation:

- This is the cleaner next training-signal candidate than direct value regression.
- The target should be to rank the Rapfi teacher move above the current_best direct move.
- Numeric-gap rows can be used for weighting or priority, but not as direct value labels.

## Prior Candidate G/H result boundary

Existing model comparison:

- `current_best`: 7 / 32 direct Rapfi-best matches
- `candidate_g`: 6 / 32 direct Rapfi-best matches
- `candidate_h`: 6 / 32 direct Rapfi-best matches

Decision boundary:

- Candidate G should not be promoted.
- Candidate H should not be promoted.
- Existing G/H results are useful as diagnostics, not as promotion evidence.

## Existing retention dataset boundary

Teacher-divergence retention data closeout records two accepted dataset stages.

### clean v2

Files:

- `analysis/integration_eval/teacher_divergence_retention_clean_v2_dataset.json`
- `analysis/integration_eval/teacher_divergence_retention_clean_v2_manifest.csv`
- `analysis/integration_eval/teacher_divergence_retention_clean_v2_report.md`

Summary:

- dataset rows: `39`
- train teacher-divergence baseline rows: `25`
- train candidate rows from Candidate G seed: `3`
- held-out retention rows: `11`

### safety v3

Files:

- `analysis/integration_eval/teacher_divergence_retention_safety_v3_dataset.json`
- `analysis/integration_eval/teacher_divergence_retention_safety_v3_manifest.csv`
- `analysis/integration_eval/teacher_divergence_retention_safety_v3_report.md`

Summary:

- total rows: `44`
- train teacher-divergence baseline rows: `25`
- train candidate rows: `8`
  - 3 Candidate G teacher-divergence seed rows
  - 5 safety-block immediate-threat rows
- held-out retention rows: `11`

Retention boundary:

- Held-out retention rows must remain separated from training rows.
- Score-gap evidence should be represented in manifests and reports without duplicating canonical rows.
- Promotion-oriented training must probe both train rows and held-out retention rows.

## Next training-signal recommendation

The next experimental unit should be a small policy-focused teacher-divergence repair probe from current-best-family.

Recommended input:

- use the 25 priority Rapfi teacher rows,
- prefer the pairwise margin dataset as the training target,
- treat numeric-gap rows as weighting or prioritization only,
- include gap-unavailable mate and NA rows as policy targets only,
- do not use direct value regression.

Required probes before any C export:

1. direct probe on the 25 priority teacher rows,
2. direct probe on the 12 numeric-gap subset,
3. direct probe on the 13 gap-unavailable subset,
4. probe on the 11 held-out retention rows,
5. tactical safety regression probe,
6. comparison against current_best on the 32-row corpus8 selected score-gap set.

## Explicit non-actions

This audit makes no model-state changes:

- no training,
- no checkpoint creation,
- no C export,
- no public benchmark,
- no promotion.

## Decision

Proceed toward a policy-only teacher-divergence repair probe.

Do not start another blind capacity experiment.
Do not promote Candidate G or Candidate H.
Do not use Rapfi mate or NA rows as numeric value labels.
Do not mix held-out retention rows into training.
