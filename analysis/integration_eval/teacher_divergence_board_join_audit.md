# Teacher-divergence board join audit

## Branch

`exp/15x15-teacher-divergence-board-join-audit`

## Scope

- Board join audit only.
- Does not update the manifest.
- Does not run current_best probe.
- No training.
- No checkpoint save.
- No C export.
- No public benchmark.
- No promotion.

## Inputs

- manifest: `analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_with_fills.csv`
- selected rows: non-duplicate rows with status `needs_board_join`

## Summary

| metric | value |
|---|---:|
| manifest rows | 362 |
| needs_board_join selected rows | 203 |
| board source records loaded | 89 |
| unique joins | 162 |
| ambiguous joins | 20 |
| no joins | 21 |

## Join status counts

| join_status | rows |
|---|---:|
| unique_join | 162 |
| no_join | 21 |
| ambiguous_join | 20 |

## Join strength counts

| join_strength | rows |
|---|---:|
| game_move | 158 |
| game_move_target | 24 |
| none | 21 |

## Join status by source class

| source_class | join_status | rows |
|---|---|---:|
| corpus8_teacher_candidate_csv | no_join | 6 |
| corpus8_teacher_candidate_csv | unique_join | 26 |
| retention_candidate_dataset | no_join | 4 |
| retention_candidate_dataset | unique_join | 76 |
| retention_metadata_manifest | ambiguous_join | 20 |
| retention_metadata_manifest | no_join | 11 |
| retention_metadata_manifest | unique_join | 60 |

## Unique-join rows preview

| manifest_id | source_class | strength | target_rc | matched_hash |
|---|---|---|---|---|
| td_exp_00066 | retention_candidate_dataset | game_move | `[4, 12]` | `73f491492b619cd2156ee5f606de909b1bad13f7` |
| td_exp_00070 | retention_candidate_dataset | game_move | `[12, 6]` | `b290815bc465c5403dac841290d28deec09891cb` |
| td_exp_00071 | retention_candidate_dataset | game_move | `[7, 9]` | `9313938cdbef92a5eb5dd39d471e6578e7dff243` |
| td_exp_00072 | retention_candidate_dataset | game_move | `[5, 6]` | `58ee9bd24b78c748b18cdc532ca4c68ddb37e7a7` |
| td_exp_00073 | retention_candidate_dataset | game_move | `[3, 7]` | `f7cc056dc7e20806709aa57b96e6261a92c0dec1` |
| td_exp_00074 | retention_candidate_dataset | game_move | `[6, 3]` | `027b1ec005717d632ab0cf991dc862e20c009f4b` |
| td_exp_00075 | retention_candidate_dataset | game_move | `[10, 6]` | `2be4fb27a92efb64cae74f7f02623491ce80a684` |
| td_exp_00076 | retention_candidate_dataset | game_move | `[7, 9]` | `2c74483f15adae07661408a3780d4f35cbab4bf2` |
| td_exp_00077 | retention_candidate_dataset | game_move | `[7, 5]` | `19849c34fc1cf45a6c89207d4db8c1cef73f3a63` |
| td_exp_00078 | retention_candidate_dataset | game_move | `[5, 11]` | `6c6e801436baecb5003f5cb4ac0a81f07439dfe1` |
| td_exp_00079 | retention_candidate_dataset | game_move | `[4, 9]` | `6cd50b750735acbb0a84f7f4aba05041f51f88ef` |
| td_exp_00080 | retention_candidate_dataset | game_move | `[8, 5]` | `55989befddf0dafc0e8e32a05f98f9443855943e` |
| td_exp_00081 | retention_candidate_dataset | game_move | `[8, 6]` | `32ab2efa9af3e6d6d61f36a2e164128b09e42459` |
| td_exp_00082 | retention_candidate_dataset | game_move | `[9, 5]` | `a9de1c69a413d8d740ad41ffb33bc3d893447dae` |
| td_exp_00083 | retention_candidate_dataset | game_move | `[7, 5]` | `c332d5126cfcd9b1666b862231236aa956de0d5a` |
| td_exp_00084 | retention_candidate_dataset | game_move | `[7, 8]` | `61be9d29ea39086d26719b933dddb3673c931397` |
| td_exp_00085 | retention_candidate_dataset | game_move | `[8, 5]` | `18d36123467b030f57285c292f24db30fc789a9d` |
| td_exp_00086 | retention_candidate_dataset | game_move | `[9, 7]` | `b69c534ce5f2efdddcbd0f5d18e8ef7c9ef919f5` |
| td_exp_00087 | retention_candidate_dataset | game_move | `[8, 6]` | `9176cc51dd0bd7acb8ff4c61edea94d761ea1c1d` |
| td_exp_00088 | retention_candidate_dataset | game_move | `[10, 5]` | `19b77e3587d8808d57fc4a4f5f44d5ae48fd1132` |
| td_exp_00089 | retention_candidate_dataset | game_move | `[5, 6]` | `a7408f1c7c200a150a579f27de8d03b7a5b3523d` |
| td_exp_00090 | retention_candidate_dataset | game_move | `[9, 6]` | `b1604ddd16651447a7a571a6737d7161bd8874a4` |
| td_exp_00091 | retention_candidate_dataset | game_move | `[8, 9]` | `dd459b55141adb69f635fdf5e603d7eca735dc0f` |
| td_exp_00092 | retention_candidate_dataset | game_move | `[7, 9]` | `e2e9b1755c7686fa3685106346f147dbaa20cc65` |
| td_exp_00093 | retention_candidate_dataset | game_move | `[8, 6]` | `c4bbda26f1db3f13ec363a894e931623a98df1a2` |
| td_exp_00094 | retention_candidate_dataset | game_move | `[6, 8]` | `ed67cf8a86167ee324577fead95cdbe9a3253867` |
| td_exp_00109 | retention_candidate_dataset | game_move | `[7, 5]` | `c332d5126cfcd9b1666b862231236aa956de0d5a` |
| td_exp_00110 | retention_candidate_dataset | game_move | `[12, 6]` | `b290815bc465c5403dac841290d28deec09891cb` |
| td_exp_00111 | retention_candidate_dataset | game_move | `[7, 8]` | `61be9d29ea39086d26719b933dddb3673c931397` |
| td_exp_00112 | retention_candidate_dataset | game_move | `[8, 5]` | `18d36123467b030f57285c292f24db30fc789a9d` |
| td_exp_00113 | retention_candidate_dataset | game_move | `[9, 7]` | `b69c534ce5f2efdddcbd0f5d18e8ef7c9ef919f5` |
| td_exp_00114 | retention_candidate_dataset | game_move | `[7, 9]` | `9313938cdbef92a5eb5dd39d471e6578e7dff243` |
| td_exp_00115 | retention_candidate_dataset | game_move | `[8, 6]` | `9176cc51dd0bd7acb8ff4c61edea94d761ea1c1d` |
| td_exp_00116 | retention_candidate_dataset | game_move | `[5, 6]` | `58ee9bd24b78c748b18cdc532ca4c68ddb37e7a7` |
| td_exp_00117 | retention_candidate_dataset | game_move | `[10, 5]` | `19b77e3587d8808d57fc4a4f5f44d5ae48fd1132` |
| td_exp_00118 | retention_candidate_dataset | game_move | `[3, 7]` | `f7cc056dc7e20806709aa57b96e6261a92c0dec1` |
| td_exp_00119 | retention_candidate_dataset | game_move | `[6, 3]` | `027b1ec005717d632ab0cf991dc862e20c009f4b` |
| td_exp_00120 | retention_candidate_dataset | game_move | `[5, 6]` | `a7408f1c7c200a150a579f27de8d03b7a5b3523d` |
| td_exp_00121 | retention_candidate_dataset | game_move | `[9, 6]` | `b1604ddd16651447a7a571a6737d7161bd8874a4` |
| td_exp_00122 | retention_candidate_dataset | game_move | `[10, 6]` | `2be4fb27a92efb64cae74f7f02623491ce80a684` |
| ... | ... | ... | ... | 122 more |

## Interpretation

Rows with `unique_join` are candidates for a later manifest board-join fill branch.

Rows with `ambiguous_join` need source-specific disambiguation before any board is attached.

Rows with `no_join` require additional board sources or should remain incomplete.

This audit intentionally does not modify the manifest because a wrong board join would corrupt all downstream rank/prob and suppress labels.

## Decision

No training.

No checkpoint.

No C export.

No public benchmark.

No promotion.
