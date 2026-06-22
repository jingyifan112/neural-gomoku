# Policy-only rank/top-k chain closeout

## Branch

exp/15x15-policy-only-rank-topk-chain-closeout

## Scope

This is a closeout-only branch.

No training, checkpoint save, C export, public benchmark, or promotion is run.

## Background

The policy-only teacher-divergence repair path started from the observation that single-suppress pairwise margin training improved local logits but did not make the audited teacher-vs-suppress gaps positive.

A stronger rank/top-k objective was then explored because the desired repair is not just margin improvement. The teacher move must enter useful rank bands such as top3, top5, or top10 without damaging anchor rows.

## Completed chain

### 1. Single-suppress repair probe

Branch:

exp/15x15-policy-only-teacher-divergence-repair-probe

Result:

- Confirmed the 25-row single-suppress pairwise margin dataset was usable.
- No training/export/promotion decision was made from the setup probe.

### 2. Single-suppress repair training

Branch:

exp/15x15-policy-only-teacher-divergence-repair-train

Result:

- 24/25 gap improved.
- 24/25 target probability improved.
- 8/25 target rank improved.
- 0 target ranks regressed.
- Mean delta gap was +0.148287.
- However, all audited gaps remained negative.

Decision:

- Reject for export.
- No public benchmark.
- No promotion.

### 3. Objective/gate design

Branch:

exp/15x15-policy-only-objective-gate-design

Result:

- Single-suppress margin was judged insufficient.
- Recommended stronger objective/gate design.
- Preferred directions were multi-suppress or rank/top-k oriented gates.

Decision:

- Proceed to multi-suppress audit/design.
- No training on the design branch.

### 4. Multi-suppress audit

Branch:

exp/15x15-policy-only-multisuppress-audit

Result:

- Existing trainer/dataset were confirmed to be single-suppress only.
- Recommended new multi-suppress builder and trainer dry-run.

Decision:

- Proceed to multi-suppress dry-run.
- No training/export/promotion.

### 5. Multi-suppress dry-run

Branch:

exp/15x15-policy-only-multisuppress-dryrun

Artifacts:

- scripts/build_rapfi_teacher_policy_multisuppress_dataset.py
- scripts/train_rapfi_teacher_policy_multisuppress_margin.py
- analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json
- analysis/integration_eval/policy_only_multisuppress_dryrun_metrics.csv
- analysis/integration_eval/policy_only_multisuppress_dryrun_report.md
- analysis/integration_eval/policy_only_multisuppress_dryrun_closeout.md

Result:

- 25/25 rows written.
- 0 skipped.
- Each row had suppress_count = 5.
- rows = 25.
- anchor_rows = 32.
- top3 = 5.
- top5 = 11.
- top10 = 15.
- target_rank_gt10 = 10.
- target_rank_gt50 = 3.
- mean_worst_suppress_gap = -4.954128.
- mean_multi_pair_hinge = 3.524615.

Decision:

- Schema and scoring path passed.
- Immediate multi-suppress training was judged risky because the primary current_best direct move remained the aggregate worst suppressor.
- Proceed to rank/top-k gate design instead of training.

### 6. Rank/top-k objective design

Branch:

exp/15x15-policy-only-rank-topk-objective-design

Result:

- Designed candidate objectives:
  - teacher CE only;
  - pure multi-suppress hinge;
  - CE plus mean-pair hinge plus worst-suppress hinge;
  - local listwise softmax.
- Defined rank/top-k gate requirements:
  - top3/top5/top10 improvement;
  - no increase in rank_gt50;
  - no protected top10 regressions;
  - suppress-gap improvement must not override rank/top-k failures.

Decision:

- No training.
- Build gate evaluator first.

### 7. Rank/top-k gate dry-run

Branch:

exp/15x15-policy-only-rank-topk-gate-dryrun

Artifacts:

- scripts/evaluate_policy_rank_topk_gate.py
- analysis/integration_eval/policy_only_rank_topk_gate_baseline_self_metrics.csv
- analysis/integration_eval/policy_only_rank_topk_gate_baseline_self_report.md

Result:

- Baseline-vs-baseline evaluator self-check passed.
- Gate report and CSV format were validated.

Decision:

- Proceed to trainer dry-run.
- No training/export/promotion.

### 8. Rank/top-k training probe scaffold and no-save smoke

Branch:

exp/15x15-policy-only-rank-topk-training-probe

Artifacts:

- scripts/train_rapfi_teacher_policy_rank_topk_probe.py
- analysis/integration_eval/policy_only_rank_topk_training_probe_dryrun_report.md
- analysis/integration_eval/policy_only_rank_topk_training_probe_nosave_smoke_report.md

Result:

- Trainer scaffold loaded the multi-suppress dataset.
- Dry-run produced initial loss terms.
- No-save smoke verified optimizer path without saving a checkpoint.

Decision:

- Proceed to one local saved checkpoint only for gate evaluation.
- No export/public benchmark/promotion.

### 9. Run1 local gate

Branch:

exp/15x15-policy-only-rank-topk-training-run1-local-gate

Artifacts:

- analysis/integration_eval/policy_only_rank_topk_training_probe_run1_report.md
- analysis/integration_eval/policy_only_rank_topk_gate_run1_metrics.csv
- analysis/integration_eval/policy_only_rank_topk_gate_run1_report.md
- analysis/integration_eval/policy_only_rank_topk_training_run1_closeout.md

Result:

- Gate verdict: FAIL_CANDIDATE_GATE.
- The saved-local checkpoint was rejected.
- Local checkpoint was deleted and not committed.

Decision:

- Reject run1.
- No export.
- No public benchmark.
- No promotion.

### 10. Run2 no-save ablations

Branch:

exp/15x15-policy-only-rank-topk-training-run2-ablation

Ablations:

- run2A: CE-only.
- run2B: CE plus weak suppress.

Result:

- top3 delta = 0.
- top5 delta = 0.
- top10 delta = +1.
- rank_gt50 delta = +1.
- mean_rank worsened by +3.64.
- mean target probability decreased.
- teacher_beats_worst decreased.
- teacher_beats_all decreased.

Decision:

- Reject run2.
- Do not save checkpoint.
- No export/public benchmark/promotion.

### 11. Protected weighting audit

Branch:

exp/15x15-policy-only-rank-topk-protected-weighting-audit

Artifacts:

- analysis/integration_eval/policy_only_rank_topk_protected_weighting_audit.csv
- analysis/integration_eval/policy_only_rank_topk_protected_weighting_audit.md

Result:

- 25 rows total.
- baseline top10 rows = 15.
- rank 11-50 rows = 7.
- rank > 50 rows = 3.
- High-rank tail and high-weight rows were unstable.
- Recommended protecting baseline top10 rows, isolating rank > 50 rows, and training only rank 11-50 rows first.

Decision:

- Proceed to protected objective dry-run.
- No training/checkpoint/export/benchmark/promotion.

### 12. Protected objective dry-run

Branch:

exp/15x15-policy-only-rank-topk-protected-objective-dryrun

Artifacts:

- analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_protected_train_11_50_weightcap3.json
- analysis/integration_eval/policy_only_rank_topk_protected_objective_dryrun_dataset_report.md
- analysis/integration_eval/policy_only_rank_topk_protected_objective_dryrun_report.md

Result:

- train_main_rank_11_50 rows = 7.
- protected_eval_top10 rows = 15.
- tail_eval_rank_gt50 rows = 3.
- weight cap = 3.0.
- Trainer dry-run loaded the protected dataset successfully.

Decision:

- Proceed to protected no-save probe.
- No saved checkpoint.

### 13. Protected no-save probe

Branch:

exp/15x15-policy-only-rank-topk-protected-nosave-probe

Artifacts:

- scripts/probe_policy_rank_topk_protected_nosave.py
- analysis/integration_eval/policy_only_rank_topk_protected_nosave_probe_group_metrics.csv
- analysis/integration_eval/policy_only_rank_topk_protected_nosave_probe_report.md
- analysis/integration_eval/policy_only_rank_topk_protected_nosave_probe_closeout.md

Result:

- Verdict: FAIL_NO_SAVE_PROBE.

Group result:

- train_main_rank_11_50:
  - mean_rank improved by -1.857143.
  - target_prob improved by +0.00049504.
  - mean_worst_gap improved by +0.041463.
  - hinge improved by -0.238577.
- protected_eval_top10:
  - target_prob dropped by -0.01282100.
  - teacher_beats_worst dropped by -1.
  - teacher_beats_all dropped by -1.
- tail_eval_rank_gt50:
  - rank_gt50 worsened by +1.
  - mean_rank worsened by +37.333333.
  - hinge worsened by +0.558160.

Decision:

- Reject protected no-save probe.
- Do not save checkpoint.
- No export.
- No public benchmark.
- No promotion.

## Final conclusion

The policy-only rank/top-k repair chain should be closed.

Evidence across the chain shows:

1. Single-suppress margin training improved local margins but did not make gaps positive.
2. Multi-suppress dry-run exposed stronger suppressors but did not justify immediate training.
3. Full-dataset rank/top-k training failed the candidate gate.
4. CE-only and weak-suppress no-save ablations were unstable.
5. Protected training on rank 11-50 rows improved the train group slightly but damaged protected top10 and tail rows.
6. The current 25-row dataset is too small and unstable for policy-head-only rank/top-k repair.

## Decision

Do not train further on this policy-only rank/top-k chain.

Do not save or keep any candidate checkpoint from this chain.

Do not export C weights.

Do not run public benchmark.

Do not promote.

## Recommended next project direction

The next useful step should move away from small policy-head-only local repair.

Recommended options:

1. Broader teacher-divergence data construction:
   - collect more validated teacher-divergence positions;
   - separate top10, rank 11-50, and tail rank >50 rows from the start;
   - avoid training decisions from only 25 rows.

2. Stronger evaluation-first gate:
   - include protected rows in the loss/gate loop before optimizer steps;
   - stop training as soon as protected buckets regress.

3. Non-policy-only diagnostics:
   - inspect value/policy interaction on teacher-divergence rows;
   - identify whether the model is rejecting teacher moves because of value head evaluation, policy prior, or board encoding limitations.

4. Return to broader 15x15 model strength:
   - capacity upgrade;
   - broader public benchmark score ladder;
   - larger supervised/self-play data before local repair.

## Status

Closed.

No checkpoint, export, benchmark, or promotion is produced from this chain.
