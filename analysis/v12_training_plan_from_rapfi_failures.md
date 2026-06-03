# v12 training plan from Rapfi failures

## Current conclusion from v11/Rapfi analysis

v11 is internally stronger than v10, but the Rapfi depth=1 failure analysis shows that the current improvement is not yet landing on the decisions that matter against Rapfi. The seven labeled positions are not enough to define a new model by themselves, but they are enough to identify the first v12 target: improve failure-position decisions before treating aggregate Rapfi win rate as the headline metric.

The clearest tactical issue is that the direct policy can miss immediate blocks. In several positions, MCTS/safety recovers the block, which keeps the final move locally correct but hides the policy weakness. In the double-threat positions, the final move can block one immediate win while another remains, so the useful training signal is earlier: avoid entering the forced-loss shape and calibrate value downward when the opponent has multiple winning continuations.

Rapfi win rate is not the first v12 goal. The first goal is measurable improvement on the curated failure-position decisions: direct policy should find immediate blocks more often, value should recognize imminent tactical danger, and the model should avoid pre-double-threat setups earlier.

## Main failure modes

### direct_policy_missed_immediate_block

Observed in game 2 move_count 29. The opponent had an immediate winning move at `4,9`; direct policy chose `3,4`, while MCTS/safety and final selected the block `4,9`. The value was already strongly negative, so this is primarily a policy-target issue rather than a value-miscalibration issue.

### value_miscalibration_and_direct_policy_missed_immediate_block

Observed in game 1 move_count 44 and move_count 46. The opponent had immediate wins at `2,10` and `4,12`; direct policy missed both blocks, while MCTS/safety recovered them. The values were near neutral (`0.059948`, `0.037243`), which means the model was not treating the position as a high-danger defensive emergency.

### forced_loss_or_double_threat

Observed in game 1 move_count 48 and game 2 move_count 33. The opponent had two immediate winning moves, and the final move blocked only one. These should be treated as forced-loss or double-threat examples, not as ordinary "find the one block" examples.

### pre_threat_setup_review

Observed in game 1 move_count 38. No immediate opponent win was detected, but Rapfi soon created a forcing line. This position should be reviewed for open-four or double-threat setup patterns that are not captured by immediate-win scanning.

### pre_double_threat_setup_review

Observed in game 2 move_count 31. No immediate opponent win was detected, but the next Rapfi bestline (`J8 J12`) indicates transition into a forcing sequence. This is an avoidance-sample candidate: the model should prefer moves that prevent the opponent's double-threat construction.

## Proposed v12 data

### Immediate block policy samples

Create supervised policy samples from positions where the opponent has exactly one immediate winning move:
- game 1 move_count 44: target block `2,10`
- game 1 move_count 46: target block `4,12`
- game 2 move_count 29: target block `4,9`

Augment these with symmetry transforms and nearby equivalent positions mined from self-play or Rapfi logs. The goal is not to memorize three boards, but to raise policy probability on forced defensive moves when an immediate loss exists.

### Forced-loss / double-threat value samples

Create value-focused samples from positions where the opponent has multiple immediate winning moves:
- game 1 move_count 48: opponent wins at `3,11` and `8,11`
- game 2 move_count 33: opponent wins at `9,6` and `9,11`

These positions should teach the value head that "blocking one" is not enough. They should be labeled as losing or near-losing for the side to move unless a verified escape exists. Policy targets should be handled carefully: choosing one block may be legal and locally sensible, but it should not be treated as a success if the second win remains.

### Pre-double-threat avoidance samples

Build a small review set around:
- game 1 move_count 38
- game 2 move_count 31

For each, reconstruct candidate alternatives and ask whether a move avoids the Rapfi forcing continuation. These samples should become avoidance data only after manual audit. Until then, keep them as review positions rather than hard labels.

## Proposed v12 training

Use a small targeted supervised fine-tuning phase, not a broad training rewrite. The targeted set should include:
- immediate-block policy examples,
- forced-loss value examples,
- audited pre-threat avoidance examples,
- symmetry-augmented variants,
- mined near-neighbor positions from additional Rapfi/debug logs.

Mix the targeted data with previous self-play and greedy-sparring data so v12 does not overfit to seven hand-picked positions. The failure set should influence the model, not become the whole training distribution.

Keep architecture, MCTS, safety, and training logic unchanged for this step. The v12 question is whether better targeted data can make the existing model/pipeline choose and evaluate these positions better.

## Proposed v12 evaluation gates

Before promotion, v12 should pass preservation gates:
- preserve performance vs greedy,
- preserve performance vs random,
- preserve performance vs mixed_v5,
- preserve or improve vs v10.

It should also pass failure-focused gates:
- improve direct-policy accuracy on immediate-block positions,
- improve value calibration on immediate-loss and double-threat positions,
- improve final decision quality on the labeled Rapfi failure set,
- avoid entering reviewed pre-double-threat setups when a verified safer alternative exists,
- improve Rapfi average survival length.

Rapfi win rate should be tracked, but it is not the first v12 goal. A v12 model that improves failure-position decisions and survives longer against Rapfi is a useful step even if short-match Rapfi win rate remains 0%.

## Practical next step

Use `analysis/rapfi_failure_set_labeled.csv` as the seed set, then expand it with additional audited positions before any training. The minimum useful expansion is to mine more Rapfi games for:
- single immediate-block misses,
- near-neutral value on immediate-loss positions,
- double-threat forced losses,
- pre-threat positions one or two plies before the immediate-loss detector fires.

Only after this expanded set exists should v12 fine-tuning begin.
