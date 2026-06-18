# Policy-only rank/top-k training run1 closeout

## Branch

`exp/15x15-policy-only-rank-topk-training-run1-local-gate`

## Scope

- Local training run only.
- A checkpoint was created only to run the gate evaluator.
- No C export, no public benchmark, no promotion.
- The checkpoint must not be committed.

## Inputs

- Trainer: `scripts/train_rapfi_teacher_policy_rank_topk_probe.py`
- Gate evaluator: `scripts/evaluate_policy_rank_topk_gate.py`
- Dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json`
- Baseline checkpoint: `checkpoints/15x15_current_best.pt`
- Local candidate checkpoint: `checkpoints/15x15_policy_rank_topk_probe_run1.pt`
- Training report: `analysis/integration_eval/policy_only_rank_topk_training_probe_run1_report.md`
- Gate report: `analysis/integration_eval/policy_only_rank_topk_gate_run1_report.md`
- Gate metrics CSV: `analysis/integration_eval/policy_only_rank_topk_gate_run1_metrics.csv`

## Gate verdict

**FAIL_CANDIDATE_GATE**

## Summary metrics

| metric | before | after | delta |
|---|---:|---:|---:|
| target top-3 rows | 5 | 7 | 2 |
| target top-5 rows | 11 | 11 | 0 |
| target top-10 rows | 15 | 16 | 1 |
| target rank > 50 rows | 3 | 3 | 0 |
| mean worst suppress gap | -4.9541279983520505 | -5.247486562728882 | -0.29335856437683105 |
| mean multi-pair hinge | 2.879263942718506 | 3.0207434062957765 | 0.1414794635772707 |
| teacher beats worst suppress rows | 0 | 0 | 0 |
| teacher beats all suppressors rows | 0 | 0 | 0 |

## Row movement

| metric | count |
|---|---:|
| rank improved | 11 |
| rank unchanged | 5 |
| rank regressed | 9 |
| target probability improved | 11 |
| target probability regressed | 14 |
| worst suppress gap improved | 9 |
| worst suppress gap regressed | 16 |
| multi-pair hinge improved | 10 |
| multi-pair hinge regressed | 15 |
| protected top-10 regressions | 0 |

## Worst rank regressions

| case_id | rank_before | rank_after | delta | prob_delta | worst_gap_delta | hinge_delta |
|---|---:|---:|---:|---:|---:|---:|
| legacy_g5_m12 | 69 | 91 | 22 | -0.00017866 | -0.431882 | 0.661270 |
| legacy_g1_m8 | 102 | 111 | 9 | -0.00006819 | 0.143696 | 0.855967 |
| legacy_g5_m14 | 17 | 24 | 7 | -0.00069125 | -0.357956 | 0.568559 |
| legacy_g5_m30 | 73 | 78 | 5 | -0.00006606 | -0.397183 | 0.233783 |
| legacy_g3_m26 | 5 | 9 | 4 | 0.00243183 | 0.709764 | 0.645326 |
| legacy_g2_m11 | 12 | 15 | 3 | -0.00029632 | -3.178347 | 1.570857 |
| legacy_g1_m4 | 4 | 5 | 1 | -0.00591549 | -0.691530 | 0.423307 |
| legacy_g2_m7 | 4 | 5 | 1 | -0.00913884 | -0.763392 | 0.802688 |
| legacy_g5_m8 | 2 | 3 | 1 | -0.01399989 | -0.164446 | 0.175677 |
| legacy_g1_m6 | 4 | 4 | 0 | 0.04468787 | 1.044686 | -0.666310 |

## Worst suppress-gap regressions

| case_id | rank_before | rank_after | prob_delta | worst_gap_delta | hinge_delta |
|---|---:|---:|---:|---:|---:|
| legacy_g2_m11 | 12 | 15 | -0.00029632 | -3.178347 | 1.570857 |
| legacy_g4_m17 | 4 | 4 | -0.00442304 | -2.687423 | 1.063270 |
| legacy_g6_m19 | 7 | 6 | -0.02007929 | -1.860752 | 1.006913 |
| legacy_g2_m21 | 47 | 45 | -0.00011804 | -1.785959 | 0.693484 |
| legacy_g2_m9 | 3 | 3 | -0.03450305 | -1.150988 | 0.034202 |
| legacy_g2_m7 | 4 | 5 | -0.00913884 | -0.763392 | 0.802688 |
| legacy_g1_m4 | 4 | 5 | -0.00591549 | -0.691530 | 0.423307 |
| legacy_g5_m6 | 3 | 2 | -0.00187490 | -0.528240 | 0.003388 |
| legacy_g5_m12 | 69 | 91 | -0.00017866 | -0.431882 | 0.661270 |
| legacy_g5_m30 | 73 | 78 | -0.00006606 | -0.397183 | 0.233783 |

## Interpretation

Run1 is rejected. The candidate failed the rank/top-k gate and showed visible local regressions.

The first CSV rows already show the failure mode: several rows lose target probability, some target ranks regress, and some worst-suppress gaps become more negative. This means the combined CE + mean-pair hinge + worst-hinge objective at the current weights is not reliably moving the teacher target into useful top-k bands.

Do not tune toward export from this checkpoint. The next experiment should be treated as a new objective/weighting probe, not as a continuation of run1.

## Decision

- Reject run1.
- Delete local checkpoint after recording the reports.
- Commit only reports/metrics/closeout.
- Do not export.
- Do not run public benchmark.
- Do not promote.

## Recommended next direction

Use a more conservative objective before another saved checkpoint run:

1. First run a no-save ablation with lower pair/worst hinge pressure.
2. Prefer CE-dominant target lifting plus weak suppress regularization.
3. Consider protecting baseline top-10 rows by downweighting rows where the teacher target is already top-10.
4. Only save a new checkpoint after a no-save ablation shows positive rank/top-k movement without large gap regressions.

Suggested next branch:

`exp/15x15-policy-only-rank-topk-training-run2-ablation`
