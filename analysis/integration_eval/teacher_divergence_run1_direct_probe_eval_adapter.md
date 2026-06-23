# Teacher-divergence run1 direct-probe eval adapter dry-run

## Branch

`exp/15x15-teacher-divergence-run1-direct-probe-eval-adapter`

## Scope

- Plans a controlled direct-probe local model-eval adapter.
- Reads controlled review and adapter selection outputs.
- Does not train.
- Does not run model eval.
- Does not read checkpoint contents.
- Does not write checkpoints.
- Does not overwrite `checkpoints/15x15_current_best.pt`.
- Does not C export.
- Does not run public benchmark.
- Does not promote.

## Adapter decision

`DIRECT_PROBE_EVAL_ADAPTER_BLOCKED`

## Summary

| metric | value | status | notes |
|---|---:|---|---|
| adapter_decision | DIRECT_PROBE_EVAL_ADAPTER_BLOCKED | INFO | Dry-run/plan only; no model eval. |
| blocker_count | 2 | FAIL | controlled review is blocked; controlled review blockers present: 2 |
| warning_count | 2 | WARN | controlled review warnings carried forward: 5; deferred adapter inputs remain: 88 |
| controlled_review_decision | LOCAL_COMPARISON_CONTROLLED_REVIEW_BLOCKED | FAIL |  |
| controlled_review_blocker_count | 2 | FAIL |  |
| controlled_review_warning_count | 5 | WARN |  |
| adapter_design_decision | LOCAL_COMPARISON_ADAPTER_DESIGN_BLOCKED | INFO |  |
| adapter_design_direct_model_eval_inputs_selected | 10 | INFO |  |
| adapter_design_deferred_adapter_inputs | 88 | WARN |  |
| candidate_checkpoint_exists_locally | 1 | PASS | Existence only; do not add to git. |
| current_best_exists | 1 | PASS |  |
| selected_inputs | 13 | INFO |  |
| core_reuse_inputs | 3 | PASS |  |
| direct_ready_inputs_from_selection | 10 | INFO |  |
| controlled_review_direct_ready_inputs | 10 | INFO |  |
| manifest_rows | 10 | INFO |  |
| would_train | 0 | PASS |  |
| would_eval_model_now | 0 | PASS |  |
| would_read_checkpoint_contents_now | 0 | PASS |  |
| would_write_checkpoint | 0 | PASS |  |
| would_c_export | 0 | PASS |  |
| would_public_benchmark | 0 | PASS |  |
| would_promote | 0 | PASS |  |

## Direct-ready eval manifest

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

- controlled review is blocked
- controlled review blockers present: 2

## Warnings

- controlled review warnings carried forward: 5
- deferred adapter inputs remain: 88

## Future executor requirements

Any future model-eval executor must require both:

```text
--execute-model-eval
--confirm-model-eval TEACHER_DIVERGENCE_DIRECT_PROBE_LOCAL_EVAL
```

It must output local comparison CSV/MD only and must not export C, run a public benchmark, or promote.

## Recommendation

Do not proceed until blockers are resolved.

## Outputs

- manifest CSV: `analysis/integration_eval/teacher_divergence_run1_direct_probe_eval_adapter_manifest.csv`
- summary CSV: `analysis/integration_eval/teacher_divergence_run1_direct_probe_eval_adapter_summary.csv`
- command plan: `analysis/integration_eval/teacher_divergence_run1_direct_probe_eval_adapter_commands.txt`
- report: `analysis/integration_eval/teacher_divergence_run1_direct_probe_eval_adapter.md`

## Final guardrails

- No current_best overwrite.
- No C export.
- No public benchmark.
- No promotion.
- Do not add local checkpoint artifacts to git.
