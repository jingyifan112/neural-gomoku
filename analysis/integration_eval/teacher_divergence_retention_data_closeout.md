# Teacher-divergence / held-out retention data closeout

This closeout records the data-construction boundary for the `exp/15x15-teacher-divergence-retention-data` branch.

No training, C export, model promotion, public benchmark run, or capacity experiment was performed in this step.

## Accepted datasets

### Clean v2

Artifact set:

- `analysis/integration_eval/teacher_divergence_retention_clean_v2_dataset.json`
- `analysis/integration_eval/teacher_divergence_retention_clean_v2_manifest.csv`
- `analysis/integration_eval/teacher_divergence_retention_clean_v2_report.md`
- `analysis/integration_eval/teacher_divergence_retention_clean_v2_acceptance.md`
- `analysis/integration_eval/teacher_divergence_retention_clean_v2_acceptance.json`

Accepted boundary:

- dataset rows: 39
- train teacher-divergence baseline rows: 25
- train candidate rows from Candidate G seed: 3
- held-out retention rows: 11
- acceptance decision: ACCEPT
- validation errors: none
- validation warnings: none

Clean v2 intentionally treats score-gap rows as audit coverage, not duplicate training rows:

- 25 score-gap rows were already covered by canonical baseline source ids.
- 7 score-gap rows matched the teacher/current-best move and were not added as divergence rows.

### Safety v3

Artifact set:

- `analysis/integration_eval/safety_block_candidate_manifest.csv`
- `analysis/integration_eval/safety_block_candidate_manifest.json`
- `analysis/integration_eval/safety_block_candidate_report.md`
- `analysis/integration_eval/teacher_divergence_retention_safety_v3_dataset.json`
- `analysis/integration_eval/teacher_divergence_retention_safety_v3_manifest.csv`
- `analysis/integration_eval/teacher_divergence_retention_safety_v3_report.md`
- `analysis/integration_eval/teacher_divergence_retention_safety_v3_acceptance.md`
- `analysis/integration_eval/teacher_divergence_retention_safety_v3_acceptance.json`

Accepted boundary:

- base clean v2 rows: 39
- new safety-block rows: 5
- total v3 rows: 44
- train teacher-divergence baseline rows: 25
- train candidate rows: 8
  - 3 Candidate G teacher-divergence seed rows
  - 5 safety-block immediate-threat rows
- held-out retention rows: 11
- acceptance decision: ACCEPT
- validation errors: none
- validation warnings: none

Accepted safety-block samples:

| sample | side | target | expected block(s) | direct | top | final | snapshot source |
|---|---|---|---|---|---|---|---|
| `legacy_g1_m44` | black | `2,10` | `2,10` | `10,7` | `10,7` | `2,10` | `b_mcts16` |
| `legacy_g1_m46` | black | `4,12` | `4,12` | `2,9` | `10,7` | `4,12` | `b_mcts16` |
| `legacy_g1_m48` | black | `8,11` | `3,11 8,11` | `10,7` | `10,7` | `8,11` | `b_mcts16` |
| `legacy_g2_m29` | white | `4,9` | `4,9` | `3,4` | `3,4` | `4,9` | `candidate_d_mcts32_nearend` |
| `legacy_g2_m33` | white | `9,6` | `9,11 9,6` | `10,8` | `7,5` | `9,6` | `candidate_d_mcts32_nearend` |

## Interpretation

This branch establishes a cleaner data boundary for future 15x15 improvement experiments.

The current conclusion is data-construction only:

- The project has a small accepted teacher-divergence / retention dataset.
- The v3 dataset adds five concrete immediate-threat safety-block teacher candidates.
- Held-out retention rows remain separated from training rows.
- Score-gap evidence is represented in manifests/reports without duplicating canonical rows.
- This branch does not provide training, benchmark, export, or model-promotion evidence.

## Recommended next step

The next step should be a small controlled training/probe experiment using the accepted v3 dataset.

The experiment should be treated as a data-signal probe, not a capacity conclusion. Capacity changes should remain deferred until teacher signal and data volume justify them.

Recommended next experimental boundary:

1. Train a small policy-focused candidate from current-best using only the accepted train rows.
2. Probe the 8 train-candidate rows directly.
3. Probe the 11 held-out retention rows.
4. Do not export C weights unless Python-side probe results are positive.
5. Do not claim public benchmark improvement unless a separate public benchmark run confirms it.
