# C Tactical Benchmark

After exporting the PyTorch CNN checkpoint to C-readable weights and verifying Python/C inference consistency, I tested the direct C CNN policy on simple tactical positions.

## Python/C consistency result

The C forward pass matches the PyTorch model closely:

policy_logits_max_abs_diff 4.991889e-07
policy_probs_max_abs_diff 1.86264515e-08
value_abs_diff 3.27825546e-07
top_legal_move C=60 Python=60

This confirms that the checkpoint-to-C weight migration is correct.

## Direct C policy tactical benchmark

I then tested direct C policy inference on simple tactical cases:

- opponent four with one playable endpoint
- opponent open three
- model four can win
- broken four pattern

Result:

opponent_four_one_endpoint: FAIL
opponent_open_three: FAIL
model_four_can_win: FAIL
broken_four_pattern: FAIL
accuracy 0/4 = 0.00%

## Interpretation

The C migration itself works, but direct CNN policy inference is still weak. The model often selects a move near the board but not the exact tactical move.

This explains why C human-vs-model play is weak: the current C path only uses direct CNN policy inference. It does not include the Python version's neural MCTS or terminal safety.

## Conclusion

Current milestone completed:

- GPU-trained PyTorch CNN checkpoint can be exported.
- C CPU inference can load the exported weights.
- C output matches PyTorch output closely.

Current limitation:

- Direct C CNN policy inference is not strong enough for tactical play.

Next step:

- Port terminal safety or a simplified MCTS/search layer to C.
