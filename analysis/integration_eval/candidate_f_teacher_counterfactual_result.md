# Candidate F teacher-counterfactual result

## Scope

This was a minimal teacher-counterfactual fine-tune experiment only. It did not
promote any checkpoint, overwrite `checkpoints/15x15_current_best.pt`, change
engine behavior, change Rapfi smoke settings, change board size/rule/time
control/draw settings/result parsing, or weaken tests.

Inputs:

- teacher ledger: `analysis/integration_eval/candidate_d_rapfi_teacher_ledger.md`
- dry-run ledger: `analysis/integration_eval/candidate_e_teacher_repair_dryrun.md`
- counterfactual validation: `analysis/integration_eval/candidate_e_teacher_counterfactual_validation.md`
- snapshots: `analysis/integration_eval/candidate_d_mcts32_debug_failure_snapshots.json`
- init/reference checkpoint: `checkpoints/15x15_current_best_margin_candidate_d_move15_lastmove.pt`

Output checkpoint:

- `checkpoints/15x15_current_best_candidate_f_teacher_counterfactual.pt`

This checkpoint is experimental and should not be promoted.

## Dataset

Dataset path:

- `analysis/integration_eval/candidate_f_teacher_counterfactual_dataset.json`

Samples:

| case | game | move | side | target | suppress | purpose |
| --- | ---: | ---: | --- | --- | --- | --- |
| `candidate_f_anchor_candidate_d_move15_retain_7_10_over_8_8` | 2 | 15 | white | `7,10` | `8,8` | Preserve Candidate D move15 regression with true last move `8,9`. |
| `candidate_f_g2_m15_teacher_7_9_over_candidate_d_7_10` | 2 | 15 | white | `7,9` | `7,10` | Rapfi teacher move over Candidate D direct/MCTS move. |
| `candidate_f_g2_m17_teacher_9_9_over_candidate_d_9_5` | 2 | 17 | white | `9,9` | `9,5` | Rapfi teacher move over Candidate D direct/MCTS move. |

The existing `scripts/train_v12l_margin_repair.py` tooling supports policy
margin loss plus anchor KL/value preservation. It does not support an explicit
teacher-vs-original value-margin label, so no separate value-margin objective
was added.

## Training

Dry-run command:

```bash
PYTHONPATH=src python scripts/train_v12l_margin_repair.py \
  --dataset analysis/integration_eval/candidate_f_teacher_counterfactual_dataset.json \
  --anchor-snapshots analysis/integration_eval/candidate_d_mcts32_debug_failure_snapshots.json \
  --init-checkpoint checkpoints/15x15_current_best_margin_candidate_d_move15_lastmove.pt \
  --reference-checkpoint checkpoints/15x15_current_best_margin_candidate_d_move15_lastmove.pt \
  --out-checkpoint checkpoints/15x15_current_best_candidate_f_teacher_counterfactual.pt \
  --margin 0.5 --lr 1e-5 --epochs 20 \
  --anchor-kl-weight 0.05 --anchor-value-weight 0.05 \
  --print-every 5 --dry-run
```

The 20-epoch version was tested first and rejected because it broke the
Candidate D move15 retention anchor: `7,10` fell below old bad move `8,8`.
Anchor-duplicated temporary variants in `/private/tmp` had the same failure
pattern. The final named Candidate F checkpoint therefore uses the conservative
5-epoch run:

```bash
PYTHONPATH=src python scripts/train_v12l_margin_repair.py \
  --dataset analysis/integration_eval/candidate_f_teacher_counterfactual_dataset.json \
  --anchor-snapshots analysis/integration_eval/candidate_d_mcts32_debug_failure_snapshots.json \
  --init-checkpoint checkpoints/15x15_current_best_margin_candidate_d_move15_lastmove.pt \
  --reference-checkpoint checkpoints/15x15_current_best_margin_candidate_d_move15_lastmove.pt \
  --out-checkpoint checkpoints/15x15_current_best_candidate_f_teacher_counterfactual.pt \
  --margin 0.5 --lr 1e-5 --epochs 5 \
  --anchor-kl-weight 0.05 --anchor-value-weight 0.05 \
  --print-every 5
```

## Focused Diagnostics

Saved-checkpoint verification command:

```bash
PYTHONPATH=src python scripts/train_v12l_margin_repair.py \
  --dataset analysis/integration_eval/candidate_f_teacher_counterfactual_dataset.json \
  --anchor-snapshots analysis/integration_eval/candidate_d_mcts32_debug_failure_snapshots.json \
  --init-checkpoint checkpoints/15x15_current_best_candidate_f_teacher_counterfactual.pt \
  --reference-checkpoint checkpoints/15x15_current_best_margin_candidate_d_move15_lastmove.pt \
  --out-checkpoint /private/tmp/unused_candidate_f_verify.pt \
  --margin 0.5 --lr 1e-5 --epochs 1 \
  --anchor-kl-weight 0.05 --anchor-value-weight 0.05 \
  --print-every 1 --dry-run
```

Policy/value comparison:

| case | metric | Candidate D before | Candidate F after |
| --- | --- | ---: | ---: |
| move15 retention `7,10` over `8,8` | target prob | 0.57045883 | 0.28233194 |
| move15 retention `7,10` over `8,8` | suppress prob | 0.08911545 | 0.15411831 |
| move15 retention `7,10` over `8,8` | target rank | 1 | 1 |
| move15 retention `7,10` over `8,8` | suppress rank | 3 | 3 |
| move15 retention `7,10` over `8,8` | logit gap | 1.856508 | 0.605363 |
| move15 retention `7,10` over `8,8` | value | -0.383926 | -0.537421 |
| move15 teacher `7,9` over `7,10` | target prob | 0.00472709 | 0.04495326 |
| move15 teacher `7,9` over `7,10` | suppress prob | 0.89996898 | 0.75868112 |
| move15 teacher `7,9` over `7,10` | target rank | 5 | 4 |
| move15 teacher `7,9` over `7,10` | suppress rank | 1 | 1 |
| move15 teacher `7,9` over `7,10` | logit gap | -5.249052 | -2.825958 |
| move15 teacher `7,9` over `7,10` | value | -0.114185 | -0.146546 |
| move17 teacher `9,9` over `9,5` | target prob | 0.00163610 | 0.00203554 |
| move17 teacher `9,9` over `9,5` | suppress prob | 0.59020567 | 0.50910848 |
| move17 teacher `9,9` over `9,5` | target rank | 40 | 28 |
| move17 teacher `9,9` over `9,5` | suppress rank | 1 | 1 |
| move17 teacher `9,9` over `9,5` | logit gap | -5.888158 | -5.521900 |
| move17 teacher `9,9` over `9,5` | value | -0.401257 | -0.517176 |

Result:

- Candidate D move15 retention stayed fixed in the narrow policy-margin
  diagnostic: `7,10` remains rank 1 and above `8,8`.
- Move15 teacher target improved substantially but did not overtake Candidate
  D's original `7,10`; `7,10` remains rank 1.
- Move17 teacher target improved only slightly and remains far behind Candidate
  D's original `9,5`; `9,5` remains rank 1.
- The value head did not learn the Rapfi counterfactual preference. Both
  teacher positions became more negative from the side-to-move perspective.

No unit tests were added because no source code changed. The focused diagnostic
was the existing read-only dry-run path for `scripts/train_v12l_margin_repair.py`.

## Smoke And Export

C weights were not exported. The Python-side diagnostics did not fully pass the
teacher-target gate because neither teacher move became preferred over Candidate
D's original move.

Rapfi smoke was not run. Running smoke would require C export, and the focused
diagnostics already showed that Candidate F is still expected to choose the
Candidate D original moves at the two teacher divergence points.

## Conclusion

Candidate F should not be promoted.

The experiment is useful as a negative/partial result:

- A small policy-margin fine-tune can move the teacher targets in the desired
  direction while preserving the Candidate D move15 regression only if the run
  is kept very conservative.
- A stronger run can make move15 teacher `7,9` preferred, but it breaks the
  Candidate D move15 retention anchor by dropping `7,10` below old bad `8,8`.
- Move17 remains too far from Candidate D's policy manifold for this minimal
  teacher-counterfactual repair.
- The current training script lacks the value-margin supervision needed to
  encode the Rapfi counterfactual result directly.

Recommended next step: do not promote Candidate F. Treat these two positions as
teacher/value disagreement evidence and consider a proper value-oriented or
teacher-supervised data path before another smoke attempt.
