# Teacher-divergence board join fill report

## Branch

`exp/15x15-teacher-divergence-board-join-fill`

## Scope

- Board join fill only.
- Uses conservative `unique_join` rows from board join audit.
- Does not update the manifest directly.
- Does not run current_best probe.
- No training.
- No checkpoint save.
- No C export.
- No public benchmark.
- No promotion.

## Inputs

- manifest: `analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_with_fills.csv`
- board_join_audit: `analysis/integration_eval/teacher_divergence_board_join_audit.csv`

## Summary

| metric | value |
|---|---:|
| input audit rows | 203 |
| filled rows | 162 |
| excluded/unfilled rows | 41 |

## New status counts

| new_status | rows |
|---|---:|
| needs_current_best_probe | 140 |
| needs_board_join | 41 |
| needs_rapfi_requery | 22 |

## Join status counts

| join_status | rows |
|---|---:|
| unique_join | 162 |
| no_join | 21 |
| ambiguous_join | 20 |

## Exclusion reasons

| exclude_reason | rows |
|---|---:|
| no_join | 21 |
| ambiguous_join | 20 |

## Filled status by join strength

| join_strength | new_status | rows |
|---|---|---:|
| game_move | needs_current_best_probe | 140 |
| game_move | needs_rapfi_requery | 17 |
| game_move_target | needs_rapfi_requery | 5 |

## Filled rows preview

| manifest_id | new_status | join_strength | matched_hash | notes |
|---|---|---|---|---|
| td_exp_00066 | needs_current_best_probe | game_move | `73f491492b619cd2156ee5f606de909b1bad13f7` | board joined; rank/prob probe needed |
| td_exp_00070 | needs_current_best_probe | game_move | `b290815bc465c5403dac841290d28deec09891cb` | board joined; rank/prob probe needed |
| td_exp_00071 | needs_current_best_probe | game_move | `9313938cdbef92a5eb5dd39d471e6578e7dff243` | board joined; rank/prob probe needed |
| td_exp_00072 | needs_current_best_probe | game_move | `58ee9bd24b78c748b18cdc532ca4c68ddb37e7a7` | board joined; rank/prob probe needed |
| td_exp_00073 | needs_current_best_probe | game_move | `f7cc056dc7e20806709aa57b96e6261a92c0dec1` | board joined; rank/prob probe needed |
| td_exp_00074 | needs_current_best_probe | game_move | `027b1ec005717d632ab0cf991dc862e20c009f4b` | board joined; rank/prob probe needed |
| td_exp_00075 | needs_current_best_probe | game_move | `2be4fb27a92efb64cae74f7f02623491ce80a684` | board joined; rank/prob probe needed |
| td_exp_00076 | needs_current_best_probe | game_move | `2c74483f15adae07661408a3780d4f35cbab4bf2` | board joined; rank/prob probe needed |
| td_exp_00077 | needs_current_best_probe | game_move | `19849c34fc1cf45a6c89207d4db8c1cef73f3a63` | board joined; rank/prob probe needed |
| td_exp_00078 | needs_current_best_probe | game_move | `6c6e801436baecb5003f5cb4ac0a81f07439dfe1` | board joined; rank/prob probe needed |
| td_exp_00079 | needs_current_best_probe | game_move | `6cd50b750735acbb0a84f7f4aba05041f51f88ef` | board joined; rank/prob probe needed |
| td_exp_00080 | needs_current_best_probe | game_move | `55989befddf0dafc0e8e32a05f98f9443855943e` | board joined; rank/prob probe needed |
| td_exp_00081 | needs_current_best_probe | game_move | `32ab2efa9af3e6d6d61f36a2e164128b09e42459` | board joined; rank/prob probe needed |
| td_exp_00082 | needs_current_best_probe | game_move | `a9de1c69a413d8d740ad41ffb33bc3d893447dae` | board joined; rank/prob probe needed |
| td_exp_00083 | needs_current_best_probe | game_move | `c332d5126cfcd9b1666b862231236aa956de0d5a` | board joined; rank/prob probe needed |
| td_exp_00084 | needs_current_best_probe | game_move | `61be9d29ea39086d26719b933dddb3673c931397` | board joined; rank/prob probe needed |
| td_exp_00085 | needs_current_best_probe | game_move | `18d36123467b030f57285c292f24db30fc789a9d` | board joined; rank/prob probe needed |
| td_exp_00086 | needs_current_best_probe | game_move | `b69c534ce5f2efdddcbd0f5d18e8ef7c9ef919f5` | board joined; rank/prob probe needed |
| td_exp_00087 | needs_current_best_probe | game_move | `9176cc51dd0bd7acb8ff4c61edea94d761ea1c1d` | board joined; rank/prob probe needed |
| td_exp_00088 | needs_current_best_probe | game_move | `19b77e3587d8808d57fc4a4f5f44d5ae48fd1132` | board joined; rank/prob probe needed |
| td_exp_00089 | needs_current_best_probe | game_move | `a7408f1c7c200a150a579f27de8d03b7a5b3523d` | board joined; rank/prob probe needed |
| td_exp_00090 | needs_current_best_probe | game_move | `b1604ddd16651447a7a571a6737d7161bd8874a4` | board joined; rank/prob probe needed |
| td_exp_00091 | needs_current_best_probe | game_move | `dd459b55141adb69f635fdf5e603d7eca735dc0f` | board joined; rank/prob probe needed |
| td_exp_00092 | needs_current_best_probe | game_move | `e2e9b1755c7686fa3685106346f147dbaa20cc65` | board joined; rank/prob probe needed |
| td_exp_00093 | needs_current_best_probe | game_move | `c4bbda26f1db3f13ec363a894e931623a98df1a2` | board joined; rank/prob probe needed |
| td_exp_00094 | needs_current_best_probe | game_move | `ed67cf8a86167ee324577fead95cdbe9a3253867` | board joined; rank/prob probe needed |
| td_exp_00109 | needs_current_best_probe | game_move | `c332d5126cfcd9b1666b862231236aa956de0d5a` | board joined; rank/prob probe needed |
| td_exp_00110 | needs_current_best_probe | game_move | `b290815bc465c5403dac841290d28deec09891cb` | board joined; rank/prob probe needed |
| td_exp_00111 | needs_current_best_probe | game_move | `61be9d29ea39086d26719b933dddb3673c931397` | board joined; rank/prob probe needed |
| td_exp_00112 | needs_current_best_probe | game_move | `18d36123467b030f57285c292f24db30fc789a9d` | board joined; rank/prob probe needed |
| td_exp_00113 | needs_current_best_probe | game_move | `b69c534ce5f2efdddcbd0f5d18e8ef7c9ef919f5` | board joined; rank/prob probe needed |
| td_exp_00114 | needs_current_best_probe | game_move | `9313938cdbef92a5eb5dd39d471e6578e7dff243` | board joined; rank/prob probe needed |
| td_exp_00115 | needs_current_best_probe | game_move | `9176cc51dd0bd7acb8ff4c61edea94d761ea1c1d` | board joined; rank/prob probe needed |
| td_exp_00116 | needs_current_best_probe | game_move | `58ee9bd24b78c748b18cdc532ca4c68ddb37e7a7` | board joined; rank/prob probe needed |
| td_exp_00117 | needs_current_best_probe | game_move | `19b77e3587d8808d57fc4a4f5f44d5ae48fd1132` | board joined; rank/prob probe needed |
| td_exp_00118 | needs_current_best_probe | game_move | `f7cc056dc7e20806709aa57b96e6261a92c0dec1` | board joined; rank/prob probe needed |
| td_exp_00119 | needs_current_best_probe | game_move | `027b1ec005717d632ab0cf991dc862e20c009f4b` | board joined; rank/prob probe needed |
| td_exp_00120 | needs_current_best_probe | game_move | `a7408f1c7c200a150a579f27de8d03b7a5b3523d` | board joined; rank/prob probe needed |
| td_exp_00121 | needs_current_best_probe | game_move | `b1604ddd16651447a7a571a6737d7161bd8874a4` | board joined; rank/prob probe needed |
| td_exp_00122 | needs_current_best_probe | game_move | `2be4fb27a92efb64cae74f7f02623491ce80a684` | board joined; rank/prob probe needed |
| td_exp_00123 | needs_current_best_probe | game_move | `2c74483f15adae07661408a3780d4f35cbab4bf2` | board joined; rank/prob probe needed |
| td_exp_00124 | needs_current_best_probe | game_move | `dd459b55141adb69f635fdf5e603d7eca735dc0f` | board joined; rank/prob probe needed |
| td_exp_00125 | needs_current_best_probe | game_move | `e2e9b1755c7686fa3685106346f147dbaa20cc65` | board joined; rank/prob probe needed |
| td_exp_00126 | needs_current_best_probe | game_move | `19849c34fc1cf45a6c89207d4db8c1cef73f3a63` | board joined; rank/prob probe needed |
| td_exp_00127 | needs_current_best_probe | game_move | `6c6e801436baecb5003f5cb4ac0a81f07439dfe1` | board joined; rank/prob probe needed |
| td_exp_00128 | needs_current_best_probe | game_move | `6cd50b750735acbb0a84f7f4aba05041f51f88ef` | board joined; rank/prob probe needed |
| td_exp_00129 | needs_current_best_probe | game_move | `c4bbda26f1db3f13ec363a894e931623a98df1a2` | board joined; rank/prob probe needed |
| td_exp_00130 | needs_current_best_probe | game_move | `55989befddf0dafc0e8e32a05f98f9443855943e` | board joined; rank/prob probe needed |
| td_exp_00131 | needs_current_best_probe | game_move | `32ab2efa9af3e6d6d61f36a2e164128b09e42459` | board joined; rank/prob probe needed |
| td_exp_00132 | needs_current_best_probe | game_move | `a9de1c69a413d8d740ad41ffb33bc3d893447dae` | board joined; rank/prob probe needed |
| td_exp_00133 | needs_current_best_probe | game_move | `ed67cf8a86167ee324577fead95cdbe9a3253867` | board joined; rank/prob probe needed |
| td_exp_00134 | needs_current_best_probe | game_move | `c332d5126cfcd9b1666b862231236aa956de0d5a` | board joined; rank/prob probe needed |
| td_exp_00135 | needs_current_best_probe | game_move | `61be9d29ea39086d26719b933dddb3673c931397` | board joined; rank/prob probe needed |
| td_exp_00136 | needs_current_best_probe | game_move | `18d36123467b030f57285c292f24db30fc789a9d` | board joined; rank/prob probe needed |
| td_exp_00137 | needs_current_best_probe | game_move | `b290815bc465c5403dac841290d28deec09891cb` | board joined; rank/prob probe needed |
| td_exp_00138 | needs_current_best_probe | game_move | `9176cc51dd0bd7acb8ff4c61edea94d761ea1c1d` | board joined; rank/prob probe needed |
| td_exp_00139 | needs_current_best_probe | game_move | `58ee9bd24b78c748b18cdc532ca4c68ddb37e7a7` | board joined; rank/prob probe needed |
| td_exp_00140 | needs_current_best_probe | game_move | `19b77e3587d8808d57fc4a4f5f44d5ae48fd1132` | board joined; rank/prob probe needed |
| td_exp_00141 | needs_current_best_probe | game_move | `b69c534ce5f2efdddcbd0f5d18e8ef7c9ef919f5` | board joined; rank/prob probe needed |
| td_exp_00142 | needs_current_best_probe | game_move | `9313938cdbef92a5eb5dd39d471e6578e7dff243` | board joined; rank/prob probe needed |
| ... | ... | ... | ... | 102 more |

## Interpretation

Rows filled here have a unique board hash from the board join audit.

Most filled rows should proceed to current_best rank/prob probing, not training.

Rows excluded because of ambiguous or missing joins remain incomplete and must not be silently included in any future dataset.

## Decision

No manifest update in this branch.

No training.

No checkpoint.

No C export.

No public benchmark.

No promotion.
