# b4c64/current-best hard-guard objective/data redesign proposal

## Scope

- Branch: `exp/15x15-rank-topk-nosave-b4c64-hardguard-objective-redesign-proposal`
- Proposal only.
- No training, checkpoint save, C export, public benchmark, promotion, or current-best overwrite was performed.

## Source

- Guarded run summary: `analysis/integration_eval/rank_topk_nosave_b4c64_guarded_split_baseline_run1/guarded_run_summary.json`
- Hard guard eval: `analysis/integration_eval/rank_topk_nosave_b4c64_guarded_split_baseline_run1/hard_guard_eval.csv`
- Row trace: `analysis/integration_eval/rank_topk_nosave_b4c64_guarded_split_baseline_run1/row_trace.csv`
- Group eval: `analysis/integration_eval/rank_topk_nosave_b4c64_guarded_split_baseline_run1/group_eval.csv`
- Source run status: `PASS_GUARDED_EVALUATOR_CAUGHT_HARD_GUARD_DAMAGE`
- Source verdict: `FAIL_HARD_GUARD_ROW_DAMAGE`

## Diagnosis

- The guarded evaluator is working: the baseline run produced `FAIL_HARD_GUARD_ROW_DAMAGE`.
- The current baseline objective is not safe even at 1 epoch and lr `1e-7`.
- The failure is not vague group-level noise anymore; it is localized to hard guard rows.

## Hard guard failures

| case_id | role | failure reasons | rank before→after | prob Δ | rank>50 before→after | beats-worst before→after | beats-all before→after |
|---|---|---|---:|---:|---:|---:|---:|
| `legacy_g1_m40` | `hard_protected_beats_guard` | `rank_delta=2.0 > 0.0;target_prob_delta=-0.27682457119226456 < -0.02;teacher_beats_all_delta=-1.0 < 0.0;teacher_beats_worst_delta=-1.0 < 0.0` | 1.0→3.0 | -0.27682457119226456 | 0→0 | 1→0 | 1→0 |
| `legacy_g1_m8` | `hard_rank_le50_preservation_guard` | `rank_after=107.0 > 50.0;rank_delta=88.0 > 0.0;rank_gt50_delta=1.0 > 0.0;target_prob_delta=-0.0005092114006401971 < 0.0` | 19.0→107.0 | -0.0005092114006401971 | 0→1 | 0→0 | 0→0 |

## Train-row signal quality

- Train rows: `7`
- Train target-prob regressions: `4`
- Train rank improvements: `3`
- Clear train winners, rank improves and probability improves: `2`

### Clear train winners

| case_id | rank before→after | prob Δ | worst gap before→after |
|---|---:|---:|---:|
| `legacy_g4_m23` | 26.0→11.0 | 0.0023981257691048086 | -7.353243827819824→-5.234453201293945 |
| `legacy_g5_m28` | 23.0→15.0 | 0.0028733813669532537 | -6.380010604858398→-5.125337600708008 |

### Train target-prob regressions

| case_id | rank before→after | prob Δ | worst gap before→after |
|---|---:|---:|---:|
| `legacy_g2_m11` | 13.0→15.0 | -7.686241406190675e-05 | -9.101638317108154→-10.571034908294678 |
| `legacy_g2_m21` | 41.0→44.0 | -6.154639413580298e-05 | -9.32773208618164→-10.745892524719238 |
| `legacy_g4_m13` | 16.0→16.0 | -0.0009794175566639751 | -5.973781585693359→-7.671762943267822 |
| `legacy_g6_m17` | 9.0→7.0 | -0.001457774080336094 | -4.109737396240234→-4.586860656738281 |

## Recommended next route

### Create guard-aware no-save objective v1

Patch a new no-save wrapper route that uses the guarded split dataset and adds hard-guard loss terms.

Initial objective proposal:

| loss term | initial weight | purpose |
|---|---:|---|
| `main_train_ce` | `0.5` | weaker train-row teacher attraction |
| `main_train_pair_hinge` | `0.5` | weaker pairwise target-over-suppress signal |
| `main_train_worst_hinge` | `0.25` | avoid aggressive worst-suppress pressure |
| `global_anchor_kl` | `1.0` | stronger global reference preservation |
| `hard_guard_reference_kl` | `4.0` | preserve current_best distribution on hard guards |
| `hard_guard_target_ce` | `1.0` | prevent target probability collapse on hard guards |
| `hard_guard_beats_hinge` | `4.0` | preserve beats-worst/all where source row already had it |

Initial run config:

- epochs: `1`
- lr: `5e-8`
- weight_decay: `0`
- seed: `17`
- dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_guarded_split_v1.json`

## Required next-run gates

- `legacy_g1_m40`: must not lose teacher_beats_worst/all.
- `legacy_g1_m8`: must not cross into rank_gt50; rank after must stay <= 50.
- If any hard guard fails, verdict must remain `FAIL_HARD_GUARD_ROW_DAMAGE`.
- Do not save a checkpoint unless a separate explicit promotion route is later authorized.

## Routes not recommended

- Do not simply increase epochs.
- Do not simply save the current no-save result.
- Do not run C export or public benchmark.
- Do not rely on group-level gates alone.
- Do not use lower LR / stronger KL alone as the main solution; previous ablations still damaged gates.

## Final decision

`CREATE_GUARD_AWARE_NO_SAVE_OBJECTIVE_WRAPPER_NEXT`

## Outputs

- `analysis/integration_eval/rank_topk_nosave_b4c64_hardguard_objective_redesign_proposal/hardguard_objective_redesign_proposal.json`
