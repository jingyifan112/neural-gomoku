# Candidate G teacher seed dataset

## Scope

This is a board-state dry-run dataset for Candidate G teacher distillation.

- no training
- no export
- no promotion
- no smoke match

Rows were selected from the Candidate G teacher seed manifest and joined with replayed board state from the Candidate D mcts32 debug log.

## Summary

- manifest rows: 14
- dataset rows: 14
- missing replay rows: 0
- side mismatches: 0

## Role counts

- general_teacher_aligned_anchor: 6
- nearby_nondivergent_anchor: 5
- retention_anchor: 1
- seed_teacher_divergence: 2

## Selected dataset rows

| role | game | ply | side | last move | model | teacher | teacher rank | weight | stones |
|---|---:|---:|---|---|---|---|---:|---:|---:|
| general_teacher_aligned_anchor | 1 | 0 | black | None | 7,7 | 7,7 | 1 | 0.75 | 0 |
| general_teacher_aligned_anchor | 1 | 6 | black | 3,4 | 3,3 | 3,3 | 1 | 0.75 | 6 |
| general_teacher_aligned_anchor | 1 | 16 | black | 6,7 | 5,6 | 5,6 | 3 | 0.75 | 16 |
| general_teacher_aligned_anchor | 1 | 18 | black | 7,6 | 5,8 | 5,8 | 2 | 0.75 | 18 |
| nearby_nondivergent_anchor | 1 | 18 | black | 7,6 | 5,8 | 5,8 | 2 | 1.00 | 18 |
| seed_teacher_divergence | 1 | 22 | black | 6,9 | 4,7 | 4,8 | 54 | 2.00 | 22 |
| nearby_nondivergent_anchor | 1 | 24 | black | 6,5 | 7,5 | 7,5 | 4 | 1.00 | 24 |
| general_teacher_aligned_anchor | 1 | 28 | black | 6,4 | 6,6 | 6,6 | 1 | 0.75 | 28 |
| general_teacher_aligned_anchor | 1 | 40 | black | 7,11 | 8,12 | 8,12 | 3 | 0.75 | 40 |
| nearby_nondivergent_anchor | 2 | 13 | white | 9,8 | 8,8 | 8,8 | 1 | 1.00 | 13 |
| retention_anchor | 2 | 15 | white | 8,9 | 7,10 | 7,9 | 5 | 1.50 | 15 |
| seed_teacher_divergence | 2 | 17 | white | 8,6 | 9,5 | 9,10 | 18 | 2.00 | 17 |
| nearby_nondivergent_anchor | 2 | 19 | white | 9,10 | 10,11 | 10,11 | 39 | 1.00 | 19 |
| nearby_nondivergent_anchor | 2 | 21 | white | 7,9 | 8,10 | 8,10 | 61 | 1.00 | 21 |

## Next step

Review this dry-run dataset before converting it into a trainable tensor dataset or launching any Candidate G training run.
