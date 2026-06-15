# Safety v3 dataset acceptance report

## Decision: ACCEPT

- safety v3 dataset passes structural validation
- only current_best eval-family safety-block candidates are accepted
- one candidate per sample_id is retained using snapshot priority
- no training/export/benchmark has been run

## Counts

- base rows: 39
- new rows: 5
- total rows: 44
- manifest rows: 36
- accepted manifest rows: 5
- skipped manifest rows: 31

## Validation

- errors: []
- warnings: []

## Accepted samples

| sample | side | target | expected | direct | top | final | snapshot |
|---|---|---|---|---|---|---|---|
| `legacy_g1_m44` | black | `2,10` | `2,10` | `10,7` | `10,7` | `2,10` | b_mcts16 |
| `legacy_g1_m46` | black | `4,12` | `4,12` | `2,9` | `10,7` | `4,12` | b_mcts16 |
| `legacy_g1_m48` | black | `8,11` | `3,11 8,11` | `10,7` | `10,7` | `8,11` | b_mcts16 |
| `legacy_g2_m29` | white | `4,9` | `4,9` | `3,4` | `3,4` | `4,9` | candidate_d_mcts32_nearend |
| `legacy_g2_m33` | white | `9,6` | `9,11 9,6` | `10,8` | `7,5` | `9,6` | candidate_d_mcts32_nearend |

## Boundary

- Accepted for dataset/manifest/report tracking only.
- Do not train from this until a separate probe plan is created.
- Do not export C weights from this step.
