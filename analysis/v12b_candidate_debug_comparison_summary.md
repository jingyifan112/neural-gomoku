# v12b candidate debug comparison summary

Branch: exp/15x15-v11-mixed-sparring

## Candidate

- Base: checkpoints/15x15_v12_candidate.pt
- v12b candidate: checkpoints/15x15_v12b_candidate.pt
- v12b method: value-head-only forced-line repair
- C weights: c_inference/weights/15x15_v12b_candidate_weights.bin

## Repair-set result

v12b_candidate improved value calibration on the v12b repair set:

- early_forcing_value_negative value average improved from about +0.664 to much lower positive / near-neutral values.
- verified_double_threat_loss values became more negative.
- pre_double_threat_warning value became strongly negative.
- old immediate-block direct accuracy remained 2/3, as expected for value-head-only training.

## Internal gates

v12b_value_head_stage1 passed internal gates:

- vs current_best: 10-10
- vs v10_frozen: 10-10
- vs greedy: 10-10
- vs random: 20-0
- vs v12_candidate: 20-0

## Rapfi smoke

v12b_candidate MCTS16 vs Rapfi depth=1 remained 0-2.

The MCTS16 smoke was valid: the losses were by five-connection, not by neural timeout or forfeit.

## Debug comparison: v12_candidate vs v12b_candidate

Game 1 forcing line:

- move_count 12:
  - v12_candidate value=0.680296 final=6,8
  - v12b_candidate value=0.141226 final=6,8
- move_count 14:
  - v12_candidate value=0.478734 final=4,5
  - v12b_candidate value=-0.075040 final=4,5
- move_count 16:
  - v12_candidate value=0.757017 final=5,2
  - v12b_candidate value=0.263702 final=5,2
- move_count 18:
  - v12_candidate value=0.695656 final=7,1
  - v12b_candidate value=0.198699 final=7,1

Conclusion: v12b substantially reduced over-optimistic value on Game 1 early forcing positions, but the final moves were unchanged.

Game 2 late forcing / double-threat line:

- move_count 31:
  - v12_candidate value=-0.830218 final=9,7
  - v12b_candidate value=-0.889725 final=10,9
- move_count 33:
  - v12_candidate value=-0.754524 final=11,9
  - v12b_candidate value=-0.887026 final=9,6

Conclusion: v12b changed late defensive choices in Game 2 and made value more negative, but this was still insufficient to avoid the Rapfi forcing line.

## Decision

Do not promote v12b_candidate.

v12b successfully repaired value calibration without breaking internal gates, but it did not teach earlier anti-forcing policy choices. The next stage should be v12c policy-safe forced-line escape repair, not ordinary self-play and not more value-only training.
