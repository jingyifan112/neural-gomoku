# Tactical-mid Preterminal Diagnostics Conclusion

## Context

The public benchmark result was:

- `neural_current_best_mcts16 vs tactical_mid = 6 - 16 - 2 = 7.0/24 = 0.292`

The original `tactical_mid_must_block_cases` looked like final defensive must-block failures, but the follow-up evaluators show these positions are already too late.

## Too-late double-threat finding

Python evaluator result:

- `cases = 16`
- `direct_target = 0/16`
- `policy_safety_target = 7/16`
- `direct_blocks = 3/16`
- `policy_safety_blocks = 16/16`
- `too_late_double_threat = 16/16`

C engine evaluator result:

- `cases = 16`
- `debug_found = 16/16`
- `c_final_exact_target = 0/16`
- `c_final_same_as_match_blunder = 16/16`
- `too_late_double_threat = 16/16`

Interpretation:

- All 16 cases already contain at least two opponent immediate winning moves before the recorded neural move.
- Blocking one endpoint is insufficient because the opponent still wins at the other endpoint.
- These 16 cases should not be used directly as ordinary single-target must-block training data.

## Preterminal extraction

A preterminal extractor was added to look backward from the too-late positions.

Back-2 extraction:

- `rows = 32`
- `opponent_create_double_threat_rows = 16/32`
- `neural_rows_with_double_threat_replies = 16/16`

Back-6 extraction:

| Back ply | Role | Main finding |
|---:|---|---|
| 1 | opponent | `16/16` opponent moves created the final double-terminal threat |
| 2 | neural | `16/16` observed neural moves allowed double-threat replies, but only `2/16` had prevention candidates |
| 4 | neural | `1/16` observed neural move allowed double-threat replies; `15/16` had some prevention candidate |
| 6 | neural | `0/16` observed neural moves allowed immediate double-threat replies; `16/16` had prevention candidates, likely too early/noisy |

## Actionable preterminal cases

Only two cases are currently actionable as clear regression cases:

| Case | Observed neural move | Target prevention move | Reason |
|---|---|---|---|
| `tactical_mid_g3_block_4_9_preterminal_back2` | `3,5` | `4,6` | observed move allows opponent `4,6`, creating immediate wins at `4,4` and `4,9` |
| `tactical_mid_g11_block_7_14_preterminal_back2` | `8,14` | `10,11` | observed move allows opponent `10,11`, creating immediate wins at `12,9` and `7,14` |

## Current-best evaluation on actionable preterminal cases

Python current-best result:

- `direct_target = 0/2`
- `policy_safety_target = 0/2`
- `direct_zero_double_threat_replies = 0/2`
- `policy_safety_zero_double_threat_replies = 0/2`

C engine mcts_safe result:

- `c_policy_safety_target = 0/2`
- `c_final_target = 0/2`
- `c_policy_safety_zero_double_threat_replies = 0/2`
- `c_final_zero_double_threat_replies = 0/2`

Interpretation:

- Python and C agree that current_best fails both actionable preterminal cases.
- `policy_safety` does not solve these because they are not single immediate-loss blocks; they require avoiding a future opponent double-terminal reply.
- These 2 cases are suitable as fixed regression benchmark cases.
- They are not sufficient by themselves to justify training or promotion.

## Recommendation

Do not train yet.

Next recommended steps:

1. Keep the original 16 too-late cases as diagnostic evidence only.
2. Use the 2 actionable preterminal cases as a tiny fixed regression benchmark.
3. Search for more actionable preterminal cases across more tactical_mid/public failure games before creating a training dataset.
4. If training later, treat this as a fork/double-threat prevention objective, not ordinary final-ply must-block repair.
