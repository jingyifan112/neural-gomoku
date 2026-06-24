# b4c96 gate-informed objective ablation plan

## Branch

`exp/15x15-b4c96-gate-informed-objective-ablation`

## Scope

- Planning and compatibility audit only.
- No training, no checkpoint read, no checkpoint write, no C export, no public benchmark, no promotion.

## Source diagnosis

- Forensics diagnosis: `B4C96_STAGEC_FAILED_DUE_TO_PROTECTED_OR_OBJECTIVE_REGRESSION`
- Rows: `25`
- Top-5 delta: `-2`
- Rank>50 delta: `1`
- Severe core regression rows: `10`
- Directionally useful rows: `9`
- Protected top-10 regression rows: `1`

## Compatibility audit

| key | value |
|---|---|
| rank_topk_train_script_has_nosave | True |
| rank_topk_train_script_has_architecture_args | False |
| protected_nosave_script_has_nosave | True |
| protected_nosave_script_has_architecture_args | False |
| b4c96_gate_has_dual_arch_args | True |
| direct_b4c96_nosave_safe | False |

## Ablation plan

| ablation_id | ce_weight | pair_weight | worst_weight | anchor_kl_weight | tail_policy | protected_policy | run_now | blocker |
|---|---|---|---|---|---|---|---|---|
| A0_failed_stagec_reference_replay |  |  |  |  | none | none | no | already completed; no rerun needed |
| A1_stronger_anchor_balanced_hinge | 1.0 | 0.6 | 0.6 | 1.0 | unchanged | strong_anchor | blocked | needs b4c96-safe no-save wrapper with architecture args |
| A2_light_worst_suppress | 1.0 | 0.6 | 0.2 | 0.8 | unchanged | anchor_guarded | blocked | needs b4c96-safe no-save wrapper with architecture args |
| A3_ce_dominant_rank_repair | 1.5 | 0.3 | 0.1 | 0.8 | unchanged | anchor_guarded | blocked | needs b4c96-safe no-save wrapper with architecture args |
| A4_tail_capped_training_set | 1.0 | 0.5 | 0.3 | 1.0 | cap_or_prune_rank_gt50 | strong_anchor | blocked | existing no-save probe has no tail cap/prune option; wrapper/dataset adapter required |
| A5_severe_regression_family_downweight | 1.0 | 0.5 | 0.3 | 1.0 | tail_cap | strong_anchor | blocked | existing no-save probe has no per-row/family reweight option; wrapper/dataset adapter required |
| REQUIRED_GATE_CONSTRAINT_protected |  |  |  |  |  | hard_guard | constraint |  |
| REQUIRED_GATE_CONSTRAINT_core_regression |  |  |  |  |  |  | constraint |  |

## Decision

`ABLATION_PLAN_READY_EXECUTION_BLOCKED_NEEDS_B4C96_SAFE_NOSAVE_WRAPPER`

## Next required action

Create a b4c96-safe no-save objective ablation wrapper before running any ablation. The wrapper must expose board-size, win-length, channels, blocks, no-save, and per-ablation weights.

## Final note

Do not execute b4c96 no-save ablations through the existing protected probe until a b4c96-safe wrapper exists.
