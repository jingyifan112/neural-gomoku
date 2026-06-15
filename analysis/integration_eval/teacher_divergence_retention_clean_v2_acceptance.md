# Clean v2 dataset acceptance report

This is a data acceptance report only. It does not train, export, benchmark, or modify model weights.

## Decision: ACCEPT

- clean v2 dataset passes structural validation
- score-gap source is represented in manifest/audit and does not duplicate baseline rows into training
- retention anchors remain held out
- no training/export/benchmark has been run

## Dataset counts

- dataset rows: 39

### split counts

| split | count |
|---|---:|
| heldout_retention | 11 |
| train_candidate | 3 |
| train_teacher_divergence | 25 |

### role counts

| role | count |
|---|---:|
| heldout_retention_anchor | 11 |
| teacher_divergence | 28 |

### source counts

| source | count |
|---|---:|
| candidate_g_seed_dataset | 3 |
| canonical_baseline_dataset | 36 |

## Train candidate rows

| id | source_id | side | teacher | model/current-best | rank/gap | weight | source |
|---|---|---|---|---|---:|---:|---|
| `tdiv_candidate_g_g1_p22_black` | `g1_p22_black` | black | `4,8` | `4,7` | 54 | 2.0 | candidate_g_seed_dataset |
| `tdiv_candidate_g_g2_p15_white` | `g2_p15_white` | white | `7,9` | `7,10` | 5 | 1.5 | candidate_g_seed_dataset |
| `tdiv_candidate_g_g2_p17_white` | `g2_p17_white` | white | `9,10` | `9,5` | 18 | 2.0 | candidate_g_seed_dataset |

## Manifest counts

- manifest rows: 109
- included: 39
- skipped/audit: 70

### score-gap handling

- score-gap manifest rows: 32

| skip reason | count |
|---|---:|
| duplicate_source_id_already_in_baseline_or_seed | 25 |
| model_matches_teacher | 7 |

### Candidate G seed handling

- Candidate G manifest rows: 14

| skip reason | count |
|---|---:|
| candidate_g_nondivergent_anchor | 11 |
| included | 3 |

### External retention anchor handling

- external retention manifest rows: 27

| skip reason | count |
|---|---:|
| duplicate_source_id | 14 |
| missing_policy_target | 13 |

## Source audit

| source_group | path | exists | rows_seen | rows_included | error |
|---|---|---:|---:|---:|---|
| canonical_baseline_dataset | `analysis/integration_eval/teacher_divergence_retention_dataset.json` | True | 36 | 36 |  |
| candidate_g_seed_dataset | `analysis/integration_eval/candidate_g_teacher_seed_dataset.json` | True | 14 | 3 |  |
| rapfi_scoregap_current_best | `analysis/public_benchmark_eval/rapfi_teacher_scoregap_corpus8_selected.csv` | True | 32 | 0 |  |
| external_retention_anchors | `analysis/integration_eval/candidate_c_g2_m19_perspective_diagnostic_anchors.json` | True | 8 | 0 |  |
| external_retention_anchors | `analysis/integration_eval/candidate_d_g2_m15_diagnostic_anchors.json` | True | 3 | 0 |  |
| external_retention_anchors | `analysis/integration_eval/candidate_e_g2_m13_diagnostic_anchors.json` | True | 1 | 0 |  |
| external_retention_anchors | `analysis/integration_eval/candidate_e_g2_m17_diagnostic_anchors.json` | True | 3 | 0 |  |
| external_retention_anchors | `analysis/integration_eval/current_best_margin_candidate_c_anchors.json` | True | 7 | 0 |  |
| external_retention_anchors | `analysis/integration_eval/current_best_margin_candidate_c_conservative_anchors.json` | True | 5 | 0 |  |

## Acceptance boundary

- Accepted for data/manifest/report tracking.
- Not accepted as evidence that training will improve score ladder until a separate training/probe step is run.
- Held-out retention rows must remain out of teacher-divergence training.
- Capacity changes remain deferred until teacher signal and data volume justify them.
