# b4c64/current-best culprit-protected split proposal

## Scope

- Branch: `exp/15x15-rank-topk-nosave-b4c64-culprit-protected-split-proposal`
- Proposal only.
- No training, checkpoint save, C export, public benchmark, promotion, or current-best overwrite was performed.

## Source

- Row trace: `analysis/integration_eval/rank_topk_nosave_b4c64_row_trace_baseline_run1/row_trace.csv`
- Source summary: `analysis/integration_eval/rank_topk_nosave_b4c64_row_trace_baseline_run1/row_trace_summary.json`
- Source dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_protected_train_11_50_weightcap3.json`
- Source trace status: `TRACE_COMPLETE_GATE_CULPRITS_IDENTIFIED`

## Hard protected rows

| case_id | current group | proposed role | rank before→after | prob Δ | key failure |
|---|---|---|---:|---:|---|
| `legacy_g1_m40` | `protected_eval_top10` | `hard_protected_beats_guard` | 1.0→3.0 | -0.27682457119226456 | teacher_beats_worst/all 1→0 |
| `legacy_g1_m8` | `tail_eval_rank_gt50` | `hard_rank_le50_preservation_guard` | 19.0→107.0 | -0.0005092114006401971 | rank_gt50 0→1 |

## Warning rows

- Tail rank regressions: `3`
- Train target-prob regressions: `4`
- Train rank regressions: `3`
- Protected target-prob regressions: `4`

### Tail rank regressions

| case_id | rank before→after | rank_gt50 before→after | prob Δ |
|---|---:|---:|---:|
| `legacy_g1_m8` | 19.0→107.0 | 0.0→1.0 | -0.0005092114006401971 |
| `legacy_g5_m12` | 85.0→92.0 | 1.0→1.0 | 0.00015571898984489962 |
| `legacy_g5_m30` | 64.0→78.0 | 1.0→1.0 | 3.068152000196278e-05 |

### Train regressions

| case_id | rank before→after | prob Δ |
|---|---:|---:|
| `legacy_g2_m11` | 13.0→15.0 | -7.686241406190675e-05 |
| `legacy_g2_m21` | 41.0→44.0 | -6.154639413580298e-05 |
| `legacy_g4_m13` | 16.0→16.0 | -0.0009794175566639751 |
| `legacy_g6_m17` | 9.0→7.0 | -0.001457774080336094 |

## Decision

- Final decision: `REQUIRE_CULPRIT_PROTECTED_SPLIT_BEFORE_NEXT_NO_SAVE_OBJECTIVE_RUN`
- Do not continue by increasing epochs.
- Do not save any candidate from the current objective.
- First materialize a guarded split that hard-protects `legacy_g1_m40` and `legacy_g1_m8`.

## Next route

- Materialize a guarded split dataset/report from this proposal.
- Then run another no-save probe against the guarded split.
- Required next-run gates:
  - `legacy_g1_m40`: no loss of teacher_beats_worst/all.
  - `legacy_g1_m8`: must not cross into rank_gt50; rank after must stay <= 50.

## Outputs

- `analysis/integration_eval/rank_topk_nosave_b4c64_culprit_protected_split_proposal/culprit_protected_split_proposal.json`
