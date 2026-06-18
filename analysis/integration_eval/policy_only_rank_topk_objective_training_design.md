# Policy-only rank/top-k objective training design

## Branch

exp/15x15-policy-only-rank-topk-objective-design

## Purpose

Design and audit the next policy-only repair objective after the multi-suppress dry-run.

This branch is design-only. It must not train a model, export weights, run public benchmark games, or promote any checkpoint.

## Context

The latest pushed chain established:

1. exp/15x15-policy-only-teacher-divergence-repair-probe
   - confirmed the 25-row single-suppress pairwise margin dataset is usable.

2. exp/15x15-policy-only-teacher-divergence-repair-train
   - policy-only single-suppress training improved most local metrics:
     - 24/25 gap improved
     - 24/25 target probability improved
     - 8/25 target rank improved
     - 0 rank regressed
     - mean delta gap +0.148287
   - however, all teacher-vs-suppress gaps remained negative.
   - decision: no export, no public benchmark, no promotion.

3. exp/15x15-policy-only-objective-gate-design
   - concluded that the next objective should be stronger than single-suppress pairwise margin.
   - preferred directions: multi-suppress or rank/top-k oriented gate.

4. exp/15x15-policy-only-multisuppress-audit
   - confirmed the existing trainer/dataset were single-suppress only.
   - recommended a new multi-suppress builder/trainer dry-run.

5. exp/15x15-policy-only-multisuppress-dryrun
   - implemented multi-suppress dataset builder and trainer dry-run path.
   - confirmed schema/scoring path works.
   - concluded that immediate training is still risky because the primary current_best direct move remains the aggregate worst suppressor.

## Inputs reviewed

- scripts/build_rapfi_teacher_policy_multisuppress_dataset.py
- scripts/train_rapfi_teacher_policy_multisuppress_margin.py
- analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json
- analysis/integration_eval/policy_only_multisuppress_dataset_build.log
- analysis/integration_eval/policy_only_multisuppress_dryrun.log
- analysis/integration_eval/policy_only_multisuppress_dryrun_metrics.csv
- analysis/integration_eval/policy_only_multisuppress_dryrun_report.md
- analysis/integration_eval/policy_only_multisuppress_dryrun_closeout.md

## Multi-suppress dry-run facts

Builder result:

- rows written: 25/25
- skipped rows: 0
- suppress count per row: 5

Dry-run result:

- rows: 25
- anchor rows: 32
- target top-3 rows: 5
- target top-5 rows: 11
- target top-10 rows: 15
- target rank greater than 10: 10
- target rank greater than 50: 3
- mean worst suppress gap: -4.954128
- mean multi-pair hinge: 3.524615

Interpretation:

- The multi-suppress dataset is usable.
- The scoring path is usable.
- The current policy still ranks teacher moves too low on a meaningful subset.
- The worst suppressor is often the direct model-preferred move.
- Therefore, a naive multi-suppress hinge training run may over-concentrate on the strongest suppressor without guaranteeing useful top-k movement.

## Core problem

The previous single-suppress objective improved local margins but did not make any margin positive.

The multi-suppress dry-run shows a larger and more realistic repair target, but also shows that the direct policy failure is severe.

The next objective should not be judged only by pairwise teacher-vs-suppress gap. It should be judged by whether the teacher move enters useful rank bands:

- top-3
- top-5
- top-10

The training gate should also protect existing anchors and tactical behavior.

## Objective candidate A: teacher CE only

Train with standard policy cross entropy on the teacher target.

Loss:

    L = CE(policy_logits, teacher_target)

Pros:

- simple
- directly raises teacher target probability
- less brittle than a pure hinge objective

Cons:

- does not explicitly demote high-probability bad alternatives
- may be too weak for rows where the teacher target is far outside top-k
- may require excessive weight to move low-rank teacher targets

Decision:

- Useful as a conservative baseline.
- Not preferred as the main next objective.

## Objective candidate B: pure multi-suppress hinge

For each row, require the teacher target logit to exceed every suppress move logit by a margin.

Constraint:

    logit_teacher >= logit_suppress_i + margin

Loss:

    L = mean_i max(0, margin - (logit_teacher - logit_suppress_i))

Pros:

- directly attacks the known failure mode
- uses the new multi-suppress dataset naturally
- easy to inspect with the existing dry-run metrics

Cons:

- can be dominated by the single worst suppressor
- does not explicitly optimize target rank bands
- may damage anchor behavior if the step is too strong
- does not distinguish between improving rank from 70 to 20 and improving rank from 11 to 5

Decision:

- Keep as a diagnostic component.
- Do not use alone as the next training objective.

## Objective candidate C: CE plus mean-pair hinge plus worst-suppress hinge

Use CE to raise the teacher target globally, mean-pair hinge to demote the suppress set, and worst-suppress hinge to directly attack the strongest bad alternative.

Recommended loss:

    L = CE(policy_logits, teacher_target)
      + lambda_pair * mean_i hinge(teacher, suppress_i)
      + lambda_worst * hinge(teacher, worst_suppress)

Where:

    hinge(teacher, suppress) = max(0, margin - (logit_teacher - logit_suppress))

Recommended first probe parameters:

    margin = 0.25
    lambda_pair = 0.25
    lambda_worst = 0.50

Rationale:

- CE improves target probability directly.
- Mean-pair hinge prevents the model from ignoring the suppress set.
- Worst-suppress hinge specifically targets the strongest bad alternative.
- Conservative weights reduce the chance of anchor damage.

Decision:

- Preferred first real training objective after the gate evaluator exists.
- Do not train it on this branch.

## Objective candidate D: local listwise softmax over teacher plus suppress set

Construct a local candidate list per row:

    C = [teacher_target, suppress_1, suppress_2, suppress_3, suppress_4, suppress_5]

Apply softmax CE over only this local list, with the teacher target as the correct class.

Loss:

    L = CE(local_logits(C), class=teacher_target)

Pros:

- naturally listwise
- directly models the teacher target against the suppress set
- less dependent on global logit scale
- suitable for multi-suppress data

Cons:

- ignores legal moves outside the local candidate list
- may overfit to selected suppressors
- still requires anchor retention checks
- may not improve global top-k rank if other non-listed moves remain above the teacher target

Decision:

- Strong second candidate.
- Prefer after evaluating Candidate C or as an ablation.

## Required rank/top-k training gate

Before any new policy-only training probe is considered successful, it must pass a rank/top-k gate.

The gate should compare baseline checkpoint vs candidate checkpoint on the same rows.

### Divergence-row rank gate

On the 25 teacher-divergence rows:

Required metrics:

- target rank before
- target rank after
- target probability before
- target probability after
- target top-3 before/after
- target top-5 before/after
- target top-10 before/after
- target rank greater than 50 before/after

Suggested first-pass threshold:

    top3_delta >= +2
    top5_delta >= +3
    top10_delta >= +3
    rank_gt50_delta <= 0
    protected_top10_regressions = 0

Protected-top10 rule:

- If a baseline row already has teacher target rank <= 10, the candidate must not push it outside top-10.

### Suppress-gap gate

On the 25 teacher-divergence rows:

Required metrics:

- teacher-vs-each-suppress gap before/after
- worst suppress gap before/after
- mean multi-pair hinge before/after
- teacher beats worst suppress count before/after
- teacher beats all suppressors count before/after

Suggested first-pass threshold:

    mean_worst_suppress_gap_delta > 0
    mean_multi_pair_hinge_delta < 0
    teacher_beats_worst_suppress_delta >= +2
    teacher_beats_all_suppressors_delta >= +1

### Anchor retention gate

On the 32 anchor rows:

Required metrics:

- anchor top-1 before/after
- anchor top-3 before/after
- anchor top-5 before/after
- anchor rank regressions
- anchor probability regressions

Suggested first-pass threshold:

    anchor_top1_regressions <= 1
    anchor_top3_regressions <= 2
    anchor_top5_regressions <= 2
    critical_tactical_anchor_regressions = 0

### Local safety gate

The candidate must not create obvious local collapse:

- no NaN logits
- no invalid policy shape
- no illegal target/suppress coordinates
- no duplicate suppress moves inside a row
- no suppress move equal to teacher target
- no catastrophic target probability collapse on protected rows

## Required implementation before training

Before running any actual training, create a gate evaluator that can compare baseline vs candidate on the exact metrics above.

Recommended next script:

    scripts/evaluate_policy_rank_topk_gate.py

Required inputs:

    --model-a checkpoints/current_best.pt
    --model-b checkpoints/<candidate>.pt
    --multisuppress-dataset analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json
    --out-csv analysis/integration_eval/<candidate>_rank_topk_gate_metrics.csv
    --out-md analysis/integration_eval/<candidate>_rank_topk_gate_report.md

Optional input:

    --anchor-dataset <existing anchor source>

Required output sections:

1. divergence-row rank movement
2. target probability movement
3. suppress-gap movement
4. worst-suppress movement
5. protected top-k regressions
6. anchor retention
7. local safety checks
8. final gate verdict

## Recommended next branch

After this design branch is committed and pushed, open:

    exp/15x15-policy-only-rank-topk-gate-dryrun

Goal of that branch:

- implement scripts/evaluate_policy_rank_topk_gate.py
- run baseline-vs-baseline first
- verify output CSV and Markdown report format
- verify all gate metrics compute correctly
- still do not train

Only after the gate evaluator is stable should a separate training probe branch be opened.

Suggested later training branch name:

    exp/15x15-policy-only-rank-topk-training-probe

## Decision

Do not train on this branch.

Do not export.

Do not run public benchmark.

Do not promote.

Proceed next with a rank/top-k gate evaluator dry-run branch.
