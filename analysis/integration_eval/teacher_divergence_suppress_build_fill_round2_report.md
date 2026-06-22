# Teacher-divergence suppress build fill round2 report

## Branch

`exp/15x15-teacher-divergence-suppress-build-fill-round2`

## Scope

- Input is current_best probe fill round2 CSV.
- Selects only rows with `status_after == needs_suppress_build`.
- Selects only legal target rows.
- Builds suppress candidates from current_best top-policy moves excluding the teacher target.
- Does not process skipped/invalid rows.
- Does not process `needs_rapfi_requery` rows.
- Does not process `needs_board_join` rows.
- No training.
- No checkpoint save.
- No C export.
- No public benchmark.
- No promotion.

## Inputs

- probe fill CSV: `analysis/integration_eval/teacher_divergence_current_best_probe_fill_round2.csv`
- selected rows: 97
- max suppress candidates per row: 5

## Summary

| metric | value |
|---|---:|
| selected needs_suppress_build rows | 97 |
| output rows | 97 |
| ready_full_schema rows | 97 |
| suppress repair rows | 0 |

## Status after suppress build

| status_after | rows |
|---|---:|
| ready_full_schema | 97 |

## Bucket after suppress build

| bucket_after | rows |
|---|---:|
| tail_rank_gt50 | 57 |
| trainable_rank_11_50 | 35 |
| protected_top10 | 5 |

## Suppress count distribution

| suppress_count | rows |
|---|---:|
| 5 | 97 |

## Notes distribution

| notes | rows |
|---|---:|
| suppress_candidates_built_tail_rank_gt50 | 57 |
| suppress_candidates_built_trainable_rank_11_50 | 35 |
| suppress_candidates_built_protected_top10 | 5 |

## Preview

| manifest_id | bucket_after | target_rc | target_rank | target_prob | suppress_rc | suppress_rank | suppress_prob | status_after | notes |
|---|---|---|---:|---:|---|---:|---:|---|---|
| td_exp_00066 | tail_rank_gt50 | `[4, 12]` | 91 | 0.00014256979920901358 | `[7, 10]` | 1 | 0.37411150336265564 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00070 | tail_rank_gt50 | `[12, 6]` | 93 | 8.739857003092766e-05 | `[8, 5]` | 1 | 0.40536731481552124 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00072 | protected_top10 | `[5, 6]` | 1 | 0.5818102359771729 | `[5, 9]` | 2 | 0.23356732726097107 | ready_full_schema | suppress_candidates_built_protected_top10 |
| td_exp_00073 | tail_rank_gt50 | `[3, 7]` | 96 | 1.7752557823769166e-06 | `[6, 7]` | 1 | 0.9519113898277283 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00075 | tail_rank_gt50 | `[10, 6]` | 67 | 9.357938324683346e-06 | `[9, 9]` | 1 | 0.9700202345848083 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00077 | tail_rank_gt50 | `[7, 5]` | 195 | 1.2841363741245004e-06 | `[8, 11]` | 1 | 0.5034058094024658 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00078 | trainable_rank_11_50 | `[5, 11]` | 23 | 0.0026402673684060574 | `[4, 5]` | 1 | 0.38212400674819946 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00079 | trainable_rank_11_50 | `[4, 9]` | 39 | 0.0007085961988195777 | `[3, 7]` | 1 | 0.3999754786491394 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00080 | trainable_rank_11_50 | `[8, 5]` | 18 | 0.0014995787059888244 | `[6, 6]` | 1 | 0.728687584400177 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00083 | tail_rank_gt50 | `[7, 5]` | 215 | 1.5816533505130792e-06 | `[6, 7]` | 1 | 0.727427065372467 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00085 | tail_rank_gt50 | `[8, 5]` | 80 | 0.00034033533302135766 | `[6, 6]` | 1 | 0.49138373136520386 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00086 | tail_rank_gt50 | `[9, 7]` | 128 | 1.498500864727248e-06 | `[5, 6]` | 1 | 0.4221777617931366 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00087 | tail_rank_gt50 | `[8, 6]` | 218 | 1.2696223450348043e-07 | `[8, 7]` | 1 | 0.8713992834091187 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00088 | trainable_rank_11_50 | `[10, 5]` | 43 | 0.0003833681985270232 | `[5, 9]` | 1 | 0.5963717699050903 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00089 | trainable_rank_11_50 | `[5, 6]` | 47 | 0.0009071464883163571 | `[8, 8]` | 1 | 0.7544541954994202 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00090 | trainable_rank_11_50 | `[9, 6]` | 14 | 0.00032802874920889735 | `[4, 6]` | 1 | 0.4877963662147522 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00093 | tail_rank_gt50 | `[8, 6]` | 67 | 2.403911366855027e-06 | `[8, 9]` | 1 | 0.9870235919952393 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00094 | tail_rank_gt50 | `[6, 8]` | 88 | 5.017169314669445e-05 | `[8, 8]` | 1 | 0.854669451713562 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00109 | tail_rank_gt50 | `[7, 5]` | 215 | 1.5816533505130792e-06 | `[6, 7]` | 1 | 0.727427065372467 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00110 | tail_rank_gt50 | `[12, 6]` | 93 | 8.739857003092766e-05 | `[8, 5]` | 1 | 0.40536731481552124 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00112 | tail_rank_gt50 | `[8, 5]` | 80 | 0.00034033533302135766 | `[6, 6]` | 1 | 0.49138373136520386 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00113 | tail_rank_gt50 | `[9, 7]` | 128 | 1.498500864727248e-06 | `[5, 6]` | 1 | 0.4221777617931366 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00115 | tail_rank_gt50 | `[8, 6]` | 218 | 1.2696223450348043e-07 | `[8, 7]` | 1 | 0.8713992834091187 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00116 | protected_top10 | `[5, 6]` | 1 | 0.5818102359771729 | `[5, 9]` | 2 | 0.23356732726097107 | ready_full_schema | suppress_candidates_built_protected_top10 |
| td_exp_00117 | trainable_rank_11_50 | `[10, 5]` | 43 | 0.0003833681985270232 | `[5, 9]` | 1 | 0.5963717699050903 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00118 | tail_rank_gt50 | `[3, 7]` | 96 | 1.7752557823769166e-06 | `[6, 7]` | 1 | 0.9519113898277283 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00120 | trainable_rank_11_50 | `[5, 6]` | 47 | 0.0009071464883163571 | `[8, 8]` | 1 | 0.7544541954994202 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00121 | trainable_rank_11_50 | `[9, 6]` | 14 | 0.00032802874920889735 | `[4, 6]` | 1 | 0.4877963662147522 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00122 | tail_rank_gt50 | `[10, 6]` | 67 | 9.357938324683346e-06 | `[9, 9]` | 1 | 0.9700202345848083 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00126 | tail_rank_gt50 | `[7, 5]` | 195 | 1.2841363741245004e-06 | `[8, 11]` | 1 | 0.5034058094024658 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00127 | trainable_rank_11_50 | `[5, 11]` | 23 | 0.0026402673684060574 | `[4, 5]` | 1 | 0.38212400674819946 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00128 | trainable_rank_11_50 | `[4, 9]` | 39 | 0.0007085961988195777 | `[3, 7]` | 1 | 0.3999754786491394 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00129 | tail_rank_gt50 | `[8, 6]` | 67 | 2.403911366855027e-06 | `[8, 9]` | 1 | 0.9870235919952393 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00130 | trainable_rank_11_50 | `[8, 5]` | 18 | 0.0014995787059888244 | `[6, 6]` | 1 | 0.728687584400177 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00133 | tail_rank_gt50 | `[6, 8]` | 88 | 5.017169314669445e-05 | `[8, 8]` | 1 | 0.854669451713562 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00134 | tail_rank_gt50 | `[7, 5]` | 215 | 1.5816533505130792e-06 | `[6, 7]` | 1 | 0.727427065372467 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00136 | tail_rank_gt50 | `[8, 5]` | 80 | 0.00034033533302135766 | `[6, 6]` | 1 | 0.49138373136520386 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00137 | tail_rank_gt50 | `[12, 6]` | 93 | 8.739857003092766e-05 | `[8, 5]` | 1 | 0.40536731481552124 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00138 | tail_rank_gt50 | `[8, 6]` | 218 | 1.2696223450348043e-07 | `[8, 7]` | 1 | 0.8713992834091187 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00139 | protected_top10 | `[5, 6]` | 1 | 0.5818102359771729 | `[5, 9]` | 2 | 0.23356732726097107 | ready_full_schema | suppress_candidates_built_protected_top10 |
| td_exp_00140 | trainable_rank_11_50 | `[10, 5]` | 43 | 0.0003833681985270232 | `[5, 9]` | 1 | 0.5963717699050903 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00141 | tail_rank_gt50 | `[9, 7]` | 128 | 1.498500864727248e-06 | `[5, 6]` | 1 | 0.4221777617931366 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00143 | trainable_rank_11_50 | `[5, 6]` | 47 | 0.0009071464883163571 | `[8, 8]` | 1 | 0.7544541954994202 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00144 | tail_rank_gt50 | `[3, 7]` | 96 | 1.7752557823769166e-06 | `[6, 7]` | 1 | 0.9519113898277283 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00146 | trainable_rank_11_50 | `[9, 6]` | 14 | 0.00032802874920889735 | `[4, 6]` | 1 | 0.4877963662147522 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00147 | tail_rank_gt50 | `[10, 6]` | 67 | 9.357938324683346e-06 | `[9, 9]` | 1 | 0.9700202345848083 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00149 | tail_rank_gt50 | `[8, 6]` | 67 | 2.403911366855027e-06 | `[8, 9]` | 1 | 0.9870235919952393 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00150 | trainable_rank_11_50 | `[8, 5]` | 18 | 0.0014995787059888244 | `[6, 6]` | 1 | 0.728687584400177 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00153 | tail_rank_gt50 | `[7, 5]` | 195 | 1.2841363741245004e-06 | `[8, 11]` | 1 | 0.5034058094024658 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00154 | trainable_rank_11_50 | `[5, 11]` | 23 | 0.0026402673684060574 | `[4, 5]` | 1 | 0.38212400674819946 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00155 | trainable_rank_11_50 | `[4, 9]` | 39 | 0.0007085961988195777 | `[3, 7]` | 1 | 0.3999754786491394 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00156 | tail_rank_gt50 | `[6, 8]` | 88 | 5.017169314669445e-05 | `[8, 8]` | 1 | 0.854669451713562 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00248 | tail_rank_gt50 | `[7, 5]` | 215 | 1.5816533505130792e-06 | `[6, 7]` | 1 | 0.727427065372467 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00249 | tail_rank_gt50 | `[12, 6]` | 93 | 8.739857003092766e-05 | `[8, 5]` | 1 | 0.40536731481552124 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00251 | tail_rank_gt50 | `[8, 5]` | 80 | 0.00034033533302135766 | `[6, 6]` | 1 | 0.49138373136520386 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00252 | tail_rank_gt50 | `[9, 7]` | 128 | 1.498500864727248e-06 | `[5, 6]` | 1 | 0.4221777617931366 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00253 | trainable_rank_11_50 | `[5, 6]` | 23 | 0.00462111784145236 | `[10, 9]` | 1 | 0.43301525712013245 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00255 | tail_rank_gt50 | `[8, 6]` | 218 | 1.2696223450348043e-07 | `[8, 7]` | 1 | 0.8713992834091187 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00256 | protected_top10 | `[5, 6]` | 1 | 0.5818102359771729 | `[5, 9]` | 2 | 0.23356732726097107 | ready_full_schema | suppress_candidates_built_protected_top10 |
| td_exp_00257 | trainable_rank_11_50 | `[10, 5]` | 43 | 0.0003833681985270232 | `[5, 9]` | 1 | 0.5963717699050903 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00259 | tail_rank_gt50 | `[3, 7]` | 96 | 1.7752557823769166e-06 | `[6, 7]` | 1 | 0.9519113898277283 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00261 | trainable_rank_11_50 | `[5, 6]` | 47 | 0.0009071464883163571 | `[8, 8]` | 1 | 0.7544541954994202 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00262 | trainable_rank_11_50 | `[9, 6]` | 14 | 0.00032802874920889735 | `[4, 6]` | 1 | 0.4877963662147522 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00264 | tail_rank_gt50 | `[10, 6]` | 67 | 9.357938324683346e-06 | `[9, 9]` | 1 | 0.9700202345848083 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00270 | tail_rank_gt50 | `[7, 5]` | 195 | 1.2841363741245004e-06 | `[8, 11]` | 1 | 0.5034058094024658 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00271 | trainable_rank_11_50 | `[5, 11]` | 23 | 0.0026402673684060574 | `[4, 5]` | 1 | 0.38212400674819946 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00272 | trainable_rank_11_50 | `[4, 9]` | 39 | 0.0007085961988195777 | `[3, 7]` | 1 | 0.3999754786491394 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00273 | tail_rank_gt50 | `[8, 6]` | 67 | 2.403911366855027e-06 | `[8, 9]` | 1 | 0.9870235919952393 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00274 | trainable_rank_11_50 | `[8, 5]` | 18 | 0.0014995787059888244 | `[6, 6]` | 1 | 0.728687584400177 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00278 | tail_rank_gt50 | `[6, 8]` | 88 | 5.017169314669445e-05 | `[8, 8]` | 1 | 0.854669451713562 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00279 | tail_rank_gt50 | `[7, 5]` | 215 | 1.5816533505130792e-06 | `[6, 7]` | 1 | 0.727427065372467 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00281 | tail_rank_gt50 | `[8, 5]` | 80 | 0.00034033533302135766 | `[6, 6]` | 1 | 0.49138373136520386 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00283 | tail_rank_gt50 | `[8, 6]` | 218 | 1.2696223450348043e-07 | `[8, 7]` | 1 | 0.8713992834091187 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00285 | trainable_rank_11_50 | `[10, 5]` | 43 | 0.0003833681985270232 | `[5, 9]` | 1 | 0.5963717699050903 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00286 | tail_rank_gt50 | `[9, 7]` | 128 | 1.498500864727248e-06 | `[5, 6]` | 1 | 0.4221777617931366 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00288 | trainable_rank_11_50 | `[5, 6]` | 47 | 0.0009071464883163571 | `[8, 8]` | 1 | 0.7544541954994202 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00291 | trainable_rank_11_50 | `[9, 6]` | 14 | 0.00032802874920889735 | `[4, 6]` | 1 | 0.4877963662147522 | ready_full_schema | suppress_candidates_built_trainable_rank_11_50 |
| td_exp_00294 | tail_rank_gt50 | `[8, 6]` | 67 | 2.403911366855027e-06 | `[8, 9]` | 1 | 0.9870235919952393 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00301 | tail_rank_gt50 | `[6, 8]` | 88 | 5.017169314669445e-05 | `[8, 8]` | 1 | 0.854669451713562 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| td_exp_00331 | tail_rank_gt50 | `[7, 5]` | 215 | 1.5816533505130792e-06 | `[6, 7]` | 1 | 0.727427065372467 | ready_full_schema | suppress_candidates_built_tail_rank_gt50 |
| . | . | . | . | . | . | . | . | . | 17 more rows in CSV |

## Interpretation

Rows with suppress candidates now have full current_best target/suppress policy fields and can be merged into the manifest as full-schema rows.

Protected top10 rows should remain protection/eval rows unless a later training export deliberately excludes them from trainable data.

Tail rank > 50 rows should remain diagnostic-only unless a later design explicitly allows them.

Trainable rank 11-50 rows are the primary candidates for a later dry-run dataset export after manifest merge.

## Decision

No training.

No checkpoint.

No C export.

No public benchmark.

No promotion.
