# Teacher-divergence run1 post-adapter route decision

## Branch

`exp/15x15-teacher-divergence-run1-post-adapter-route-decision`

## Scope

- Routes the next step after direct-probe eval adapter dry-run/plan.
- Reads adapter decision and manifest.
- Does not train.
- Does not run model eval.
- Does not read checkpoint contents.
- Does not write checkpoints.
- Does not overwrite `checkpoints/15x15_current_best.pt`.
- Does not C export.
- Does not run public benchmark.
- Does not promote.

## Final route decision

`POST_ADAPTER_ROUTE_BLOCKED`

## Next branch

`none`

## Summary

| metric | value | status | notes |
|---|---:|---|---|
| final_route_decision | POST_ADAPTER_ROUTE_BLOCKED | INFO | Route only; no model eval. |
| route_decision | ROUTE_BLOCKED_FIX_ADAPTER_BLOCKERS | INFO |  |
| next_branch | none | INFO |  |
| next_action | Fix adapter blockers before continuing. | INFO |  |
| blocker_count | 2 | FAIL | adapter blockers present: 2; adapter decision is blocked |
| warning_count | 1 | WARN | adapter warnings carried forward: 2 |
| adapter_decision | DIRECT_PROBE_EVAL_ADAPTER_BLOCKED | INFO |  |
| adapter_blocker_count | 2 | FAIL |  |
| adapter_warning_count | 2 | WARN |  |
| controlled_review_decision | LOCAL_COMPARISON_CONTROLLED_REVIEW_BLOCKED | INFO |  |
| core_reuse_inputs | 3 | PASS |  |
| direct_ready_inputs_from_selection | 10 | INFO |  |
| manifest_rows | 10 | INFO |  |
| would_train | 0 | PASS |  |
| would_eval_model_now | 0 | PASS |  |
| would_read_checkpoint_contents_now | 0 | PASS |  |
| would_write_checkpoint | 0 | PASS |  |
| would_c_export | 0 | PASS |  |
| would_public_benchmark | 0 | PASS |  |
| would_promote | 0 | PASS |  |

## Direct-probe manifest rows

| eval_manifest_id | adapter_kind | stage | path | rows/count |
|---|---|---|---|---:|
| run1_direct_probe_eval_001 | direct_model_eval_fixed_probe_candidate | fixed_probe_candidate | `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_closeout.md` | 0 |
| run1_direct_probe_eval_002 | direct_model_eval_fixed_probe_candidate | fixed_probe_candidate | `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_design.md` | 0 |
| run1_direct_probe_eval_003 | direct_model_eval_fixed_probe_candidate | fixed_probe_candidate | `analysis/integration_eval/policy_only_teacher_divergence_repair_probe_script_audit.md` | 0 |
| run1_direct_probe_eval_004 | direct_model_eval_heldout_candidate | heldout_candidate | `analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_blocker_position_review.md` | 0 |
| run1_direct_probe_eval_005 | direct_model_eval_anchor_candidate | anchor_candidate | `analysis/integration_eval/candidate_c_g2_m19_perspective_diagnostic_anchors.json` | 8 |
| run1_direct_probe_eval_006 | direct_model_eval_anchor_candidate | anchor_candidate | `analysis/integration_eval/candidate_d_g2_m15_diagnostic_anchors.json` | 3 |
| run1_direct_probe_eval_007 | direct_model_eval_anchor_candidate | anchor_candidate | `analysis/integration_eval/candidate_e_g2_m13_diagnostic_anchors.json` | 1 |
| run1_direct_probe_eval_008 | direct_model_eval_anchor_candidate | anchor_candidate | `analysis/integration_eval/candidate_e_g2_m17_diagnostic_anchors.json` | 3 |
| run1_direct_probe_eval_009 | direct_model_eval_anchor_candidate | anchor_candidate | `analysis/integration_eval/current_best_margin_candidate_c_anchors.json` | 7 |
| run1_direct_probe_eval_010 | direct_model_eval_anchor_candidate | anchor_candidate | `analysis/integration_eval/current_best_margin_candidate_c_conservative_anchors.json` | 5 |

## Blockers

- adapter blockers present: 2
- adapter decision is blocked

## Warnings

- adapter warnings carried forward: 2

## Recommendation

Fix adapter blockers before continuing.

## Outputs

- summary CSV: `analysis/integration_eval/teacher_divergence_run1_post_adapter_route_decision_summary.csv`
- next plan: `analysis/integration_eval/teacher_divergence_run1_post_adapter_route_decision_next_plan.txt`
- report: `analysis/integration_eval/teacher_divergence_run1_post_adapter_route_decision.md`

## Final guardrails

- No current_best overwrite.
- No C export.
- No public benchmark.
- No promotion.
- Do not add local checkpoint artifacts to git.
