# Candidate G teacher seed manifest

## Scope

This is a dry-run selection manifest for Candidate G teacher distillation.

- no training
- no export
- no promotion
- no smoke match

The manifest is not yet a trainable dataset because the source census CSV does not include full board tensors or last-move planes.

## Selection counts

- total_selected: 14
- seed_teacher_divergence: 2
- retention_anchor: 1
- nearby_nondivergent_anchor: 5
- general_teacher_aligned_anchor: 6

## Selected rows

| role | game | ply | side | model | teacher | teacher rank | teacher prob | model prob | weight | reason |
|---|---:|---:|---|---|---|---:|---:|---:|---:|---|
| general_teacher_aligned_anchor | 1 | 0 | black | 7,7 | 7,7 | 1 | 0.97672105 | 0.97672105 | 0.75 | teacher-aligned top-3 policy retention anchor |
| general_teacher_aligned_anchor | 1 | 6 | black | 3,3 | 3,3 | 1 | 0.31756800 | 0.31756800 | 0.75 | teacher-aligned top-3 policy retention anchor |
| general_teacher_aligned_anchor | 1 | 16 | black | 5,6 | 5,6 | 3 | 0.10252603 | 0.10252603 | 0.75 | teacher-aligned top-3 policy retention anchor |
| general_teacher_aligned_anchor | 1 | 18 | black | 5,8 | 5,8 | 2 | 0.29127601 | 0.29127601 | 0.75 | teacher-aligned top-3 policy retention anchor |
| nearby_nondivergent_anchor | 1 | 18 | black | 5,8 | 5,8 | 2 | 0.29127601 | 0.29127601 | 1.00 | non-divergent anchor within ±4 plies of seed g1 p22 |
| seed_teacher_divergence | 1 | 22 | black | 4,7 | 4,8 | 54 | 0.00005404 | 0.45865965 | 2.00 | strong teacher continuation preference and model/teacher divergence |
| nearby_nondivergent_anchor | 1 | 24 | black | 7,5 | 7,5 | 4 | 0.01789638 | 0.01789638 | 1.00 | non-divergent anchor within ±4 plies of seed g1 p22 |
| general_teacher_aligned_anchor | 1 | 28 | black | 6,6 | 6,6 | 1 | 0.56154114 | 0.56154114 | 0.75 | teacher-aligned top-3 policy retention anchor |
| general_teacher_aligned_anchor | 1 | 40 | black | 8,12 | 8,12 | 3 | 0.10064502 | 0.10064502 | 0.75 | teacher-aligned top-3 policy retention anchor |
| nearby_nondivergent_anchor | 2 | 13 | white | 8,8 | 8,8 | 1 | 0.17895336 | 0.17895336 | 1.00 | non-divergent anchor within ±4 plies of seed g2 p17 |
| retention_anchor | 2 | 15 | white | 7,10 | 7,9 | 5 | 0.00472709 | 0.89996898 | 1.50 | Candidate D move15 repair neighborhood anchor |
| seed_teacher_divergence | 2 | 17 | white | 9,5 | 9,10 | 18 | 0.00464902 | 0.59020561 | 2.00 | strong teacher continuation preference and model/teacher divergence |
| nearby_nondivergent_anchor | 2 | 19 | white | 10,11 | 10,11 | 39 | 0.00255240 | 0.00255240 | 1.00 | non-divergent anchor within ±4 plies of seed g2 p17 |
| nearby_nondivergent_anchor | 2 | 21 | white | 8,10 | 8,10 | 61 | 0.00181551 | 0.00181551 | 1.00 | non-divergent anchor within ±4 plies of seed g2 p17 |

## Next step

Modify the replay/census pipeline to emit full board state and last-move plane for these selected rows before any training run.
