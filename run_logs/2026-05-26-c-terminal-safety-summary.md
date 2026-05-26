# C Terminal Safety Summary

This stage extends the C CPU inference path.

## Previous milestone

The first C inference milestone was completed:

- PyTorch 9x9 CNN checkpoint was exported to C-readable weights.
- C CPU inference loaded the exported weights.
- C forward pass matched PyTorch output closely.
- Python/C consistency test showed very small differences.

Example consistency result:

policy_logits_max_abs_diff 4.991889e-07
policy_probs_max_abs_diff 1.86264515e-08
value_abs_diff 3.27825546e-07
top_legal_move C=60 Python=60

This confirmed that the checkpoint-to-C weight migration was correct.

## Problem found

Direct C CNN policy inference was still weak in play and in tactical benchmark.

The direct policy-only benchmark failed simple tactical cases, showing that the exported model alone was not enough for reliable tactical play.

## New change

I added a C terminal safety layer.

The C play path now has:

- CNN policy inference
- legal move masking
- terminal safety checking
- immediate win/block handling
- shallow terminal-risk filtering

The goal is not to implement a full handcrafted Gomoku strategy engine. The safety layer only checks terminal win/loss situations and shallow immediate risks, while the CNN policy still provides the main move ranking.

## Validation

I ran:

make clean
make
./test_infer
./benchmark_c weights/9x9_weights.bin
./play_c weights/9x9_weights.bin

The C inference path builds and runs successfully.

## Manual observation

I also tested human-vs-model play. The C policy plus terminal safety version is still not a strong Gomoku AI, but it is more playable than direct policy-only inference. It can avoid some immediate terminal mistakes, although the current checkpoint is still undertrained and can still lose to a human player.

## Conclusion

This completes the next engineering milestone:

- GPU-trained PyTorch weights can be used in C CPU inference.
- C inference can run with a terminal safety layer.
- C play is closer to the Python play path than direct CNN policy alone.

Current limitation:

- The model checkpoint is still not strong enough for reliable human-level play.
- Further improvement should focus on stronger 9x9 training, better checkpoint evaluation, and possibly later porting simplified MCTS/search to C.
