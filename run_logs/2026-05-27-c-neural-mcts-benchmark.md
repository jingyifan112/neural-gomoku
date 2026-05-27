# C Neural MCTS Benchmark

This stage adds C neural MCTS to the C/CPU inference path.

## Python/C consistency test

The C CNN forward pass still matches the PyTorch model after adding C neural MCTS:

policy_logits_max_abs_diff 4.991889e-07
policy_probs_max_abs_diff 1.86264515e-08
value_abs_diff 3.27825546e-07
top_legal_move C=60 Python=60

This confirms that the CNN inference path was not broken by the MCTS integration.

## Tactical benchmark

The C benchmark compared four modes:

direct_policy_accuracy 0/5 0.00%
policy_plus_safety_accuracy 5/5 100.00%
mcts_raw_accuracy 1/5 20.00%
mcts_plus_safety_accuracy 5/5 100.00%

## Interpretation

The full C play-time inference path now runs with:

- CNN policy-value inference
- neural MCTS
- terminal safety

However, raw MCTS is still weak with the current checkpoint. The benchmark shows that terminal safety is currently essential for handling simple tactical cases. MCTS plus safety passes the benchmark, but MCTS alone does not.

## Conclusion

The C neural MCTS migration is functionally complete. The remaining limitation is model/search strength: the current checkpoint and raw MCTS behavior are still not strong enough without terminal safety.

Future improvement should focus on stronger checkpoint training and further debugging/improving raw MCTS behavior, including value backup, player perspective, and search quality.
