# Teacher-divergence current_best probe fill round2 report

## Branch

`exp/15x15-teacher-divergence-current-best-probe-fill-round2`

## Scope

- Fill current_best rank/prob/direct move only.
- Selected manifest rows with status `needs_current_best_probe`.
- Does not process `needs_rapfi_requery` rows.
- Does not process `needs_board_join` rows.
- No training.
- No checkpoint save.
- No C export.
- No public benchmark.
- No promotion.

## Inputs

- manifest: `analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_with_board_joins.csv`
- checkpoint used for inference: `checkpoints/15x15_current_best.pt`
- board source records indexed by hash: 196
- selected rows: 140

## Summary

| metric | value |
|---|---:|
| rows selected | 140 |
| legal target rows | 97 |
| illegal target rows | 43 |

## Status after fill

| status_after | rows |
|---|---:|
| needs_suppress_build | 97 |
| skipped_invalid | 43 |

## Bucket after fill

| bucket_after | rows |
|---|---:|
| tail_rank_gt50 | 57 |
| unknown_rank | 43 |
| trainable_rank_11_50 | 35 |
| protected_top10 | 5 |

## Filled rows preview

| manifest_id | status_after | bucket_after | target_rc | rank | prob | direct_rc | excluded | notes |
|---|---|---|---|---:|---:|---|---:|---|
| td_exp_00066 | needs_suppress_build | tail_rank_gt50 | `[4, 12]` | 91 | 0.00014256979920901358 | `[7, 10]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00070 | needs_suppress_build | tail_rank_gt50 | `[12, 6]` | 93 | 8.739857003092766e-05 | `[8, 5]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00071 | skipped_invalid | unknown_rank | `[7, 9]` | NA | 0.0 | `[4, 2]` | 1 | excluded_target_illegal |
| td_exp_00072 | needs_suppress_build | protected_top10 | `[5, 6]` | 1 | 0.5818102359771729 | `[5, 6]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00073 | needs_suppress_build | tail_rank_gt50 | `[3, 7]` | 96 | 1.7752557823769166e-06 | `[6, 7]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00074 | skipped_invalid | unknown_rank | `[6, 3]` | NA | 0.0 | `[6, 7]` | 1 | excluded_target_illegal |
| td_exp_00075 | needs_suppress_build | tail_rank_gt50 | `[10, 6]` | 67 | 9.357938324683346e-06 | `[9, 9]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00076 | skipped_invalid | unknown_rank | `[7, 9]` | NA | 0.0 | `[3, 7]` | 1 | excluded_target_illegal |
| td_exp_00077 | needs_suppress_build | tail_rank_gt50 | `[7, 5]` | 195 | 1.2841363741245004e-06 | `[8, 11]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00078 | needs_suppress_build | trainable_rank_11_50 | `[5, 11]` | 23 | 0.0026402673684060574 | `[4, 5]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00079 | needs_suppress_build | trainable_rank_11_50 | `[4, 9]` | 39 | 0.0007085961988195777 | `[3, 7]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00080 | needs_suppress_build | trainable_rank_11_50 | `[8, 5]` | 18 | 0.0014995787059888244 | `[6, 6]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00081 | skipped_invalid | unknown_rank | `[8, 6]` | NA | 0.0 | `[9, 4]` | 1 | excluded_target_illegal |
| td_exp_00082 | skipped_invalid | unknown_rank | `[9, 5]` | NA | 0.0 | `[9, 7]` | 1 | excluded_target_illegal |
| td_exp_00083 | needs_suppress_build | tail_rank_gt50 | `[7, 5]` | 215 | 1.5816533505130792e-06 | `[6, 7]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00084 | skipped_invalid | unknown_rank | `[7, 8]` | NA | 0.0 | `[6, 6]` | 1 | excluded_target_illegal |
| td_exp_00085 | needs_suppress_build | tail_rank_gt50 | `[8, 5]` | 80 | 0.00034033533302135766 | `[6, 6]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00086 | needs_suppress_build | tail_rank_gt50 | `[9, 7]` | 128 | 1.498500864727248e-06 | `[5, 6]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00087 | needs_suppress_build | tail_rank_gt50 | `[8, 6]` | 218 | 1.2696223450348043e-07 | `[8, 7]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00088 | needs_suppress_build | trainable_rank_11_50 | `[10, 5]` | 43 | 0.0003833681985270232 | `[5, 9]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00089 | needs_suppress_build | trainable_rank_11_50 | `[5, 6]` | 47 | 0.0009071464883163571 | `[8, 8]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00090 | needs_suppress_build | trainable_rank_11_50 | `[9, 6]` | 14 | 0.00032802874920889735 | `[4, 6]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00091 | skipped_invalid | unknown_rank | `[8, 9]` | NA | 0.0 | `[6, 6]` | 1 | excluded_target_illegal |
| td_exp_00092 | skipped_invalid | unknown_rank | `[7, 9]` | NA | 0.0 | `[6, 6]` | 1 | excluded_target_illegal |
| td_exp_00093 | needs_suppress_build | tail_rank_gt50 | `[8, 6]` | 67 | 2.403911366855027e-06 | `[8, 9]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00094 | needs_suppress_build | tail_rank_gt50 | `[6, 8]` | 88 | 5.017169314669445e-05 | `[8, 8]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00109 | needs_suppress_build | tail_rank_gt50 | `[7, 5]` | 215 | 1.5816533505130792e-06 | `[6, 7]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00110 | needs_suppress_build | tail_rank_gt50 | `[12, 6]` | 93 | 8.739857003092766e-05 | `[8, 5]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00111 | skipped_invalid | unknown_rank | `[7, 8]` | NA | 0.0 | `[6, 6]` | 1 | excluded_target_illegal |
| td_exp_00112 | needs_suppress_build | tail_rank_gt50 | `[8, 5]` | 80 | 0.00034033533302135766 | `[6, 6]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00113 | needs_suppress_build | tail_rank_gt50 | `[9, 7]` | 128 | 1.498500864727248e-06 | `[5, 6]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00114 | skipped_invalid | unknown_rank | `[7, 9]` | NA | 0.0 | `[4, 2]` | 1 | excluded_target_illegal |
| td_exp_00115 | needs_suppress_build | tail_rank_gt50 | `[8, 6]` | 218 | 1.2696223450348043e-07 | `[8, 7]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00116 | needs_suppress_build | protected_top10 | `[5, 6]` | 1 | 0.5818102359771729 | `[5, 6]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00117 | needs_suppress_build | trainable_rank_11_50 | `[10, 5]` | 43 | 0.0003833681985270232 | `[5, 9]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00118 | needs_suppress_build | tail_rank_gt50 | `[3, 7]` | 96 | 1.7752557823769166e-06 | `[6, 7]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00119 | skipped_invalid | unknown_rank | `[6, 3]` | NA | 0.0 | `[6, 7]` | 1 | excluded_target_illegal |
| td_exp_00120 | needs_suppress_build | trainable_rank_11_50 | `[5, 6]` | 47 | 0.0009071464883163571 | `[8, 8]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00121 | needs_suppress_build | trainable_rank_11_50 | `[9, 6]` | 14 | 0.00032802874920889735 | `[4, 6]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00122 | needs_suppress_build | tail_rank_gt50 | `[10, 6]` | 67 | 9.357938324683346e-06 | `[9, 9]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00123 | skipped_invalid | unknown_rank | `[7, 9]` | NA | 0.0 | `[3, 7]` | 1 | excluded_target_illegal |
| td_exp_00124 | skipped_invalid | unknown_rank | `[8, 9]` | NA | 0.0 | `[6, 6]` | 1 | excluded_target_illegal |
| td_exp_00125 | skipped_invalid | unknown_rank | `[7, 9]` | NA | 0.0 | `[6, 6]` | 1 | excluded_target_illegal |
| td_exp_00126 | needs_suppress_build | tail_rank_gt50 | `[7, 5]` | 195 | 1.2841363741245004e-06 | `[8, 11]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00127 | needs_suppress_build | trainable_rank_11_50 | `[5, 11]` | 23 | 0.0026402673684060574 | `[4, 5]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00128 | needs_suppress_build | trainable_rank_11_50 | `[4, 9]` | 39 | 0.0007085961988195777 | `[3, 7]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00129 | needs_suppress_build | tail_rank_gt50 | `[8, 6]` | 67 | 2.403911366855027e-06 | `[8, 9]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00130 | needs_suppress_build | trainable_rank_11_50 | `[8, 5]` | 18 | 0.0014995787059888244 | `[6, 6]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00131 | skipped_invalid | unknown_rank | `[8, 6]` | NA | 0.0 | `[9, 4]` | 1 | excluded_target_illegal |
| td_exp_00132 | skipped_invalid | unknown_rank | `[9, 5]` | NA | 0.0 | `[9, 7]` | 1 | excluded_target_illegal |
| td_exp_00133 | needs_suppress_build | tail_rank_gt50 | `[6, 8]` | 88 | 5.017169314669445e-05 | `[8, 8]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00134 | needs_suppress_build | tail_rank_gt50 | `[7, 5]` | 215 | 1.5816533505130792e-06 | `[6, 7]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00135 | skipped_invalid | unknown_rank | `[7, 8]` | NA | 0.0 | `[6, 6]` | 1 | excluded_target_illegal |
| td_exp_00136 | needs_suppress_build | tail_rank_gt50 | `[8, 5]` | 80 | 0.00034033533302135766 | `[6, 6]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00137 | needs_suppress_build | tail_rank_gt50 | `[12, 6]` | 93 | 8.739857003092766e-05 | `[8, 5]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00138 | needs_suppress_build | tail_rank_gt50 | `[8, 6]` | 218 | 1.2696223450348043e-07 | `[8, 7]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00139 | needs_suppress_build | protected_top10 | `[5, 6]` | 1 | 0.5818102359771729 | `[5, 6]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00140 | needs_suppress_build | trainable_rank_11_50 | `[10, 5]` | 43 | 0.0003833681985270232 | `[5, 9]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00141 | needs_suppress_build | tail_rank_gt50 | `[9, 7]` | 128 | 1.498500864727248e-06 | `[5, 6]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00142 | skipped_invalid | unknown_rank | `[7, 9]` | NA | 0.0 | `[4, 2]` | 1 | excluded_target_illegal |
| td_exp_00143 | needs_suppress_build | trainable_rank_11_50 | `[5, 6]` | 47 | 0.0009071464883163571 | `[8, 8]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00144 | needs_suppress_build | tail_rank_gt50 | `[3, 7]` | 96 | 1.7752557823769166e-06 | `[6, 7]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00145 | skipped_invalid | unknown_rank | `[6, 3]` | NA | 0.0 | `[6, 7]` | 1 | excluded_target_illegal |
| td_exp_00146 | needs_suppress_build | trainable_rank_11_50 | `[9, 6]` | 14 | 0.00032802874920889735 | `[4, 6]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00147 | needs_suppress_build | tail_rank_gt50 | `[10, 6]` | 67 | 9.357938324683346e-06 | `[9, 9]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00148 | skipped_invalid | unknown_rank | `[7, 9]` | NA | 0.0 | `[3, 7]` | 1 | excluded_target_illegal |
| td_exp_00149 | needs_suppress_build | tail_rank_gt50 | `[8, 6]` | 67 | 2.403911366855027e-06 | `[8, 9]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00150 | needs_suppress_build | trainable_rank_11_50 | `[8, 5]` | 18 | 0.0014995787059888244 | `[6, 6]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00151 | skipped_invalid | unknown_rank | `[8, 9]` | NA | 0.0 | `[6, 6]` | 1 | excluded_target_illegal |
| td_exp_00152 | skipped_invalid | unknown_rank | `[7, 9]` | NA | 0.0 | `[6, 6]` | 1 | excluded_target_illegal |
| td_exp_00153 | needs_suppress_build | tail_rank_gt50 | `[7, 5]` | 195 | 1.2841363741245004e-06 | `[8, 11]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00154 | needs_suppress_build | trainable_rank_11_50 | `[5, 11]` | 23 | 0.0026402673684060574 | `[4, 5]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00155 | needs_suppress_build | trainable_rank_11_50 | `[4, 9]` | 39 | 0.0007085961988195777 | `[3, 7]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00156 | needs_suppress_build | tail_rank_gt50 | `[6, 8]` | 88 | 5.017169314669445e-05 | `[8, 8]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00157 | skipped_invalid | unknown_rank | `[8, 6]` | NA | 0.0 | `[9, 4]` | 1 | excluded_target_illegal |
| td_exp_00158 | skipped_invalid | unknown_rank | `[9, 5]` | NA | 0.0 | `[9, 7]` | 1 | excluded_target_illegal |
| td_exp_00248 | needs_suppress_build | tail_rank_gt50 | `[7, 5]` | 215 | 1.5816533505130792e-06 | `[6, 7]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00249 | needs_suppress_build | tail_rank_gt50 | `[12, 6]` | 93 | 8.739857003092766e-05 | `[8, 5]` | 0 | rank_prob_filled_but_suppress_missing |
| td_exp_00250 | skipped_invalid | unknown_rank | `[7, 8]` | NA | 0.0 | `[6, 6]` | 1 | excluded_target_illegal |
| td_exp_00251 | needs_suppress_build | tail_rank_gt50 | `[8, 5]` | 80 | 0.00034033533302135766 | `[6, 6]` | 0 | rank_prob_filled_but_suppress_missing |
| . | . | . | . | . | . | . | . | 60 more rows in CSV |

## Interpretation

Legal probed rows now have current_best policy rank/prob/direct-move diagnostics and should proceed to suppress candidate build.

Illegal target rows are excluded/skipped invalid and must not enter suppress build or training.

## Decision

No training.

No checkpoint.

No C export.

No public benchmark.

No promotion.
