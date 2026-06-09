# Candidate E teacher repair dry-run

## Scope

This is a diagnostic dry-run only. It does not train a checkpoint, save a
Candidate E checkpoint, promote Candidate D or Candidate E, overwrite
`15x15_current_best.pt`, change engine behavior, or change Rapfi smoke settings.

Inputs:

- teacher ledger: `analysis/integration_eval/candidate_d_rapfi_teacher_ledger.md`
- debug snapshots: `analysis/integration_eval/candidate_d_mcts32_debug_failure_snapshots.json`
- init/reference checkpoint: `checkpoints/15x15_current_best_margin_candidate_d_move15_lastmove.pt`
- dry-run command: `PYTHONPATH=src python scripts/train_v12l_margin_repair.py --dataset /private/tmp/candidate_e_teacher_repair_dryrun_dataset.json --anchor-snapshots /private/tmp/no_candidate_e_anchors.json --init-checkpoint checkpoints/15x15_current_best_margin_candidate_d_move15_lastmove.pt --reference-checkpoint checkpoints/15x15_current_best_margin_candidate_d_move15_lastmove.pt --out-checkpoint /private/tmp/unused_candidate_e_teacher_repair.pt --dry-run`

The temporary dataset contained only the two Candidate D mcts32 game2 positions
where Rapfi teacher differed from Candidate D:

- move15: target Rapfi teacher `7,9` over Candidate D direct/MCTS `7,10`
- move17: target Rapfi teacher `9,9` over Candidate D direct/MCTS `9,5`

The dry-run script printed `dry-run only; not training or saving`.

## Dry-run ledger

| game | move | side | candidate_direct | candidate_mcts | rapfi_teacher | teacher_prob | teacher_rank | candidate_prob | candidate_rank | logit_gap_teacher_minus_candidate | value | teacher_safe | suitability |
| --- | ---: | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 2 | 15 | white | 7,10 | 7,10 | 7,9 | 0.00472709 | 5 | 0.89996898 | 1 | -5.249052 | -0.114185 | yes | risky |
| 2 | 17 | white | 9,5 | 9,5 | 9,9 | 0.00163610 | 40 | 0.59020567 | 1 | -5.888158 | -0.401257 | yes | reject for single-step repair |

## Position notes

### Game2 move15

- Candidate D direct and MCTS final both choose `7,10`.
- Rapfi teacher chooses `7,9`, and the teacher move passes current safety/fork checks.
- The policy gap is large: teacher rank 5 and probability `0.00472709` versus Candidate D rank 1 and probability `0.89996898`.
- The value estimate is near neutral at `-0.114185` despite the known losing trajectory.
- Suitability: risky. This is a real teacher divergence, but it directly conflicts with the Candidate D move15 repair that fixed `7,10` over the previous bad `8,8`. A margin repair from `7,10` to `7,9` should not be used as a Candidate E target unless a separate audit proves it preserves the Candidate D move15 fix and improves the same Rapfi smoke path.

### Game2 move17

- Candidate D direct and MCTS final both choose `9,5`.
- Rapfi teacher chooses `9,9`, and the teacher move passes current safety/fork checks.
- The policy gap is very large: teacher rank 40 and probability `0.00163610` versus Candidate D rank 1 and probability `0.59020567`.
- The value estimate is losing but not decisive at `-0.401257`.
- Suitability: reject for single-step repair. The teacher move is legal and safe, but the rank/probability gap is too large for a small explainable margin repair. This is better treated as evidence for teacher-supervised data or value/search diagnostics, not as a narrow Candidate E margin target.

## Conclusion

Neither divergence point is currently suitable for a small Candidate E
single-position margin repair.

- Move15 is the more interesting teacher/data-gap case, but it conflicts with
  the newly fixed Candidate D move15 behavior and needs a separate retention
  audit before any training.
- Move17 is too far from the model's policy manifold for a minimal margin repair
  target: rank 40, probability `0.00163610`, and logit gap `-5.888158`.

Recommended next step: keep this as a dry-run teacher ledger. Do not train or
promote Candidate E from these two targets alone.
