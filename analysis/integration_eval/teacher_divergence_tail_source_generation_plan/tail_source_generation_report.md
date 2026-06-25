# Teacher-divergence tail source generation plan

## Scope

- Planning only.
- No dataset build.
- No training.
- No checkpoint read or write.
- No C export, no public benchmark, no promotion.

## Why this plan is needed

The expansion source audit found partial candidates only.

- P0 tail guard candidates: `0` / `12`
- P0 protected guard candidates: `13` / `12`
- P1 train candidates: `15` / `20`

The blocker is tail guard coverage. Source artifacts currently expose zero usable P0 tail guard candidates under the generic audit.

## Unclassified source inventory

| source | unclassified rows |
|---|---:|
| `analysis/integration_eval/teacher_divergence_data_inventory_manifest.csv` | 274 |
| `analysis/integration_eval/teacher_divergence_expansion_source_audit.csv` | 36 |
| `analysis/integration_eval/teacher_divergence_retention_expanded_dataset.json` | 58 |
| `analysis/integration_eval/teacher_divergence_retention_expanded_manifest.csv` | 231 |
| `analysis/integration_eval/teacher_divergence_source_schema_audit.json` | 3 |

## Plan steps

| step | phase | output | training_allowed |
|---:|---|---|---|
| 1 | schema_recovery | tail_source_schema_recovery_manifest.csv | no |
| 2 | tail_candidate_mining | tail_guard_candidate_manifest.csv | no |
| 3 | protected_train_gap_review | protected_train_candidate_review.csv | no |
| 4 | candidate_materialization_dryrun | candidate review dataset only | no |
| 5 | future_no_save_probe_gate | no-save metrics only | no checkpoint-producing training |

## Detailed acceptance rules

### Step 1: schema_recovery

- purpose: Inspect the 599 unclassified_review rows and recover missing rank/prob/role fields from source-specific schemas.
- input: source_candidate_manifest.csv plus original source artifacts
- output: tail_source_schema_recovery_manifest.csv
- acceptance: At least one source-specific extractor identifies candidate rows with usable board/side/target fields.
- training allowed: `no`

### Step 2: tail_candidate_mining

- purpose: Mine rank>50 or near-tail teacher-divergence cases from recovered source rows.
- input: schema recovery manifest
- output: tail_guard_candidate_manifest.csv
- acceptance: At least 12 unique P0 tail_guard candidates, preferably from multiple games/families.
- training allowed: `no`

### Step 3: protected_train_gap_review

- purpose: Keep already found protected candidates and identify at least 5 more train candidates only if schemas are reliable.
- input: source audit candidate buckets
- output: protected_train_candidate_review.csv
- acceptance: Protected remains >=12 and P1 train candidate pool reaches >=20 without using quarantine rows.
- training allowed: `no`

### Step 4: candidate_materialization_dryrun

- purpose: Materialize a candidate-only review dataset with tail/protected held out and train candidates separated.
- input: tail/protected/train candidate manifests
- output: candidate review dataset only
- acceptance: Schema validates, suppress_rcs are complete, no overlap across train/protected/tail/quarantine.
- training allowed: `no`

### Step 5: future_no_save_probe_gate

- purpose: Only after candidate review passes, run no-save probes to check guard stability.
- input: candidate review dataset
- output: no-save metrics only
- acceptance: tail rank_gt50_delta <= 0, tail mean_rank_delta <= 0, protected top5_delta >= 0, protected top10_delta >= 0.
- training allowed: `no checkpoint-producing training`

## Decision

`TAIL_SOURCE_GENERATION_PLAN_REQUIRED`

Recommended next branch:

`exp/15x15-teacher-divergence-tail-schema-recovery`

The next branch should recover source-specific schemas from unclassified rows and attempt to mine tail guard candidates. It should not train.

## Final note

This plan does not authorize training, checkpoint save, C export, public benchmark, promotion, or current_best overwrite.
