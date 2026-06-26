# b4c64/current-best guarded split v1 materialization

## Scope

- Branch: `exp/15x15-rank-topk-nosave-b4c64-guarded-split-v1`
- Materialization only.
- No training, checkpoint save, C export, public benchmark, promotion, or current-best overwrite was performed.

## Inputs

- Source dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_protected_train_11_50_weightcap3.json`
- Source proposal: `analysis/integration_eval/rank_topk_nosave_b4c64_culprit_protected_split_proposal/culprit_protected_split_proposal.json`

## Outputs

- Guarded dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_guarded_split_v1.json`
- Manifest: `analysis/integration_eval/rank_topk_nosave_b4c64_guarded_split_v1/guarded_split_v1_manifest.csv`
- Summary: `analysis/integration_eval/rank_topk_nosave_b4c64_guarded_split_v1/guarded_split_v1_summary.json`

## Group counts

| group | rows |
|---|---:|
| `samples` | 7 |
| `protected_eval_samples` | 15 |
| `tail_eval_samples` | 3 |

## Hard guard rows

| case_id | original group | hard guard role | required gate |
|---|---|---|---|
| `legacy_g1_m40` | `protected_eval_samples` | `hard_protected_beats_guard` | `{"rank_delta_max": 0, "target_prob_delta_min": -0.02, "teacher_beats_all_delta_min": 0, "teacher_beats_worst_delta_min": 0}` |
| `legacy_g1_m8` | `tail_eval_samples` | `hard_rank_le50_preservation_guard` | `{"rank_after_max": 50, "rank_delta_max": 0, "rank_gt50_delta_max": 0, "target_prob_delta_min": 0}` |

## Decision

- `legacy_g1_m40` is now a hard beats-worst/all preservation guard.
- `legacy_g1_m8` is now a hard rank<=50 preservation guard.
- Existing train/protected/tail groups are preserved for compatibility.
- Next step should be a guarded no-save probe/evaluator that fails on hard guard row damage.

## Non-actions

- No checkpoint was saved.
- No C export was run.
- No public benchmark was run.
- No promotion/current-best overwrite was performed.
