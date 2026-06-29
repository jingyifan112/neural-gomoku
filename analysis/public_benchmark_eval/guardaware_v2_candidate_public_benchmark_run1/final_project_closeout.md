# 15x15 neural-gomoku project closeout

## Branch

`exp/15x15-rank-topk-b4c64-guardaware-v2-modefix-saved-candidate-run1`

## Final committed benchmark artifact

- Public benchmark Excel:
  `analysis/public_benchmark_eval/guardaware_v2_candidate_public_benchmark_run1/guardaware_v2_candidate_public_score_table.xlsx`
- Candidate score CSV:
  `analysis/public_benchmark_eval/guardaware_v2_candidate_public_benchmark_run1/candidate_public_benchmark_score_summary.csv`
- Candidate benchmark report:
  `analysis/public_benchmark_eval/guardaware_v2_candidate_public_benchmark_run1/candidate_public_benchmark_score_report.md`

## Candidate

- Checkpoint used locally:
  `checkpoints/probes/15x15_b4c64_guardaware_v2_modefix_candidate_run1.pt`
- Candidate SHA256:
  `bdb0020ac851d9c9a4ff7b369364d719d21574d8a53659b4c98c3aa3878d662a`
- Architecture:
  - board size: 15
  - win length: 5
  - channels: 64
  - residual blocks: 4
- C export was used only for public benchmark scoring.
- No current-best overwrite was performed.

## Public benchmark result

| Baseline opponent | Candidate config | Candidate score / 24 | W-L-D | Gap vs Rapfi full |
|---|---|---:|---:|---:|
| random | MCTS32 | 24.0 | 24-0-0 | 0.0 |
| tactical_lite | MCTS32 | 23.0 | 23-1-0 | -1.0 |
| tactical_mid | MCTS16 | 7.0 | 6-16-2 | -17.0 |
| tactical_plus | MCTS16 | 3.0 | 2-20-2 | -21.0 |
| rapfi_fast_depth1 | MCTS32 | 0.0 | 0-24-0 | -24.0 |

## Interpretation

The saved candidate matched the previous current-best public benchmark ladder:

`24, 23, 7, 3, 0`

This does not prove that increasing model capacity or increasing teacher-divergence training data is fundamentally wrong. It shows that this specific conservative b4c64 guard-aware candidate route did not translate the training/gate-side changes into public benchmark improvement.

Likely explanation:

- The route was intentionally conservative.
- The final saved candidate used tiny learning rate and one epoch to avoid damaging hard-guard rows.
- Gate safety was preserved, but public tactical strength did not improve.
- The remaining public benchmark weakness is still tactical search/forcing strength, especially against tactical_mid, tactical_plus, and rapfi_fast_depth1.

## Final decision

- Do not promote this candidate.
- Do not overwrite current-best.
- Treat the public benchmark Excel as the final score table for this project stage.
- Close this project stage as complete.

## Recommended future direction, if reopened

Only reopen if there is a new scoped objective, for example:

1. stronger tactical-search-aware training target;
2. larger, cleaner teacher-divergence dataset with explicit tactical failure labels;
3. capacity upgrade only after a dataset/gate demonstrates transferable benchmark signal;
4. separate Rapfi-depth or tactical-suite target rather than another tiny b4c64 safe update.

No further action is required for the current project stage.
