# Policy-only rank/top-k training run2 ablation closeout

## Branch

`exp/15x15-policy-only-rank-topk-training-run2-ablation`

## Scope

Run2 was a no-save ablation only.

No checkpoint was saved. No C export, public benchmark, or promotion was run.

## Ablations

### Run2A: CE-only

Configuration:

- epochs: 20
- lr: 3e-6
- margin: 0.25
- ce_weight: 1.0
- pair_weight: 0.0
- worst_weight: 0.0
- anchor_kl_weight: 0.05
- no-save: true

### Run2B: CE + weak suppress

Configuration:

- epochs: 20
- lr: 3e-6
- margin: 0.25
- ce_weight: 1.0
- pair_weight: 0.05
- worst_weight: 0.10
- anchor_kl_weight: 0.05
- no-save: true

## Results

| metric | run2A before | run2A after | run2A delta | run2B before | run2B after | run2B delta |
|---|---:|---:|---:|---:|---:|---:|
| top3 | 7 | 7 | 0.0 | 7 | 7 | 0.0 |
| top5 | 11 | 11 | 0.0 | 11 | 11 | 0.0 |
| top10 | 15 | 16 | 1.0 | 15 | 16 | 1.0 |
| rank_gt50 | 2 | 3 | 1.0 | 2 | 3 | 1.0 |
| mean_rank | 15.48 | 19.12 | 3.64 | 15.48 | 19.12 | 3.64 |
| mean_target_prob | 0.0290818578 | 0.0227206219 | -0.0063612359 | 0.0290818578 | 0.0227248551 | -0.0063570027 |
| mean_worst_gap | -5.7818367118 | -5.2476167488 | 0.5342199630 | -5.7818367118 | -5.2475705814 | 0.5342661303 |
| mean_pair_hinge_margin_025 | 3.1210833648 | 3.0206813889 | -0.1004019760 | 3.1210833648 | 3.0207215900 | -0.1003617748 |
| teacher_beats_worst | 1 | 0 | -1.0 | 1 | 0 | -1.0 |
| teacher_beats_all | 1 | 0 | -1.0 | 1 | 0 | -1.0 |

## Interpretation

Run2A and Run2B are both rejected.

The ablations improved mean worst-suppress gap and mean pairwise hinge, but they did not produce useful rank/top-k movement.

The dangerous regressions are:

- target top3 did not improve;
- target top5 did not improve;
- target top10 improved by only one row;
- rank_gt50 worsened by one row;
- mean target rank worsened substantially;
- mean target probability decreased;
- teacher_beats_worst decreased;
- teacher_beats_all decreased.

Run2B is nearly identical to Run2A, which means the weak suppress terms were not the deciding factor. The CE-dominant update itself is not safe under this setup.

## Decision

Reject run2.

Do not save a checkpoint.

Do not run gate evaluation from a saved checkpoint.

Do not export.

Do not run public benchmark.

Do not promote.

## Recommended next direction

The current full-dataset update is too unstable even when no suppress term is used.

The next branch should not continue increasing CE or suppress weights. Instead, it should audit weighting and protection strategy.

Recommended next branch:

`exp/15x15-policy-only-rank-topk-protected-weighting-audit`

Recommended audit questions:

1. Are high-weight hard rows dominating and damaging easier top-k rows?
2. Should rows with baseline target rank <= 10 be protected or downweighted?
3. Should target-rank > 50 rows be isolated instead of trained together with near-top10 rows?
4. Should the next objective optimize only a small priority bucket first?
5. Should training use a much smaller update budget, such as epochs 1-3 or lr 1e-6, before any saved checkpoint?

The next step should be audit/design, not another checkpoint-saving run.
