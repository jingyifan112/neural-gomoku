# Retention family split dry-run closeout

Scope: closeout report only. No training, checkpoint save, C export, benchmark, or promotion was run.

## Branch and commit context

- branch: `exp/15x15-retention-family-split-dryrun-closeout`
- HEAD: `b7599c6 Add retention family split application dry run`

Recent branch chain:

```text
b7599c6 Add retention family split application dry run
021a701 Materialize retention family split proposal
e304760 Add retention family split proposal builder
7c28fca Add retention family split design
32f52e7 Add mixed CE heldout blocker position review
4b9eb2a Add mixed CE heldout regression audit
```

## Artifact chain

| stage | branch | primary outputs | purpose |
| --- | --- | --- | --- |
| design | exp/15x15-retention-family-split-design | retention family split design report | manually classify heldout-retention family conflict modes |
| proposal builder | exp/15x15-retention-family-split-builder | `retention_family_split_proposal.csv`, `.md` | label heldout-retention rows with family_id and conflict/gain/blocker signals |
| materialize | exp/15x15-retention-family-split-materialize | `retention_family_materialized_split_manifest.csv`, `.json`, report | convert proposal rows into explicit split roles and gate scopes |
| apply dry-run | exp/15x15-retention-family-split-apply-dryrun | `retention_family_applied_split_dryrun_manifest.csv`, `.json`, report | map materialized split back to tracked safety-v3 dataset without mutating input |
| closeout | exp/15x15-retention-family-split-dryrun-closeout | `retention_family_split_dryrun_closeout.md` | summarize readiness and remaining review blockers before any training |

## Proposal-stage summary

- proposal rows: 11
- proposal families: 7
- rows marked repeated blocker: 2
- rows marked stable top1 gain: 1
- rows in families needing non-heldout retention anchor: 3

## Materialized-stage summary

- materialized rows: 11
- materialized families: 7
- materialized role counts: `{'heldout_retention_gate': 1, 'heldout_retention_gate_review': 8, 'nonheldout_retention_anchor': 2}`
- gate scope counts: `{'external_or_family_level_only_not_sibling_only': 1, 'not_a_gate': 2, 'review_before_use_as_gate': 8}`

## Apply dry-run summary

- applied dataset rows: 44
- matched materialized rows: 11
- unmatched materialized rows: 0
- proposed split counts: `{'heldout_retention_gate': 1, 'heldout_retention_gate_review': 8, 'train_candidate': 8, 'train_retention_anchor': 2, 'train_teacher_divergence': 25}`
- proposed role counts: `{'heldout_retention_gate': 1, 'heldout_retention_gate_review': 8, 'nonheldout_retention_anchor': 2, 'teacher_divergence': 33}`
- match method counts: `{'row_key': 11, 'unmatched': 33}`

## Critical sibling-conflict family

Family `bd:ea22cc14729b88fd` remains the central constraint for the next candidate split.

### Proposal signal

| target | outcomes | repeated_blocker | stable_top1_gain | sibling_conflict | mixed_signal | needs_nonheldout | proposal |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 7,10 | regression:8 | yes | no | yes | yes | yes | nonheldout_retention_anchor_candidate |
| 10,7 | regression:8 | yes | no | yes | yes | yes | nonheldout_retention_anchor_candidate |
| 7,9 | top1_gain:8 | no | yes | yes | yes | yes | heldout_gate_candidate |

### Materialized split

| target | materialized_role | gate_scope | only_sibling_gate_ok | reason |
| --- | --- | --- | --- | --- |
| 7,10 | nonheldout_retention_anchor | not_a_gate | no | repeated heldout blocker; regression signal; sibling target conflict family; mixed signal family |
| 10,7 | nonheldout_retention_anchor | not_a_gate | no | repeated heldout blocker; regression signal; sibling target conflict family; mixed signal family |
| 7,9 | heldout_retention_gate | external_or_family_level_only_not_sibling_only | no | stable top1 gain gate, but not valid as the only sibling-family heldout check |

### Applied dry-run

| target | matched | match_method | proposed_split | proposed_role | gate_scope | only_sibling_gate_ok |
| --- | --- | --- | --- | --- | --- | --- |
| 7,10 | yes | row_key | train_retention_anchor | nonheldout_retention_anchor | not_a_gate | no |
| 10,7 | yes | row_key | train_retention_anchor | nonheldout_retention_anchor | not_a_gate | no |
| 7,9 | yes | row_key | heldout_retention_gate | heldout_retention_gate | external_or_family_level_only_not_sibling_only | no |

Interpretation:

- Targets `7,10` and `10,7` in the critical family are treated as `nonheldout_retention_anchor` / `train_retention_anchor` candidates.
- Target `7,9` remains a `heldout_retention_gate`, but with `external_or_family_level_only_not_sibling_only` gate scope.
- Therefore `7,9` must not be used as the only heldout evidence for sibling targets `7,10` or `10,7` in the same family.

## Neutral and unmatched review items

- neutral/review proposal rows: 8
- unmatched materialized rows after dry-run application: 0

Neutral proposal rows:

| family_id | source | target | outcomes | proposal |
| --- | --- | --- | --- | --- |
| bd:690e24eaa9cbf978 | b_mcts16_g1_m46_target_5_11_over_4_12 | 5,11 | neutral_or_unknown:8 | heldout_gate_review |
| bd:4e43e8574f31dd70 | b_mcts16_g2_m19_target_10_7_over_7_11 | 10,7 | neutral_or_unknown:8 | heldout_gate_review |
| bd:fa22a82f75e4b3c2 | candidate_e_g2_m13_white_target_5_8_over_8_8 | 5,8 | neutral_or_unknown:8 | heldout_gate_review |
| bd:fcfbf3a577067568 | candidate_e_g2_m17_white_last_9_9_target_block_left_7_9_over_live_final_9_10 | 7,9 | neutral_or_unknown:8 | heldout_gate_review |
| bd:fcfbf3a577067568 | candidate_e_g2_m17_white_last_9_9_target_block_right_10_9_over_live_final_9_10 | 10,9 | neutral_or_unknown:8 | heldout_gate_review |
| bd:fcfbf3a577067568 | candidate_e_g2_m17_white_last_9_9_target_future_block_8_10_over_live_final_9_10 | 8,10 | neutral_or_unknown:8 | heldout_gate_review |
| bd:a2b4f843dfbb182a | v12l_g2_m13_target_8_6_over_9_4 | 8,6 | neutral_or_unknown:8 | heldout_gate_review |
| bd:9af3d20c637fd30d | v12l_g2_m15_target_8_6_over_6_6 | 8,6 | neutral_or_unknown:8 | heldout_gate_review |

No unmatched materialized rows were reported by the apply dry-run artifact.

## Readiness assessment

This chain is ready as a split-audit artifact, but not yet sufficient to start training automatically.

Training should remain blocked until the following are reviewed:

1. Confirm the neutral/review rows are acceptable heldout gates or remove them from gate-critical evaluation.
2. Confirm any unmatched materialized rows, if present, are expected because the selected input dataset is narrower than the proposal source.
3. Confirm that no sibling target from `bd:ea22cc14729b88fd` is used as the sole heldout check for another sibling target in that family.
4. Confirm the next training script consumes `train_retention_anchor` and restricted `heldout_retention_gate` semantics explicitly rather than relying only on old `heldout_retention` labels.

## Explicit non-actions

- No model training was run.
- No checkpoint was saved.
- No C weights were exported.
- No benchmark was run.
- No promotion decision was made.

## Recommended next branch

A safe next step is a training-input construction dry-run that consumes the applied split artifact and emits a candidate train/eval manifest, still without training.

Suggested branch:

```bash
git checkout -b exp/15x15-retention-family-training-input-dryrun
```
